import os
from tempfile import NamedTemporaryFile
from typing import List, Set

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, load_only, noload, subqueryload

from zam_repondeur.models import (
    Amendement,
    AmendementList,
    Article,
    Batch,
    DBSession,
    Lecture,
)
from zam_repondeur.resources import LectureResource
from zam_repondeur.services.import_export.json import export_json
from zam_repondeur.services.import_export.pdf import write_pdf, write_pdf_multiple
from zam_repondeur.services.import_export.xlsx import write_xlsx

DOWNLOAD_FORMATS = {
    "json": (export_json, "application/json"),
    "pdf": (write_pdf, "application/pdf"),
    "xlsx": (
        write_xlsx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}


AMDT_OPTIONS = [
    joinedload("user_content"),
    joinedload("location").options(
        joinedload("user_table").joinedload("user").load_only("email", "name")
    ),
    joinedload("article").options(
        load_only("lecture_pk", "mult", "num", "pos", "type"),
        joinedload("user_content"),
    ),
]

EXPORT_OPTIONS = [
    subqueryload("amendements").options(*AMDT_OPTIONS),
    subqueryload("articles").joinedload("user_content"),
]

PDF_OPTIONS = [
    joinedload("dossier").load_only("titre"),
    subqueryload("articles").options(
        joinedload("user_content"),
        subqueryload("amendements").options(
            subqueryload("children"),
            joinedload("user_content").defer("comments"),
            *AMDT_OPTIONS,
        ),
    ),
]


@view_config(context=LectureResource, name="download_amendements")
def download_amendements(context: LectureResource, request: Request) -> Response:

    fmt: str = request.params.get("format", "")
    if fmt not in DOWNLOAD_FORMATS.keys():
        raise HTTPBadRequest(f'Invalid value "{fmt}" for "format" param')

    if fmt == "pdf":
        options = PDF_OPTIONS
    else:
        options = EXPORT_OPTIONS

    lecture = context.model(*options)

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_func, content_type = DOWNLOAD_FORMATS[fmt]
        write_func(lecture, tmp_file_path, request)  # type: ignore

        response = FileResponse(tmp_file_path)
        attach_name = (
            f"lecture-{lecture.chambre}-{lecture.texte.numero}-"
            f"{lecture.organe}.{fmt}"
        )
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


@view_config(context=LectureResource, name="export_xlsx")
def export_xlsx(context: LectureResource, request: Request) -> Response:
    num_params = request.params.getall("n")
    try:
        nums: Set[int] = {int(num) for num in num_params}
    except ValueError:
        raise HTTPBadRequest()

    article_param = request.params.get("article")
    try:
        article_type, article_num, article_mult, article_pos = article_param.split(".")
    except ValueError:
        raise HTTPBadRequest()

    lecture = context.model(noload("amendements"))
    amendements = (
        DBSession.query(Amendement)
        .filter(
            Article.pk == Amendement.article_pk,
            Amendement.lecture == lecture,
            Article.type == article_type,
            Article.num == article_num,
            Article.mult == article_mult,
            Article.pos == article_pos,
            Amendement.num.in_(nums),  # type: ignore
        )
        .options(
            joinedload("user_content"),
            joinedload("location").options(
                joinedload("user_table").joinedload("user").load_only("email", "name")
            ),
        )
    )
    expanded_amendements = list(Batch.expanded_batches(amendements))

    with NamedTemporaryFile() as file_:
        tmp_file_path = os.path.abspath(file_.name)
        write_xlsx(lecture, tmp_file_path, request, amendements=expanded_amendements)
        response = FileResponse(tmp_file_path)

        fmt = "xlsx"
        attach_name = generate_attach_name(
            lecture=lecture,
            article=expanded_amendements[0].article,
            amendements=expanded_amendements,
            extension=fmt,
        )
        response.content_type = DOWNLOAD_FORMATS[fmt][1]
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


@view_config(context=LectureResource, name="export_pdf")
def export_pdf(context: LectureResource, request: Request) -> Response:
    params = request.params.getall("n")
    try:
        nums: List[int] = [int(num) for num in params]
    except ValueError:
        raise HTTPBadRequest()

    article_param = request.params.get("article")
    try:
        article_type, article_num, article_mult, article_pos = article_param.split(".")
    except ValueError:
        raise HTTPBadRequest()

    lecture = context.model(
        noload("amendements"),
        joinedload("dossier").load_only("titre"),
        subqueryload("articles").options(joinedload("user_content"),),
    )
    article_amendements = (
        DBSession.query(Amendement)
        .filter(
            Article.pk == Amendement.article_pk,
            Amendement.lecture == lecture,
            Article.type == article_type,
            Article.num == article_num,
            Article.mult == article_mult,
            Article.pos == article_pos,
        )
        .options(
            joinedload("user_content"),
            joinedload("location").options(
                joinedload("user_table").joinedload("user").load_only("email", "name")
            ),
        )
    )
    amendements = [
        amendement for amendement in article_amendements if amendement.num in nums
    ]
    expanded_amendements = list(Batch.expanded_batches(amendements))
    article = amendements[0].article

    with NamedTemporaryFile() as file_:
        tmp_file_path = os.path.abspath(file_.name)
        write_pdf_multiple(
            lecture=lecture,
            amendements=amendements,
            article_amendements=AmendementList(article_amendements),
            filename=tmp_file_path,
            request=request,
        )

        fmt = "pdf"
        response = FileResponse(tmp_file_path)
        attach_name = generate_attach_name(
            lecture=lecture,
            article=article,
            amendements=expanded_amendements,
            extension=fmt,
        )
        response.content_type = DOWNLOAD_FORMATS[fmt][1]
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


def generate_attach_name(
    lecture: Lecture, article: Article, amendements: List[Amendement], extension: str
) -> str:
    article_name = f"{article.url_key.replace('.', '')}-"
    nb_amendements = len(amendements)
    if nb_amendements > 10:
        amendements_name = f"{nb_amendements}amendements-{amendements[0].num}etc-"
    else:
        amendements_name = (
            f"amendement{'s' if len(amendements) > 1 else ''}-"
            f"{'_'.join(str(amdt.num) for amdt in amendements)}-"
        )
    lecture_name = f"{lecture.chambre}-{lecture.texte.numero}-{lecture.organe}"
    return f"{article_name}{amendements_name}{lecture_name}.{extension}"

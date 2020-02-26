import os
from tempfile import NamedTemporaryFile
from typing import List, Tuple

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

USER_CONTENT_OPTIONS = joinedload("user_content")
LOCATION_OPTIONS = joinedload("location").options(
    joinedload("user_table").joinedload("user").load_only("email", "name")
)
ARTICLE_OPTIONS = joinedload("article").options(
    load_only("lecture_pk", "mult", "num", "pos", "type"), joinedload("user_content"),
)
DOSSIER_OPTIONS = joinedload("dossier").load_only("titre")

EXPORT_OPTIONS = [
    subqueryload("amendements").options(
        USER_CONTENT_OPTIONS, LOCATION_OPTIONS, ARTICLE_OPTIONS,
    ),
    subqueryload("articles").joinedload("user_content"),
]

PDF_OPTIONS = [
    DOSSIER_OPTIONS,
    subqueryload("articles").options(
        USER_CONTENT_OPTIONS,
        subqueryload("amendements").options(
            subqueryload("children"),
            joinedload("user_content").defer("comments"),
            USER_CONTENT_OPTIONS,
            LOCATION_OPTIONS,
            ARTICLE_OPTIONS,
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
    lecture = context.model(noload("amendements"))
    nums, article_param = parse_params(request, lecture=lecture)
    if article_param == "all":
        amendements = (
            DBSession.query(Amendement)
            .join(Article)
            .filter(
                Amendement.lecture == lecture, Amendement.num.in_(nums),  # type: ignore
            )
            .options(USER_CONTENT_OPTIONS, LOCATION_OPTIONS)
        )
    else:
        article_type, article_num, article_mult, article_pos = article_param.split(".")
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
            .options(USER_CONTENT_OPTIONS, LOCATION_OPTIONS)
        )

    expanded_amendements = list(Batch.expanded_batches(amendements))

    with NamedTemporaryFile() as file_:
        tmp_file_path = os.path.abspath(file_.name)
        write_xlsx(lecture, tmp_file_path, request, amendements=expanded_amendements)
        return write_response(
            tmp_file_path=tmp_file_path,
            fmt="xlsx",
            lecture=lecture,
            article_param=article_param,
            amendements=expanded_amendements,
        )


@view_config(context=LectureResource, name="export_pdf")
def export_pdf(context: LectureResource, request: Request) -> Response:
    lecture = context.model(
        noload("amendements"),
        DOSSIER_OPTIONS,
        subqueryload("articles").options(joinedload("user_content")),
    )
    nums, article_param = parse_params(request, lecture=lecture)
    if article_param == "all":
        # TODO: deal with that special case!
        article_amendements = (
            DBSession.query(Amendement)
            .join(Article)
            .filter(Amendement.lecture == lecture,)
            .options(USER_CONTENT_OPTIONS, LOCATION_OPTIONS)
        )
    else:
        article_type, article_num, article_mult, article_pos = article_param.split(".")
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
            .options(USER_CONTENT_OPTIONS, LOCATION_OPTIONS,)
        )

    amendements = [
        amendement for amendement in article_amendements if amendement.num in nums
    ]
    expanded_amendements = list(Batch.expanded_batches(amendements))

    with NamedTemporaryFile() as file_:
        tmp_file_path = os.path.abspath(file_.name)
        write_pdf_multiple(
            lecture=lecture,
            amendements=amendements,
            article_amendements=AmendementList(article_amendements),
            filename=tmp_file_path,
            request=request,
        )
        return write_response(
            tmp_file_path=tmp_file_path,
            fmt="pdf",
            lecture=lecture,
            article_param=article_param,
            amendements=expanded_amendements,
        )


def parse_params(request: Request, lecture: Lecture) -> Tuple[List[int], str]:
    params = request.params.getall("n")
    try:
        nums: List[int] = [int(num) for num in params]
    except ValueError:
        raise HTTPBadRequest()

    total_count_amendements = lecture.nb_amendements
    max_amendements_for_full_index = int(
        request.registry.settings.get("zam.limits.max_amendements_for_full_index", 1000)
    )
    too_many_amendements = total_count_amendements > max_amendements_for_full_index
    default_param = "article.1.." if too_many_amendements else "all"
    article_param = request.params.get("article", default_param)
    return nums, article_param


def write_response(
    tmp_file_path: str,
    fmt: str,
    lecture: Lecture,
    article_param: str,
    amendements: List[Amendement],
) -> FileResponse:
    response = FileResponse(tmp_file_path)
    attach_name = generate_attach_name(
        lecture=lecture,
        article_param=article_param,
        amendements=amendements,
        extension=fmt,
    )
    response.content_type = DOWNLOAD_FORMATS[fmt][1]
    response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
    return response


def generate_attach_name(
    lecture: Lecture, article_param: str, amendements: List[Amendement], extension: str
) -> str:
    lecture_name = f"{lecture.chambre}-{lecture.texte.numero}-{lecture.organe}-"
    article_name = (
        f"{article_param.replace('.', '')}-" if article_param != "all" else ""
    )
    nums = sorted(amdt.num for amdt in amendements)
    nb_amendements = len(nums)
    if nb_amendements > 10:
        amendements_name = f"{nb_amendements}amendements-{nums[0]}etc"
    else:
        amendements_name = (
            f"amendement{'s' if nb_amendements > 1 else ''}-"
            f"{'_'.join(str(num) for num in nums)}"
        )
    return f"{lecture_name}{article_name}{amendements_name}.{extension}"

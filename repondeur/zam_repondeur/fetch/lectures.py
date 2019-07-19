import logging

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.models import DBSession, Dossier, Lecture, Texte
from zam_repondeur.models.events.lecture import LectureCreee


logger = logging.getLogger(__name__)


def get_lectures(dossier: Dossier) -> bool:
    from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements  # Circular.

    changed = False
    dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()
    dossier_ref = dossiers_by_uid[dossier.uid]

    for lecture_ref in dossier_ref.lectures:
        texte = Texte.get_or_create_from_ref(lecture_ref.texte, lecture_ref.chambre)
        lecture = Lecture.create_from_ref(lecture_ref, dossier, texte)
        if lecture is not None:
            changed = True
            LectureCreee.create(request=None, lecture=lecture)

            # Schedule task to run in worker
            DBSession.flush()

            fetch_articles(lecture.pk)
            fetch_amendements(lecture.pk)

    return changed

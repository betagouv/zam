import logging
from typing import Dict

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.models import DBSession, Dossier, Lecture, Texte
from zam_repondeur.models.events.lecture import LectureCreee

logger = logging.getLogger(__name__)


def get_lectures(dossier: Dossier, settings: Dict[str, str]) -> bool:
    from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements  # Circular.

    changed = False

    # First fetch data from existing lectures, starting with recents.
    for lecture in reversed(dossier.lectures):
        # Refetch the lecture to apply the FOR UPDATE.
        lecture = DBSession.query(Lecture).with_for_update().get(lecture.pk)

        # Only fetch articles for recent lectures.
        if lecture.refreshable_for("articles", settings):
            changed |= fetch_articles.call_local(lecture.pk)

        # Only fetch amendements for recent lectures.
        if lecture.refreshable_for("amendements", settings):
            changed |= fetch_amendements.call_local(lecture.pk)

    # Then try to create missing lectures.
    dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()
    dossier_ref = dossiers_by_uid[dossier.uid]

    for lecture_ref in reversed(dossier_ref.lectures):
        texte = Texte.get_or_create_from_ref(lecture_ref.texte, lecture_ref.chambre)
        lecture = Lecture.create_from_ref(lecture_ref, dossier, texte)
        if lecture is not None:
            changed = True
            LectureCreee.create(request=None, lecture=lecture)
            fetch_articles.call_local(lecture.pk)
            fetch_amendements.call_local(lecture.pk)

    return changed

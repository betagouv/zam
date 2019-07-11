import logging

import transaction

from zam_repondeur.dossiers import get_dossiers_legislatifs_from_cache
from zam_repondeur.fetch.an.dossiers.models import DossierRefsByUID
from zam_repondeur.models import Dossier, Lecture
from zam_repondeur.models.events.lecture import LectureCreee


logger = logging.getLogger(__name__)


def get_lectures(dossier: Dossier) -> bool:
    from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements  # Circular.

    changed = False
    dossiers_by_uid: DossierRefsByUID = get_dossiers_legislatifs_from_cache()
    dossier_ref = dossiers_by_uid[dossier.uid]

    for lecture_ref in dossier_ref.lectures:
        lecture = Lecture.create_from_ref(dossier, lecture_ref)
        if lecture is not None:
            changed = True
            LectureCreee.create(request=None, lecture=lecture)
            # Call to fetch_* tasks below being asynchronous, we need to make
            # sure the lecture already exists once and for all in the database
            # for future access. Otherwise, it may create many instances and
            # thus many objects within the database.
            transaction.commit()

            fetch_articles(lecture.pk)
            fetch_amendements(lecture.pk)

    return changed

from dataclasses import fields
from sqlalchemy import inspect

import pytest

from zam_repondeur.models import Amendement


@pytest.mark.parametrize("name", [field.name for field in fields(Amendement)])
def test_amendement_field_is_mapped(name):
    insp = inspect(Amendement)
    mapped_cols = [c_attr.key for c_attr in insp.mapper.column_attrs]
    assert name in mapped_cols


class TestLectureToStr:
    def test_an_seance_publique(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="bla bla",
            organe="PO717460",
        )
        assert (
            str(lecture)
            == "Assemblée nationale, 15e législature, Séance publique, texte nº 269"
        )

    def test_an_commission(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an", session="15", num_texte=269, titre="bla bla", organe="PO59048"
        )
        assert (
            str(lecture)
            == "Assemblée nationale, 15e législature, Commission des finances, texte nº 269"  # noqa
        )

    def test_senat_seance_publique(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            titre="bla bla",
            organe="PO78718",
        )
        assert str(lecture) == "Sénat, session 2017-2018, Séance publique, texte nº 63"

import pytest
import transaction
from sqlalchemy.exc import IntegrityError

EXAMPLES = [
    ("", 0, 0, "0"),
    ("COM-1", 1, 0, "1"),
    ("COM-48 rect.", 48, 1, "48 rect."),
    ("CE208", 208, 0, "208"),
    ("CE|208", 208, 0, "208"),
    ("42", 42, 0, "42"),
    ("42 rect.", 42, 1, "42 rect."),
    ("42 rect. bis", 42, 2, "42 rect. bis"),
    ("42 rect. ter", 42, 3, "42 rect. ter"),
    ("42 rect. nonies", 42, 9, "42 rect. nonies"),
    ("42 rect. novies", 42, 9, "42 rect. nonies"),
    ("42 rect. undecies", 42, 11, "42 rect. undecies"),
]


@pytest.mark.parametrize("text,num,rectif,disp", EXAMPLES)
def test_parse_num(text, num, rectif, disp):
    from zam_repondeur.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif,disp", EXAMPLES)
def test_num_disp(lecture_senat, article1_senat, text, num, rectif, disp):
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=num,
        rectif=rectif,
        auteur="M. Dupont",
        parent=None,
    )
    assert amendement.num_disp == disp


def test_amendement_parent_relationship(amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    a, b = DBSession.query(Amendement).all()

    assert a.parent is None
    assert b.parent is None

    b.parent = a

    # Note: when updating a relationship, the foreign key is only updated on a flush
    DBSession.flush()
    assert b.parent_pk == a.pk


def test_amendement_batches(amendements_an):
    from zam_repondeur.models import DBSession, Amendement, Batch

    a, b = DBSession.query(Amendement).all()

    assert a.location.batch is None
    assert b.location.batch is None

    batch = Batch.create()
    a.location.batch = batch
    b.location.batch = batch

    a, b = DBSession.query(Amendement).all()
    assert a.location.batch == b.location.batch == batch


def test_amendement_unicity(amendements_an, article1av_an):
    from zam_repondeur.models import Amendement, DBSession

    existing = amendements_an[0]
    with transaction.manager, pytest.raises(IntegrityError) as error_info:
        Amendement.create(
            lecture=existing.lecture,
            num=existing.num,
            rectif=existing.rectif + 1,
            article=article1av_an,
            parent=None,
            objet="don't worry, this is an expected error",
        )
        DBSession.flush()
    assert "constraint" in error_info.value._message()


class TestDisplayableIdentiques:
    def test_without_batch(self, amendements_an):
        from zam_repondeur.models import Amendement, DBSession

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Sagesse"
            amendement_999.user_content.avis = "Sagesse"

        amendements_an = DBSession.query(Amendement).all()  # reload

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == [amendement_999]
        assert list(amendement_999._displayable_identiques()) == [amendement_666]

    def test_with_batch(self, amendements_an_batch):
        from zam_repondeur.models import Amendement, DBSession

        amendements_an_batch = DBSession.query(Amendement).all()  # reload
        amendement_666, amendement_999 = amendements_an_batch
        # DBSession.add_all(amendements_an_batch)

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an_batch)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Sagesse"
            amendement_999.user_content.avis = "Sagesse"

        amendements_an_batch = DBSession.query(Amendement).all()  # reload
        amendement_666, amendement_999 = amendements_an_batch

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []


class TestDisplayableIdentiquesAreSimilaire:
    def test_same_avis_and_no_reponse(self, amendements_an):
        from zam_repondeur.models import Amendement, DBSession

        amendements_an = DBSession.query(Amendement).all()

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Favorable"
            amendement_999.user_content.avis = "Favorable"

        amendements_an = DBSession.query(Amendement).all()  # reload

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == [amendement_999]
        assert list(amendement_999._displayable_identiques()) == [amendement_666]
        assert amendement_666.all_displayable_identiques_have_same_response()
        assert amendement_999.all_displayable_identiques_have_same_response()

    def test_same_avis_and_same_reponse(self, amendements_an):
        from zam_repondeur.models import Amendement, DBSession

        amendements_an = DBSession.query(Amendement).all()

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Favorable"
            amendement_999.user_content.avis = "Favorable"
            amendement_666.user_content.reponse = "Une réponse"
            amendement_999.user_content.reponse = "Une réponse"

        amendements_an = DBSession.query(Amendement).all()  # reload

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == [amendement_999]
        assert list(amendement_999._displayable_identiques()) == [amendement_666]
        assert amendement_666.all_displayable_identiques_have_same_response()
        assert amendement_999.all_displayable_identiques_have_same_response()

    def test_same_avis_and_same_reponse_with_spaces(self, amendements_an):
        from zam_repondeur.models import Amendement, DBSession

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Favorable"
            amendement_999.user_content.avis = "Favorable"
            amendement_666.user_content.reponse = "Une réponse"
            amendement_999.user_content.reponse = "  Une réponse   " ""

        amendements_an = DBSession.query(Amendement).all()  # reload

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == [amendement_999]
        assert list(amendement_999._displayable_identiques()) == [amendement_666]
        assert amendement_666.all_displayable_identiques_have_same_response()
        assert amendement_999.all_displayable_identiques_have_same_response()

    def test_different_avis(self, amendements_an):
        from zam_repondeur.models import Amendement, DBSession

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Favorable"
            amendement_999.user_content.avis = "Défavorable"

        amendements_an = DBSession.query(Amendement).all()  # reload

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == [amendement_999]
        assert list(amendement_999._displayable_identiques()) == [amendement_666]
        assert not amendement_666.all_displayable_identiques_have_same_response()
        assert not amendement_999.all_displayable_identiques_have_same_response()

    def test_different_reponse(self, amendements_an):
        from zam_repondeur.models import Amendement, DBSession

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == []
        assert list(amendement_999._displayable_identiques()) == []

        with transaction.manager:
            DBSession.add_all(amendements_an)
            amendement_666.id_identique = 41
            amendement_999.id_identique = 41
            amendement_666.id_discussion_commune = 42
            amendement_999.id_discussion_commune = 42
            amendement_666.user_content.avis = "Favorable"
            amendement_999.user_content.avis = "Favorable"
            amendement_666.user_content.reponse = "Une réponse"
            amendement_999.user_content.reponse = "Une autre réponse"

        amendements_an = DBSession.query(Amendement).all()  # reload

        amendement_666, amendement_999 = amendements_an

        assert list(amendement_666._displayable_identiques()) == [amendement_999]
        assert list(amendement_999._displayable_identiques()) == [amendement_666]
        assert not amendement_666.all_displayable_identiques_have_same_response()
        assert not amendement_999.all_displayable_identiques_have_same_response()


@pytest.mark.usefixtures("amendements_repository")
class TestAmendementEdition:
    def test_amendement_is_not_being_edited(self, amendements_an):
        assert not amendements_an[0].is_being_edited

    def test_amendement_is_being_edited(self, amendements_an, user_david_table_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.add_amendement(amendements_an[0])
        amendements_an[0].start_editing()
        assert amendements_an[0].is_being_edited

    def test_amendement_no_longer_being_edited(
        self, amendements_an, user_david_table_an
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.add_amendement(amendements_an[0])
        amendements_an[0].start_editing()
        assert amendements_an[0].is_being_edited
        amendements_an[0].stop_editing()
        assert not amendements_an[0].is_being_edited


class TestHasObjet:
    def test_non_empty_objet(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.objet = "bla bla"

        DBSession.add(amendements_an[0])
        assert amendements_an[0].user_content.has_objet

    def test_empty_objet(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.objet = ""

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_objet

    def test_whitespace_objet(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.objet = "    "

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_objet

    def test_empty_paragraph_objet(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.objet = "<p></p>"

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_objet

    def test_null_objet(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.objet = None

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_objet


class TestHasReponse:
    def test_non_empty_reponse(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.reponse = "bla bla"

        DBSession.add(amendements_an[0])
        assert amendements_an[0].user_content.has_reponse

    def test_empty_reponse(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.reponse = ""

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_reponse

    def test_whitespace_reponse(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.reponse = "    "

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_reponse

    def test_empty_paragraph_reponse(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.reponse = "<p></p>"

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_reponse

    def test_null_reponse(self, amendements_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(amendements_an[0])
            amendements_an[0].user_content.reponse = None

        DBSession.add(amendements_an[0])
        assert not amendements_an[0].user_content.has_reponse

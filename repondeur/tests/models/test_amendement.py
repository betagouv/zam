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

    assert a.batch is None
    assert b.batch is None

    batch = Batch.create()
    a.batch = batch
    b.batch = batch

    a, b = DBSession.query(Amendement).all()
    assert a.batch == b.batch == batch


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


def test_amendement_displayable_identiques(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Sagesse"
    amendement_999.user_content.avis = "Sagesse"

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]


def test_amendement_displayable_identiques_with_batch(amendements_an_batch):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Sagesse"
    amendement_999.user_content.avis = "Sagesse"

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []


def test_amendement_displayable_identiques_are_similaires(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Favorable"
    amendement_999.user_content.avis = "Favorable"

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]
    assert amendement_666.displayable_identiques_are_similaires
    assert amendement_999.displayable_identiques_are_similaires


def test_amendement_displayable_identiques_are_similaires_reponses(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Favorable"
    amendement_999.user_content.avis = "Favorable"
    amendement_666.user_content.reponse = "Une réponse"
    amendement_999.user_content.reponse = "Une réponse"

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]
    assert amendement_666.displayable_identiques_are_similaires
    assert amendement_999.displayable_identiques_are_similaires


def test_amendement_displayable_identiques_are_similaires_reponses_with_spaces(
    amendements_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Favorable"
    amendement_999.user_content.avis = "Favorable"
    amendement_666.user_content.reponse = "Une réponse"
    amendement_999.user_content.reponse = """
    Une
 réponse"""

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]
    assert amendement_666.displayable_identiques_are_similaires
    assert amendement_999.displayable_identiques_are_similaires


def test_amendement_displayable_identiques_are_similaires_reponses_with_tags(
    amendements_an
):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Favorable"
    amendement_999.user_content.avis = "Favorable"
    amendement_666.user_content.reponse = "Une réponse"
    amendement_999.user_content.reponse = """
    <p>Une
 réponse</p>"""

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]
    assert amendement_666.displayable_identiques_are_similaires
    assert amendement_999.displayable_identiques_are_similaires


def test_amendement_displayable_identiques_are_not_similaires(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Favorable"
    amendement_999.user_content.avis = "Défavorable"

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]
    assert not amendement_666.displayable_identiques_are_similaires
    assert not amendement_999.displayable_identiques_are_similaires


def test_amendement_displayable_identiques_are_not_similaires_reponses(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.displayable_identiques == []
    assert amendement_999.displayable_identiques == []

    amendement_666.id_identique = 41
    amendement_999.id_identique = 41
    amendement_666.id_discussion_commune = 42
    amendement_999.id_discussion_commune = 42
    amendement_666.user_content.avis = "Favorable"
    amendement_999.user_content.avis = "Favorable"
    amendement_666.user_content.reponse = "Une réponse"
    amendement_999.user_content.reponse = "Une autre réponse"

    assert amendement_666.displayable_identiques == [amendement_999]
    assert amendement_999.displayable_identiques == [amendement_666]
    assert not amendement_666.displayable_identiques_are_similaires
    assert not amendement_999.displayable_identiques_are_similaires


@pytest.mark.usefixtures("amendements_repository")
class TestAmendementEdition:
    def test_amendement_is_not_being_edited(self, amendements_an):
        assert not amendements_an[0].is_being_edited

    def test_amendement_is_being_edited(self, amendements_an, user_david_table_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.amendements.append(amendements_an[0])
        amendements_an[0].start_editing()
        assert amendements_an[0].is_being_edited

    def test_amendement_no_longer_being_edited(
        self, amendements_an, user_david_table_an
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(user_david_table_an)
            user_david_table_an.amendements.append(amendements_an[0])
        amendements_an[0].start_editing()
        assert amendements_an[0].is_being_edited
        amendements_an[0].stop_editing()
        assert not amendements_an[0].is_being_edited

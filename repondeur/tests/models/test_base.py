class TestRepr:
    def test_no_repr_keys(self):
        from sqlalchemy import Column, Integer
        from zam_repondeur.models.base import Base

        class Foo(Base):
            __tablename__ = "foo"
            id = Column(Integer, primary_key=True)

        foo = Foo()
        assert repr(foo) == f"<Foo at 0x{id(foo):x}>"

    def test_dossier(self, dossier_plfss2018):
        expected_repr = (
            "<Dossier pk=1 slug='plfss-2018'"
            " titre='Sécurité sociale : loi de financement 2018'"
            " uid='DLR5L15N36030' owned_by_team=None>"
        )
        assert repr(dossier_plfss2018) == expected_repr

    def test_lecture(self, lecture_an):
        expected_repr = (
            "<Lecture pk=1 chambre=<Chambre.AN: 'Assemblée nationale'>"
            " organe='PO717460' partie=None>"
        )
        assert repr(lecture_an) == expected_repr

    def test_article(self, article1_an):
        expected_repr = (
            "<Article pk=1 lecture_pk=1 type='article' num='1' mult='' pos=''>"
        )
        assert repr(article1_an) == expected_repr

    def test_amendement(self, amendements_an):
        expected_repr = (
            "<Amendement pk=1 num=666 rectif=0 lecture_pk=1 article_pk=1"
            " parent_pk=None>"
        )
        assert repr(amendements_an[0]) == expected_repr

    def test_team(self, team_zam):
        expected_repr = "<Team name='Zam'>"
        assert repr(team_zam) == expected_repr

    def test_user(self, user_david):
        expected_repr = "<User name='David' email='david@exemple.gouv.fr' teams=[]>"
        assert repr(user_david) == expected_repr

    def test_user_with_team(self, team_zam, user_david):
        user_david.teams.append(team_zam)
        expected_repr = (
            "<User name='David' email='david@exemple.gouv.fr' "
            "teams=[<Team name='Zam'>]>"
        )
        assert repr(user_david) == expected_repr

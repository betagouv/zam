class TestRepr:
    def test_no_repr_keys(self):
        from sqlalchemy import Column, Integer
        from zam_repondeur.models.base import Base

        class Foo(Base):
            __tablename__ = "foo"
            id = Column(Integer, primary_key=True)

        foo = Foo()
        assert repr(foo) == f"<Foo at 0x{id(foo):x}>"

    def test_lecture(self, lecture_an):
        expected_repr = (
            "<Lecture pk=1 chambre='an' session='15' organe='PO717460' num_texte=269 "
            "partie=None owned_by_team=None>"
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
        expected_repr = "<User name='David' email='david@example.com' teams=[]>"
        assert repr(user_david) == expected_repr

    def test_user_with_team(self, team_zam, user_david):
        user_david.teams.append(team_zam)
        expected_repr = (
            "<User name='David' email='david@example.com' teams=[<Team name='Zam'>]>"
        )
        assert repr(user_david) == expected_repr

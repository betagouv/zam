import pytest


@pytest.fixture
def amendements(db, lecture_an, article1_an):
    from zam_repondeur.models import Amendement

    return [
        Amendement.create(
            lecture=lecture_an, article=article1_an, num=num, position=position
        )
        for position, num in enumerate((1, 2, 3, 4), 1)
    ]


class TestCollapsedBatches:
    def test_unbatched_amendements_are_left_alone(self, amendements):
        from zam_repondeur.models.amendement import Batch

        assert [a.num for a in Batch.collapsed_batches(amendements)] == [1, 2, 3, 4]

    def test_batched_amendements_are_grouped(self, amendements):
        from zam_repondeur.models.amendement import Batch

        amendements[0].batch = amendements[2].batch = Batch.create()
        assert [a.num for a in Batch.collapsed_batches(amendements)] == [1, 2, 4]


class TestExpandedBatches:
    def test_unbatched_amendements_are_left_alone(self, amendements):
        from zam_repondeur.models.amendement import Batch

        assert [a.num for a in Batch.expanded_batches(amendements)] == [1, 2, 3, 4]

    def test_batched_amendements_are_expanded(self, amendements):
        from zam_repondeur.models.amendement import Batch

        amendements[0].batch = amendements[2].batch = Batch.create()
        assert {
            a.num
            for a in Batch.expanded_batches(
                [amendements[0], amendements[1], amendements[3]]
            )
        } == {1, 2, 3, 4}


@pytest.fixture
def batched_amendements(lecture_an, article1_an):
    from zam_repondeur.models.amendement import Amendement, Batch

    amendements = [
        Amendement.create(lecture=lecture_an, article=article1_an, num=i + 1)
        for i in range(10)
    ]

    amendements[0].batch = amendements[3].batch = Batch.create()
    amendements[2].batch = amendements[4].batch = amendements[8].batch = Batch.create()

    return amendements


def test_reversibility(batched_amendements):
    from zam_repondeur.models.amendement import Batch

    assert set(
        Batch.expanded_batches(Batch.collapsed_batches(batched_amendements))
    ) == set(batched_amendements)

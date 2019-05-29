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

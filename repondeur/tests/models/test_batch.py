from datetime import timedelta
from itertools import islice
from random import randint, shuffle
from typing import Any, Iterable

from hypothesis import given, settings
from hypothesis.strategies import integers

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


def partition(
    li: Iterable[Any], min_chunk: int = 1, max_chunk: int = 100
) -> Iterable[Any]:
    it = iter(li)
    while True:
        nxt = list(islice(it, randint(min_chunk, max_chunk)))
        if nxt:
            yield nxt
        else:
            break


@given(integers(min_value=2, max_value=27))
@settings(deadline=timedelta(milliseconds=500))
def test_reversibility(lecture_an, article1_an, nb_amendements):
    from zam_repondeur.models.amendement import Amendement, Batch

    amendements = [
        Amendement.create(lecture=lecture_an, article=article1_an, num=i + 1)
        for i in range(nb_amendements)
    ]

    shuffle(amendements)

    batches = []
    for chunk in partition(amendements, max_chunk=max(1, len(amendements))):
        if len(chunk) < 2:
            continue
        batch = Batch.create()
        batch.amendements.extend(chunk)
        batches.append(batch)

    assert not any(len(batch.amendements) == 1 for batch in batches)

    assert set(Batch.expanded_batches(Batch.collapsed_batches(amendements))) == set(
        amendements
    )

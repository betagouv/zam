from typing import TYPE_CHECKING, Iterable, List, Optional, Set

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from .base import Base, DBSession

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .amendement import Amendement  # noqa


class Batch(Base):
    __tablename__ = "batches"

    pk: int = Column(Integer, primary_key=True)

    _amendements = relationship("Amendement", back_populates="batch")

    __repr_keys__ = ("pk",)

    @property
    def amendements(self) -> List["Amendement"]:
        return sorted(self._amendements)

    @property
    def nums(self) -> List[int]:
        return [amendement.num for amendement in self.amendements]

    @property
    def groupes(self) -> Set[str]:
        return deduplicate(
            amendement.groupe or amendement.auteur for amendement in self.amendements
        )

    @classmethod
    def create(cls) -> "Batch":
        batch = cls()
        DBSession.add(batch)
        return batch

    @staticmethod
    def collapsed_batches(amendements: Iterable["Amendement"]) -> List["Amendement"]:
        """
        Filter amendements to only include the first one from each batch
        """

        def _collapsed_batches(
            amendements: Iterable["Amendement"]
        ) -> Iterable["Amendement"]:
            seen_batches: Set[Batch] = set()
            for amendement in amendements:
                if amendement.batch:
                    if amendement.batch in seen_batches:
                        continue
                    seen_batches.add(amendement.batch)
                yield amendement

        return list(_collapsed_batches(amendements))

    @staticmethod
    def expanded_batches(amendements: Iterable["Amendement"]) -> Iterable["Amendement"]:
        """
        Expand list of amendements to include those in batches
        """
        for amendement in amendements:
            if amendement.batch:
                yield from amendement.batch.amendements
            else:
                yield amendement


def deduplicate(items: Iterable[Optional[str]]) -> Set[str]:
    return set(filter(None, items))

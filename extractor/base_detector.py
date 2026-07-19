from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass(order=True)
class Candidate(Generic[T]):
    score: int
    value: T
    source: str


class BaseDetector(Generic[T]):

    def __init__(self):

        self.candidates: List[Candidate[T]] = []

    def clear(self):

        self.candidates.clear()

    def add_candidate(
        self,
        value: T,
        score: int,
        source: str
    ):

        if value is None:
            return

        value = self.normalize(value)

        if not self.validate(value):
            return

        for candidate in self.candidates:

            if candidate.value == value:

                if score > candidate.score:

                    candidate.score = score
                    candidate.source = source

                return

        self.candidates.append(

            Candidate(

                score=score,

                value=value,

                source=source

            )

        )

    def normalize(self, value: T) -> T:

        return value

    def validate(self, value: T) -> bool:

        return True

    def best(self) -> Optional[Candidate[T]]:

        if not self.candidates:
            return None

        self.candidates.sort(reverse=True)

        return self.candidates[0]

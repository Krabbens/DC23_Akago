from typing import AsyncGenerator

from morfeusz2 import Morfeusz


class Analyzer:
    def __init__(self) -> None:
        self._morf = Morfeusz()

    def inflect(self, lemma: str, tag: str) -> str:
        results = self._morf.generate(lemma)

        return next(result[0] for result in results if result[2] == tag)


async def get_analyzer() -> AsyncGenerator[Analyzer, None]:
    analyzer = Analyzer()

    yield analyzer

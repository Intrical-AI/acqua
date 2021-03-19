import re
from typing import Any


from .indexExtractors import AbstractIndexExtractor
from .points import AvgPoint, CounterPoint
from .utils import decouple


class AbstractValueExtractor:

    def __init__(self, index_extractor: AbstractIndexExtractor) -> None:
        self.index_extractor = index_extractor

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class BinaryPatternExtractor(AbstractValueExtractor):

    POINT_CLASS = CounterPoint
    KEY = None

    def __init__(self, index_extractor: AbstractIndexExtractor, KEY: str, regex: str, unpack: str) -> None:
        self.index_extractor = index_extractor
        self.KEY = KEY
        self.regex = re.compile(regex, re.IGNORECASE)
        self.unpack = unpack

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        for text in decouple(doc, self.unpack):
            res = self.regex.search(text)
            if res:
                return 1

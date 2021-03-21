import re
from typing import Any


from .indexExtractors import AbstractIndexExtractor
from .points import CountedListPoint
from .utils import decouple


class AbstractValueExtractor:

    def __init__(self, index_extractor: AbstractIndexExtractor) -> None:
        self.index_extractor = index_extractor

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class BinaryPatternExtractor(AbstractValueExtractor):

    POINT_CLASS = CountedListPoint
    KEY = None

    def __init__(self,
                 index_extractor: AbstractIndexExtractor,
                 KEY: str,
                 regex: str,
                 unpack: str,
                 identifier=lambda x: 1) -> None:
        self.index_extractor = index_extractor
        self.KEY = KEY
        self.regex = re.compile(regex, re.IGNORECASE)
        self.unpack = unpack
        self.identifier = identifier

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        res = []
        for text in decouple(doc, self.unpack):
            res = self.regex.search(text)
            if res:
                return res.append(self.identifier(doc))
        return res

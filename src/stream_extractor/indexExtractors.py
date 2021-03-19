from typing import Any
from .utils import decouple


class AbstractIndexExtractor:

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class NameExtractor(AbstractIndexExtractor):

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        return [self.name]

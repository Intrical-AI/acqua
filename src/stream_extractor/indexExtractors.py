from typing import Any
from .utils import decouple


class AbstractIndexExtractor:

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError

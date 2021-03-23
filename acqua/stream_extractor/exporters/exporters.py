from typing import Any

from ..utils import rec_dd


class AbstractExporter:

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class InMemoryExporter:

    def __init__(self) -> None:
        self.values = rec_dd()

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        keys, x, value = item
        d = self.values
        for _key in keys[:-1]:
            d = d[_key]
        d[keys[-1]] = x

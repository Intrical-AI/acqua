from typing import Any

from ..utils import rec_dd


class AbstractExporter:

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class InMemoryExporter:

    def __init__(self) -> None:
        self.values = rec_dd()

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        index, key, date_p, date, x, value = item
        self.values[index][key][date_p] = x

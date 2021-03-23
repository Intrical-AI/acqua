from typing import Any


class AbstractKVExtractors:

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError

from typing import Any

from stream_extractor.points import AvgPoint, CounterPoint


class AbstractValueExtractor:

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class SentimentScoreExtractor(AbstractValueExtractor):

    POINT_CLASS = AvgPoint
    KEY = 'sentiment'

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        return doc.sentiment_score

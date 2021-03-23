import re
from typing import Any
import dateutil.parser

from stream_extractor.utils import decouple
from stream_extractor.points import AvgPoint, CounterPoint, AvgListPoint
from stream_extractor.kvextractors import AbstractKVExtractors


class CompanyKVextractor(AbstractKVExtractors):

    POINT_CLASS = AvgListPoint

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        indexes = decouple(item, 'sentenceScore[].entityLink[].entity.company')
        return list(
            set(
                map(
                    lambda x: x.clean_name,
                    filter(
                        lambda x: x != {},
                        indexes
                    )
                )
            )
        )

    def _level0(self, item, key):
        return 'sentiment'

    def _level1(self, item, key):
        return dateutil.parser.parse(item.publish_date).date().isoformat()

    def get_value(self, doc, key):
        return doc.sentiment_score, int(doc.meta.id)


class KeywordsKVextractor(AbstractKVExtractors):

    POINT_CLASS = CounterPoint

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        indexes = decouple(item, 'sentenceScore[].entityLink[].entity.company')
        return list(
            set(
                map(
                    lambda x: x.clean_name,
                    filter(
                        lambda x: x != {},
                        indexes
                    )
                )
            )
        )

    def _level0(self, item, key):
        return 'keywords'

    def _level1(self, item, key):
        indexes = decouple(item, 'keywords[].value')
        return list(
            set(
                map(
                    lambda x: x,
                    filter(
                        lambda x: x != {},
                        indexes
                    )
                )
            )
        )

    def get_value(self, doc, key):
        return 1


class SectorPatternExtractor(AbstractKVExtractors):

    POINT_CLASS = CounterPoint

    def __init__(self,
                 name: str,
                 regex: str,
                 unpack: str):

        self.name = name
        self.regex = re.compile(regex, re.IGNORECASE)
        self.unpack = unpack

    def __call__(self, item):
        for text in decouple(item, self.unpack):
            res = self.regex.search(text)
            if res is None:
                return
        names = ['sentiment', 'orgs', 'places']
        return [self.name + '_' + name for name in names]

    def filter_entity_kind(self, item, type):
        indexes = decouple(item, 'sentenceScore[].entityLink[].entity')
        return list(
            map(
                lambda x: str(x.id),
                filter(
                    lambda x: x.kind == type,
                    indexes
                )
            )
        )

    def _level0(self, item, key):
        for i in ['sentiment', 'places', 'orgs']:
            if i in key:
                return i

    def _level1(self, item, key):
        if 'sentiment' in key:
            indexes = decouple(item, 'categoryDoc[].category.value')
            return indexes
        if 'places' in key:
            return self.filter_entity_kind(item, 'GPE')
        if 'orgs' in key:
            return self.filter_entity_kind(item, 'ORGANIZATION')

    def get_value(self, item, keys):
        if keys[0] == 'sentiment':
            return item.sentiment_score
        return 1

import pickle
import sys
import logging
from typing import Any
from dotenv import load_dotenv

sys.path.append('../..')

from stream_extractor.extractor import StreamFactory
from stream_extractor.indexExtractors import AbstractIndexExtractor, NameExtractor
from stream_extractor.streams import ElasticSearchStream, ElasticSearchOrderedStream
from stream_extractor.utils import decouple
from stream_extractor.valueExtractors import AbstractValueExtractor, BinaryPatternExtractor
from stream_extractor.exporters.exporters import InMemoryExporter
from stream_extractor.exporters.db import MongoDbExporter
from stream_extractor.resumers import LastIdResumer
from stream_extractor.points import AvgPoint, CounterPoint

load_dotenv()
logging.basicConfig(level=logging.INFO)


class CompanyIndexExtractor(AbstractIndexExtractor):

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        indexes = decouple(doc, 'sentenceScore[].entityLink[].entity.company')
        return list(
            map(
                lambda x: x.clean_name,
                filter(
                    lambda x: x != {},
                    indexes
                )
            )
        )


class CompanyIndexExtractor(AbstractIndexExtractor):

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        indexes = decouple(doc, 'sentenceScore[].entityLink[].entity.company')
        return list(
            map(
                lambda x: x.clean_name,
                filter(
                    lambda x: x != {},
                    indexes
                )
            )
        )


def create_sector_extractors(sectors):
    res = []
    for sector in sectors:
        regex = '|'.join(sector)
        res.append(BinaryPatternExtractor(NameExtractor(sector[0]), 'sector', regex, 'text', lambda doc: int(doc.meta.id)))
    return res


class SentimentScoreExtractor(AbstractValueExtractor):

    POINT_CLASS = AvgPoint
    KEY = 'sentiment'

    def __call__(self, doc, *args: Any, **kwds: Any) -> Any:
        return [doc.sentiment_score]


resumer = LastIdResumer()

stream = ElasticSearchStream()
index_extractor = CompanyIndexExtractor()
names = [('carbonated soft drinks',), ('proptech',), ('alternative protein',), ('drinks',), ('diabetes',), ('tyre',),
         ('Artificial Intelligence',), ('covid',), ('agtech',), ('ketchup',), ('semiconductor',), ('Computer Science',), ('iot',)]
value_extractors = [
    SentimentScoreExtractor(index_extractor),
    *create_sector_extractors(names)]
exporters = [
    InMemoryExporter(),
    # MongoDbExporter()
]

extractor = StreamFactory(
    stream,
    'publish_date',
    value_extractors,
    10,
    exporters=exporters
)

extractor.run()
# exporters[1].bulk_insert()
print(exporters[0].values)

with open('dump', 'wb') as outfile:
    pickle.dump(exporters[0], outfile)

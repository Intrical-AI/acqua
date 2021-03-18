import sys
from typing import Any
from dotenv import load_dotenv

sys.path.append('../..')

from stream_extractor.extractor import StreamFactory
from stream_extractor.indexExtractors import AbstractIndexExtractor
from stream_extractor.streams import ElasticSearchStream
from stream_extractor.utils import decouple
from stream_extractor.valueExtractors import SentimentScoreExtractor
from stream_extractor.exporter import InMemoryExporter

load_dotenv()


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


stream = ElasticSearchStream()
index_extractor = CompanyIndexExtractor()
value_extractors = [SentimentScoreExtractor()]
exporter = InMemoryExporter()

extractor = StreamFactory(
    stream,
    index_extractor,
    'publish_date',
    value_extractors,
    1,
    exporter
)

extractor.run()
print(extractor.values)
print(exporter.values)

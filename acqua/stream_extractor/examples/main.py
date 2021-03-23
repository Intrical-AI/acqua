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
from stream_extractor.exporters.exporters import InMemoryExporter
from stream_extractor.exporters.db import DynamoDBExporter, MongoDbExporter
from stream_extractor.resumers import LastIdResumer
from stream_extractor.points import AvgPoint, CounterPoint, AvgListPoint
from stream_extractor.kvextractors import AbstractKVExtractors

try:
    from extractors import *
    from db import *
except:
    from .extractors import *
    from .db import *


load_dotenv()
logging.basicConfig(level=logging.INFO)


def create_sector_extractors(sectors):
    res = []
    for sector in sectors:
        regex = '|'.join(sector)
        res.append(SectorPatternExtractor(sector[0], regex, 'text'))
    return res


resumer = LastIdResumer()

stream = ElasticSearchStream()


value_extractors = create_sector_extractors(sectors_names)
exporters = [
    InMemoryExporter(),
    MongoDbExporter()
]

extractor = StreamFactory(
    stream,
    'publish_date',
    value_extractors,
    num_max_items=100,
    exporters=exporters
)

extractor.run()

# exporters[1].bulk_insert()
print(exporters[0].values['covid_sector_places'])

with open('dump', 'wb') as outfile:
    pickle.dump(exporters[0], outfile)

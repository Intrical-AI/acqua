import typing
import dateutil.parser

from rx.subject import Subject

from .streams import AbstractStream
from .indexExtractors import AbstractIndexExtractor
from .exporter import AbstractExporter
from .utils import rec_dd


class StreamFactory:

    def __init__(self,
                 stream: AbstractStream,
                 index_extractor: AbstractIndexExtractor,
                 datefield: str,
                 value_extractors: list,
                 num_max_items=float('inf'),
                 exporter: AbstractExporter = None):

        self.stream = stream
        self.index_extractor = index_extractor
        self.datefield = datefield
        self.value_extractors = value_extractors
        self.max_num_items = num_max_items
        self.values = rec_dd()
        self.exporter = exporter
        self._product_subject = Subject()

        if exporter:
            self._product_subject.subscribe(exporter)

    def run(self):
        for i, doc in self.stream.subscribe():
            if i > self.max_num_items:
                return
            date = dateutil.parser.parse(getattr(doc, self.datefield))
            date_p = (date.year, date.month, date.day)
            indexes = self.index_extractor(doc)
            for extractor in self.value_extractors:
                value = extractor(doc)

                for index in indexes:
                    x = self.values[index][extractor.KEY][date_p]
                    if x == {}:
                        x = extractor.POINT_CLASS()
                        self.values[index][extractor.KEY][date_p] = x
                    x(value)
                    if self.exporter:
                        self._product_subject.on_next((index, extractor.KEY, date_p, x))

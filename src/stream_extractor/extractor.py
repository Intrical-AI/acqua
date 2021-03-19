import typing
from typing import List
import dateutil.parser

from rx.subject import Subject

from .streams import AbstractStream
from .indexExtractors import AbstractIndexExtractor
from .exporter import AbstractExporter
from .valueExtractors import AbstractValueExtractor
from .utils import rec_dd


class StreamFactory:

    def __init__(self,
                 stream: AbstractStream,
                 index_extractor: AbstractIndexExtractor,
                 datefield: str,
                 value_extractors: List[AbstractValueExtractor],
                 num_max_items=float('inf'),
                 exporter: AbstractExporter = None,
                 save_every=1):

        self.stream = stream
        self.index_extractor = index_extractor
        self.datefield = datefield
        self.value_extractors: List[AbstractValueExtractor] = value_extractors
        self.max_num_items = num_max_items
        self.values = rec_dd()
        self.exporter = exporter
        self._product_subject = Subject()
        self.doc_counter = 0
        self.save_every = save_every

        if exporter:
            self._product_subject.subscribe(exporter)

    def load_state(self):
        self.stream.load_state()

    def run(self):
        self.load_state()
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
            if self.doc_counter % self.save_every == 0:
                self.stream.save_state()
            self.doc_counter += 1

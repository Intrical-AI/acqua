from typing import List
from copy import deepcopy

from rx.subject import Subject


from .streams import AbstractStream
from .indexExtractors import AbstractIndexExtractor
from .exporters.exporters import AbstractExporter
from .kvextractors import AbstractKVExtractors
from .utils import rec_dd


class StreamFactory:

    def __init__(self,
                 stream: AbstractStream,
                 datefield: str,
                 value_extractors: List[AbstractKVExtractors],
                 num_max_items=float('inf'),
                 exporters: List[AbstractExporter] = [],
                 save_every=1):

        self.stream = stream
        self.datefield = datefield
        self.value_extractors: List[AbstractKVExtractors] = value_extractors
        self.max_num_items = num_max_items
        self.values = rec_dd()
        self.exporters = exporters
        self._product_subject = Subject()
        self.doc_counter = 0
        self.save_every = save_every

        for exporter in exporters:
            self._product_subject.subscribe(exporter)

    def load_state(self):
        self.stream.load_state()

    def run(self):
        self.load_state()

        for i, doc in self.stream.subscribe():
            if i > self.max_num_items:
                return
            print(i, end='\r')
            for extractor in self.value_extractors:
                keys = extractor(doc)
                if keys is None:
                    continue
                keys = list(map(lambda key: ([key], 0), keys))
                while len(keys) > 0:
                    keyset = keys.pop()
                    nested_keys, level = keyset
                    key = nested_keys[-1]

                    level_function = getattr(extractor, '_level' + str(level), False)
                    if not level_function:
                        # do insert pass
                        value = extractor.get_value(doc, nested_keys)
                        if value is None:
                            continue
                        d = self.values
                        for _key in nested_keys[:-1]:
                            d = d[_key]
                        if d[nested_keys[-1]] == {}:
                            x = extractor.POINT_CLASS()
                        else:
                            x = d[nested_keys[-1]]
                        x(value)
                        if self.exporters:
                            self._product_subject.on_next((nested_keys, x, value))
                        break

                    new_nested_keys = level_function(doc, key)
                    if not isinstance(new_nested_keys, list):
                        new_nested_keys = [new_nested_keys]

                    for key in new_nested_keys:
                        new_key_set = deepcopy(keyset)
                        nested_keys, level = new_key_set
                        nested_keys.append(key)
                        keys.append((nested_keys, level + 1))
            if self.doc_counter % self.save_every == 0:
                self.stream.save_state()
            self.doc_counter += 1

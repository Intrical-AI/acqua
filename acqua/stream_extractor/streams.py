import os
import json
import logging
import queue

from simple_settings import settings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import connections

from .resumers import AbstractResumer

logger = logging.getLogger()


class AbstractStream:

    resumer = None

    def __init__(self, resumer: AbstractResumer = None) -> None:
        self.resumer: AbstractResumer = resumer

    def subscribe(self):
        raise NotImplementedError()

    def save_state(self, gentle=True, *args, **kwargs):
        assert self.resumer is not None or gentle, '''
        To save the input stream state, you need to pass the 
        resumer to the instance
        ---> Stream(resumer)
        '''
        if self.resumer:
            self.resumer.save(self.__getstate__(), *args, **kwargs)

    def __setstate__(self):
        return super().__setstate__()

    def __getstate__(self):
        raise NotImplementedError

    def load_state(self):
        if self.resumer:
            self.resumer = self.resumer.load()
            self.last_id = self.resumer.last_id
            logger.info('ElasticSearchStream loaded correctly, last_id: ' + str(self.last_id))


class ElasticSearchStream(AbstractStream):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        connections.create_connection(hosts=[os.environ['ELASTICSEARCH_HOST']],
                                      http_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                      timeout=20)

        self.client = Elasticsearch()

    def subscribe(self):
        s = Search(index='intrical3').query('match_all')

        for i, doc in enumerate(s.scan()):
            yield i, doc


class ElasticSearchOrderedStream(ElasticSearchStream):

    last_id = 0
    page_size = settings.ELASTICSEARCH_PAGE_SIZE

    def subscribe(self):
        while True:
            logger.info(self.last_id)
            s = Search(index='intrical').query('match_all')\
                .filter('range', id={'gt': self.last_id + 1, 'lt': self.last_id + self.page_size})
            for i, doc in enumerate(s.scan()):
                yield i, doc
                self.last_id = int(doc.meta.id)
            self.last_id += self.page_size

    def __setstate__(self, last_id):
        self.last_id = last_id

    def __getstate__(self):
        return self.last_id


class FileStream(AbstractStream):

    def __init__(self, filename, format='json', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.filename = filename
        if format == 'json':
            with open(filename, 'r') as infile:
                self.doc = json.load(infile)
                assert isinstance(self.doc, list), 'The file must contain a list of items'
        else:
            raise NotImplementedError('Non Json format not supported yet')

    def subscribe(self):
        return iter(self.doc)


class BufferStream(AbstractStream):

    def __init__(self) -> None:
        self.queue = queue.Queue()
        self.counter = 0

    def subscribe(self):
        while True:
            doc= self.queue.get()
            yield self.counter, doc
            self.counter += 1
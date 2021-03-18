import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import connections

from .resumers import AbstractResumer


class AbstractStream:

    def __init__(self, resumer: AbstractResumer = None) -> None:
        self.resumer: AbstractResumer = resumer

    def subscribe(self):
        raise NotImplementedError()

    def save_state(self, *args, **kwargs):
        assert self.resumer is not None, '''
        To save the input stream state, you need to pass the 
        resumer to the instance
        ---> Stream(resumer)
        '''
        self.resumer.save(*args, **kwargs)


class ElasticSearchStream(AbstractStream):

    def __init__(self) -> None:
        super().__init__()

        connections.create_connection(hosts=[os.environ['ELASTICSEARCH_HOST']],
                                      http_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
                                      timeout=20)

        self.client = Elasticsearch()

    def subscribe(self):
        s = Search(index='intrical').query('match_all')

        for i, doc in enumerate(s.scan()):
            yield i, doc

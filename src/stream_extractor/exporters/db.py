import os
import pymongo
import boto3

from simple_settings import settings
from frozendict import frozendict
from typing import Any

from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer

from .exporters import AbstractExporter
from ..utils import rec_dd


class MongoDbExporter(AbstractExporter):

    def __init__(self) -> None:
        super().__init__()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://{os.environ.get('MONGO_DB_USER')}:{os.environ.get('MONGO_DB_PASSWORD')}@cluster0.jo4tb.mongodb.net/{os.environ.get('MONGO_DB_DB')}?retryWrites=true&w=majority")

        self.db = self.client.cache
        self.collection = self.db.sector
        self.batch = set()
        self.values = rec_dd()
        self._doc_counter = 0
        self.collection_counter = 0

    def build_id(self, values):
        id = '_'.join(values)
        return {'_id': id}

    def bulk_upsert(self):
        to_update = []
        for key in self.batch:
            item = self.values[key]
            record = item
            record['_id'] = key
            to_update.append(record)

        self.collection.update_many(to_update, upsert=True)

    def online_upsert(self, keys, obj, value):
        item = self.collection.find_one({'_id': keys[0]})
        if item is not None:
            d = item
            for last_i, k in enumerate(keys[1:-1]):
                last_d = d
                d = d.get(k, None)
                if d is None:
                    break
            if d is not None:
                d[keys[-1]] = {**d[keys[-1]], **(obj.__class__(d[keys[-1]]) + obj).to_dict()}
            else:
                for key in keys[1 + last_i:-1]:
                    nd = {}
                    last_d[key] = nd
                    last_d = nd
                nd[keys[-1]] = obj.to_dict()

            id = {'_id': item['_id']}
            self.collection.replace_one(id, item, upsert=True)

    def bulk_insert(self):
        to_insert = []

        for k, item in self.values.items():
            record = item
            record['_id'] = k
            to_insert.append(record)
        if settings.MONGO_DB_COLLECTION_OVERRIDE:
            self.collection.remove()
            self.collection.insert_many(to_insert)
        else:
            collection = getattr(self.db, 'collection' + str(self.collection_counter))
            collection.insert_many(to_insert)
            self.collection_counter += 1

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        keys, x, value = item

        d = self.values[keys[0]]
        for _key in keys[1:-1]:
            d = d[_key]

        if not settings.MONGO_DB_COLLECTION_BULK:
            self.batch.add(keys[0])
        if settings.MONGO_DB_ONLINE:
            d[keys[-1]] = x
            self.online_upsert(keys, x, value)
        else:
            d[keys[-1]] = x.to_dict()
        self._doc_counter += 1
        if settings.MONGO_DB_ITERATIONS > 0 and self._doc_counter % settings.MONGO_DB_ITERATIONS == 0:
            if settings.MONGO_DB_COLLECTION_BULK:
                self.bulk_insert()
            else:
                self._doc_counter = 0
                self.bulk_upsert()
                self.batch = set()


class DynamoDBExporter(AbstractExporter):

    def __init__(self) -> None:
        super().__init__()
        if 'DYNAMODB_ENDPOINT_URL' in os.environ:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ['DYNAMODB_ENDPOINT_URL'])
        else:
            self.dynamodb = boto3.resource('dynamodb')

        self.table = self.dynamodb.Table(os.environ['DYNAMODB_TABLENAME'])

        if settings.DYNAMODB_COLLECTION_OVERRIDE:
            try:
                self.table.delete()
            except:
                # pass in case the table does not exist
                pass
            try:
                self.dynamodb.create_table(
                    TableName=os.environ['DYNAMODB_TABLENAME'],
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'  # Partition key
                        },
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        },

                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
                )
            except:
                # pass in case the table does not exist
                pass

        self.values = rec_dd()
        self.serializer = TypeSerializer()

    def bulk_insert(self):
        to_insert = []

        for k, item in self.values.items():
            record = item
            record['id'] = k
            to_insert.append(record)
        with self.table.batch_writer() as batch:
            for r in to_insert:
                batch.put_item(r)

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        keys, x, value = item

        # only bulk insert is supported for now
        d = self.values[keys[0]]
        for _key in keys[1:-1]:
            d = d[_key]
        new_x = {}
        for k, v in x.to_dict().items():
            if isinstance(v, float):
                v = Decimal(v)
            new_x[k] = v
        d[keys[-1]] = self.serializer.serialize(new_x)

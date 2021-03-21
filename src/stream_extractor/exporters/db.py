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
        self.collection = self.db.testCollection
        self.batch = set()
        self.values = rec_dd()
        self._doc_counter = 0
        self.collection_counter = 0

    def build_id(self, values):
        id = '_'.join(values)
        return {'_id': id}

    def bulk_upsert(self):
        to_insert = {}
        for mongo_id, item in self.batch:
            index, key, date_p, date, x, value = item

            old_value = self.collection.find_one(mongo_id)
            if old_value is not None:
                del old_value['_id']
                x_old = x.__class__(old_value)
                # this is to check if the stored values has the necessary values, in case subsititute with
                # the new one
                try:
                    new_value = x.__class__(old_value) + x
                except:
                    new_value = x

                record = new_value.to_dict()
                date = date.isoformat()
                self.collection.update_one(mongo_id, {"$set": {date: record}}, upsert=True)
            else:
                record = x.to_dict()
                date = date.isoformat()
                if mongo_id['_id'] in to_insert:
                    self.collection.insert_many(to_insert.values())
                    to_insert = {}
                else:
                    to_insert[mongo_id['_id']] = {date: record, **mongo_id}

        if to_insert:
            self.collection.insert_many(to_insert.values())

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

        if settings.MONGO_DB_COLLECTION_BULK:
            d = self.values[keys[0]]
            for _key in keys[1:-1]:
                d = d[_key]
            d[keys[-1]] = x.to_dict()
        else:
            self.batch.add((frozendict(mongo_id), tuple(item)))
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
                    TableName='cache',
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

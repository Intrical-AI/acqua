import os
import pymongo

from typing import Any

from .exporters import AbstractExporter


class MongoDbExporter(AbstractExporter):

    def __init__(self) -> None:
        super().__init__()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://{os.environ.get('MONGO_DB_USER')}:{os.environ.get('MONGO_DB_PASSWORD')}@cluster0.jo4tb.mongodb.net/{os.environ.get('MONGO_DB_DB')}?retryWrites=true&w=majority")

        self.db = self.client.cache
        self.collection = self.db.testCollection

    def build_id(self, index, key):

        id = '_'.join([index, key])
        return {'_id': id}

    def __call__(self, item, *args: Any, **kwds: Any) -> Any:
        index, key, date_p, date, x, value = item
        mongo_id = self.build_id(index, key)

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
            self.collection.insert_one({date: record, **mongo_id})

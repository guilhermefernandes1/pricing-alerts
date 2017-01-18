import uuid

from src.common.database import Database
import src.models.stores.constants as store_constants
import src.models.stores.errors as store_errors


class Store(object):
    def __init__(self, name, url_prefix, tag_name, query, _id=None):
        self.name = name
        self.url_prefix = url_prefix
        self.tag_name = tag_name
        self.query = query
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Store {}>".format(self.name)

    def get_tag_name(self):
        return self.tag_name

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url_prefix": self.url_prefix,
            "tag_name": self.tag_name,
            "query": self.query
        }

    @classmethod
    def get_by_id(cls, id):
        return cls(**Database.find_one(store_constants.COLLECTION, {"_id": id}))

    def save_to_mongo(self):
        Database.update(store_constants.COLLECTION, {"_id": self._id}, self.json())

    @classmethod
    def get_by_name(cls, name):
        return cls(**Database.find_one(store_constants.COLLECTION, {"name": name}))

    @classmethod
    def get_by_url_prefix(cls, url_prefix):
        return cls(**Database.find_one(store_constants.COLLECTION, {"url_prefix": {"$regex": '^{}'.format(url_prefix)}}))

    @classmethod
    def find_by_url(cls, url):
        """
        Return a store from a url like "http://www.johnlewis.com/item/sdfj4h5g4g21k.html"
        :param url: The item's URL
        :return: a Store, or raises a StoreNotFoundException if no store matches the URL
        """
        for i in range(0, len(url)+1):
            try:
                store = cls.get_by_url_prefix(url[:i])
                return store
            except:
                raise store_errors.\
                    StoreNotFoundException("The URL Prefix used to find the store didn't give us any results!")

    @classmethod
    def all(cls):
        return [cls(**item) for item in Database.find(store_constants.COLLECTION, {})]

    def remove_store(self):
        Database.remove(store_constants.COLLECTION, {'_id': self._id})

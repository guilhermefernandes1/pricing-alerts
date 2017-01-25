import uuid

from bs4 import BeautifulSoup
import requests
import re
import src.models.items.constants as item_constants

from src.common.database import Database
from src.models.stores.store import Store


class Item(object):
    def __init__(self, name, url, price=None, _id=None):
        self.name = name
        self.url = url
        self.store = Store.find_by_url(url)
        self.tag_name = self.store.get_tag_name()
        self.query = self.store.query
        self.price = None if price is None else price
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Item {} with URL {}>".format(self.name, self.url)

    def load_price(self):
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()
        print("******************************")
        print(string_price)

        pattern = re.compile("(\d+.\d+)")
        match = pattern.search(string_price)

        self.price = float(match.group())

        return self.price

    def save_to_mongo(self):
        Database.update(item_constants.COLLECTION, {'_id': self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url": self.url,
            "price": self.price
        }

    @classmethod
    def get_by_item_id(cls, item_id):
        return cls(**Database.find_one(item_constants.COLLECTION, {"_id": item_id}))

    def get_id(self):
        return self._id

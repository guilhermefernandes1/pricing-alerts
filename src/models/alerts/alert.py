import uuid

import datetime
import requests
import src.models.alerts.constants as alert_constants
from src.common.database import Database
from src.models.items.item import Item


class Alert(object):
    def __init__(self, user_email, price_limit, item_id, activated=True, last_checked=None, _id=None):
        self.user_email = user_email
        self.price_limit = price_limit
        self.item = Item.get_by_item_id(item_id)
        self.last_checked = datetime.datetime.utcnow() if last_checked is None else last_checked
        self._id = uuid.uuid4().hex if _id is None else _id
        self.activated = activated

    def __repr__(self):
        return "<Alert for {} on item {} with price {}>".format(self.user_email, self.item.name, self.price_limit)

    def send(self):
        return requests.post(
            alert_constants.URL,
            auth=("api", alert_constants.API_KEY),
            data={
                "from": alert_constants.FROM,
                "to": self.user_email,
                "subject": "Price limit reached for {}".format(self.item.name),
                "text": "We've found a deal ({})".format(self.item.url)
            }
        )

    @classmethod
    def find_needing_update(cls, minutes_since_update=alert_constants.ALERT_TIMEOUT):
        last_updated_limit = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes_since_update)
        return [cls(**elem) for elem in Database.find(alert_constants.COLLECTION,
                                                      {"last_checked": {"$lte": last_updated_limit},
                                                       "activated": True})]

    def save_to_mongo(self):
        Database.update(alert_constants.COLLECTION, {"_id": self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "price_limit": self.price_limit,
            "last_checked": self.last_checked,
            "user_email": self.user_email,
            "item_id": self.item.get_id(),
            "activated": self.activated
        }

    def load_item_price(self):
        self.item.load_price()
        self.send_email_if_price_reached()
        self.last_checked = datetime.datetime.utcnow()
        self.item.save_to_mongo()
        self.save_to_mongo()
        return self.item.price

    def send_email_if_price_reached(self):
        if self.item.price < self.price_limit:
            self.send()

    @classmethod
    def get_alerts_by_user_email(cls, user_email):
        return [cls(**elem) for elem in Database.find(alert_constants.COLLECTION, {"user_email": user_email})]

    @classmethod
    def get_by_id(cls, alert_id):
        return cls(**Database.find_one(alert_constants.COLLECTION, {'_id': alert_id}))

    def deactivate(self):
        self.activated = False
        self.save_to_mongo()

    def activate(self):
        self.activated = True
        self.save_to_mongo()

    def remove_alert(self):
        Database.remove(alert_constants.COLLECTION, {"_id": self._id})

    def get_id(self):
        return self._id

import uuid

from src.common.database import Database
from src.common.utils import Utils

import src.models.users.constants as users_constants
import src.models.users.errors as user_errors
from src.models.alerts.alert import Alert


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<User {}>".format(self.email)

    @staticmethod
    def is_login_valid(email, password):
        """
        This method verifies if a login is valid and if its password matches
        :param email: The user's email
        :param password: A sha512 hashed password
        :return: True if is valid, false otherwise
        """

        user_data = Database.find_one(users_constants.COLLECTION, {"email": email})
        if user_data is None:
            raise user_errors.UserNotExistsError('Your user does not exists.')
        if not Utils.check_hashed_password(password, user_data['password']):
            raise user_errors.IncorrectPasswordError('Your password is wrong.')

        return True

    @staticmethod
    def register_user(email, password):
        """
        This method verifies if the user exists. If not, registers him.
        :param email:
        :param password:
        :return:
        """

        user_data = Database.find_one(users_constants.COLLECTION, {"email": email})

        if user_data is not None:
            raise user_errors.UserAlreadyRegisteredError('The user already exists.')
        if not Utils.email_is_valid(email):
            raise user_errors.InvalidEmailError('Not a valid email.')

        User(email, Utils.hash_password(password)).save_to_db()

        return True

    def save_to_db(self):
        Database.insert(users_constants.COLLECTION, self.json())

    def json(self):
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password
        }

    @classmethod
    def get_user_by_email(cls, email):
        return cls(**Database.find_one(users_constants.COLLECTION, {"email": email}))

    def get_alerts(self):
        return Alert.get_alerts_by_user_email(self.email)

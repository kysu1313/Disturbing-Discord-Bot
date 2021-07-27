
import redis
import hashlib
import json
import ast
from helpers.user import User

class BotCache:
    def __init__(self):
        self.redis = redis.Redis(
            host= 'localhost',
            port= '6379')

    def get_value(self, key):
        rconn = self.redis
        value = rconn.get(key)
        to_return = json.loads(value)
        return rconn.get(key)
        
    def set_value(self, key, value):
        rconn = self.redis
        to_insert = json.dumps(value)
        rconn.set(key, to_insert)
        
    def set_values(self, keys, values):
        rconn = self.redis
        count = 0
        for value in values:
            to_insert = json.dumps(value)
            rconn.set(keys[count], to_insert)

    def __create_key(self, user_id, server_id):
        key = str(user_id) + ":" + str(server_id)
        return key

    def update_cache_user(self, user_id, server_id, username=None, bank=None, wallet=None, messages=None, userLevel=None, experience=None, emojiSent=None, reactionsReceived=None, dateUpdated=None):
        data = {}
        key = self.__create_key(user_id, server_id)
        user = self.get_cache_user(user_id, server_id)
        if user is not None:
            #TODO: Fix User object --->
            if user.username is None:
                user.username = username
            if user.bank is None:
                user.bank = bank
            if user.wallet is None:
                user.wallet = wallet
            if user.messages is None:
                user.messages = messages
            if user.userLevel is None:
                user.userLevel = userLevel
            if user.experience is None:
                user.experience = experience
            if user.emojiSent is None:
                user.emojiSent = emojiSent
            if user.reactionsReceived is None:
                user.reactionsReceived = reactionsReceived
            if user.dateUpdated is None:
                user.dateUpdated = dateUpdated
            #data = json.dumps(user)
            self.set_value(key, data)
        else:
            data[key] = {}
            data[key]["user_id"] = user_id
            data[key]["server_id"] = server_id
            if username is not None:
                data[key]["username"] = username
            if bank is not None:
                data[key]["bank"] = bank
            if wallet is not None:
                data[key]["wallet"] = wallet
            if messages is not None:
                data[key]["messages"] = messages
            if userLevel is not None:
                data[key]["userLevel"] = userLevel
            if experience is not None:
                data[key]["experience"] = experience
            if emojiSent is not None:
                data[key]["emojiSent"] = emojiSent
            if reactionsReceived is not None:
                data[key]["reactionsReceived"] = reactionsReceived
            if dateUpdated is not None:
                data[key]["dateUpdated"] = dateUpdated
            self.set_value(key, data)

    def get_cache_user(self, user_id, server_id):
        key = self.__create_key(user_id, server_id)
        dd = self.get_value(key)
        if dd is None or dd == b'{}':
            return None
        dd = dd.decode("UTF-8")
        data = ast.literal_eval(dd)
        user = User(user_id, server_id)
        if "username" in data[key] and data[key]["username"] is not None:
            user.username = data[key]["username"]
        if "bank" in data[key] and data[key]["bank"] is not None:
            user.bank = data[key]["bank"]
        if "wallet" in data[key] and data[key]["wallet"] is not None:
            user.wallet = data[key]["wallet"]
        if "messages" in data[key] and data[key]["messages"] is not None:
            user.messages = data[key]["messages"]
        if "userLevel" in data[key] and data[key]["userLevel"] is not None:
            user.userLevel = data[key]["userLevel"]
        if "experience" in data[key] and data[key]["experience"] is not None:
            user.experience = data[key]["experience"]
        if "emojiSent" in data[key] and data[key]["emojiSent"] is not None:
            user.emojiSent = data[key]["emojiSent"]
        if "reactionsReceived" in data[key] and data[key]["reactionsReceived"] is not None:
            user.reactionsReceived = data[key]["reactionsReceived"]
        if "dateUpdated" in data[key] and data[key]["dateUpdated"] is not None:
            user.dateUpdated = data[key]["dateUpdated"]
        return user

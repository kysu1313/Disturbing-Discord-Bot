
import redis

class BotCache:
    def __init__(self):
        self.redis = redis.Redis(
            host= 'localhost',
            port= '6379')

    async def get_rconn(self):
        rconn = self.redis.get_connection()
        return rconn

    async def get_value(self, key):
        rconn = await self.get_rconn()
        return rconn.get(key)
        
    async def set_value(self, key, value):
        rconn = await self.get_rconn()
        rconn.set(key, value)
        
    async def set_values(self, keys, values):
        rconn = await self.get_rconn()
        count = 0
        for key in keys:
            rconn.set(key, values[count])

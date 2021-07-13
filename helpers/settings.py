import os


class Settings:
    def __init__(self, is_production=False):
        self.is_production = is_production
        self.members = []

    def get_bot_id(self):
        bot_id = ""
        if self.is_production:
            bot_id = os.environ['bot-id']
        else:
            bot_id = os.environ['test-discord-token']
        return bot_id

    def get_is_production(self):
        return self.is_production

    def get_bot_token(self):
        token = ""
        if self.is_production:
            token = os.environ['discord-token']
        else:
            token = os.environ['test-discord-token']
        return token
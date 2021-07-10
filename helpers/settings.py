import os


class Settings:
    def __init__(self, is_production=False):
        self.is_production = is_production

    def get_bot_id(self):
        bot_id = ""
        if self.is_production:
            bot_id = os.environ['test-bot-id']
        else:
            bot_id = os.environ['test-discord-token']
        return bot_id

    def get_bot_token(self):
        token = ""
        if self.is_production:
            token = os.environ['test-discord-token']
        else:
            token = os.environ['discord-token']
        return token
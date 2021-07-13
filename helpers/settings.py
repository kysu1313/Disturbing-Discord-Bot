import os


class Settings:
    def __init__(self, is_production=False):
        self.is_production = is_production
        self.token = ""
        self.id = ""
        self.members = []

    def get_bot_id(self):
        if self.is_production:
            self.id = os.environ['bot-id']
        else:
            self.id = os.environ['test-discord-token']
        return self.id

    def get_is_production(self):
        return self.is_production

    def get_bot_token(self):
        if self.is_production:
            self.token = os.environ['discord-token']
        else:
            self.token = os.environ['test-discord-token']
        return self.token
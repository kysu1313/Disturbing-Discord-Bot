import requests
import json
import cryptocompare

class Apis:
    def get_joke(self):
        try:
            response = requests.get("https://official-joke-api.appspot.com/random_joke") 
            jid = 0
            joke_type = ""
            setup = ""
            punchline = ""
            if response is not None:
                data = json.loads(response.text)
                jid = data.get("id")
                joke_type = data.get("type")
                setup = data.get("setup")
                punchline = data.get("punchline")
            return setup, punchline
        except Exception as e:
            print("Error: {}".format(e))
            return None

    def get_crypto_price(self, coin):
        price = cryptocompare.get_price(coin, 'USD')
        return price

    def get_skills(self, name):
        try:
            response = requests.get("https://pokeapi.co/api/v2/{}/{}".format("pokemon", name))
            skills = []
            abilities = []
            if response is not None:
                data = json.loads(response.text)
                skills = data.get("abilities")
                for skill in skills:
                    abilities.append(skill['ability']['name'])
            return abilities
        except Exception as e:
            print("Error: {}".format(e))
            return None

    def get_doggo(self):
        try:
            response = requests.get("https://api.thedogapi.com/v1/images/search")
            name = ""
            url = ""
            breeds = ""
            if response is not None:
                data = json.loads(response.text)
                try:
                    breeds = data[0]["breeds"]
                    name = breeds[0].get("name")
                except Exception as e:
                    pass
                if name == "":
                    name = "random doggy"
                url = data[0]["url"]
            return name, url
        except Exception as e:
            print("Error: {}".format(e))
            return None
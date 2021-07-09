import chatterbot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.comparisons import LevenshteinDistance
#from chatterbot.response_selection import GetFirstResponse
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import sqlite3


bot = ChatBot(
    'robot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
    ],
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.90,
            'statement_comparison_function': LevenshteinDistance,
            #'response_selection_method': chatterbot.response_selection.
        },
        'chatterbot.logic.MathematicalEvaluation'
    ],
    database_uri='sqlite:///database.db',
    read_only=True
)


## training corpus list
## Disable these two lines below AFTER first run when a *.db file is generated in project directory
trainer = ChatterBotCorpusTrainer(bot)
trainer.train("static/chatterbot_data.yml")
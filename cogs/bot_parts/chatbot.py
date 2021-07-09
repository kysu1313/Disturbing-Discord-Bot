from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.comparisons import LevenshteinDistance
import sqlite3
import chatterbot
import json
import os

comments = []
replies = []

#def import_db(filename):
#    conn = sqlite3.connect(filename)
#    c = conn.cursor()
#    c.execute("SELECT parent, comment FROM parent_reply;")
#    for parent, comment in c:
#        if parent == None or comment == None:
#            pass
#        elif (max(len(comment.split(' ')), len(parent.split(' '))) < 10) and (min(len(comment.split(' ')), len(parent.split(' '))) > 0):
#            comments.append(parent)
#            comments.append(comment)

#import_db("G:\\PROGRAMS\\Python\\ChatBot-V2\\2018-06-3.db")

#file_path = os.path.join(os.getcwd(),'chatterbot_data.json')
#with open(file_path, 'w') as f:
#    json.dump(comments, f)

#bot = ChatBot("Ron Obvious")

bot = ChatBot(
    'robot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
    ],
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'wut?',
            'maximum_similarity_threshold': 0.90,
            'statement_comparison_function': LevenshteinDistance,
            #'response_selection_method': chatterbot.response_selection.get_first_response
        },
        'chatterbot.logic.MathematicalEvaluation'
    ],
    database_uri='sqlite:///database.db',
    read_only=True
)


## training corpus list
## Disable these two lines below AFTER first run when a *.db file is generated in project directory
trainer = ChatterBotCorpusTrainer(bot)
file_path = os.path.join(os.getcwd(),'chatterbot_data.yml')
#trainer.train(file_path)
trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations"
)

#conversation = list(zip(comments, replies))

conversation = comments

#conversation = [
#    "Hello",
#    "Hi there!",
#    "How are you doing?",
#    "I'm doing great.",
#    "That is good to hear",
#    "Thank you.",
#    "You're welcome."
#]

#trainer = ListTrainer(bot)

#trainer.train(conversation)

#print("training complete")
#bot = ChatBot('Norman')
#bot = ChatBot(
#    'Norman',
#    storage_adapter='chatterbot.storage.SQLStorageAdapter',
#    logic_adapters=[
#        'chatterbot.logic.MathematicalEvaluation',
#        'chatterbot.logic.TimeLogicAdapter'
#    ],
#    database_uri='sqlite:///database.sqlite3'
#)

while True:
    try:
        bot_input = bot.get_response(input())
        print(bot_input)

    except(KeyboardInterrupt, EOFError, SystemExit):
        break
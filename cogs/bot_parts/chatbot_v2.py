from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import sqlite3

comments = []
replies = []

def import_db(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT parent, comment FROM parent_reply;")
    for parent, comment in c:
        comments.append(parent)
        comments.append(comment)

import_db("G:\\PROGRAMS\\Python\\ChatBot-V2\\2018-06-3.db")

chatbot = ChatBot("Ron Obvious")

conversation = comments

part_lengths = len(conversation) / 20
curr = 0
for i in range(0, 20):
    sub_list = conversation[curr:curr+part_lengths]
    curr = part_lengths
    part_lengths *= 2
    

trainer = ListTrainer(chatbot)

trainer.train(conversation)

print("training complete")
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

#while True:
#    try:
#        bot_input = bot.get_response(input())
#        print(bot_input)

#    except(KeyboardInterrupt, EOFError, SystemExit):
#        break
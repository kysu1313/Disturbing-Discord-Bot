import discord
from discord.ext import commands
import os
import time
#from helpers.settings import Settings
import json
import random

IMAGES = [
    ["cherry", "./images/cherry.png"],
    ["diamond", "./images/diamond.png"],
    ["grapes", "./images/grapes.png"],
    ["heart", "./images/heart.png"],
    ["seven", "./images/seven.png"],
]


wheel1 = IMAGES[random.randint(0, len(IMAGES) - 1)]
pass
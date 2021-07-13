import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from cogs.bot_parts.apis import Apis
from cogs.commands import Commands
from helpers.settings import Settings
import random
import re
import time
import random
import os
import platform
from distutils.command.config import config
from boto.s3.connection import S3Connection

coins = ['AUR','BCC','BCH','BTC','DASH','DOGE','EOS','ETC','ETH','GRC','LTC','KOI','MZC','NANO','NEO','NMC','NXT','POT','PPC','TIT','USDC','USDT','VTC','XEM','XLM','XMR','XPM','XRP','XVG','ZEC']
greetings = ['hi', 'hey', 'yo', 'hello', 'whats up', "what's up", 'yoo', 'yooo', 'sup', 'ayo', 'ayoo']
times = {}
description = '''None of your business, mkay'''
BOT_ID = ""
ENABLED = True
settings = None


#################################################
####### IMPORTANT: CHANGE FOR PRODUCTION ######## 
#################################################
PROD_MODE = True


intents = discord.Intents.all()
#intents.members = True
#intents.guilds = True
#intents.messages = True
#intents.bans = True
client = discord.Client()
bot = Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")


@bot.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await member.send(server, fmt.format(member, server))

@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    print(
        f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.event
async def on_message(message):
    global ENABLED
    if '!startbot' in message.content:
        ENABLED = True
    if ENABLED:
        if message.author == bot.user:
            return

        if message.author.name == "Lil-Bot" or message.author.name == "Test-Bot": 
            return

        msg = message.content.lower()

        if '!stopbot' in msg:
            ENABLED = False
            return 

        api = Apis()
        items = msg.split(' ')
        for item in items:
            if item.upper() in coins:
                await message.channel.send('The current price of {} is ${}'.format(item.upper(), api.get_crypto_price(item.upper())))

        if 'yay' in msg.split(' '):
            await message.channel.send("🤩")

        if '🔪' in msg:
            await message.channel.send('🔫🙂')

        if 'bitch' in msg.lower():
            await message.channel.send("fuck you bitch")

        if 'kys' in msg.split(' '):
            await message.channel.send(':sob:')

        if 'kms' in msg.split(' '):
            await message.channel.send('🙂  Here, take this 🔫')

        if any(word in msg.split(" ") for word in greetings):
            await message.channel.send('hi 🙂')

        if 'skills:' in msg.lower():
            item = message.channel.content.split(":")[1].strip()
            result = api.get_skills(item)
            if result is None:
                await message.channel.send('No skills found 😢')
            else:
                await message.channel.send(', '.join(result))

        await bot.process_commands(message)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == '__main__':
    ENABLED = True
    settings = Settings(PROD_MODE)
    TOKEN = settings.get_bot_token()
    bot.run(TOKEN)



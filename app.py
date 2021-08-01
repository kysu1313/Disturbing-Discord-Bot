

from discord.ext import commands, tasks
from discord.ext.commands import Bot
from cogs.bot_parts.apis import Apis
from cogs.commands import Commands
from helpers.settings import Settings
from helpers.stats import Stats
import discord
import random
import re
import time
import random
import os
import platform
from distutils.command.config import config
import matplotlib
import matplotlib.pyplot as plt
import json
from helpers.dbconn import DbConn

coins = ['AUR','BCH','BTC','DASH','DOGE','EOS','ETC','ETH','GRC','LTC','MZC','NANO','NEO','NMC','NXT','POT','PPC','TIT','USDC','USDT','VTC','XEM','XLM','XMR','XPM','XRP','XVG','ZEC']
greetings = ['hi', 'hey', 'yo', 'hello', 'whats up', "what's up", 'yoo', 'yooo', 'sup', 'ayo', 'ayoo', 'howdy']
times = {}
description = '''None of your business, mkay'''
BOT_ID = ""
ENABLED = True
settings = None
STARTING_MONEY = 500


#################################################
####### IMPORTANT: CHANGE FOR PRODUCTION ########
#################################################
PROD_MODE = False


intents = discord.Intents.all()
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
    '''
        Welcome new users to server.

        Attributes:
            member: person to welcome
        '''
    conn = DbConn()
    conn.add_user(member.user.id, member.guild.id, STARTING_MONEY, STARTING_MONEY, member.user.name)
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await member.send(server, fmt.format(member, server))

@bot.event
async def on_command_completion(ctx):
    '''
        Print commands as they are executed.

        Attributes:
            ctx: user who sent command
        '''
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
    '''
        General message listener
        Attributes:
            message: the message to check
    '''
    global ENABLED
    if '!startbot' in message.content:
        await message.channel.send("I'm alive! 😃")
        ENABLED = True
    if ENABLED:
        if message.author == bot.user:
            return

        if message.author.name == "Lil-Bot" or message.author.name == "Test-Bot":
            return

        msg = message.content.lower()

        if '!stopbot' in msg:
            ENABLED = False
            await message.channel.send("ok, I'll be quiet 😔")
            return

        api = Apis()
        items = msg.split(' ')
        for item in items:
            if item.upper() in coins:
                # TODO: This should be moved...
                old_coin = api.get_crypto_price(item.upper())
                price = old_coin.price
                last_time = old_coin.dateAdded
                plt.figure(figsize=(1,1))
                fig, ax = plt.subplots()
                fig.set_size_inches(5, 2.25, 0)
                plt.legend(facecolor="white", edgecolor="yellow")
                ax.set_facecolor("#2F3136")
                fig.set_facecolor("#2F3136")
                frame1 = plt.gca()
                frame1.axes.get_xaxis().set_visible(False)
                plt.plot([1, 2, 3, 4],[old_coin.oldestPrice, old_coin.olderPrice, old_coin.midPrice, old_coin.price], label=f'{item.upper()}')
                plt.savefig(fname='figure.jpg', edgecolor='w')
                diff = price - old_coin.midPrice
                percent_change = diff / old_coin.midPrice * 100
                await message.channel.send(f'The current price of {item.upper()} is ${price}. It changed by {percent_change:.3f}% since last check.', file=discord.File('./figure.jpg'))

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

        stats = Stats(bot)

        await bot.process_commands(message)
        await stats.update_stats(message)

# Activate all commands in cog classes
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# Run the bot
if __name__ == '__main__':
    ENABLED = True
    settings = Settings(PROD_MODE)
    TOKEN = settings.get_bot_token()
    print("Setting tokens")
    bot.run(TOKEN)

    print("Tokens set successfully")


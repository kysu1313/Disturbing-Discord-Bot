import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import os
import time
from helpers.settings import Settings
from helpers.dbconn import DbConn
import json
import random
from cogs.commands import Commands
from discord.ext.commands.errors import MissingPermissions
import re
#from emoji import UNICODE_EMOJI


class Stats:
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.id

    @commands.Cog.listener()
    async def on_ready(self):
        print("Stats connected")

    async def update_stats(self, message):
        conn = DbConn()
        #user = conn.get_user_in_server(message.author.name, message.author.id, message.guild.id)
        #new_messages = user.messages + 1
        #new_exp = user.experience + 1
        #new_level = self.get_level(user.messages)
        ##emojis = 0
        ##for item in message.split(" "):
        ##    if item in UNICODE_EMOJI['en']:
        ##        emojis = 1
        ##        break
        ##new_emojis = user.emojiCount + emojis
        #new_date = time.datetime.now()
        #conn.update_user_values(message.author.id, message.guild.id, message.author.name, user.bank, user.wallet, new_messages, new_level, new_exp, 0, 0, new_date)
        return
    
    async def get_level(self, messages):
        if messages > 10:
            return 1
        if messages > 40:
            return 2
        if messages > 90:
            return 3
        if messages > 150:
            return 4
        if messages > 250:
            return 5
        if messages > 400:
            return 6
        if messages > 600:
            return 7
        if messages > 900:
            return 8
        if messages > 1100:
            return 9
        if messages > 1500:
            return 10
        return 0

    def get_guild_id(self, ctx):
        guild_id = ctx.message.guild.id
        return guild_id

    def get_guild_name(self, ctx):
        guild_name = ctx.message.guild.name
        return guild_name

    def get_user_id(self, ctx):
        user_id = ctx.message.author.id
        return user_id

def setup(bot):
    bot.add_cog(DiscRoles(bot))
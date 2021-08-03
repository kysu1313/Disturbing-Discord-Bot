
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext.commands.errors import MissingPermissions
from helpers.settings import Settings
from cogs.commands import Commands
from helpers.dbconn import DbConn
from discord.ext import commands
import discord
import random
import json
import time
import re
import os

class Controls(commands.Cog):

    _slow_mode = False
    _slow_time = 15

    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()


    @has_permissions(administrator=True)
    @commands.command(name='slowmode', help='!slowmode <1-60 sec?> <on / off?>, enable / disable slowmode. Default time = 15 sec.')
    async def slowmode(self, ctx, enable=None, time=None):
        server_id =  ctx.message.guild.id
        conn = DbConn()
        if enable is None:
            enable = 0
        if time is None:
            time = 15
        conn.set_slow_mode(server_id, enable, time)
        await ctx.send("SlowMode set to {}".format(enable))

    async def getslowmode(self, server_id):
        conn = DbConn()
        enabled, time = conn.get_slow_mode(server_id)
        return enabled, time


    #@has_permissions(administrator=True)
    #@commands.command(name='slowmode', help='!slowmode <1-60 sec?> <on / off?>, enable / disable slowmode. Default time = 15 sec.')
    #async def slowmode(self, ctx, enabled=None, time=None):
    #    '''
    #    (Admin) Enable or disable slowmode.
    #    Set certain time interval between messages.

    #    Attributes:
    #        ctx: user who sent command
    #        time: number of seconds between messages
    #        enabled: set slowmode "on" or "off"
    #    '''
    #    if enabled is not None:
    #        if enabled == "on":
    #            Controls._slow_mode = True
    #            #app.SLOW_MODE = True
    #            Controls._slow_time = 15
    #        elif enabled == "off":
    #            Controls._slow_mode = False
    #            app.SLOW_MODE = False
    #    if time is not None:
    #        Controls._slow_time = time
    #    await ctx.send("SlowMode set to {}".format(enabled))


    #@slowmode.error
    #async def slowmode_error(self, error, ctx):
    #    if isinstance(error, MissingPermissions):
    #        text = "NOPE 🤣".format(ctx.message.author)
    #        await bot.send_message(ctx.message.channel, text)

def setup(bot):
    bot.add_cog(Controls(bot))

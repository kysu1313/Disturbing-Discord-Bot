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


class DiscRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.id

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roles connected")

    @has_permissions(administrator=True)
    @commands.command(name='addrole', help='Shows how much cash you or user have in your bank and wallet.')
    async def addrole(self, ctx, role: discord.Role, user: discord.Member):
        await user.add_roles(role)
        await ctx.send("Added role")

    @has_permissions(administrator=True)
    @commands.command(name='removerole', help='Shows how much cash you or user have in your bank and wallet.')
    async def removerole(self, ctx, role: discord.Role, user: discord.Member):
        await user.remove_roles(role)
        await ctx.send("Added role")

    @commands.command(name='roles', help='View all roles')
    async def roles(self, ctx):
        roles = ctx.guild.roles
        description = ""
        for role in roles:
            description += f' @{role.name}'
        embedd = discord.Embed(
            title="Roles",
            description=description,
            color=0x42F56C
        )
        embedd.set_footer(
            text="To get a certain role, talk to a moderator"
        )
        await ctx.send(embed=embedd)

    @addrole.error
    async def addrole_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            text = "NOPE 🤣".format(ctx.message.author)
            await ctx.send(ctx.message.channel, text)
    
    @removerole.error
    async def removerole_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            text = "NOPE 🤣".format(ctx.message.author)
            await ctx.send(ctx.message.channel, text)

def setup(bot):
    bot.add_cog(DiscRoles(bot))
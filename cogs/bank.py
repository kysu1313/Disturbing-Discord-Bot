import discord
from discord.ext import commands
import os
import time
from helpers.settings import Settings
import json
import random

IMAGES = [
    ["cherry", "./images/cherry.png"],
    ["diamond", "./images/diamond.png"],
    ["grapes", "./images/grapes.png"],
    ["heart", "./images/heart.png"],
    ["seven", "./images/seven.png"],
]


class BankAccount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.get_bot_id()

    # Events
    @commands.Cog.listener()
    async def on_ready(self, ctx):
        await ctx.send('💰 Connected Bank Accounts 💸')

        # TODO: add startup notifications about commands to use with bank

    @commands.command(name='bank', help='Shows how much cash you have in your bank and wallet.')
    async def bank(self, ctx):
        wallet, bank = await self.open_account()
        await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.user.name, bank, wallet))

    @commands.command(name='slots', help='$10 to spin the wheel 🎰')
    async def slots(self, ctx):
        global IMAGES

        wallet, bank = await self.open_account()
        pay_to_play = await update_balance(-10)

        if not pay_to_play:
            await ctx.send("{}, you are soo poor 😂. Transaction Failed".format(ctx.user.name))
            return
        
        wheel1 = IMAGES[random.randint(0, len(IMAGES) - 1)]
        wheel2 = IMAGES[random.randint(0, len(IMAGES) - 1)]
        wheel3 = IMAGES[random.randint(0, len(IMAGES) - 1)]
        wheel4 = IMAGES[random.randint(0, len(IMAGES) - 1)]

        #for i in range(0, len(IMAGES)-1): 
        #    if 

        await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.user.name, bank, wallet))

    async def update_balance(self, amount):
        wallet, bank = await self.open_account()
        if amount == 0:
            return
        if amount > 0:
            bank += amount
        elif bank > amount:
            bank -= amount
        elif wallet > amount:
            wallet -= amount
        elif bank + wallet > amount:
            bank += wallet
            wallet = 0
            bank -= amount
        else:
            return False
        return True
            

    async def open_account(self, user):

        balance = 1000
        users = await self.get_bank_data()
        
        if str(user.id) in users:
            return users[str(user.id)]["wallet"], users[str(user.id)]["bank"]

        users[str(user.id)]["wallet"] = balance
        users[str(user.id)]["bank"] = balance
        
        with open("main-bank.json", "w") as f:
            json.dump(users, f)

        return balance, balance

    async def get_bank_data(self):
        users = None
        with open("main-bank.json", "r") as f:
            users = json.load(f)
        return users


def setup(bot):
    bot.add_cog(Commands(bot))
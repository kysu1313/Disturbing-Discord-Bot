import discord
from discord.ext import commands
import os
import time
from helpers.settings import Settings
import json
import random
from cogs.commands import Commands

IMAGES = [
    ["💎"],
    ["🔥"],
    ["🍒"],
    ["🍇"],
    ["❤️"],
]

#if diamonds >= 4: prize += 500
#        if fires >= 4: prize += 200
#        if cherries >= 4: prize += 100

#        if diamonds >= 2 and fires >= 2 and cherries >= 2 and grapes >= 1: prize += 50

#        if grapes >= 2: prize += 5
#        if hearts > 0: prize += hearts
#        if diamonds >= 4 and fires >= 2 and cherries >= 2: 
#            prize += jackpot_amt

# SLOTS PRIZES
# 💎 4 diamond = $500
# 🔥 4 fire = $200
# 🍒 4 cherry = $100 
# 🍇 2 grapes = $5
# ❤️ hearts = $1 per
# jackpot = 4 diamond + 2 fire + 2 cherry = $5000

class BankAccount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.get_bot_id()
        if not self.settings.get_is_production():
            bot.remove_command("bank")
            bot.remove_command("slots")

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Banks connected")

        # TODO: add startup notifications about commands to use with bank

    @commands.command(name='bank', help='Shows how much cash you have in your bank and wallet.')
    async def bank(self, ctx):
        wallet, bank = await self.open_account(ctx)
        await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.message.author, bank, wallet))

    @commands.command(name='adjust', help='Server ownder / Mods can update users banks.')
    async def adjust(self, ctx):
        wallet, bank = await self.open_account(ctx)
        await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.message.author, bank, wallet))

    @commands.command(name='prizes', help='Shows the prizes for each game.')
    async def prizes(self, ctx):
        description = """
        # SLOTS PRIZES
        # 💎 4 diamond = $500
        # 🔥 4 fire = $150
        # 🍒 4 cherry = $70 
        # 🍇 2 grapes = $5
        # ❤️ hearts = $1 per
        # jackpot = 4 diamond + 2 fire + 2 cherry = $5000
        """
        await ctx.send(description)

    #@commands.command(name='adjust', help='Server ownder / Mods can update users banks.')
    #async def adjust(self, ctx):
    #    wallet, bank = await self.open_account(ctx)
    #    await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.message.author, bank, wallet))


    @commands.command(name='slots', help='$30 to spin the wheel 🎰')
    async def slots(self, ctx):
        global IMAGES
        cost = -20
        wallet, bank = await self.open_account(ctx)
        pay_to_play = await self.update_balance(ctx, cost)

        if not pay_to_play:
            await ctx.send("LOL, you are soo fucking poor 😂. Transaction Failed")
            return

        prize = 0
        hit_jackpot = False
        jackpot_amt = 5000

        diamonds = 0
        fires = 0
        cherries = 0
        grapes = 0
        hearts = 0
        wheels = []

        for i in range(0, 9):
            wheel = IMAGES[random.randint(0, len(IMAGES) - 1)]
            wheels.append(wheel)
            if wheel[0] == '💎': diamonds += 1
            elif wheel[0] == '🔥': fires += 1
            elif wheel[0] == '🍒': cherries += 1
            elif wheel[0] == '🍇': grapes += 1
            elif wheel[0] == '❤️': hearts += 1
        
        if diamonds >= 4: prize += 500
        if fires >= 4: prize += 150
        if cherries >= 4: prize += 70

        if diamonds >= 2 and fires >= 2 and cherries >= 2 and grapes >= 1: prize += 50

        if grapes >= 2: prize += 5
        if hearts > 0: prize += hearts
        if diamonds >= 4 and fires >= 2 and cherries >= 2: 
            prize += jackpot_amt
            hit_jackpot = True

        if hit_jackpot:
            title = "💸 $ JACKPOT $ 💸"
        else:
            title = "Slot Machine 🤑"

        description = """
            {:2s} - {:2s} - {:2s}
            {:2s} - {:2s} - {:2s}
            {:2s} - {:2s} - {:2s}
        """.format(
            wheels[0][0],wheels[3][0],wheels[6][0],
            wheels[1][0],wheels[4][0],wheels[7][0],
            wheels[2][0],wheels[5][0],wheels[8][0],
        )
        

        
        await self.update_balance(ctx, prize)

        embedd = discord.Embed(
            title=title,
            description="Cost = ${}".format(cost),
            color=0x42F56C
        )
        embedd.add_field(name="Spin", value=description)
        embedd.add_field(name="Winnings:", value="${}".format(prize))
        embedd.set_footer(
            text=f"Spun by: {ctx.message.author}"
        )
        await ctx.send(embed=embedd)
        
    async def update_balance(self, context, amount):
        wallet, bank = await self.open_account(context)
        user_id = context.message.author.id
        if amount == 0:
            return
        if amount > 0:
            bank += amount
        elif bank > abs(amount):
            bank += amount
        elif wallet > abs(amount):
            wallet += amount
        elif bank + wallet > abs(amount):
            bank += wallet
            wallet = 0
            bank += amount
        else:
            return False
        users = await self.get_bank_data()
        for user in users:
            if user["id"] == user_id:
                user["wallet"] = wallet
                user["bank"] = bank
        with open("main-bank.json", "w") as f:
            json.dump(users, f)
        return True
            

    async def open_account(self, context):
        user = context.message.author
        user_id = context.message.author.id
        balance = 500
        users = await self.get_bank_data()
        
        for user in list(users):
            if user["id"] == user_id:
                return user["bank"], user["wallet"]
        
        users += [{"id": user_id,
                    "wallet": balance, 
                    "bank": balance}]
        
        with open("main-bank.json", "w") as f:
            json.dump(users, f)

        return balance, balance

    async def get_bank_data(self):
        users = None
        with open("main-bank.json", "r") as f:
            users = json.load(f)
        return users


def setup(bot):
    bot.add_cog(BankAccount(bot))
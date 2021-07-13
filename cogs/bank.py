import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import os
import time
from helpers.settings import Settings
import json
import random
from cogs.commands import Commands
from discord.ext.commands.errors import MissingPermissions
import re

IMAGES = [
    ["💎"],
    ["🔥"],
    ["🍒"],
    ["🍇"],
    ["❤️"],
]

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

    @has_permissions(administrator=True)
    @commands.command(name='adjust', help='Server owner / Mods can update users banks.')
    async def adjust(self, ctx, username, amount, location):
        
        members = self.find_all_members(ctx)
        #members = list(ctx.message.server.members)
        member = [a for a in members if a.name.lower() == username.lower()][0]
        if member is not None:
            bank, wallet = await self.get_simple_bank(member, member.id)
            if location.lower() == "bank": 
                await self.set_money(member.id, amount, wallet)
            elif location.lower() == "wallet": 
                await self.set_money(member.id, bank, amount)
            #self.update_balance(member, amount)
        else:
            await ctx.send("User not found.")
            return
        await ctx.send("Updated {}'s {} to ${}.".format(member.name, location, amount))

    @adjust.error
    async def adjust_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            text = "NOPE 🤣".format(ctx.message.author)
            await bot.send_message(ctx.message.channel, text)
        
    @commands.command(name='transfer', help='Transfer money from wallet to bank and vice-versa. i.e: (!transfer 40 bank) transfers $40 from wallet to bank')
    async def transfer(self, ctx, amount, destination):
        bank, wallet = await self.open_account(ctx)
        amount = int(amount)
        if amount < 0:
            await ctx.send("{}, you can't transfer a negative amount".format(ctx.message.author, bank, wallet))
            return
        elif destination.lower() == "bank": 
            if wallet - amount >= 0:
                await self.set_money(ctx.message.author.id, bank + amount, wallet - amount)
        elif destination.lower() == "wallet": 
            if bank - amount >= 0:
                await self.set_money(ctx.message.author.id, bank - amount, wallet + amount)
        bank, wallet = await self.open_account(ctx)
        await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.message.author, bank, wallet))

    @commands.command(name='highlow', help='Cost: $5. Bet wether the number will be higher or lower than 5 / 10')
    async def highlow(self, ctx, amount, choice):
        bank, wallet = await self.open_account(ctx)
        price = 5
        amount = int(re.sub("[^0-9]", "", amount))
        remove_from = wallet
        if wallet < price and bank < price:
            await ctx.send("You are too poor LOL")
            return
        elif wallet > price:
            remove_from = wallet
            await self.set_money(ctx.message.author.id, bank, wallet - price)
        elif bank > price:
            remove_from = bank
            await self.set_money(ctx.message.author.id, bank - price, wallet)

        prize = amount*2
        result = random.randrange(1,10)
        description = ""
        title = ""

        if choice.lower() == "higher": 
            if result >= 5:
                await self.set_money(ctx.message.author.id, bank, wallet + (prize))
                description = "{}".format(result)
                title = "Congrats! You won ${}".format(prize)
            else:
                if remove_from == bank:
                    await self.set_money(ctx.message.author.id, bank - amount, wallet)
                else:
                    await self.set_money(ctx.message.author.id, bank, wallet - amount)
                description = "{}".format(result)
                title = "You win nothing"
        elif choice.lower() == "lower":
            if result < 5:
                await self.set_money(ctx.message.author.id, bank, wallet + (prize))
                description = "{}".format(result)
                title = "Congrats! You won ${}".format(prize)
            else:
                if remove_from == bank:
                    await self.set_money(ctx.message.author.id, bank - amount, wallet)
                else:
                    await self.set_money(ctx.message.author.id, bank, wallet - amount)
                description = "{}".format(result)
                title = "You win nothing"
        
        embedd = discord.Embed(
            title=title,
            description="Cost = ${}".format(price),
            color=0x42F56C
        )
        embedd.add_field(name="Roll", value=description)
        embedd.add_field(name="Potential Winnings:", value="${}".format(prize))
        embedd.set_footer(
            text=f"{ctx.message.author} rolled a {result} / 10"
        )
        await ctx.send(embed=embedd)

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

    @commands.command(name='slots', help='$20 to spin the wheel 🎰')
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
        
    async def set_money(self, user_id, new_bank, new_wallet):
        #user_id = context.message.author.id
        users = await self.get_bank_data()
        for user in users:
            if user["id"] == user_id:
                user["wallet"] = int(new_wallet)
                user["bank"] = int(new_bank)
        with open("main-bank.json", "w") as f:
            json.dump(users, f)

    async def update_balance(self, context, amount):
        bank, wallet = await self.open_account(context)
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
            
    async def get_simple_bank(self, user, user_id):
        users = await self.get_bank_data()
        for user in list(users):
            if user["id"] == user_id:
                return user["bank"], user["wallet"]

    def find_all_members(self, ctx):
        server = ctx.message.guild
        members = []
        for member in server.members:
            members.append(member)
        return members

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
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
        self.bot_id = self.settings.id
        if not self.settings.get_is_production():
            bot.remove_command("bank")
            bot.remove_command("slots")

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Banks connected")

        # TODO: add startup notifications about commands to use with bank

    @commands.command(name='bank', help='Shows how much cash you or user have in your bank and wallet.')
    async def bank(self, ctx, username=None):
        if username is not None:
            user = await self.get_user_from_name(ctx, username)
            wallet, bank = await self.open_account_userid(user.id)
            await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(user.name, bank, wallet))
        else:
            wallet, bank = await self.open_account(ctx)
            await ctx.send("{} ---> Bank: ${}, Wallet: ${}".format(ctx.message.author, bank, wallet))

    @has_permissions(administrator=True)
    @commands.command(name='adjust', help='<username> <amount> <bank/wallet>. Adjusts users money')
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
        
    @commands.command(name='pay', help='Pay an amount of $$ to another user.')
    async def pay(self, ctx, username, amount):
        
        members = self.find_all_members(ctx)
        usr_bank, usr_wallet = await self.open_account(ctx)
        #members = list(ctx.message.server.members)
        member = [a for a in members if a.name.lower() == username.lower()][0]
        if member is not None and int(amount) > 0 and int(usr_wallet) > 0:
            bank, wallet = await self.open_account_userid(member.id)
            await self.set_money(member.id, bank, int(wallet) + int(amount))
            await self.set_money(ctx.message.author.id, usr_bank, int(usr_wallet) - int(amount))
        else:
            await ctx.send("User not found. Or you don't have enough $$")
            return
        await ctx.send("{} Paid {} ${}.".format(ctx.message.author, member.name, amount))

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
        prize = amount*2
        remove_from = wallet
        if wallet < price and bank < price:
            await ctx.send("You are too poor LOL")
            return
        elif wallet > amount+price:
            remove_from = wallet
            await self.set_money(ctx.message.author.id, bank, wallet - price)
        elif bank > amount+price:
            remove_from = bank
            await self.set_money(ctx.message.author.id, bank - price, wallet)

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

    @commands.command(name='steal', help='<guess(1-5)> <victim> <amount>, Attempt to steal from another user.')
    async def steal(self, ctx, guess, victim, amount):
        '''
        Steal from another member by guessing a number between 1 and 5
        Parameters
        ----------
        ctx: user who sent command
        guess: number guess between 1 and 5
        victim: username of target
        '''
        members = self.find_all_members(ctx)
        member = [a for a in members if a.name.lower() == victim.lower()][0]
        usr_bank, usr_wallet = await self.open_account_userid(member.id)
        bank, wallet = await self.open_account(ctx)
        rand = random.randint(1, 5)
        # If user guesses wrong, give 0.2% of amount to victim and deduct from attacker
        if int(guess) != rand:
            cost = 0.2 * int(amount)
            await self.set_money(member.id, usr_bank, int(usr_wallet) + cost)
            await self.set_money(ctx.message.author.id, bank, int(wallet) - cost)
            await ctx.send("You got caught! @{} took {} from you.".format(victim, cost))
            return
        check_amount = await self.check_for_enough_balance(member.id, amount)
        if check_amount == "":
            await ctx.send("{} doesn't even have that much money! LOL".format(member.name))
            return
        if member is not None and int(amount) > 0:
            if check_amount == "wallet":
                await self.set_money(member.id, usr_bank, int(usr_wallet) - int(amount))
                await self.set_money(ctx.message.author.id, bank, int(wallet) + int(amount))
            elif check_amount == "bank":
                await self.set_money(member.id, int(usr_bank) - int(amount), usr_wallet)
                await self.set_money(ctx.message.author.id, int(bank) + int(amount), wallet)

        await ctx.send("Success! @{} stole {} from @{}".format(ctx.author, amount, member))

    @commands.command(name='leaderboard', help='Shows the prizes for each game.')
    async def leaderboard(self, ctx):
        members = self.find_all_members(ctx)
        title = "Leaderboard"
        
        member_list = ""
        count = 1
        for m in members:
            wallet, bank = await self.open_account_userid(m.id)
            total = int(wallet) + int(bank)
            member_list += "{}. {}: ${}\n".format(count, m.name, total)
            count += 1

        

        embedd = discord.Embed(
            title=title,
            description=member_list,
            color=0x42F56C
        )
        embedd.set_footer(
            text=f"Spun by: {ctx.message.author}"
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
        cost = -100
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
        
        if diamonds >= 4: prize += 800
        if fires >= 4: prize += 550
        if cherries >= 4: prize += 150

        if diamonds >= 2 and fires >= 2 and cherries >= 2 and grapes >= 1: prize += 80

        if grapes >= 2: prize += 25
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
    
    async def get_user_from_name(self, ctx, username):
        members = self.find_all_members(ctx)
        usr_bank, usr_wallet = await self.open_account(ctx)
        #members = list(ctx.message.server.members)
        member = [a for a in members if a.name.lower() == username.lower()][0]
        return member
    
    async def check_for_enough_balance(self, user_id, amount):
        usr_bank, usr_wallet = await self.open_account_userid(user_id)
        bank = int(usr_bank)
        wallet = int(usr_wallet)
        amt = int(amount)
        if wallet > amt:
            return "wallet"
        elif bank > amt:
            return "bank"
        else:
            return ""
        

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

    async def open_account_userid(self, user_id):
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
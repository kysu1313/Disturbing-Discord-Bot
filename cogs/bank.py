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

IMAGES = [
    ["💎"],
    ["🔥"],
    ["🍒"],
    ["🍇"],
    ["❤️"],
]
MONEY_SYMBOL = "💸"
STARTING_MONEY = 500

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
        '''
        View bank details.

        Attributes:
            ctx: user who sent command
            username: (optional) users bank details to view
        '''
        if username is not None:
            user = await self.get_user_from_name(ctx, username)
            wallet, bank = await self.open_account_userid(ctx, user)
            await ctx.send("{} ---> Bank: {} 🍬, Wallet: {} 🍬".format(user.name, bank, wallet))
        else:
            wallet, bank = await self.open_account(ctx)
            await ctx.send("{} ---> Bank: {} 🍬, Wallet: {} 🍬".format(ctx.message.author, bank, wallet))

    @has_permissions(administrator=True)
    @commands.command(name='adjust', help='<username> <amount> <bank/wallet>. Adjusts users money')
    async def adjust(self, ctx, username, amount, location):
        '''
        (Admin) Adjust bank details.

        Attributes:
            ctx: user who sent command
            username: (optional) users bank details to adjust
            amount: Amount to set $$
            location: bank or wallet
        '''
        members = self.find_all_members(ctx)
        #members = list(ctx.message.server.members)
        member = [a for a in members if a.name.lower() == username.lower()][0]
        if member is not None:
            wallet, bank = await self.get_simple_bank(ctx, member, member.id)
            if location.lower() == "bank":
                await self.set_money(ctx, member.id, amount, wallet)
            elif location.lower() == "wallet":
                await self.set_money(ctx, member.id, bank, amount)
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
        '''
        Pay another member $xx amount.

        Attributes:
            ctx: user who sent command
            username: (optional) user to send $xx to
            amount: amount to pay
        '''
        members = self.find_all_members(ctx)
        usr_bank, usr_wallet = await self.open_account(ctx)
        #members = list(ctx.message.server.members)
        member = [a for a in members if a.name.lower() == username.lower()][0]
        if member is not None and int(amount) > 0 and int(usr_wallet) > 0:
            bank, wallet = await self.open_account_userid(ctx, member)
            await self.set_money(ctx, member.id, bank, int(wallet) + int(amount))
            await self.set_money(ctx, ctx.message.author.id, usr_bank, int(usr_wallet) - int(amount))
        else:
            await ctx.send("User not found. Or you don't have enough $$")
            return
        await ctx.send("{} Paid {} {} {} tokens.".format(ctx.message.author, member.name, amount, MONEY_SYMBOL))

    @commands.command(name='transfer', help='Transfer money from wallet to bank and vice-versa. i.e: (!transfer 40 bank) transfers $40 from wallet to bank')
    async def transfer(self, ctx, amount, destination):
        '''
        Transfer money from bank to wallet and vice-versa.

        Attributes:
            ctx: user who sent command
            destination: where to transfer to, 'bank' or 'wallet'
        '''
        bank, wallet = await self.open_account(ctx)
        amount = int(amount)
        if amount < 0:
            await ctx.send("{}, you can't transfer a negative amount".format(ctx.message.author, bank, wallet))
            return
        elif destination.lower() == "bank":
            if wallet - amount >= 0:
                await self.set_money(ctx, ctx.message.author.id, bank + amount, wallet - amount)
        elif destination.lower() == "wallet":
            if bank - amount >= 0:
                await self.set_money(ctx, ctx.message.author.id, bank - amount, wallet + amount)
        bank, wallet = await self.open_account(ctx)
        await ctx.send("{} ---> Bank: {}, Wallet: {}".format(ctx.message.author, bank, wallet))

    @commands.command(name='highlow', help='Cost: 5. Bet wether the number will be higher or lower than 5 / 10')
    async def highlow(self, ctx, amount, choice):
        '''
        Guess wether the number will be higher or lower than 5 / 10. If correct you double your bet amount.

        Attributes:
            ctx: user who sent command
            amount: the amount you want to bet
            choice: "higher" / "lower"
        '''
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
            await self.set_money(ctx, ctx.message.author.id, bank, wallet - price)
        elif bank > amount+price:
            remove_from = bank
            await self.set_money(ctx, ctx.message.author.id, bank - price, wallet)

        result = random.randrange(1,10)
        description = ""
        title = ""

        if choice.lower() == "higher":
            if result >= 5:
                await self.set_money(ctx, ctx.message.author.id, bank, wallet + (prize))
                description = "{}".format(result)
                title = "Congrats! You won ${}".format(prize)
            else:
                if remove_from == bank:
                    await self.set_money(ctx, ctx.message.author.id, bank - amount, wallet)
                else:
                    await self.set_money(ctx, ctx.message.author.id, bank, wallet - amount)
                description = "{}".format(result)
                title = "You win nothing"
        elif choice.lower() == "lower":
            if result < 5:
                await self.set_money(ctx, ctx.message.author.id, bank, wallet + (prize))
                description = "{}".format(result)
                title = "Congrats! You won ${}".format(prize)
            else:
                if remove_from == bank:
                    await self.set_money(ctx, ctx.message.author.id, bank - amount, wallet)
                else:
                    await self.set_money(ctx, ctx.message.author.id, bank, wallet - amount)
                description = "{}".format(result)
                title = "You win nothing"

        embedd = discord.Embed(
            title=title,
            description="Cost = {} {}'s".format(price, MONEY_SYMBOL),
            color=0x42F56C
        )
        embedd.add_field(name="Roll", value=description)
        embedd.add_field(name="Potential Winnings:", value="{} {}'\s".format(prize, MONEY_SYMBOL))
        embedd.set_footer(
            text=f"{ctx.message.author} rolled {result} / 10"
        )
        await ctx.send(embed=embedd)

    @commands.command(name='steal', help='<guess(1-5)> <victim> <amount>, Attempt to steal from another user.')
    async def steal(self, ctx, guess, victim, amount):
        '''
        Steal from another member by guessing a number between 1 and 5

        Attributes:
            ctx: user who sent command
            guess: number guess between 1 and 5
            victim: username of target
        '''
        members = self.find_all_members(ctx)
        member = [a for a in members if a.name.lower() == victim.lower()][0]
        usr_bank, usr_wallet = await self.open_account_userid(ctx, member)
        bank, wallet = await self.open_account(ctx)
        rand = random.randint(1, 5)
        # If user guesses wrong, give 0.2% of amount to victim and deduct from attacker
        if int(guess) != rand:
            cost = 0.2 * int(amount)
            await self.set_money(ctx, member.id, usr_bank, int(usr_wallet) + cost)
            await self.set_money(ctx, ctx.message.author.id, bank, int(wallet) - cost)
            await ctx.send("You got caught! @{} took {} from you.".format(victim, cost))
            return
        check_amount = await self.check_for_enough_balance(ctx, member.id, amount)
        if check_amount == "":
            await ctx.send("{} doesn't even have that much money! LOL".format(member.name))
            return
        if member is not None and int(amount) > 0:
            if check_amount == "wallet":
                await self.set_money(ctx, member.id, usr_bank, int(usr_wallet) - int(amount))
                await self.set_money(ctx, ctx.message.author.id, bank, int(wallet) + int(amount))
            elif check_amount == "bank":
                await self.set_money(ctx, member.id, int(usr_bank) - int(amount), usr_wallet)
                await self.set_money(ctx, ctx.message.author.id, int(bank) + int(amount), wallet)

        await ctx.send("Success! @{} stole {} from @{}".format(ctx.author, amount, member))

    @commands.command(name='leaderboard', help='Shows the prizes for each game.')
    async def leaderboard(self, ctx):
        '''
        Returns list of users sorted by total wealth.

        Attributes:
            ctx: user who sent command
        '''
        members = self.find_all_members(ctx)
        title = "💰 Leaderboard 💰"

        member_list = ""
        total_lst = []
        result_lst = ""
        count = 1

        for m in members:
            wallet, bank = await self.open_account_userid(ctx, m)
            total = int(wallet) + int(bank)
            total_lst.append((m.name, total))

        total_lst.sort(key=lambda x: x[1])
        reverse_lst = total_lst[::-1]
        for m in reverse_lst:
            result_lst += "{}. {}: {}\n".format(count, m[0], m[1])
            count += 1

        embedd = discord.Embed(
            title=title,
            description=result_lst,
            color=0x42F56C
        )
        embedd.set_footer(
            text=f"Spun by: {ctx.message.author}"
        )
        await ctx.send(embed=embedd)

    @commands.command(name='prizes', help='Shows the prizes for each game.')
    async def prizes(self, ctx):
        '''
        View slots prize details.

        Attributes:
            ctx: user who sent command
        '''
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

    @commands.command(name='slots', help='Costs 20 to spin the wheel 🎰, use !prizes to see rewards')
    async def slots(self, ctx):
        '''
        Play slots. Costs $70 to play.

        Attributes:
            ctx: user who sent command
        '''
        global IMAGES
        cost = -70
        wallet, bank = await self.open_account(ctx)
        pay_to_play = await self.update_balance(ctx, cost)

        if not pay_to_play:
            await ctx.send("LOL, you are soo poor 😂. Transaction Failed")
            return

        prize = 0
        hit_jackpot = False
        jackpot_amt = 50000

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

        if diamonds >= 4: prize += 1100
        if fires >= 4: prize += 850
        if cherries >= 4: prize += 350

        if diamonds >= 2 and fires >= 2 and cherries >= 2 and grapes >= 1: prize += 180

        if grapes >= 2: prize += 45
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

    async def get_user_from_name(self, ctx, username) -> object:
        '''
        Get user object from username.

        Attributes:
            ctx: user who sent command
            username: username of person to get
        '''
        members = self.find_all_members(ctx)
        usr_bank, usr_wallet = await self.open_account(ctx)
        #members = list(ctx.message.server.members)
        member = [a for a in members if a.name.lower() == username.lower()][0]
        return member

    async def check_for_enough_balance(self, ctx, user_id, amount) -> str:
        '''
        Validates the user with user_id has enough balance.

        Attributes:
            ctx: user who sent command
            user_id: user id of user
            amount: amount to validate
        '''
        guild_id = self.get_guild_id(ctx)
        member = self.get_user_from_discord_id(ctx, user_id)
        usr_bank, usr_wallet = await self.open_account_userid(ctx, member)
        bank = int(usr_bank)
        wallet = int(usr_wallet)
        amt = int(amount)
        if wallet > amt:
            return "wallet"
        elif bank > amt:
            return "bank"
        else:
            return ""

    async def set_money(self, ctx, user_id, new_bank, new_wallet) -> (int, int):
        '''
        Set / update users money.

        Attributes:
            ctx: user who sent command
            user_id: user id of user
            new_bank: updated bank amount
            new_wallet: updated wallet amount
        '''
        conn = DbConn()
        await self.check_user_and_server(ctx, user_id)
        guild_id = self.get_guild_id(ctx)
        username = self.get_user_from_discord_id(ctx, user_id).name
        conn.update_user_money(user_id, guild_id, username, new_wallet, new_bank)
        return new_bank, new_wallet

    async def update_balance(self, ctx, amount) -> (int, int):
        '''
        Update users total balance adding / deducting amount from appropriate location (bank or wallet).

        Attributes:
            ctx: user who sent command
            amount: amount to update balance by
        '''
        bank, wallet = await self.open_account(ctx)
        user_id = ctx.message.author.id
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

        conn = DbConn()
        await self.check_user_and_server(ctx, user_id)
        guild_id = self.get_guild_id(ctx)
        username = self.get_user_from_discord_id(ctx, user_id).name
        conn.update_user_money(user_id, guild_id, username, wallet, bank)
        return wallet, bank

    async def get_simple_bank(self, ctx, member, user_id) -> (int, int):
        '''
        Returns the bank and wallet of user_id

        Attributes:
            ctx: user who sent command
            member: get bank and wallet of member
            user_id: get bank and wallet of user
        '''
        guild_id = self.get_guild_id(ctx)
        conn = DbConn()
        user = conn.get_user_in_server(user_id, guild_id, member.name)
        if user is None:
            conn.add_user(user_id, guild_id, STARTING_MONEY, STARTING_MONEY, member.name)
            return STARTING_MONEY, STARTING_MONEY
        else:
            return user.bank, user.wallet

    async def check_user_and_server(self, ctx, user_id):
        conn = DbConn()
        guild_id = self.get_guild_id(ctx)
        users = await self.get_users(guild_id)
        server = conn.get_server(guild_id)
        username = self.get_user_from_discord_id(ctx, user_id).name
        if server is None:
            guild_name = self.get_guild_name(ctx)
            conn.add_server(guild_id, guild_name, 0, 0)
        user = conn.get_user_in_server(user_id, guild_id, username)
        if user is None:
            conn.add_user(user_id, guild_id, STARTING_MONEY, STARTING_MONEY, username)
            return

    def find_all_members(self, ctx):
        '''
        Returns all members in server

        Attributes:
            ctx: user who sent command
        '''
        server = ctx.message.guild
        members = []
        for member in server.members:
            members.append(member)
        return members

    def get_user_from_discord_id(self, ctx, user_id):
        members = self.find_all_members(ctx)
        member = [a for a in members if a.id == user_id][0]
        return member

    async def open_account_userid(self, ctx, member) -> (int, int):
        '''
        Open new bank account and wallet for member

        Attributes:
            ctx: user who sent command
            member: open bank for
        '''
        balance = 500
        guild_id = self.get_guild_id(ctx)
        guild_name = self.get_guild_name(ctx)
        conn = DbConn()
        server = conn.get_server(guild_id)
        if server is None:
            conn.add_server(guild_id, guild_name, 0, 0)
        user = conn.get_user_in_server(member.id, guild_id, member.name)
        if user is None:
            conn.add_user(member.id, guild_id, STARTING_MONEY, STARTING_MONEY, member.name)
            return STARTING_MONEY, STARTING_MONEY
        else:
            return user.wallet, user.bank

    async def open_account(self, ctx) -> (int, int):
        '''
        Open new account for ctx

        Attributes:
            ctx: user who sent command
        '''
        guild_id = self.get_guild_id(ctx)
        guild_name = self.get_guild_name(ctx)
        user_id = self.get_user_id(ctx)
        username = self.get_username(ctx)
        conn = DbConn()
        server = conn.get_server(guild_id)
        if server is None:
            conn.add_server(guild_id, guild_name, 0, 0)
        user = conn.get_user_in_server(ctx.message.author.id, guild_id, ctx.message.author.name)
        if user is None:
            conn.add_user(user_id, guild_id, STARTING_MONEY, STARTING_MONEY, username)
            return STARTING_MONEY, STARTING_MONEY
        else:
            return user.wallet, user.bank

    def get_guild_id(self, ctx):
        guild_id = ctx.message.guild.id
        return guild_id

    def get_guild_name(self, ctx):
        guild_name = ctx.message.guild.name
        return guild_name

    def get_user_id(self, ctx):
        user_id = ctx.message.author.id
        return user_id

    def get_username(self, ctx):
        user_name = ctx.message.author.name
        return user_name

    @commands.command(name='test', help='Used for testing commands. Development mode only')
    async def test(self, ctx):
        '''
        Test command method

        Attributes:
            ctx: user who sent command
        '''
        guild_id = self.get_guild_id(ctx)
        guild_name = self.get_guild_name(ctx)
        user_id = self.get_user_id(ctx)
        username = self.get_username(ctx)
        conn = DbConn()

        conn.update_user_money(user_id, guild_id, username, 2000, 2000)
        user = conn.get_user(user_id, guild_id)

        user.print()


        #if server is None:
        #    conn.add_server(guild_id, guild_name)
        #user = conn.get_user_in_server(ctx.message.author.id, guild_id, ctx.message.author.name)
        #if user is None:
        #    conn.add_user(user_id, guild_id, STARTING_MONEY, STARTING_MONEY, username)
        #    return STARTING_MONEY, STARTING_MONEY
        #else:
        #    return user.wallet, user.bank

    async def get_users(self, guild_id):
        '''
        Get all users from database.

        Attributes:
            ctx: user who sent command
        '''
        conn = DbConn()
        return conn.get_users_by_server(guild_id)

def setup(bot):
    bot.add_cog(BankAccount(bot))

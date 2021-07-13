import discord
from discord.ext import commands
import os
import random
import threading
import datetime
import time
from cogs.bot_parts.apis import Apis
from helpers.settings import Settings

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = Settings()
        self.bot_id = self.settings.id
        if not self.settings.get_is_production():
            bot.remove_command("joke")
            bot.remove_command("ping")
            bot.remove_command("guess")
            bot.remove_command("poll")
            bot.remove_command("invite")
            bot.remove_command("8ball")
            bot.remove_command("server")
            bot.remove_command("roll")

        

    # Events
    @commands.Cog.listener()
    async def on_ready(self,):
        print(f'{self.bot.user.name} has connected to Discord!')

    def checkTime(self):
        # This function runs periodically every 1 second
        threading.Timer(1, checkTime).start()

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        if(current_time == '02:11:00'):  # check if matches with the desired time
            print('sending message')

    @commands.command(name='joke', help='Tells a joke')
    async def joke(self, ctx):
        joke = Apis()
        setup, punchline = joke.get_joke()
        await ctx.send(setup)
        time.sleep(5)
        await ctx.send(punchline)

    # Commands
    @commands.command(help='Simple check to verify bot is functioning properly')
    async def ping(self, ctx):
        await ctx.send('🏓 Pong!')

    @commands.command(name='guess', help='Guess the number between 1 and 10')
    async def guess(self, ctx):
        await ctx.send('Guess a number between 1 to 10')

        def guess_check(m):
            return m.content.isdigit()
        is_good = False
        for i in range(0,3):
            guess = await ctx.wait_for('message', check=guess_check, timeout=15)
            answer = random.randint(1, 10)
            if guess is None:
                fmt = 'Sorry, you took too long. It was {}.'
                await self.bot.send(fmt.format(answer))
                return
            if int(guess.content) == answer:
                await ctx.send('You are right!')
                is_good = True
            else:
                await ctx.send('WRONG, fucking idiot')
        if not is_good:
            await ctx.send('Sorry. It is actually {}.'.format(answer))

    @commands.command(name="poll", help='Creates new poll with responses: 👍, 👎, 🤷')
    async def poll(self, context, *, title):
        """
        Creates a new poll where members can vote
        """
        embed = discord.Embed(
            title="A new poll has been created!",
            description=f"{title}",
            color=0x42F56C
        )
        embed.set_footer(
            text=f"Poll created by: {context.message.author} • React to vote!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(name="invite", help='Sends you a private message you can use to invite the bot to another server')
    async def invite(self, context):
        """
        Get the invite link of the bot to be able to invite it.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={self.bot_id}&scope=bot&permissions=470150263).",
            color=0xD75BF4
        )
        try:
            # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.command(name="8ball", help='!8ball <ask a question>')
    async def eight_ball(self, context, *, question):
        """
        Ask any question to the bot.
        """
        answers = ['It is certain.', 'It is decidedly so.', 'You may rely on it.', 'Without a doubt.',
                   'Yes - definitely.', 'As I see, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                   'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
                   'Cannot predict now.', 'Concentrate and ask again later.', 'Don\'t count on it.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers)-1)]}",
            color=0x42F56C
        )
        embed.set_footer(
            text=f"The question was: {question}"
        )
        await context.send(embed=embed)

    @commands.command(name='server', help='Returns server information')
    async def fetchServerInfo(self, context):
        guild = context.guild
        
        await context.send(f'Server Name: {guild.name}')
        await context.send(f'Server Size: {len(guild.members)}')
        await context.send(f'Server Name: {guild.owner.display_name}')

    @commands.command(name='roll', help='!roll <# of dice> <# of sides>')
    async def roll(self, ctx, number_of_dice: int, number_of_sides: int):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(', '.join(dice) + ' 🎲')


def setup(bot):
    bot.add_cog(Commands(bot))
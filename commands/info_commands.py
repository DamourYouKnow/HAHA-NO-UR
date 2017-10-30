from time import time
from discord.ext import commands
from core.checks import check_mongo
from bot import HahaNoUR
from data import data_path


class Info:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot
        with data_path.joinpath('info.txt').open() as f:
            self.info_msg = f.read()

    @commands.command()
    async def info(self):
        """
        Description: Displays information about the bot.
        """
        await self.bot.say(self.info_msg)

    @commands.command()
    async def help(self, *, command=''):
        """
        Description: Help command.
        Usage: "`{prefix}help` for a list of all commands,
        `{prefix}help command name` for help for the specific command."
        """
        await self.bot.say(
            embed=self.bot.all_help.get(command, self.bot.help_general)
        )

    @commands.command()
    async def ping(self):
        """
        Description: Command to check network ping.
        Usage: "`{prefix}ping`"
        """
        start = time()
        msg = await self.bot.say('Loading... :hourglass:')
        end = time()
        diff = end - start
        await self.bot.edit_message(
            msg, new_content=f':ping_pong: Pong! | {round(diff*1000)}ms'
        )

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def feedback(self, ctx, *args: str):
        """
        Description: |
            Provide feedback and suggestions.
        """
        user_id = ctx.message.author.id
        username = ctx.message.author.name
        message = ctx.message.content[len('!feedback'):].strip()
        if message == '':
            return

        await self.bot.db.feedback.add_feedback(user_id, username, message)
        await self.bot.send_message(
                self.bot.feedbag_log, '**' + username + '**: ' + message)
        await self.bot.send_message(
            ctx.message.channel,
            f'<@{ctx.message.author.id }> Thank you for your feedback!'
        )

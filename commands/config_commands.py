import discord
from discord.ext import commands
from core.checks import check_mongo
from bot import HahaNoUR

class Config:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def prefix(self, ctx, *args: str):
        """
        Description: |
            Allows changing of the command prefix character.
            This requires the Manage Server permission.
        """
        banned = ['@', '#']
        server_id = None
        msg_spl = ctx.message.content.split(' ')
        server = ctx.message.server
        user = ctx.message.author
        channel = ctx.message.channel

        if not ctx.message.server:
            server_id = user.id
        else:
            server_id = server.id

        reply = '<@' + user.id + '> '
        if not channel.permissions_for(user).manage_server:
            reply += 'You do not have permission to do this!'
        elif len(msg_spl) < 2:
            reply += 'You must specify a prefix character!'
        elif len(msg_spl[1]) < 1:
            reply += 'The command prefix must be a more than one character!'
        else:
            # Validated, let's do this!
            await self.bot.db.servers.set_prefix(server_id, msg_spl[1])
            reply += 'Prefix updated! If you would like to revert you can use '
            reply += '`!resetprefix`.\n'
            reply += 'The new prefix is now `' + msg_spl[1] + '`.'

        await self.bot.send_message(channel, reply)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def resetprefix(self, ctx, *args: str):
        """
        Description: |
            Reset a server's command prefix to '!'.
            This requires the Manage Server permission.
        """
        server_id = None
        server = ctx.message.server
        user = ctx.message.author
        channel = ctx.message.channel

        if not ctx.message.server:
            server_id = user.id
        else:
            server_id = server.id

        reply = '<@' + user.id + '> '
        if not channel.permissions_for(user).manage_server:
            reply += 'You do not have permission to do this!'
        else:
            # Validated, let's do this!
            await self.bot.db.servers.set_prefix(server_id, self.bot.prefix)
            reply += 'Prefix updated!\n'
            reply += 'The new prefix is now `!`.'

        await self.bot.send_message(channel, reply)
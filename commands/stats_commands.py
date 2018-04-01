import discord
from discord.ext import commands
from core.checks import check_mongo
from bot import HahaNoUR

class Stats:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['stats'])
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def mystats(self, ctx, *args: str):
        """
        Description: |
            Provides stats about you.
        """
        user_id = ctx.message.author.id

        stats = []
        album = await self.bot.db.users.get_user_album(user_id, True)
        counter = AlbumCounter(album)
        counter.run_count()
        stats.append(('Unique cards collected', counter.distinct_count))
        stats.append(('Total cards', counter.total_count))
        stats.append(('Unidolized cards', counter.unidolized_count))
        stats.append(('Idolized cards', counter.idolized_count))

        for rarity, count in counter.rarity_counts.items():
            stats.append((rarity + ' cards', count))

        for attribute, count in counter.attribute_counts.items():
            stats.append((attribute + ' cards', count))

        emb = _create_embed('Stats for ' + ctx.message.author.name, stats)
        await self.bot.send_message(ctx.message.channel, embed=emb)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def botstats(self, ctx, *args: str):
        """
        Description: |
            Provides stats about the bot.
        """
        stats = []
        stats.append(('Servers', len(self.bot.servers)))
        stats.append(('Users', await self.bot.db.users.get_user_count()))

        emb = _create_embed('My stats', stats)
        await self.bot.send_message(ctx.message.channel, embed=emb)


class AlbumCounter:
    def __init__(self, album):
        self.album = album
        self.rarity_counts = {'N': 0, 'R': 0, 'SR': 0, 'SSR': 0, 'UR': 0}
        self.attribute_counts = {'Smile': 0, 'Pure': 0, 'Cool': 0, 'All': 0}
        self.total_count = 0
        self.unidolized_count = 0
        self.idolized_count = 0
        self.distinct_count = 0

    def run_count(self):
        for card in self.album:
            curr_total = card['unidolized_count'] + card['idolized_count']

            self.rarity_counts[card['rarity']] += curr_total
            self.attribute_counts[card['attribute']] += curr_total
            self.unidolized_count += card['unidolized_count']
            self.idolized_count += card['idolized_count']

        self.total_count = self.idolized_count + self.unidolized_count
        self.distinct_count = len(self.album)


def _create_embed(title: str, stats: list):
    """
    Create a stats embed.

    :param title: Title of embed.
    :param stats: List of tuples (stat name, stat value).
    """
    desc = '\n'.join([str(k) + ': ' + str(v) for k,v in stats])
    emb = discord.Embed(title=title, description=desc)
    return emb

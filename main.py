from bot import HahaNoUR
from scout_commands import Scout

if __name__ == '__main__':
    with open("token.txt", "r") as f:
        token = f.read().strip('\n')
        f.close()
    bot = HahaNoUR('!')
    bot.remove_command('help')
    bot.add_cog(Scout(bot))
    bot.run(token)

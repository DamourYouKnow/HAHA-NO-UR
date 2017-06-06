from bot import HahaNoUR
from bot_commands import BotCommands

if __name__ == '__main__':
    with open("token.txt", "r") as f:
        token = f.read().strip('\n')
        f.close()

    bot = HahaNoUR('!')
    bot.remove_command('help')
    bot.add_cog(BotCommands(bot))
    bot.run(token)

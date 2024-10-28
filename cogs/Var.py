import disnake
from disnake.ext import commands

class Var(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot




# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot): 
    bot.add_cog(Var(bot))
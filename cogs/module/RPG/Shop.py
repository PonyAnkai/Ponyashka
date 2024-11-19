import disnake
from disnake.ext import commands
from random import randint

import asyncio
import json
from ..REQ_database import DataBase

class Shop(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot




class _Error(Exception):
    pass

class Shopper:
    def __init__(self):
        pass

    # check stack shop on this day
    # shop refresh each 3-7 days
    def CheckStack(self):
        pass




def setup(bot:commands.Bot):
    bot.add_cog(Shop(bot))
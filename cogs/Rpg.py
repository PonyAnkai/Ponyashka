import disnake
from disnake.ext import commands

import json
import time
from time import time, strftime, gmtime

from .module.RPG.System import *
from .module.REQ_database import DataBase

db = DataBase

class RPG(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command(name='daily', aliases=['подарок', 'сбор', 'gift'])
    async def daily(self, ctx):
        
        user = ctx.message.author.id
        times = db.Lock(user_id=user, slot=5).info()[0]
        gift = ["ESSENCE", "SHARD", "SOUL", "CRISTALL_SOUL", "COU", "VCOIN", "ACOIN", "TCOIN"]
        gift_chance = [.459, .40, .10, .001, .01, .01, .01, .01]
        with open('../PonyashkaDiscord/content/SYS/association.json', encoding='UTF-8') as file:
            associat = json.load(file, )

        if db.Lock(user_id=user, slot=5).ready():
            drop = choices(gift, weights=gift_chance)[0]
            color = disnake.Colour.from_rgb(255, 244, 33)

            db.Money(user=user, currency=drop, value=1).add()
            db.Lock(user_id=user, slot=5, value=43_200).lock()
            embed = disnake.Embed(
                title='Подарочная коробка 🎉', 
                description=f'```Ого! Ты получил из коробки: \n>> [{associat['money'][drop]['name']}] (+1 {associat['money'][drop]['tag']}). \nПриходи завтра ещё!```',
                colour=color)
            await ctx.send(embed=embed)
            return
        good_format_time = strftime('%H:%M:%S', gmtime(times-time.time()))
        color = disnake.Colour.from_rgb(89, 85, 8)

        embed = disnake.Embed(
            title='Подарочная коробка', 
            description=f'```Увы, ты уже забирал коробочку, \nприходи чуть позже, \nскажем... \nЧерез {good_format_time}, хорошо?```',
            colour=color)
        await ctx.send(embed=embed)

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(RPG(bot))
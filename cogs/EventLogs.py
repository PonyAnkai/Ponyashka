import disnake
from disnake.ext import commands

from .module import REQ_database as Rdb
import json

db = Rdb.DataBase

class EventsLogs(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

        with open('../PonyashkaDiscord/config/settings.json') as f:
            self.settings = json.load(f)


    async def money_income(self, member, value:int, currency:str='ESSENCE'):
        '''Valid currency: ESSENCE, SHARD, SOUL, CRISTALL_SOUL, COU, VCOIN, ACOIN, TCOIN'''
        channelLogs = await self.bot.fetch_channel(self.settings['MoneyIncomeChannel'])
        embed = disnake.Embed(
            description=f"**Пользователь:** `{member.name}`\n**Валюта:** `{currency}`\n**Изменение:** `{value}`",
            color=disnake.Color.dark_gold()
            )
        await channelLogs.send(embed=embed)
    
    async def new_user(self, name, posERR):
        channelLogs = await self.bot.fetch_channel(self.settings['guildLogs'])
        embed = disnake.Embed(
            description=f"**Новый пользователь:** `{name}`\n**Добавлено позиций:** `{posERR}`",
            color=disnake.Color.dark_blue()
            )
        await channelLogs.send(embed=embed)

    async def invite_user(self, invite):
        channelLogs = await self.bot.fetch_channel(self.settings['guildLogs'])
        embed = disnake.Embed(
                description=f'`{invite.inviter}` Создал приглашение на сервер.',
                color=disnake.Color.dark_green()
            )
        await channelLogs.send(embed=embed)

    async def delete_user(self, name):
        channelLogs = await self.bot.fetch_channel(self.settings['guildLogs'])
        embed = disnake.Embed(
            description=f"**Ушедший пользователь:** {name}",
            color=disnake.Color.dark_red()
            )
        await channelLogs.send(embed=embed)

    async def DB_update(self):
        pass
    

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(EventsLogs(bot))
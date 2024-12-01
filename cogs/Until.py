import disnake
from disnake.ext import commands

import asyncio
import time

from .module import System as sys
from .module import REQ_database as Rdb
from .module import Views as View

db = Rdb.DataBase

#! Селектор для команды !help
# Тело команды, вызов селектора на 212 строке
class DropDownMenuHelp(disnake.ui.StringSelect):
    def __init__(self, time,  map:map= None, user:int= None):
        self.index= 0
        self.map= map
        self.user= user
        self.time= time

        options = [
            disnake.SelectOption(label='Главная', value='1'),
            disnake.SelectOption(label='Экономика', value='2'),
            disnake.SelectOption(label='RPG-Команды', value='3'),
            disnake.SelectOption(label='Администрирование', value='4'),
            disnake.SelectOption(label='Утилиты', value='5')
        ]
        super().__init__(
            placeholder='Выбор категорий',
            min_values=1,
            max_values=1,
            options=options,
            )

        if map is None:
            raise 'Not have map: [components] [embed]'
            return
    
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id:
            await inter.response.send_message('Данное взаимодействие не ваше.', ephemeral=True)
            return
        if self.values[0] == '1':
            embed = self.map[0]
        if self.values[0] == '2':
            embed = self.map[1]
        if self.values[0] == '3':
            embed = self.map[2]
        if self.values[0] == '4':
            embed = self.map[3]
        if self.values[0] == '5':
            embed = self.map[4]
        if self.time < time.time():
            embed = disnake.Embed(description='**Вышло время взаимодействия**', colour=disnake.Color.red())
            await inter.response.edit_message(embed=embed, view=None)
            return
        else:
            await inter.response.edit_message(embed=embed)

class DropDownViewHelp(disnake.ui.View):
    def __init__(self, map: map, user:int, time:float):
        super().__init__(timeout=None)
        self.add_item(DropDownMenuHelp(time, map, user, ))


class Until(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    
    @commands.command(name='leaders', aliases=['lead', 'лидеры', 'топ'])
    async def leaders(self, ctx):

        try: userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        except: userEnter = None
        if userEnter in ['?', 'help']:
            await Until(self.bot).helpedUser(context=ctx, ctx=ctx, info='leaders')
            return
        else: del userEnter

        if ctx.guild is None:
            await ctx.send(embed=disnake.Embed(description='**Доступно, только на сервере.**'))
            return

        user = ctx.message.author.id
        usersE = db.Info().takeFromRPG(table='user_main_info')
        usersM = db.Info().takeFromRPG(table='user_money')
        
        # !Создание списка топ 10 участников по опыту-уровню
        # Занесение в список всех заригистрированных участников
        topListE = {}
        for index, item in enumerate(usersE):
            topListE[item[0]] = [item[2], item[1]]
        # Сортировка занесенных в список участников
        sortTopListE = sorted(topListE.items(), key= lambda items: items[1], reverse=True)
        # Поиск места в топе автора вызова лидерборда
        callAuthorE = None
        for index, item in enumerate(sortTopListE):
            if user == int(item[0]):
                callAuthorE = index+1
        # Создание списка для вывода
        EmbedText = ''
        for index, item in enumerate(sortTopListE):
            user_ctx = ctx.guild.get_member(item[0])
            try:
                if user_ctx.nick: name = user_ctx.nick
                else: name = user_ctx.name
            except:
                name = db.Info(user_id=item[0]).takeFromRPG(table='user_ds_info')
                if not name: continue
                else: name = name[1]
            EmbedText += f'**``{index + 1}``** **{name}**\n|ㅤУровень: {item[1][1]} ``({item[1][0]} exp)``\n'
            if index == 9:
                break
        # Плашка с итоговой информацией 
        embed_exp = disnake.Embed(
            title='**Топ лидеров по опыту** 🏆', 
            description=EmbedText
            )
        if not ctx.guild is None:
            embed_exp.set_thumbnail(url=ctx.guild.icon)
            embed_exp.set_footer(
                text=f'Вы находитесь на {callAuthorE} месте по опыту', 
                icon_url=ctx.message.author.avatar)
        

        # !Создание списка топ 10 участников по валюте
        topListM = {}
        for index, item in enumerate(usersM):
            summ = item[1] + item[2]*400 + item[3]*3200 + item[4]*6400
            topListM[item[0]] = [summ, item[1], item[2], item[3], item[4]]
        # Сортировка занесенных в список участников
        sortTopListM = sorted(topListM.items(), key= lambda items: items[1], reverse=True)
        # Поиск места в топе автора вызова лидерборда
        callAuthorM = None
        for index, item in enumerate(sortTopListM):
            if user == int(item[0]):
                callAuthorM = index+1
        # Создание списка для вывода
        EmbedText = ''
        for index, item in enumerate(sortTopListM):
            user_ctx = ctx.guild.get_member(item[0])
            try:
                if user_ctx.nick: name = user_ctx.nick
                else: name = user_ctx.name
            except:
                try:
                    name = db.Info(user_id=int(item[0])).takeFromRPG(table='user_ds_info')[1]
                except: name = '`[unknow]`'
            EmbedText += f'**``{index + 1}``** **{name}**\n|ㅤЦенность кошелька ``({item[1][0]:,})``\n'
            if index == 9:
                break
        # Плашка с итоговой информацией 
        embed_money = disnake.Embed(
            title='**Топ лидеров по валюте** 💲', 
            description=EmbedText
            )
        if not ctx.guild is None:
            embed_money.set_thumbnail(url=ctx.guild.icon)
            embed_money.set_footer(
                text=f'Вы находитесь на {callAuthorM} месте по валюте', 
                icon_url=ctx.message.author.avatar)
        

        # !Создание списка топ 10 участников по винстрикам
        # Занесение в список всех заригистрированных участников
        # topListW = {}
        # for index, item in enumerate(usersW):
        #     summ = item[1] + item[2] + item[3]
        #     topListW[item[0]] = [item[1], item[2], item[3], summ]
        # # Сортировка занесенных в список участников
        # sortTopListW = sorted(topListW.items(), key= lambda items: items[1][3], reverse=True)
        # # Поиск места в топе автора вызова лидерборда
        # callAuthorW = None
        # for index, item in enumerate(sortTopListW):
        #     if user == int(item[0]):
        #         callAuthorW = index+1
        # # Создание списка для вывода
        # EmbedText = ''
        # for index, item in enumerate(sortTopListW):
        #     EmbedText += f'**``{index + 1}``** <@{item[0]}>\n|ㅤ**Стриков:** **``{item[1][3]}``**\n|ㅤ[{item[1][0]}сn] [{item[1][1]}cs] [{item[1][2]}rr]\n'
        #     if index == 9:
        #         break
        # # Плашка с итоговой информацией 
        # embed_win = disnake.Embed(
        #     title='**Топ лидеров по винстрикам** 💀', 
        #     description=EmbedText
        #     )
        # if not ctx.guild is None:
        #     embed_win.set_thumbnail(url=ctx.guild.icon)
        #     embed_win.set_footer(
        #         text=f'Вы находитесь на {callAuthorW} месте по винстрикам', 
        #         icon_url=ctx.message.author.avatar)
        
        # !Создание списка топ 1, 10 топов по характиристика РПГ
        # 1. Здоровье(ХП) + Стойкость(DR)
        # 2. Атака(ATK) + Защита(DEF)
        # 3. Выносливость(ST)
        # 4. Крит. урон(CrM) + Крит. шанс(CrC)
        # 5. Сила души(SS)
        # 6. Удача(Luck)

        callAuthorRPG = None
        embed_rpg = disnake.Embed(
            title='**Топ по характиристикам** ', 
            description='В разработке~')
        if not ctx.guild is None:
            embed_rpg.set_thumbnail(url=ctx.guild.icon)
            embed_rpg.set_footer(
                text=f'Вы находитесь на {callAuthorRPG} месте по характиристикам', 
                icon_url=ctx.message.author.avatar)
        # embed_win
        # Список таблиц
        maps = [embed_exp, embed_money, embed_rpg]
        view = View.DropDownViewLeader(map=maps, user=user, time=time.time()+180)
        await ctx.send(embed=embed_exp, view=view)
    
    # TODO: on when got ready a litle RPG content 
    @commands.command(name='help', aliases=['Help', 'помощь', 'Помощь', 'хелп', 'Хелп']) #aliases=['хелп', 'помощь', 'команды']
    async def helpedUser(self, ctx, info=None):

        def embedBase():
            embed = disnake.Embed(
            title='Общая информация',
            description='''
Для дополнительной информации о каждой команде по отдельности используйте: `!help <название>` **->** `(!help work)` либоже после команды указать `?` **->** `(!work ?)`. Если что-то сильно не понятно, спрашивайте у администратора - Поня.

<:SoundGood:1306072180693401690> **Общие команды:**
`leaders` `avatar` `rand` `gif` `russianrollete` `coin`

<:ohYa:1306072065543114752> **Команды понимонов**:
`wallet` `work` `lotery` `craft` `uncraft` `sellpoke` `setpokework` `lookdivpoke` `look` `lookbag` `fightpoke` `setfightgroup` `tradepoke` `support` `upgradepoke` `remelting` `marketpoke` `memorysoul`
            ''',
            colour=disnake.Color.yellow()
            )
            embed.set_footer(text='Поняшь ©2024 Все права запоняшены.', icon_url='https://media.discordapp.net/attachments/1306066774860763146/1306067476601245716/7_-_17.08.2024.png?ex=6735519f&is=6734001f&hm=fbaacb4ca01e0a09222dbdea3d5790d464c100b5ab14724e73a8f48cb9ac4ac5&=&format=webp&quality=lossless&width=290&height=350')
            return ctx.send(embed=embed)

        try: userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        except: userEnter = None
        if userEnter == ctx.message.content.split(' ')[0]:
            await embedBase()
            return
        
        if info:
            aboutSystem = sys.loadJson(path='../PonyashkaDiscord/config/help.json')
            try: helped = aboutSystem[info.lower()]
            except: return await ctx.send(embed=disnake.Embed(description='**Об этом у меня нет информации.**'))
            embed = disnake.Embed(
                title=f'{helped['status']}',
                description=helped['text']
            )
            await ctx.send(embed=embed) 
            return

        aboutSystem = sys.loadJson(path='../PonyashkaDiscord/config/help.json')

        try:
            helped = aboutSystem[userEnter.lower()]
        except:
            embed = disnake.Embed(description='**О таком я не знаю.**', colour=disnake.Color.dark_red())
            await ctx.send(embed=embed)
            return

        embed = disnake.Embed(
            title=f'{helped['status']}',
            description=helped['text']
            )
        await ctx.send(embed=embed) 

    @commands.command(name='avatar',  aliases=['a', 'а', 'ава', 'аватар'])
    async def avatar(self, ctx):
        
        try: userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        except: userEnter = None
        if userEnter in ['?', 'help']:
            await Until(self.bot).helpedUser(context=ctx, ctx=ctx, info='avatar')
            return
        else: del userEnter

        if ctx.message.raw_mentions:
            mentioned = ctx.guild.get_member(ctx.message.raw_mentions[0])
            embed = disnake.Embed(title=f'Аватар пользователя: {mentioned.name}')
            embed.set_image(mentioned.avatar)
            await ctx.send(embed=embed)
            return
        embed = disnake.Embed(title=f'Аватар пользователя: {ctx.message.author.name}')
        embed.set_image(ctx.message.author.avatar)
        await ctx.send(embed=embed)
    
        import requests

        raw = ctx.guild.get_member(ctx.message.raw_mentions[0])
        avatar = raw.avatar
        responce = requests.get(url=avatar)
        with open(f'../PonyashkaDiscord/content/avatar/{raw.id}.png', 'wb') as file:
            file.write(responce.content)
            file.close()

        await ctx.send(f'/ all ok')


    @commands.command(name='clearconsole', aliases=['cls'])
    async def clearConsole(self, ctx):
        import os
        os.system('cls')
        os.system('ECHO DUBUG: System console has been cleared')
        os.system('ECHO ' + '_'*40)

    @commands.command(name='carddrop', aliases=['card'])
    async def card(self, ctx):
        from random import choice, randint
        
        mast = ['пики ♠', 'буби ♦', 'червы ♥', 'трефы ♣']
        value = [2, 3, 4, 5, 6, 7, 8, 9, 'Валет', 'Дама', 'Король', 'Туз']

        text = f'{choice(value)} {choice(mast)}'
        if randint(1, 100) > 90:
            text = f'О нет! {choice('Красный', 'Черный')} джокер!'
        
        embed = disnake.Embed(title=text)
        await ctx.send(embed=embed)


# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot): 
    bot.add_cog(Until(bot))
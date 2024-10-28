from .module import REQ_database as Rdb

import disnake
from disnake.ext import commands
import asyncio
import time
from datetime import date

db = Rdb.DataBase
#! Основное тело селектора лидерборда
# тело самой команды, что вызывает данный селектор на 63 строке
class DropDownMenuLeader(disnake.ui.StringSelect):
    def __init__(self, map:map, user:int, time:float):
        self.index = 0
        self.map = map
        self.user= user
        self.time= time

        # disnake.SelectOption(label='Аркады', value='arcade', description='Сортировка по самому большому винстрику')
        options = [
            disnake.SelectOption(label='Опыт', value='exp', description='Сортировка по свободному опыту'),
            disnake.SelectOption(label='Валюта', value='money', description='Сортировка по валюте [1sl = 3200es, 1sh = 400es]'),
            disnake.SelectOption(label='Характиристикам', value='stat', description='Топ 1, по каждой характиристике')
            ]
        super().__init__(
            placeholder='Сортировка по...',
            min_values=1,
            max_values=1,
            options=options
            )
        
        if map is None:
            raise 'Not have map: [components] [embed]'
        
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id:
            await inter.response.send_message('Не вы вызвали таблицу', ephemeral=True)
        if self.values[0] == 'exp':
            embed= self.map[0]
        elif self.values[0] == 'money':
            embed= self.map[1]
        # elif self.values[0] == 'arcade':
        #     embed= self.map[2]
        elif self.values[0] == 'stat':
            embed= self.map[2]


        if self.time < time.time():
            embed = disnake.Embed(description='**Вышло время взаимодействия**', colour=disnake.Color.red())
            await inter.response.edit_message(embed=embed, view=None)
            return
        else:
            await inter.response.edit_message(embed=embed)

# Прослушиватель выбора
class DropDownViewLeader(disnake.ui.View):
    def __init__(self, map: map, user:int, time:float):
        super().__init__(timeout=None)
        self.add_item(DropDownMenuLeader(map, user, time))

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


#! Модалка для таймера
class Modal(disnake.ui.Modal):
        def __init__(self, comp):
            self.comp = comp
            components = [
                disnake.ui.TextInput(
                    label='Причина',
                    placeholder='Напишите причину по которой я (поняшка) вас позову.',
                    custom_id='reason',
                    style=disnake.TextInputStyle.paragraph
                    )
                ]
            super().__init__(
                title='Создание напоминания',
                custom_id='modal',
                components=components
                )
        async def callback(self, inter: disnake.ModalInteraction):
            y = {}
            for key, item in inter.text_values.items():
                y[key] = item
            await inter.response.send_message(f'Я вас позову!')
            await Timer(user_id= self.comp[0], times=self.comp[1], bot= self.comp[2], message_context=y['reason'], channel=self.comp[3]).start()

#! Таймер
class Timer:
    def __init__(self, user_id, times, channel, bot, message_context):
        self.message_context = message_context
        self.channel = channel
        self.user_id = user_id
        self.time= times
        self.bot= bot

    async def start(self):
        await asyncio.sleep(self.time)
        embed= disnake.Embed(description=self.message_context)
        await self.bot.get_channel(self.channel).send(f'<@{self.user_id}> я вас зову, по вашей просьбе!', embed=embed)



class Until(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    
    @commands.command(name='leaders', aliases=['lead', 'лидеры', 'топ'])
    async def leaders(self, ctx):

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
                name = db.Info(user_id=item[0]).takeFromRPG(table='user_ds_info')[1]
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
        view = DropDownViewLeader(map=maps, user=user, time=time.time()+180)
        await ctx.send(embed=embed_exp, view=view)
    
    # TODO: on when got ready a litle RPG content 
    @commands.command(name='_') #aliases=['хелп', 'помощь', 'команды']
    async def help(self, ctx):
        
        user = ctx.message.author.id

        #! Общая информация
        embed_main = disnake.Embed(
            title='Общая информация',
            description=
'''
```Данный бот создан пользователем @anki_ponyash(Поняшь) при поддержке @ksldi(Симба), @lesnyaa(Лесник) и многим другим пользователями```
```Он предназначен для единоличного использования сервером: "Зарато"```

# Данный бот имеет:
1. **Экономическую систему** 
Данная система позволяет покупать разные диковинные вещи на сервере
будь-то роль, право или проходка. Возможно будет нечто экслюзивное.
Валюта, что является мерилом чата — ChatPoint (ChP)

2. **Систему RPG** 
Во многом система завязана на лоре и многих знаковых моментах сервера.
Данная система является основной, где происходят интересности для самих игроков.
Во многом она является отстраненной от основной атмосферы сервера, но не полностью и возможно
Понь ошибается и это станет частью самого сервера. Мерилом всего.

3. **Разные утилиты**
Данные функции не сильно завязаны на каких-либо особенностях
и просто существуют, либо по просьбе членов сервера, либо просто по желанию Поня.

4. **Администрирование**
Функции для администраторского состава, в частности двух людей сервера: Мага и Поня.
(Понь все ищёт себе помощника, но увы пока достойного человека нет)

||Список команд будет пополняться||
Для просмотра команд, используйте выпадающий список снизу.
'''
            )
        #! Базовые команды
        embed_eco = disnake.Embed(
            title='Экономика',
            description=
'''
# Общий список команд, для экономики

**``1. [leaders] | (lead, лидеры, топ)``**
``` Без параметров ```
Список 10-ти пользователей, что лидируют по опыту (ChatPoint), что зарабатываются в процессе общения.
Также там есть и другие топы пользователей: Валюта, Аркады, RPG-характиристики.

**``2. [work] | (w, работа)``**
``` Без параметров ```
Обычная команда, что позволяет заработать немного базовой валюты сервера.
Будет возможность становиться лучше по професии, однако сильно много тут не заработать,
Если не становиться лучше с каждым разом.

**``3. [crafts] | (cfs, крафтдуш)``**
``` ~cfs <количество из скольки крафт> ```
Способ предобразования душ в более сильные концентраты.
Требуется для получения осколком и душ. Не позволяет получать кристальные души.
s - в конце означает «души (soul)»
'''
            )
        #! Админ-команды
        embed_RPG = disnake.Embed(
            title='RPG-команды',
                        description=
'''
# Общий список RPG-команд

**``1. [stat] | (statistic, стат, статус, профиль)``**
``` Без параметров ```
Показывает некоторую информацию пользователя.
Часто применяется, для отслеживания денег, предметов или просто уровня с опытом.

**``2. [russianRollete] | (rr, рулетка, rollete)``**
``` ~rr <Количество пуль 1-6> ```
Решив сыграть в эту игру, ожидайте последствий.
Игра проста, просто нажимайте на курок и получите немного денег.
Однако проигрышь сделает на один труп больше в этом мире.
(Не полный функционал)
'''
            )
        #! RPG команды
        embed_admin = disnake.Embed(
            title='Администрирование',
                        description=
'''
# Общий список команд для администраторов

**``1. [addChannel] | (ответы, addch)``**
``` ~addch <упоминание канала> ```
Команда для добавления каналов Поняшке, в которых она будет случайно разговаривать.

**``2. [RChannel] | (нуль, rc)_``**
``` Без параметров ```
Команда для проверки разрешенных каналов для случайных разговоров Поняшки.

**``3. [exp] | (—)``**
``` ~exp <+/- Число> <Упоминание пользователя>```
Изменить количество ChatPoint пользователя.
Используется в каких-то особых случаях, как например если ты не Понь.

**``4. [gifadd] | (добгиф, новгиф)``**
``` ~gifadd <приложение сыллки на гифку от дискорда> ```
Простое добавление новых гифок в поняшку.
Позже будет переработана, так как сложно отлавливать рабочие гифки, или гифки что не вливаются.

'''
            )
        #! Другое
        embed_other = disnake.Embed(
            title='Утилиты',
                        description=
'''
# Общий список команд-утилит

**``1. [rand] | (рандом, ранд, случ)``**
``` ~rand <от какого число> <до какого числа> ```
Случайная генерация числа от и до определнного порога.
Если указано одно число, то генерация от 0 и до указанного числа.

**``2. [coin] | (монетка, монеточка, коин)``**
``` ~coin <орёл/решка> ```
Простая игра в орёл или решку с Поняшкой, ничего интересного.
Количество побед подряд сохраняются в профиле.

**``3. [gif] | (гиф, гифка)``**
``` Без параметров ```
Поняшка отправит случайную гифку в чат.
Что попадётся, совершенно не ясно, и будет ли эта гифка уместа.

'''
            )


        maps = [embed_main, embed_eco, embed_RPG, embed_admin, embed_other]
        view = DropDownViewHelp(map=maps, user=user, time=time.time()+1200)
        await ctx.send(embed=embed_main, view=view)

    @commands.slash_command(name='timer', description='Простая напоминалка. Указывать в минутах.', guild_ids=[1199488197885968515, 958063150144577558])
    async def timer(self, inter: disnake.AppCmdInter, time:int):
        if not inter.channel.id in [1205649033125830706, 992673176448417792]:
            return
        
        timeValue= 60
        try:
            timeValue = time * 60
        except:
            pass
        embed= disnake.Embed(title=f'Через {timeValue} я вас позову.')
        user_id = inter.author.id

        comp = [user_id, timeValue, self.bot, inter.channel.id]
        await inter.response.send_modal(modal=Modal(comp=comp))

    @commands.command(name='avatar',  aliases=['ava', 'a', 'ава', 'аватар'])
    async def avatar(self, ctx):
        
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
        with open(f'../bots/content/avatar/{raw.id}.png', 'wb') as file:
            file.write(responce.content)
            file.close()

        await ctx.send(f'/ all ok')

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot): 
    bot.add_cog(Until(bot))
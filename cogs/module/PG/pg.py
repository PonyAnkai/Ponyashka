from disnake.ext import commands
import disnake

import matplotlib
import matplotlib.pyplot as plt
import random
import numpy as np
import math

from ...Until import Until
from .sub_PG import *

import sqlite3
import random
import copy
import time

# Модуль описывающий команды для ВПИ
def xmax(num:int, to_order:int=2) -> int:
    if num > 10_000: to_order += 1
    if num > 1_000_000: to_order += 1
    if num > 100_000_000: to_order += 1
    under = (len(str(num))-to_order)
    return int(f"{math.ceil(num/(10 ** under))}{"0"*under}") if num >= 10 else num

class DataBase:
    def __init__(self):
        self.con = sqlite3.connect(f'./content/PG/_pg.db')
        self.cur = self.con.cursor()
    def save_db(self):
        return self.con.commit()
    
    def create_new_record(self, nameCountry:str, player:bool = False, UID:int = None):
        self.cur.execute(f'SELECT uid FROM user_wins WHERE uid = {self.user_id}')
        if self.cur.fetchone() is None: self.cur.execute("INSERT INTO user_wins VALUES (?, ?, ?, ?)", (self.user_id, 0, 0, 0))
    def refresh_point_rank(self, countrys:list):
        '''Обязательно сделать проверку на верность количеству стран в бд и в реальности, и только потом передать значения на запись. Для создания новых записей указывать в словаре "create":True'''
        '''Данная команда для пересчета очков рейтинга по формулам, рейтинг всегда меняется. Даже при падении.'''
        pass

    def add_stat_graph(self, step, data:map) -> None:
        '''Form -> UID : {POPULATION, ARMY_POWER, BUDGET, PRODUCTION_POWER, REPUTATION, TECH_POWER, COUNTRY_SIZE}'''
        for user in data:
            self.cur.execute('INSERT INTO GRAPH VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (user, step, data[user]['POPULATION'], data[user]['ARMY_POWER'], data[user]['BUDGET'], data[user]['PRODUCTION_POWER'], data[user]['REPUTATION'], data[user]['COUNTRY_SIZE'], data[user]['TECH_POWER'], data[user]['TECH_POWER_MANA'], data[user]['TECH_POWER_PRANA'], data[user]['TECH_POWER_GOD']))
        self.con.commit()
    
    def get_stat_graph(self, UID=None, all=False) -> tuple | None:
        listColumns = ["POPULATION", "ARMY_POWER", "BUDGET", "PRODUCTION_POWER", "REPUTATION", "TECH_POWER", "COUNTRY_SIZE", "TECH_POWER_MANA", "TECH_POWER_PRANA", "TECH_POWER_GOD"]
        returnedData = {}
        if all:
            self.cur.execute('SELECT UID FROM GRAPH')
            userData = set(self.cur.fetchall())

            for user in userData:
                returnedData[user] = {}
                for item in listColumns:
                    self.cur.execute(f'SELECT {item} FROM GRAPH WHERE UID = {user}')
                    returnedData[user][item] = self.cur.fetchall()
            
            return returnedData
        
        else:
            if not UID: return None
            returnedData[UID] = {}
            for item in listColumns:
                self.cur.execute(f'SELECT {item} FROM GRAPH WHERE UID = {UID}')
                returnedData[UID][item] = self.cur.fetchall()
            
            return returnedData

class PG(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command(name='top')
    async def topGraph(self, ctx):

        with open(f'./content/PG/config.json', encoding='UTF-8') as f:
            config = json.load(f)
        with open(f'./content/PG/bots.json', encoding='UTF-8') as f:
            botStat = json.load(f)

        pathPlayer = f'./content/PG/GRAPH/{ctx.author.id}.png'
        fig, ax = plt.subplots(figsize=(12, 8))

        players = os.listdir(f'./content/PG/Game/{config["step"]}')
        dataPlayers = []

    
        def getPBN(config) -> list:
            barColor = [f'{item[1]['color']}' for item in config]
            names = [f'{item[1]['name']}' for item in config]
            dataPlayers = [int(f'{item[1]['data']}') for item in config]

            return barColor, names, dataPlayers

        nameEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        name = nameEnter.split()[0]
        
        # Топ по общей оценке гос-ва
        # Берутся данные со всех сфер и проблем. Больше всего влияет мировое мнение.
        if name == ctx.message.content.split(' ')[0]:
            return await ctx.send(embed=disnake.Embed(description='**В данный момент доступны топы:**\n\n- Население\n- Развитие\n- Технологии\n- Мана\n- Прана\n- Божественность').set_footer(text='!top <категория>'))
            # for user in players:
            #     with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
            #         temp = json.load(f)

            #         pass
        
        elif name.lower() == 'население':
            plt.title('Топ по населению')
            for user in players:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    countHumans = 0
                    nation = temp['population']['nation']
                    for nat in nation: countHumans += nation[nat]['count']

                    config['colors'][user]['data'] = countHumans
            
            for bot in botStat:
                config['bots'][bot]['data'] = botStat[bot]['population']['count']


            config['colors'] = config['colors'] | config['bots']
            sortedConfig = sorted(config['colors'].items(), key=lambda item: item[1]['data'], reverse=True)
            barColor, names, dataPlayers = getPBN(sortedConfig)

        elif name.lower() == 'развитие':
            plt.title('Топ по развитию')
            for user in players:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    tech = temp['tech']['list']
                    mana = temp['mana']['list']
                    prana = temp['prana']['list']
                    god = temp['god']['list']
                    weight = 0

                    if tech: 
                        for item in tech: weight += tech[item]['weight'] 
                    if mana:
                        for item in mana: weight += mana[item]['weight'] 
                    if prana:
                        for item in prana: weight += prana[item]['weight'] 
                    if god:
                        for item in god: weight += god[item]['weight'] 

                    config['colors'][user]['data'] = weight
            
            for bot in botStat:
                config['bots'][bot]['data'] = botStat[bot]['dev']['tech'] + botStat[bot]['dev']['mana'] + botStat[bot]['dev']['prana'] + botStat[bot]['dev']['god']


            config['colors'] = config['colors'] | config['bots']
            sortedConfig = sorted(config['colors'].items(), key=lambda item: item[1]['data'], reverse=True)
            barColor, names, dataPlayers = getPBN(sortedConfig)

        elif name.lower() == 'технологии':
            plt.title('Топ по технологиям')
            for user in players:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    tech = temp['tech']['list']
                    weight = 0
                    if tech: 
                        for item in tech: weight += tech[item]['weight'] 
                    config['colors'][user]['data'] = weight
            for bot in botStat:
                config['bots'][bot]['data'] = botStat[bot]['dev']['tech']

            config['colors'] = config['colors'] | config['bots']
            sortedConfig = sorted(config['colors'].items(), key=lambda item: item[1]['data'], reverse=True)
            barColor, names, dataPlayers = getPBN(sortedConfig)

        elif name.lower() == 'мана':
            plt.title('Топ по мана-знаниям')
            for user in players:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    mana = temp['mana']['list']
                    weight = 0
                    if mana:
                        for item in mana: weight += mana[item]['weight'] 
                    config['colors'][user]['data'] = weight
            for bot in botStat:
                config['bots'][bot]['data'] = botStat[bot]['dev']['mana']

            config['colors'] = config['colors'] | config['bots']
            sortedConfig = sorted(config['colors'].items(), key=lambda item: item[1]['data'], reverse=True)
            barColor, names, dataPlayers = getPBN(sortedConfig)

        elif name.lower() == 'прана':
            plt.title('Топ по прано-знаниям')
            for user in players:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    prana = temp['prana']['list']
                    weight = 0
                    if prana:
                        for item in prana: weight += prana[item]['weight'] 
                    config['colors'][user]['data'] = weight
            for bot in botStat:
                config['bots'][bot]['data'] = botStat[bot]['dev']['prana']

            config['colors'] = config['colors'] | config['bots']
            sortedConfig = sorted(config['colors'].items(), key=lambda item: item[1]['data'], reverse=True)
            barColor, names, dataPlayers = getPBN(sortedConfig)

        elif name.lower() == 'божественность':
            plt.title('Топ по божественности')
            for user in players:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    god = temp['god']['list']
                    weight = 0
                    if god:
                        for item in god: weight += god[item]['weight'] 
                    config['colors'][user]['data'] = weight
            for bot in botStat:
                config['bots'][bot]['data'] = botStat[bot]['dev']['god']

            config['colors'] = config['colors'] | config['bots']
            sortedConfig = sorted(config['colors'].items(), key=lambda item: item[1]['data'], reverse=True)
            barColor, names, dataPlayers = getPBN(sortedConfig)


        else: return
        # print(f'players= {players}\nbarColor= {barColor}\nnames= {names}\ndataP= {dataPlayers}')

        ax.barh(names, dataPlayers, color=barColor, height=1)
        ax.set_yticks(np.arange(len(names)), labels=names)
        ax.invert_yaxis()

        if max(dataPlayers) >= 10:
            upperLim = xmax(max(dataPlayers), 2)+xmax(xmax(max(dataPlayers), 1)//20, 1)
            division = xmax(xmax(max(dataPlayers), 1)//20, 1)

            ax.set_xlim(0, upperLim)
            ax.set_xticks(np.arange(0, upperLim, division)) 

        try: color = config['color'][ctx.author.id]
        except: color = '#FFFFFF'
        # plt.setp(ax.get_xticklabels(), **{'rotation':20})
        plt.margins(y=0)
        ax.set_xticks([])
        fig.patch.set_facecolor(color)
        fig.patch.set_alpha(0.8)
        

        plt.savefig(pathPlayer)

        embed = disnake.Embed(description=f'')
        embed.set_image(file=disnake.File(pathPlayer))

        await ctx.send(embed=embed)

    @commands.command(name='graph', aliases=['gph', 'gp'])
    async def CreateGraph(self, ctx):
        if ctx.author.id not in [374061361606688788, 621318749794074654]:
            return

        userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        if len(userEnter.split()) >= 1 and userEnter != ctx.message.content.split(' ')[0]:
            enter = [abs(int(eval(item))) for item in userEnter.split()]
        else:
            enter = [0, 50, 55, 62, 73, 90, 120, 234, 279, 372, 477, 607, 809]
        
        fig, ax = plt.subplots()
        
        pathPlayer = f'./content/PG/GRAPH/{ctx.author.id}.png'
        
        with open(f'./content/PG/config.json', encoding='UTF-8') as f:
            config = json.load(f)

        try: color = config['color'][ctx.author.id]
        except: color = '#FFFFFF'

        plt.title('График населения')
        ax.plot(enter, color='#f37373')

        ax.grid(True)
        fig.patch.set_facecolor(color)
        fig.patch.set_alpha(0.5)

        ax.set_xlim(0, len(enter)-1)
        ax.set_xticks([item for item in range(len(enter))])
        # ax.axis([0, len(testingData), 0, max(testingData)])

        upperLim = xmax(max(enter), 1)+xmax(xmax(max(enter), 1)//20, 1) if max(enter) >= 10 else max(enter)
        division = xmax(xmax(max(enter), 1)//20, 1) if max(enter) >= 10 else max(enter)
        ax.set_ylim(0, upperLim)
        ax.set_yticks(np.arange(0, upperLim, division)) 
        plt.setp(ax.get_yticklabels(), **{'rotation':0})

        ax.set_xlabel('Цикл хода игры')
        ax.set_ylabel('Население игрока')

        ax.set_xmargin(0)
        ax.set_ymargin(0)

        plt.savefig(pathPlayer) # if need cut [bbox_inches='tight', pad_inches=0]
        embed = disnake.Embed(description=f'Данные для графика: \n{enter}\n- Максимум Y: {max(enter)} -> {xmax(max(enter), 1)}\n- Шаг Y: {max(enter)//20} -> {xmax(xmax(max(enter), 1)//20, 1)}\n- Цвет: Линии(#f37373) - Задник({color})')
        embed.set_image(file=disnake.File(pathPlayer))

        await ctx.send(embed=embed)

    @commands.command(name='info', aliases=['Инфо', 'инфо', 'страна'])
    async def info(self, ctx):
        
        try: userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        except: userEnter = None
        if userEnter in ['?', 'help']:
            await Until(self.bot).helpedUser(context=ctx, ctx=ctx, info='info')
            return
        else: del userEnter

        with open(f'./content/PG/config.json', encoding='UTF-8') as f:
            config = json.load(f)
        if config['inWork'] == 1:
            return await ctx.send(embed=disnake.Embed(description='Похоже сейчас данные обновляются. Подождите новостей, они скоро.'))

        nameEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        name = nameEnter.split()[0]
    
        try: secondComm = nameEnter.split()[1]
        except: secondComm = ''
 
        dirList = os.listdir(f'./content/PG/Game/{config['step']}')
        if str(ctx.author.id) not in dirList and ctx.author.id != 374061361606688788:
            return await ctx.send(f'Похоже вы не являетесь участником данной игры. Обратитесь к текущему ДМ-у.\nЛибо же произошла ошибка и вашей формы нет/сломалась.')

        #? Подгрузить определенный файл по ID о гос-ве игрока. 
        #? Тип файла <DataCountry>
        if ctx.author.id == 374061361606688788: 
            if secondComm in dirList: selectedUser = int(secondComm)
            else: selectedUser = random.choice(dirList)
            dataCountry = getDataPlayer(selectedUser)
        else: 
            selectedUser = ctx.author.id
            dataCountry = getDataPlayer(ctx.author.id)
        # ///

        if name == ctx.message.content.split(' ')[0]:

            nameCounty = dataCountry['static']['countryName']
            if nameCounty == '': nameCounty = 'НЕИЗВЕСТНО'
            sizeCountry = dataCountry['countrySupInfo']['size']
            if sizeCountry == 0: sizeCountry = 'НЕИЗВЕСТНО'
            generalRank = ''
            if generalRank == '': generalRank = 'В-РАЗРАБОТКЕ'

            climatZone = ''
            for index, item in enumerate(dataCountry['zones']['climat']):
                if index+1 != len(dataCountry['zones']['climat']): climatZone += f'{item}, '
                else: climatZone += f'{item}'


            countHumans = 0
            nation = dataCountry['population']['nation']
            for nat in nation:
                countHumans += nation[nat]['count']
            growthTrend = 0  
            for tr in nation:
                growthTrend += round(nation[tr]['count'] * (nation[tr]['trend']/100))

            nationalPlayer = ''
            tempCountNat = 0
            for index, item in enumerate(dataCountry['static']['nationalMain']):
                if index+1 != len(dataCountry['static']['nationalMain']): nationalPlayer += f'{item}, '
                else: nationalPlayer += f'{item}'

                try: tempCountNat += nation[item]['count']
                except: pass
            percentNationalPlayer = tempCountNat / countHumans


            relig = sorted(dataCountry['population']['religion'], key=lambda e:dataCountry['population']['religion'][e]['influence'])
            if not relig: 
                mainReligion = ''
                percentReligionAddept = 0
            else: 
                maxCountAdept = dataCountry['population']['religion'][relig[0]]['count']
                mainReligion = relig[0]
                percentReligionAddept = maxCountAdept / countHumans

            idea = sorted(dataCountry['population']['ideology'], key=lambda e:dataCountry['population']['ideology'][e]['influence'])
            if not idea: 
                mainIdea = ''
                percentIdeaAddept = 0
            else: 
                maxCountIdea = dataCountry['population']['ideology'][idea[0]]['count']
                mainIdea = idea[0]
                percentIdeaAddept = maxCountIdea / countHumans

            mainWay = dataCountry['mainInfo']['mainWay']
            percentWayAddept = dataCountry['mainInfo']['percentWayAddept']

            mainFormGoverment = dataCountry['mainInfo']['mainForm']
            percentGovermentSuport = dataCountry['mainInfo']['percentGovermentSuport']

            if mainWay == '': mainWay = 'НЕТ'
            if mainIdea == '': mainIdea = 'НЕТ'
            if mainReligion == '': mainReligion = 'НЕТ'
            if mainFormGoverment == '': mainFormGoverment = 'НЕТ'

            budgetCountry = dataCountry['countrySupInfo']['budget']
            growthTrendCountry = 0

            rel = dataCountry['politics']['relation']
            for item in rel:
                if not rel[item]['contract']: continue
                for inner in rel[item]['contract']:
                    growthTrendCountry += rel[item]['contract'][inner]['count'] * rel[item]['contract'][inner]['price']

            TECHLVL = dataCountry['tech']['development']
            GODLVL = dataCountry['god']['development']
            PRANALVL = dataCountry['prana']['development']
            MANALVL = dataCountry['mana']['development']

            problem = sorted(dataCountry['problems'], key=lambda e: dataCountry['problems'][e]['power'], reverse=True)
            if problem:
                mainProblemCountry = problem[0] 

            else: mainProblemCountry = 'НЕТ'

            trades = ''
            ally = ''
            enemy = ''


            
            if trades == '': trades = 'НЕТ'
            if ally == '': ally = 'НЕТ'
            if enemy == '': enemy = 'НЕТ'

            embed = disnake.Embed(
                title='Общая информация о вашем государстве',
                description=f'**Название:** `[{nameCounty}]`\n**Мувов:** `[{dataCountry['mainInfo']['moves']}]`\n**Площадь страны:** `[{reduct(sizeCountry) if type(sizeCountry) == int else sizeCountry}]`\n**Нация игрока:** `[{nationalPlayer}]` `({percentNationalPlayer:.2%})`\n\n**Главенствующая религия:** `[{mainReligion}]` `({percentReligionAddept:.2%})`\n**Главенствующая идеалогия:** `[{mainIdea}]` `({percentIdeaAddept:.2%})`\n**Путь развития:** `[{mainWay}]` `({percentWayAddept/1000:.2%})`\n**Форма правления:** `[{mainFormGoverment}]` `({percentGovermentSuport/1000:.2%})`\n\n**Численность населения:** `{reduct(countHumans)}` `существ`\n**Бюджет страны:** `{reduct(budgetCountry)}` `({reduct(growthTrendCountry)}/ход)`\n\n**Уровень божественности:** `[{stepDevelopmentGod(GODLVL)}]`\n**Уровень технологий:** `[{stepDevelopment(TECHLVL)}]`\n**Уровень магии:** `[{stepDevelopmentMana(MANALVL)}]`\n**Уровень праны:** `[{stepDevelopmentPrana(PRANALVL)}]`\n\n**Главная проблема:** `[{mainProblemCountry}]`\n\n**Репутация:** `[{repMaps(dataCountry['politics']['rep'])}]`'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return
        
        elif name.lower() == 'проблемы':

            embed = disnake.Embed(
                    title=f'Вызванная{' случайная' if rrMap else ''} карта: [{ruType[mapEnter]}]',
                    description=f'**Разные карты доступны, после определенных решений.**\n**Доступные карты:** `{canMapCheck}`'
                    ).set_image(file=disnake.File(f'./content/PG/Players/{ctx.author.id}/{mapEnter}'))
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'карта':


            matrix = [0,0,0,0,0]
            typeMaps = ['PMap.png', 'TMap.png', 'RMap.png', 'BMap.png', 'ZMap.png']
            typeMaps_ = copy.copy(typeMaps)
            listTypeMaps = os.listdir(f'./content/PG/Players/{ctx.author.id}/')
            # political, topographics, Relationships, Biome, Zones

            haveMaps = True
            for item in typeMaps_:  
                if item not in listTypeMaps: typeMaps.remove(item)
            if typeMaps: haveMaps = False
            listTypeMaps_ = copy.copy(listTypeMaps)
            for item in listTypeMaps_: 
                if 'Map' not in item: listTypeMaps.remove(item) 
            if haveMaps:
                embed = disnake.Embed(
                    title='Вы не обладаете данными по карте',
                    description='Возможно вам стоит подумать над тем, чтобы развить картографию или озадачить картографа создать нужную карту.'
                    )
            else:
                mapEnter = 'PMap.png'
                rrMap = False
                if secondComm.lower() == "политическая" and 'PMap.png' in typeMaps: mapEnter = 'PMap.png'
                elif secondComm.lower() == "топографическая" and 'TMap.png' in typeMaps: mapEnter = 'TMap.png'
                elif secondComm.lower() == "отношений" and 'RMap.png' in typeMaps: mapEnter = 'RMap.png'
                elif secondComm.lower() == "биомная" and 'BMap.png' in typeMaps: mapEnter = 'BMap.png'
                elif secondComm.lower() == "зоны" and 'ZMap.png' in typeMaps: mapEnter = 'ZMap.png'
                else:
                    mapEnter = random.choice(typeMaps)
                    rrMap = True

                ruType = {'PMap.png':'Политическая', 'TMap.png':'Топографическая', 'RMap.png':'Отношений', 'BMap.png':'Биомная', 'ZMap.png':'Зоны'}
                canMapCheck = ''
                for index, item in enumerate(listTypeMaps):
                    if len(listTypeMaps)-1 != index: canMapCheck += f'{ruType[item]}, '
                    else: canMapCheck += f'{ruType[item]}'
                
                embed = disnake.Embed(
                    title=f'Вызванная{' случайная' if rrMap else ''} карта: [{ruType[mapEnter]}]',
                    description=f'**Разные карты доступны, после определенных решений.**\n**Доступные карты:** `{canMapCheck}`'
                    ).set_image(file=disnake.File(f'./content/PG/Players/{ctx.author.id}/{mapEnter}'))
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'население':


            race = ''
            disease = ''
            specialHuman = ''
            supIdealogy = ''
            supRelig = ''
            countHumans = 0
            growthTrend = 0  
            averageSupp = 0
            averageDown = 0
            nation = dataCountry['population']['nation']
            for item in nation:


                natC = nation[item]['count']*nation[item]['trend']/100
                natC_ = (int(natC*0.5) + int(natC*1.7)) / 2

                if natC_ > 0: PNT = '+'
                elif natC_ == 0: PNT = ''
                else: PNT = '-'

                race += f'**{item}:** `[{nation[item]['supp']/100:.0%}]` \n ╠`Количество: [{reduct(nation[item]['count'])}]`\n ╚`Тенденция: ~[{reduct(natC_)}]` `({PNT})`\n'    

                countHumans += nation[item]['count']
                growthTrend += natC_
                averageSupp += nation[item]['supp'] if nation[item]['supp'] > 0 else 0
                averageDown -= nation[item]['supp'] if nation[item]['supp'] < 0 else 0

            else: 
                averageSupp /= len(nation)
                averageDown /= len(nation)
                if race == '': race = '\n'

            dise = dataCountry['population']['diseases']
            for item in dise:
                disease += f'**{item}:** \n ╠`Зараженных: {reduct(dise[item]['count'])} [{dise[item]['count']/countHumans:.3%}]`\n ╠`Тенденция: {'+' if dise[item]['temp'] >= 0 else '-'}{dise[item]['temp']/100:.0%} (ход)`\n ╚`Смертность: {dise[item]['death']/100:.0%}`\n'

            spec = dataCountry['population']['specialHuman']
            for item in spec:
                specialHuman += f'**{item}:** `{spec[item]['modf']}` \n ╚`Усиление: [{spec[item]['power']/100:.0%}] `\n'

            ideal = dataCountry['population']['ideology']
            for item in ideal:
                supIdealogy = f'**{item}:** \n ╠`Последователей: [{reduct(ideal[item]['count'])}]|[{ideal[item]['count']/countHumans:.5%}]` \n ╚`Влияние: [{ideal[item]['influence']/10000:.2%}]`\n'

            relig = dataCountry['population']['religion']
            for item in relig:
                supRelig = f'**{item}:** \n ╠`Последователей: [{reduct(relig[item]['count'])}]|[{relig[item]['count']/countHumans:.5%}]` \n ╚`Влияние: [{relig[item]['influence']/10000:.2%}]`\n'

            if race == '': race = '`Это странно. Обратитесь к поню.`\n'
            if disease == '': disease = '`Ваша страна здорова. Отрадно.`\n'
            if specialHuman == '': specialHuman = '`У вас никто не выделяется.`\n'
            if supIdealogy == '': supIdealogy = '`Ваша страна не подвержена идеалогиям.`\n'
            if supRelig == '': supRelig = '`У вас нет религиозных идей.`\n'

            if growthTrend > 0: PGT = '+'
            elif growthTrend == 0: PGT = ''
            else: PGT = '-'

            embed = disnake.Embed(
                title='Население страны',
                description=f'**Численность:** `[{reduct(countHumans)}]`\n**Общий прирост:** `~[{reduct(growthTrend)}]` `({PGT})`\n\n**Поддержка:** `[{averageSupp/100:.2%}]`\n**Гнев:** `[{averageDown/100:.2%}]`\n# ```[Болезни]```\n{disease}# ```[Народы]```\n{race}# ```[Особенные]```\n{specialHuman}# ```[Идеалогии]```\n{supIdealogy}# ```[Религии]```\n{supRelig}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'военное':


            armyCountFighters = 0
            armyPower = 0
            armyPowerS = 0

            armyStruct = ''
            armyBase = ''
            WMD = ''

            struct = dataCountry['war']['struct']
            base = dataCountry['war']['base']
            wmd = dataCountry['war']['WMD']
            for item in struct:
                armyStruct = f'**{item}:** \n ╠`Назначение: {struct[item]['target']}`\n ╠`Численность: {reduct(struct[item]['count'])}` \n ╚`Сила: {struct[item]['atk']} | {struct[item]['def']}`\n'
                armyCountFighters += struct[item]['count']
                armyPower += (struct[item]['count'] * (1 + struct[item]['atk']/100) * (1 + struct[item]['def']/100))
            for item in base:
                armyBase = f'**{item}:** \n ╠`Фортификация: {base[item]['lvlDef']} LvL`\n ╠`Снабжение: {base[item]['suplie']/100:.0%}` \n ╚`Гарнизон: {reduct(base[item]['garnisone'])}`\n'
                armyCountFighters += base[item]['garnisone']
                armyPowerS += base[item]['garnisone']
            for item in wmd:
                WMD = f'**{item}:** `{wmd[item]['count']}ед ({wmd[item]['power']} МТ)`\n'
                

            if armyStruct == '': armyStruct = '`У вас нет военных подразделений.`\n'
            if armyBase == '': armyBase = '`У вас нет военных структур.`\n'
            if WMD == '': WMD = '`У вас нет весомого аргумента.`\n'

            embed = disnake.Embed(
                title='Военное дело страны',
                description=f'**Численность армии:** `{reduct(armyCountFighters)}`\n**Военная сила:** `{reduct(armyPower)}ед.` `(+{reduct(armyPowerS)})`\n# ```[Состав]```\n{armyStruct}# ```[Структуры]```\n{armyBase}# ```[ОМП]```\n{WMD}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'политика':


            fractions = ''
            puppetCountry = ''
            relativeCountry = ''

            frac = dataCountry['politics']['fractions']
            pupp = dataCountry['politics']['puppet']
            rel = dataCountry['politics']['relation']

            inf = 0
            for item in frac: inf += frac[item]['influence']
            for item in frac:
                fractions += f'**{item}**\n ╠`Участников: [{frac[item]['count']}]`\n ╚`Влияние: [{frac[item]['influence']/inf:.2%}]`\n'
            for item in pupp:
                puppetCountry += f'**{item}**\n ╠`Подчинение: {pupp[item]['submission']/100:.0%}` `[{pupp[item]['relTrend']/100:.0%}/ход]`\n ╚`Отношение: {pupp[item]['relation']}`\n'
            for item in rel:
                relativeCountry += f'**{item}**\n ╠`Отношения: {rel[item]['relation']}`\n ╚`Договоренности: {rel[item]['argeement']}`'

            if fractions == '': fractions = '`У вас не фракций.`\n'
            if puppetCountry == '': puppetCountry = '`Вы не обладаете марионетками.`\n'
            if relativeCountry == '': relativeCountry = '`Вы не встречали иные страны`\n'

            if dataCountry['politics']['coalition'] == None: coalitions = '`Одиночка`'
            else: coalitions = dataCountry['politics']['coalition']

            embed = disnake.Embed(
                title='Политика',
                description=f'**Репутация:** `{repMaps(dataCountry['politics']['rep'])}`\n**Состояние(Война/нет):** `{'Война' if dataCountry['politics']['inWar'] else 'Мир'}`\n**Коалиция:** {coalitions}\n**Политический статус:** `{dataCountry['politics']['status']}`\n# ```[Фракции]```\n{fractions}# ```[Марионетки]```\n{puppetCountry}# ```[Отношения]```\n{relativeCountry}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'торговля':


            trade = ''
            volumeTrade = 0
            rel = dataCountry['politics']['relation']
            for item in rel:
                if rel[item]['contract']: 
                    trade += f'**{item}**'
                    for inner in rel[item]['contract']:
                        trade += f'\n ╔`Товар: {inner}`\n ╠`Тип: {rel[item]['contract'][inner]['type']}`\n ╚`Тенденция: {rel[item]['contract'][inner]['count']/1000:.3f} тонн ({reduct(abs(rel[item]['contract'][inner]['price']))}/кг) → [{reduct(rel[item]['contract'][inner]['price']*rel[item]['contract'][inner]['count'])}/ход]`'
                        volumeTrade += rel[item]['contract'][inner]['count']
                    trade += '\n'
            else: 
                volumeTrade /= 1000
            
            wealthCountry = 0 
            res = dataCountry['resources']['res']
            for item in res:
                wealthCountry += res[item]['count']*res[item]['price']

            if trade == '': trade = '`Ваша страна ни с кем не торгует`\n'

            embed = disnake.Embed(
                title='Торговля',
                description=f'**Бюджет:** {reduct(dataCountry['countrySupInfo']['budget'])} Маркалей\n**Объём торговли:** {volumeTrade:.3f} тонн/ход\n**Ваша торговая ценность:** {reduct(wealthCountry)}\n# ```[Торговля]```\n{trade}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'производство':


            volumeProduct = 0
            volumeExtract = 0
            createProduct = ''
            exctractProduct = ''

            prod = dataCountry['production']['product']
            extr = dataCountry['production']['extraction']
            for item in prod:
                createProduct += f'**{item}:** `{prod[item]/1000:.3f} Тонн/ход`\n'
                volumeProduct += prod[item]
            for item in extr:
                exctractProduct += f'**{item}** `{extr[item]/1000:.3f} Тонн/ход`\n'
                volumeExtract += extr[item]

            if createProduct == '': createProduct = '`Ваша страна ничего не производит`\n'
            if exctractProduct == '': exctractProduct = '`Ваша страна ничего не добывает`\n'

            embed = disnake.Embed(
                title='Производство',
                description=f'**Объёмы производства:** `{volumeProduct/1000:.3f} Тонн/ход`\n**Объёмы добычи:** `{volumeExtract/1000:.3f} Тонн/ход`\n# ```[Производство]```\n{createProduct}# ```[Добыча]```\n{exctractProduct}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'ресурсы':


            wealthCountry = 0 
            resources = ''
            res = dataCountry['resources']['res']
            for item in res:
                resources += f'**{item}:** `{res[item]['count']/1000:.3f} Тонн(ы) (цена за кг - {res[item]['price']})`\n'
                wealthCountry += res[item]['count']*res[item]['price']

            if resources == '': resources = '`Ваши склады пусты.`\n'

            embed = disnake.Embed(
                title='Ресурсы',
                description=f'**Ценность:** `{reduct(wealthCountry)}`\n# ```[Ресурсы]```\n{resources}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'технологии':

            techWeight = 0
            techHave = ''
            techResearch = ''
            have = sorted(dataCountry['tech']['list'], key=lambda e: dataCountry['tech']['list'][e]['weight'])
            resh = sorted(dataCountry['tech']['sience'], key=lambda e: dataCountry['tech']['sience'][e]['weight'])
            for index, item in enumerate(have):
                if index != len(have)-1: techHave += f'`{item}({dataCountry['tech']['list'][item]['weight']})` '
                else: techHave += f'`{item}({dataCountry['tech']['list'][item]['weight']})`\n'

                techWeight += dataCountry['tech']['list'][item]['weight']
            for index, item in enumerate(resh):
                sience = dataCountry['tech']['sience'][item]
                if index != len(resh)-1: techResearch += f'`({sience['count']}x) {item} [{sience["timesieceN"]}/{sience["timesieceM"]}]` '
                else: techResearch += f'`({sience['count']}x) {item} [{sience["timesieceN"]}/{sience["timesieceM"]}]`\n'

            if techHave == '': techHave = '`У вас нет изученных технологий.`\n'
            if techResearch =='': techResearch = '`У вас нет изучаемых технологий`\n'

            embed = disnake.Embed(
                title='Технологии',
                description=f'**Уровень развития:** `{stepDevelopment(dataCountry['tech']['development'])}`\n**Научных центров:** `{dataCountry['tech']['sienceBase']}`\n**Технологический вес:** `{techWeight}`\n# ```[Технологии]```\n{techHave}# ```[Исследование]```\n{techResearch}\n'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'мана':


            manaWeight = 0
            manaHave = ''
            manaResearch = ''
            have = sorted(dataCountry['mana']['list'], key=lambda e: dataCountry['mana']['list'][e]['weight'])
            resh = sorted(dataCountry['mana']['sience'], key=lambda e: dataCountry['mana']['sience'][e]['weight'])
            for index, item in enumerate(have):
                if index != len(have)-1: manaHave += f'`{item}({dataCountry['mana']['list'][item]['weight']})` '
                else: manaHave += f'`{item}({dataCountry['mana']['list'][item]['weight']})`\n'

                manaWeight += dataCountry['mana']['list'][item]['weight']
            for index, item in enumerate(resh):
                if index != len(resh)-1: manaResearch += f'`{item}({dataCountry['mana']['sience'][item]['weight']})` '
                else: manaResearch += f'`{item}({dataCountry['mana']['sience'][item]['weight']})`\n'

            if manaHave == '': manaHave = '`У вас нет изученных технологий.`\n'
            if manaResearch =='': manaResearch = '`У вас нет изучаемых технологий`\n'

            embed = disnake.Embed(
                title='Мана',
                description=f'**Уровень развития:** `{stepDevelopmentMana(dataCountry['mana']['development'])}`\n**Колдовских центров:** `{dataCountry['mana']['sienceBase']}`\n**Магический вес:** `{manaWeight}`\n# ```[Мано-знания]```\n{manaHave}# ```[Исследование]```\n{manaResearch}\n'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'прана':


            pranaWeight = 0
            pranaHave = ''
            pranaResearch = ''
            have = sorted(dataCountry['prana']['list'], key=lambda e: dataCountry['prana']['list'][e]['weight'])
            resh = sorted(dataCountry['prana']['sience'], key=lambda e: dataCountry['prana']['sience'][e]['weight'])
            for index, item in enumerate(have):
                if index != len(have)-1: pranaHave += f'`{item}({dataCountry['prana']['list'][item]['weight']})` '
                else: pranaHave += f'`{item}({dataCountry['prana']['list'][item]['weight']})`\n'

                pranaWeight += dataCountry['prana']['list'][item]['weight']
            for index, item in enumerate(resh):
                if index != len(resh)-1: pranaResearch += f'`{item}({dataCountry['prana']['sience'][item]['weight']})` '
                else: pranaResearch += f'`{item}({dataCountry['prana']['sience'][item]['weight']})`\n'

            if pranaHave == '': pranaHave = '`У вас нет изученных технологий.`\n'
            if pranaResearch =='': pranaResearch = '`У вас нет изучаемых технологий`\n'

            embed = disnake.Embed(
                title='Прана',
                description=f'**Уровень развития:** `{stepDevelopmentPrana(dataCountry['prana']['development'])}`\n**Колдовских центров:** `{dataCountry['mana']['sienceBase']}`\n**Магический вес:** `{pranaWeight}`\n# ```[Прано-знания]```\n{pranaHave}# ```[Исследование]```\n{pranaResearch}\n'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'божественность':


            godWeight = 0
            godHave = ''
            godResearch = ''
            have = sorted(dataCountry['god']['list'], key=lambda e: dataCountry['god']['list'][e]['weight'])
            resh = sorted(dataCountry['god']['sience'], key=lambda e: dataCountry['god']['sience'][e]['weight'])
            for index, item in enumerate(have):
                if index != len(have)-1: godHave += f'`{item}({dataCountry['god']['list'][item]['weight']})` '
                else: godHave += f'`{item}({dataCountry['god']['list'][item]['weight']})`\n'

                godWeight += dataCountry['god']['list'][item]['weight']
            for index, item in enumerate(resh):
                if index != len(resh)-1: godResearch += f'`{item}({dataCountry['god']['sience'][item]['weight']})` '
                else: godResearch += f'`{item}({dataCountry['god']['sience'][item]['weight']})`\n'

            if godHave == '': godHave = '`У вас нет изученных технологий.`\n'
            if godResearch =='': godResearch = '`У вас нет изучаемых технологий`\n'

            embed = disnake.Embed(
                title='Божественность',
                description=f'**Уровень развития:** `{stepDevelopmentGod(dataCountry['god']['development'])}`\n**Колдовских центров:** `{dataCountry['god']['sienceBase']}`\n**Магический вес:** `{godWeight}`\n# ```[Откровения]```\n{godHave}# ```[Познание]```\n{godResearch}\n'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'модификаторы':

            forerunners = ''
            modificator = ''
            contracts = ''
            modf = dataCountry['modificator']['modif']
            con = dataCountry['modificator']['contracts']
            for item in dataCountry['static']['forerunners']:
                forerunners += f'{item} '
            for item in modf:
                modificator += f'- **{item}**\n  `Мод: {modf[item]['modf']}`\n  `Пост: {modf[item]['desc']}`\n'
            for item in con:
                contracts += f'- **{item}**\n  `Сила контракта: {con[item]['power']}-го порядка`\n  `Требование: {con[item]['want']}`\n  `Награда: {con[item]['prise']}`\n'

            if forerunners == '': forerunners = '`Вы первый в своём поколении.`'
            if modificator == '': modificator = '`У вас нет особенностей нации.`\n'
            if contracts == '': contracts = '`Вы не обременены контрактами богов.`\n'

            try: 
                beast = dataCountry['modificator']['sacredBeast']['name']
                beastEvol = f' ({dataCountry['modificator']['sacredBeast']['evol']} Эвол.)'
            except: 
                beast = '[—]'
                beastEvol = '0'

            embed = disnake.Embed(
                title='Модификаторы',
                description=f'**Предтечи:** {forerunners}\n**Священный зверь:** `{beast}{beastEvol}`\n# ```[Модификаторы]```\n{modificator}# ```[Контракты]```\n{contracts}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

        elif name.lower() == 'поселения':

            
            city = ''
            town = ''
            villagers = ''
            camp = ''
            towns = dataCountry['towns']
            
            countHumans = 0
            nation = dataCountry['population']['nation']
            for item in nation:
                countHumans += nation[item]['count']
            APCP = 0
            for num in towns: 
                if num == 'capital': continue
                for item in towns[num]:
                    APCP  += towns[num][item]['populary']   

            countTowns = 0
            for item in towns['city']:
                city += f'**{item}:** `{reduct(countHumans * (towns['city'][item]['populary'] / APCP))}` ({towns['city'][item]['mainCreate']})\n'
                countTowns += 1
            for item in towns['town']:
                town += f'**{item}:** `{reduct(countHumans * (towns['town'][item]['populary'] / APCP))}` ({towns['town'][item]['mainCreate']})\n'
                countTowns += 1
            for item in towns['villagers']:
                villagers += f'**{item}:** `{reduct(countHumans * (towns['villagers'][item]['populary'] / APCP))}` ({towns['villagers'][item]['mainCreate']})\n'
                countTowns += 1
            for item in towns['camp']:
                camp += f'**{item}:** `{reduct(countHumans * (towns['camp'][item]['populary'] / APCP))}` ({towns['camp'][item]['mainCreate']})\n'
                countTowns += 1

            embed = disnake.Embed(
                title='Поселения',
                description=f'**Столица:** `{towns['capital']}`\n**Количество поселений:** `{countTowns}`\n**Население:** `{reduct(countHumans)}`\n# ```[Большой город]```\n{city}# ```[Город]```\n{town}# ```[Деревня]```\n{villagers}# ```[Поселения]```\n{camp}'
                )
            Fuser = await self.bot.fetch_user(selectedUser)
            embed.set_footer(text=f'Игрок: {Fuser}')
            await ctx.send(embed=embed)
            return

    @commands.command(name='core')
    async def core(self, ctx):
        if ctx.author.id != 374061361606688788: return

        userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        listDataJson = {}
        if userEnter == 'init':
            dataPlayer = os.listdir(f'./content/PG/Players/')
            import shutil
            try: os.mkdir(f'./content/PG/Game/')
            except: pass

            for item in dataPlayer:
                try:shutil.copytree(f'./content/PG/Players/{item}', f'./content/PG/Game/0/{item}')
                except: pass

            for user in dataPlayer:
                with open(f'./content/PG/Game/0/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    countHumans = 0
                    nation = temp['population']['nation']
                    for nat in nation: countHumans += nation[nat]['count']

                    armyPower = 0
                    struct = temp['war']['struct']
                    for item in struct: armyPower += (struct[item]['count'] * (1 + struct[item]['atk']/100) * (1 + struct[item]['def']/100))

                    volumeProduct = 0
                    volumeExtract = 0
                    prod = temp['production']['product']
                    extr = temp['production']['extraction']
                    for item in prod: volumeProduct += prod[item]
                    for item in extr: volumeExtract += extr[item]
                    prodPower = volumeExtract + volumeProduct

                    techWeight = 0
                    have = temp['tech']['list']
                    for item in have: techWeight += temp['tech']['list'][item]['weight']
                    manaWeight = 0
                    haveM = temp['mana']['list']
                    for item in haveM: techWeight += temp['mana']['list'][item]['weight']
                    pranaWeight = 0
                    haveP = temp['prana']['list']
                    for item in haveP: techWeight += temp['prana']['list'][item]['weight']
                    godWeight = 0
                    haveG = temp['god']['list']
                    for item in haveG: techWeight += temp['god']['list'][item]['weight']

                    listDataJson[user] = {
                        "POPULATION":countHumans, 
                        "ARMY_POWER":armyPower, 
                        "BUDGET":temp['countrySupInfo']['budget'], 
                        "PRODUCTION_POWER":prodPower, 
                        "REPUTATION":temp['politics']['rep'], 
                        "COUNTRY_SIZE":temp['countrySupInfo']['size'],
                        "TECH_POWER":techWeight,
                        "TECH_POWER_MANA":manaWeight,
                        "TECH_POWER_PRANA":pranaWeight, 
                        "TECH_POWER_GOD":godWeight 
                        }
            
            DataBase().add_stat_graph(step=0, data=listDataJson)

            config = {"step":0, "inWork":0, "target":"None", "world":0, "colors":{}}
            with open(f'./content/PG/config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=3, ensure_ascii=False)

            await ctx.send('init is ready.\nConfig:\nSet step to 0\nSet main target to «None»\nSet world warning to 0\n\nPlease write a HEX color for user.')
        
        elif userEnter == 'next':
            with open(f'./content/PG/config.json', encoding='UTF-8') as f:
                config = json.load(f)

            step = config['step']
            beforeDataPlayer = os.listdir(f'./content/PG/Game/{step}')

            import shutil
            for item in beforeDataPlayer:
                shutil.copytree(f'./content/PG/Game/{step}/{item}', f'./content/PG/Game/{step+1}/{item}')
            
            config['step'] += 1
            config['inWork'] = 1

            with open(f'./content/PG/config.json', 'w', encoding="utf-8") as f:
                json.dump(config, f, indent=3, ensure_ascii=False)

            # METADATA
            world_population_increase = 0
            info_problem = ''

            afterDataPlayer = os.listdir(f'./content/PG/Game/{config["step"]}')
            timebeforeStart = time.time()
            # шерстения и изменение данных, что динамические
            for user in afterDataPlayer:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    # Население
                    # TODO: Сделать и просчет для ботов
                    nation = temp['population']['nation']
                    for nat in nation: 
                        natAdd = round((nation[nat]['trend']/100) * nation[nat]['count'])
                        randAdd = random.randint(int(natAdd*0.5), int(natAdd*(1.7)))
                        nation[nat]['count'] += randAdd
                        world_population_increase += randAdd

                    # Производство

                    # Добыча

                    # Торговля

                    # Эскалация проблем
                    problem = temp['problems']
                    for prob in problem:
                        problem[prob]['escalation'] += 1
                        if problem[prob]['escalation'] == 10:
                            problem[prob]['escalation'] = 0
                            problem[prob]['power'] += 1
                            info_problem += f'[{prob}] +1 напряженности\n'
 
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'w', encoding='UTF-8') as f:
                    json.dump(temp, f, ensure_ascii=False, indent=2)
            
            #? Автоматика для ботов 
            with open (f'./content/PG', encoding='UTF-8') as f: botsData = json.load(f) 
            for bot in botsData:
                botSelect = botsData[bot]

                # Население
                natAdd_bot = round((botSelect['population']['trend']/100) * botSelect['population']['count'])
                randAdd_bot = random.randint(int(natAdd_bot*0.5), int(natAdd_bot*(1.7)))
                botSelect['population']['count'] += randAdd_bot
                world_population_increase += randAdd_bot

                # Технологии
                for energy in botSelect['dev']:
                    chance = config['bot_tech'] / 100
                    if random.random() < chance: 
                        botSelect['dev'][energy] += 1
                        if random.random() < chance: 
                            botSelect['dev'][energy] += 1
                            if random.random() < chance: 
                                botSelect['dev'][energy] += 1



            else:
                with open (f'./content/PG', 'w', encoding='UTF-8') as f: json.dump(botsData, f) 

            # Шерстение и закидывания в статистику
            for user in afterDataPlayer:
                with open(f'./content/PG/Game/{config['step']}/{user}/data.json', 'r', encoding='UTF-8') as f:
                    temp = json.load(f)

                    countHumans = 0
                    nation = temp['population']['nation']
                    for nat in nation: countHumans += nation[nat]['count']

                    armyPower = 0
                    struct = temp['war']['struct']
                    for item in struct: armyPower += (struct[item]['count'] * (1 + struct[item]['atk']/100) * (1 + struct[item]['def']/100))

                    volumeProduct = 0
                    volumeExtract = 0
                    prod = temp['production']['product']
                    extr = temp['production']['extraction']
                    for item in prod: volumeProduct += prod[item]
                    for item in extr: volumeExtract += extr[item]
                    prodPower = volumeExtract + volumeProduct

                    techWeight = 0
                    have = temp['tech']['list']
                    for item in have: techWeight += temp['tech']['list'][item]['weight']
                    manaWeight = 0
                    haveM = temp['mana']['list']
                    for item in haveM: techWeight += temp['mana']['list'][item]['weight']
                    pranaWeight = 0
                    haveP = temp['prana']['list']
                    for item in haveP: techWeight += temp['prana']['list'][item]['weight']
                    godWeight = 0
                    haveG = temp['god']['list']
                    for item in haveG: techWeight += temp['god']['list'][item]['weight']

                    listDataJson[user] = {
                        "POPULATION":countHumans, 
                        "ARMY_POWER":armyPower, 
                        "BUDGET":temp['countrySupInfo']['budget'], 
                        "PRODUCTION_POWER":prodPower, 
                        "REPUTATION":temp['politics']['rep'], 
                        "COUNTRY_SIZE":temp['countrySupInfo']['size'],
                        "TECH_POWER":techWeight,
                        "TECH_POWER_MANA":manaWeight,
                        "TECH_POWER_PRANA":pranaWeight, 
                        "TECH_POWER_GOD":godWeight 
                        }
                
            DataBase().add_stat_graph(step=config['step'], data=listDataJson)
            await ctx.send(f'Автоматические расчеты сделаны. Остальное - ручками.\nSTEP={config['step']}\n\nПрирост населения по миру +[{randAdd_bot}]\n{info_problem}')

        elif userEnter == 'steps':
            dataPlayer = os.listdir(f'./content/PG/Game')
            await ctx.send(dataPlayer)

        elif userEnter == "update":
            pass

    @commands.command(name='gd')
    async def gd(self, ctx):

        userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        if userEnter != ctx.message.content.split(' ')[0]:
            await ctx.send(DataBase().get_stat_graph(UID=userEnter))

def setup(bot:commands.Bot):
    bot.add_cog(PG(bot))
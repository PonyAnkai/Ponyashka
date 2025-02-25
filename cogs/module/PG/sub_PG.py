from disnake.ext import commands
import disnake

import json
import yaml
import os

from ...Until import Until


def loadFilePG_json(path):
    with open(f'./content/PG/{path}', encoding='UTF-8') as file: 
        return json.load(file)
def loadFilePG_yaml(path):
    with open(f'./content/PG/{path}', encoding='UTF-8') as file: 
        return yaml.safe_load(file)
def reduct(num) -> str:
    if num // 1_000_000_000_000 > 0:
        return f"{(num/1_000_000_000_000):.2f} Тлрд."
    if num // 1_000_000_000 > 0:
        return f"{(num/1_000_000_000):.2f} Млрд."
    if num // 1_000_000 > 0:
        return f"{(num/1_000_000):.2f} Млн."
    if num // 1_000 > 0:
        return f"{(num/1_000):.2f} Тыс."
    return f"{num:.0f}"
def createNewPlayer(UID):
    data = {
        
        "static":{
            "countryName":"",
            "nationalMain":[],
            "forerunners":[],
            "complexity":""
            },
            "mainInfo":{
            "mainWay":"",
            "percentWayAddept":500,
            "mainForm":"",
            "percentGovermentSuport":500
        },
        "mainInfo":{
            "moves":0,
            "mainWay":"",
            "percentWayAddept":0,
            "mainForm":"",
            "percentGovermentSuport":0
        },
        "countrySupInfo":{
            "size":0,
            "budget":0
            },
        "zones":{
            "climat":[]
            },
        "population":{
            "diseases":{}, # name: percent defeats
            "nation":{}, # name: +-%support (trend population)
            "specialHuman":{}, # name: specialist (%buff) (%support)
            "ideology":{}, # name: %support
            "religion":{}
            },
        "war":{
            "struct":{}, # name: size (general) (%supp)
            "base":{}, # name: size (fortification)
            "WMD":{}
            },
        "politics":{
            "rep":0,
            "inWar":False,
            "coalition":None,
            "status":"Спокойный",
            "fractions":{},
            "puppet":{}, # country: relationship (%submission)
            "relation":{} # name: relationship (conract)↓(what)
            },
        "production":{
            "product":{}, # name: size [x.xxx тонн/ход]
            "extraction":{} # name: size [x.xxx тонн/ход]
            },
        "resources":{
            "res":{} # name: size [x.xxx тонн/ход]
            },
        "tech":{
            "development":0, # all 12 tech lvl
            "sienceBase":0,
            "list":{}, # name (lvl/3)
            "sience":{} # name (lvl/3)
            },
        "mana":{
            "development":0, # all 12 tech lvl
            "sienceBase":0,
            "list":{}, # name (lvl/3)
            "sience":{} # name (lvl/3)
            },
        "prana":{
            "development":0, # all 12 tech lvl
            "sienceBase":0,
            "list":{}, # name (lvl/3)
            "sience":{} # name (lvl/3)
            },
        "god":{
            "development":0, # all 12 tech lvl
            "sienceBase":0,
            "list":{}, # name (lvl/3)
            "sience":{} # name (lvl/3)
            },
        "modificator":{
            "sacredBeast":"[—]",
            "modif":{}, # name ↓(what give)
            "contracts":{} # name [to open give a description and other information what need]
            },
        "towns":{
            "capital":"[—]",
            "city":{}, # name: size (what delivers)
            "town":{}, # name: size (what delivers)
            "villagers":{}, # name: size (what delivers)
            "camp":{}, # name: size (what delivers)

            },
        "problems":{}
        }

    dirList = os.listdir('./content/PG/Players')
    if str(UID) not in dirList:
        os.mkdir(f'./content/PG/Players/{UID}')

        with open(f'./content/PG/Players/{UID}/data.json', 'w', encoding='UTF-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=3)

        return f"Пользователь с UID={UID} — Создан."
    else:
        return f"Данный пользователь с UID={UID} — Уже существует."    
def getDataPlayer(UID):
    with open(f'./content/PG/config.json', encoding='UTF-8') as f:
        config = json.load(f)

    with open(f'./content/PG/Game/{config['step']}/{str(UID)}/data.json', 'r', encoding='UTF-8') as f:
        return json.load(f)
    
def repMaps(enter:int) -> str:
    """Диапазон чисел, от -10 и до 10"""
    if not 10 >= enter >= -10: return "UnknowRep" 
    repMap = {'-10':"Владыка демонов", '-9':"Приспешник зла", '-8':"Злой правитель ", "-7":"Генерал армии зла", '-6':"Отвратительная нация", '-5':"Отвергнутая нация", '-4':"Очень плохая репутация", '-3':"Негативная репутация", '-2':"Порченная репутация", '-1':"Холодное отношение", '0':"Нейтральное отношение", '1':"Благосклонное отношение", '2':"Хорошая репутация", "3":"Положительная репутация", "4":"Очень хорошая репутация", "5":"Принятая миром нация", "6":"Прекрасная нация", "7":"Боец академии репутации", "8":"Вековая нация", "9":"Эталон чистоты", "10":"Истинная нация чистоты репутации"}
    return repMap[str(enter)]
def stepDevelopment(step:int) -> str:
    """Шаги от 0 до 10"""
    steps = {0:"Каменный век", 1:"Неолит", 2:"Античность", 3:"Ранее средневековье", 4:"Позднее средневековье", 5:"1-я промышленная революция", 6:"2-я промышленная революция", 7:"Атом", 8:"Электронная эпоха", 9:"Квант", 10:"Будущее"}
    return steps[step]
def stepDevelopmentMana(step:int) -> str:
    """Шаги от 0 до 1"""
    steps = {0:"Познание азов", 1:"Познание маны", 2:"Применение маны", 3:"Создание кристала маны", 4:"Начальный уровень", 5:"1-е отсеевание", 6:"Средний уровень", 7:"2-е отсеевание", 8:"Эпоха архимагов", 9:"ВЫсший пик магии", 10:"Новая магия"}
    return steps[step]
def stepDevelopmentPrana(step:int) -> str:
    """Шаги от 0 до 10"""
    steps = {0:"Обуздание жертвы", 1:"Познание праны", 2:"Жертва сердцем", 3:"Создание ядра праны", 4:"Создание правил мироздания", 5:"Понимание цикла рождения", 6:"Слом цикла сансары", 7:"Формирование медиан", 8:"Рождение нового тела", 9:"Становление небожителем", 10:"Бессмертие"}
    return steps[step]
def stepDevelopmentGod(step:int) -> str:
    """Шаги от 0 до 10"""
    steps = {0:"Богослужение", 1:"Вечная клятва", 2:"Три божественных догмы", 3:"Последователи идеи бога", 4:"Чудо света", 5:"Начало возвышения", 6:"Рождение внутренней звезды", 7:"12 звезд рождения", 8:"Становление богом", 9:"Осознание тщетности", 10:"10-й порядок божетсвенности"}
    return steps[step]




class sub_PG(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command(name='CNP')
    async def createNewPlayer(self, ctx):

        try: userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        except: userEnter = None
        if userEnter in ['?', 'help']:
            await Until(self.bot).helpedUser(context=ctx, ctx=ctx, info='CNP')
            return
        else: del userEnter

        name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        name = name.split()

        for item in name:
            await ctx.send(createNewPlayer(item))


def setup(bot:commands.Bot):
    bot.add_cog(sub_PG(bot))
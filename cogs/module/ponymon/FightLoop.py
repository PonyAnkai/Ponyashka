import disnake
from disnake.ext import commands

import yaml
import random
from .data import *

from ..REQ_database import DataBase
from .Ponymons import *

def install(users, players, adress) -> None:

    data = {
        "step" : 0,
        "log":[],

        "message_adress" : list(adress),
        "Dbox" : [None],
        "Lbox" : [None],

        "p1" : {
            "loseBool":False,
            "ready" : False,

            "id":players['p1'][0],
            "name":players['p1'][1],
            "bot":players['p1_bot'],

            "pokemons":players['p1_pokemons'],
            "move" : {
                # Если None, значит система выбирает стандартное действие
                'slot0':None, 
                'slot1':None,
                'slot2':None
                },

            "items":players['p1_items'],
            "useItem" : {
                # Если None значит ничего не применяется, тупо пропускается слот
                'slot0':None,
                'slot1':None,
                'slot2':None
                },
            },
        
        "p2" : {
            "loseBool":False,
            "ready" : players['p2_bot'],

            "id":players['p2'][0],
            "name":players['p2'][1],
            "bot":players['p2_bot'],

            "pokemons":players['p2_pokemons'],
            "move" : {
                # Если None, значит система выбирает стандартное действие
                'slot0':None, 
                'slot1':None,
                'slot2':None
                },

            "items":players['p2_items'],
            "useItem" : {
                'slot0':None,
                'slot1':None,
                'slot2':None
                },
            },
    }
    saveObjectFight(users=users, yamls=data)

def addRecLog(file_adress, message):
    try:
        with open(f'../PonyashkaDiscord/content/lotery/logs/{file_adress}.txt', 'r', encoding='utf-8') as file:
            log = file.read()
        log += f'\n{message}'
        with open(f'../PonyashkaDiscord/content/lotery/logs/{file_adress}.txt', 'w', encoding='utf-8') as file:
            file.write(log)
    except: 
        with open(f'../PonyashkaDiscord/content/lotery/logs/{file_adress}.txt', 'w', encoding='utf-8') as file:
            file.write(message)


# Небольшие систематизирующие функции
def HPbar(percent) -> str|bool:
    import math
    '''Only take: [0 <= percent <= 1]'''
    if percent > 1: return 'ERROR'
    if percent == 0: return f'`[DEAD]`'
    hp = '█'
    noHp = '...'
    count = math.ceil((percent * 100)//10)
    countNoHp = 10 - count
    return f'|{count*hp}{countNoHp*noHp}|'

async def fightButtonsUpdate(message, p1:bool=None, p2:bool=None, bots=None):
    if p1 is not None and p2 is not None:
        if bots: botCheck = disnake.ui.Button(style=message.components[0].children[1].style, label=f'P2', custom_id=message.components[0].children[1].custom_id, disabled=True)
        else: botCheck = disnake.ui.Button(style=message.components[0].children[1].style, label=f'P2', custom_id=message.components[0].children[1].custom_id)

        buttons = [
        disnake.ui.Button(label=f'P1', custom_id=message.components[0].children[0].custom_id),
        botCheck,

        disnake.ui.Button(style=message.components[0].children[2].style, label=f'Решения', custom_id=message.components[0].children[2].custom_id),
        disnake.ui.Button(style=message.components[0].children[3].style, label=f'Предметы', custom_id=message.components[0].children[3].custom_id),
        disnake.ui.Button(style=message.components[0].children[4].style, label=f'Побег', custom_id=message.components[0].children[4].custom_id)
        ]

        for index, item in enumerate(buttons):
            if item.label == 'P1': 
                if p1: style = disnake.ButtonStyle.green
                else: style = disnake.ButtonStyle.red
                buttons[index].style = style
            if item.label == 'P2': 
                if p2: style = disnake.ButtonStyle.green
                else: style = disnake.ButtonStyle.red
                buttons[index].style = style
            
    if p1 is not None and p2 is None:
        if bots: botCheck = disnake.ui.Button(style=message.components[0].children[1].style, label=f'P2', custom_id=message.components[0].children[1].custom_id, disabled=True)
        else: botCheck = disnake.ui.Button(style=message.components[0].children[1].style, label=f'P2', custom_id=message.components[0].children[1].custom_id)

        buttons = [
        disnake.ui.Button(style=p1, label=f'P1', custom_id=message.components[0].children[0].custom_id),
        botCheck,

        disnake.ui.Button(style=message.components[0].children[2].style, label=f'Решения', custom_id=message.components[0].children[2].custom_id),
        disnake.ui.Button(style=message.components[0].children[3].style, label=f'Предметы', custom_id=message.components[0].children[3].custom_id),
        disnake.ui.Button(style=message.components[0].children[4].style, label=f'Побег', custom_id=message.components[0].children[4].custom_id)
        ]

        for index, item in enumerate(buttons):
            if item.label == 'P1': 
                if p1: style = disnake.ButtonStyle.green
                else: style = disnake.ButtonStyle.red
                buttons[index].style = style
    if p2 is not None and p1 is None:
        buttons = [
        disnake.ui.Button(style=message.components[0].children[0].style, label=f'P1', custom_id=message.components[0].children[0].custom_id),
        disnake.ui.Button(style=p2, label=f'P2', custom_id=message.components[0].children[1].custom_id),
        disnake.ui.Button(style=message.components[0].children[2].style, label=f'Решения', custom_id=message.components[0].children[2].custom_id),
        disnake.ui.Button(style=message.components[0].children[3].style, label=f'Предметы', custom_id=message.components[0].children[3].custom_id),
        disnake.ui.Button(style=message.components[0].children[4].style, label=f'Побег', custom_id=message.components[0].children[4].custom_id)
        ]

        for index, item in enumerate(buttons):
            if item.label == 'P2': 
                if p2: style = disnake.ButtonStyle.green
                else: style = disnake.ButtonStyle.red
                buttons[index].style = style
    await message.edit(components=buttons)

# mainLoop — главный объект
def loadObjectFight(users) -> map:
    with open(f'../PonyashkaDiscord/content/lotery/fight/{users}.yaml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    loop = MainLoop(data=data, fileUsers=users)
    return loop
def saveObjectFight(users, yamls) -> None:
    with open(f'../PonyashkaDiscord/content/lotery/fight/{users}.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(yamls, file)

def updateMainText(obj) -> disnake.Embed:
    textP1 = ''
    for index, ix in enumerate(obj.p1['pokemons']):
        item = obj.p1['pokemons'][ix]
        if item is None: 
            textP1 += f'**{index+1} ]|[ None ]**\n'
            continue
        percentHp = item['other_param']['healpoint_now']/item['params']['healpoint']

        attack = f'{round(item['params']['attack']*0.8)}-{round(item['params']['attack']*1.2)}'
        hp = f'{item['other_param']['healpoint_now']}/{item['params']['healpoint']}'

        textP1 += f'**{index+1} ]|[ . ]|[ {item['name']} ]**\n`[ HP: {hp} ]|[ ATK: {attack} ]`\n{HPbar(percentHp)}\n'

    textP2 = ''
    for index, ix in enumerate(obj.p2['pokemons']):
        item = obj.p2['pokemons'][ix]
        if item is None: 
            textP2 += f'**{index+1} ]|[ None ]**\n'
            continue
        percentHp = item['other_param']['healpoint_now']/item['params']['healpoint']

        attack = f'{round(item['params']['attack']*0.8)}-{round(item['params']['attack']*1.2)}'
        hp = f'{item['other_param']['healpoint_now']}/{item['params']['healpoint']}'

        textP2 += f'**{index+1} ]|[ . ]|[ {item['name']} ]**\n`[ HP: {hp} ]|[ ATK: ~{attack} ]`\n{HPbar(percentHp)}\n'

    body = f'``` <-- Игрок P1: {obj.p1['name']} --> ```\n{textP1}\n``` <-- Игрок P2: {obj.p2['name']} --> ```\n{textP2}\n```Логи боя```\n{obj.temporalLogs}'

    if obj.p2['bot']: title = "Бой против бота"
    else: title = "Бой между игроками"

    embed = disnake.Embed(
        title=title,
        description=body
        ).set_footer(text=f'Шаг боя: {int(obj.step)+1}')
    return embed

class ViewDropDownMenus(disnake.ui.View):
    def __init__(self, options:list, user:int, fileID):
        super().__init__(timeout=None)
        self.add_item(DropDownMenu(options, user, fileID))
class DropDownMenu(disnake.ui.StringSelect):
    def __init__(self, options, user, fileID):
        self.user = user
        self.fileID = fileID

        super().__init__(
            placeholder=f'Доступные действия понимона',
            min_values=1,
            max_values=1,
            options=options
            )

    async def callback(self, inter: disnake.MessageInteraction):

        objFile = loadObjectFight(users=self.fileID)

        if int(self.user) == int(objFile.p2['id']): 
            userInteract = objFile.p2
            Enemy = objFile.p1
        else: 
            userInteract = objFile.p1
            Enemy = objFile.p2

        if self.values[0] != 'cannelSelectMovePonymons':
        #! / / / / / / / / / / / / / /
            indexed, move, pokeSlot, users = (self.values[0]).split('|')

            #? Описать разные сценарии: Атака, защита/уворот, баффинг, хил
            
            #? Описание сценария атакующего действия
            if move == 'atk':
                moves = ''
                for index, item in enumerate(Enemy['pokemons']):
                    entry = Enemy['pokemons'][item]
                    try: 
                        percentHp = entry['other_param']['healpoint_now']/entry['params']['healpoint']
                        hp = f'{entry['other_param']['healpoint_now']}/{entry['params']['healpoint']}'

                        moves += f'**{index+1} ]|[ {entry['name']} ]:**\n{HPbar(percentHp)} `[{hp}]`\n\n'
                        
                    except: moves += f'\n~~**{index+1} ]|[ None ]**~~\n'

                text = f'```Выберите кого атаковать```\n{moves}'

                embed = disnake.Embed(description=text)
                buttons = []
                for i, item in enumerate(Enemy['pokemons']):

                    if Enemy['pokemons'][item] is None: 
                        buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label=f'{i+1}', custom_id=f'SelectTargetToUseMove|{self.fileID}|{pokeSlot}|{move}-{item}', disabled=True))
                        continue

                    buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{i+1}', custom_id=f'SelectTargetToUseMove|{self.fileID}|{pokeSlot}|{move}-{item}'))
                else:
                    buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label='Отмена', custom_id=f'MVBF-BACKSTEP|{self.fileID}'))

                await inter.response.edit_message(embed=embed, view=None)
                await inter.followup.edit_message(inter.message.id, components=buttons)
            elif move in ['deff', 'env', 'sheal']:
                #! / / / / / / / / / / / / / /

                userInteract['move'][pokeSlot] = f'{move}-{pokeSlot}'
                saveObjectFight(users=users, yamls=objFile.toSave())

                #! / / / / / / / / / / / / / /

                moves = ''
                for index, item in enumerate(userInteract['move']):
                    if userInteract['move'][item] is None: 
                        try: moves += f'**{index+1} ]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| Действие (Базовое): Атака {index+1}-го покемона`\n'
                        except: moves += f'\n~~**{index+1} ]|[ None ]**~~\n'
                    else: 
                        moves += f'**{index+1}]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| {await decriptedCommandLocale(userInteract['move'][item])}`\n'
                    

                text = f'```Выбранные действия покемонов```\n{moves}'
                embed = disnake.Embed(description=text) 
                buttons = []
                for i, item in enumerate(userInteract['pokemons']):

                    if userInteract['pokemons'][item] is None: 
                        buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label=f'{i+1}', custom_id=f'SelectedMOVIESPOKEENDED|{item}|{self.fileID}|{self.user}', disabled=True))
                        continue

                    buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{i+1}', custom_id=f'SelectedMOVIESPOKEENDED|{item}|{self.fileID}|{self.user}'))
                else:
                    buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Назад', custom_id=f'MVBF-BACKSTEP|{self.fileID}'))
                

                await inter.response.edit_message(embed=embed, view=None)
                await inter.followup.edit_message(inter.message.id, components=buttons)

        #! / / / / / / / / / / / / / /
        else:
            moves = ''
            for index, item in enumerate(userInteract['move']):
                if userInteract['move'][item] is None: 
                    try: moves += f'**{index+1} ]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| Действие (Базовое): Атака {index+1}-го покемона`\n\n'
                    except: moves += f'\n~~**{index+1} ]|[ None ]**~~\n'
                else: 
                    moves += f'**{index+1}]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| {await decriptedCommandLocale(userInteract['move'][item])}`\n\n'
                
            text = f'```Выбранные действия покемонов```\n{moves}'

            embed = disnake.Embed(description=text) 

            buttons = []
            for i, item in enumerate(userInteract['pokemons']):

                if userInteract['pokemons'][item] is None: 
                    buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label=f'{i+1}', custom_id=f'SelectedMOVIESPOKEENDED|{item}|{self.fileID}|{self.user}', disabled=True))
                    continue

                buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{i+1}', custom_id=f'SelectedMOVIESPOKEENDED|{item}|{self.fileID}|{self.user}'))
            else:
                buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Назад', custom_id=f'MVBF-BACKSTEP|{self.fileID}'))

            await inter.response.edit_message(embed=embed, view=None)
            await inter.followup.edit_message(inter.message.id, components=buttons)


# Основной прослушиватель для кнопок боя
class FightLoop(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    #! Лютый рофл, потом обмозговать
    async def getMessageOBJ(self, message_adress) -> disnake.message:
        return await self.bot.get_guild(message_adress['guild']).get_channel(message_adress['channel']).fetch_message(message_adress['message'])

    # Прослушиватель готовности к бою (Подтверждения окончания хода)
    # Такая же динамическая кнопка как и при потверждении готовности к бою
    # Если оба игрока готовы, то запуск функции NextStep
    @commands.Cog.listener('on_button_click')
    async def getReadyButton(self, inter: disnake.MessageInteraction):
        accList = ['RBF_P1', 'RBF_P2']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return
        
        comm, userID, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(userID) == int(objFile.p1['id']) or int(userID) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return

        # Описание первого игрока
        print(inter.author.id, objFile.p1['id'], userID)
        if int(inter.author.id) == int(objFile.p1['id']) and int(inter.author.id) == int(userID):
            objFile.p1["ready"] = not objFile.p1["ready"]

            await fightButtonsUpdate(inter.message, p1=objFile.p1["ready"], bots=objFile.p2['bot'])
            saveObjectFight(users=users, yamls=objFile.toSave())


        # Описание второго игрока
        if int(inter.author.id) == int(objFile.p2['id']) and int(inter.author.id) == int(userID):
            objFile.p2["ready"] = not objFile.p2["ready"]

            await fightButtonsUpdate(inter.message, p2=objFile.p2["ready"])
            saveObjectFight(users=users, yamls=objFile.toSave())

        # Описание полной готовности двух игроков
        if  objFile.p1["ready"] and  objFile.p2["ready"]:

            await objFile.nextStep(message=inter.message)

            objFile.p1["ready"] = not objFile.p1["ready"]
            if not objFile.p2['bot']: objFile.p2["ready"] = not objFile.p2["ready"]

            if not objFile.EndBattle: await fightButtonsUpdate(inter.message, p1=objFile.p1["ready"], p2=objFile.p2["ready"], bots=objFile.p2['bot'])

            saveObjectFight(users=users, yamls=objFile.toSave())



        await inter.response.defer()

    # Прослушиватель кнопки действий
    # Активация навыка не требует ОД (очков действия), но занимают выбор действия у покемона
    # Действия все требуют от 1 до 5 ОД, также занимают выбор действия у покемона
    @commands.Cog.listener('on_button_click')
    async def getMoves(self, inter: disnake.MessageInteraction):
        accList = ['MVBF', 'MVBF-BACKSTEP', 'CFB']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        
        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2

        if comm == 'CFB':
            userInteract['move'] = {
                # Если None, значит система выбирает стандартное действие
                'slot0':None, 
                'slot1':None,
                'slot2':None
                }
            saveObjectFight(users=users, yamls=objFile.toSave())

            

        buttons = [
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Навыки', custom_id=f'PFB|{users}'),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Действия', custom_id=f'DFB|{users}'),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Очистить', custom_id=f'CFB|{users}'),
            ]
        
        moves = ''
        for index, item in enumerate(userInteract['move']):
            if userInteract['move'][item] is None: 
                try: moves += f'**{index+1} ]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| Базовое действие (Атака:{index+1}-го)`\n\n'
                except: moves += f'~~**{index+1} ]|[ None ]**~~\n\n'
            else: 
                try: moves += f'**{index+1}]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| {await decriptedCommandLocale(userInteract['move'][item])}`\n\n'
                except: moves += f'~~**{index+1} ]|[ None ]**~~\n\n'

        text = f'```Выбранные действия покемонов```\n{moves}\n'

        embed = disnake.Embed(description=text)
        if comm == 'CFB' or comm == 'MVBF-BACKSTEP':
            await inter.response.edit_message(embed=embed, components=buttons)
        else:
            await inter.response.send_message(ephemeral=True, embed=embed, components=buttons)
    
    # Прослушиватель для предметов
    @commands.Cog.listener('on_button_click')
    async def getItems(self, inter: disnake.MessageInteraction):
        accList = ['ISBF', 'ICFB']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return

        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2

        if comm == 'ICFB':
            userInteract['useItem'] = {
                # Если None, значит система выбирает стандартное действие
                'slot0':None, 
                'slot1':None,
                'slot2':None
                }
            saveObjectFight(users=users, yamls=objFile.toSave())

        buttons = []
        if objFile.p2['items'] is None:
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Добавить', custom_id=f'ISFB-2|{users}', disabled=True))
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Очистить', custom_id=f'ICFB|{users}', disabled=True))
        else:
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Добавить', custom_id=f'ISFB-2|{users}'))
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.primary, label='Очистить', custom_id=f'ICFB|{users}'))
        
        #? Окошко предметов до 100 (5 кнопок по 20) [Не забыть про компрессию предметов, как и с покесами]
        text = f'### Доступные предметы:\n'
        if objFile.p2['items'] is None:
            text += '`< Доступных предметов не наблюдается >`'
        else:
            pass


        embed = disnake.Embed(description=text)
        if comm == 'ICFB':
            await inter.response.edit_message(embed=embed, components=buttons)
        else:
            await inter.response.send_message(ephemeral=True, embed=embed, components=buttons)

    # Прослушиватель для инвентаря предметов
    # Максимум 20 предметов в списке, при придметном выборе, давать возможность выбрать 1 из 5 кнопок списков. Максимум 100 предметов в инвентаре пользлвателя.
    @commands.Cog.listener('on_button_click')
    async def getItemUseCommand(self, inter: disnake.MessageInteraction):
        accList = ['ISFB-2']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return

    # Прослушиватель для действий [навыки/возможные действия]
    # Навыки считываются напрямую с покемонов
    # Количество применимых предметов за ход: 3
    # Действия динамически отображаются, по ситуации
    # Примеры стандартных действий: Атаковать (от урона покемона), ожидать (накапливание очков действия), Укрепление (защититься от 1-й атаки)
    # Примеры динамических действий: Собрать волю(+15% atk), защитить честь (+10% def), выбро атаки покемонов (кто-кого), стандартное значение атаковать покемона той же интдексации
    #! Собственно активация навыка
    @commands.Cog.listener('on_button_click')
    async def moveSelectPerksToreadyExit(self, inter: disnake.MessageInteraction):
        accList = ['EPUFB']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users, pokes, perk_select = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        else: interact = inter.author.id

        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2

        userInteract['move'][pokes]

        saveObjectFight(users=users, yamls=objFile.toSave())
        await self.getMoves(inter=inter)
    
    #! конкретно после выбора покемона которому активировать навык
    @commands.Cog.listener('on_button_click')
    async def moveSelectPerksToready(self, inter: disnake.MessageInteraction):
        accList = ['SMslot0', 'SMslot1', 'SMslot2']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, pokes, users, userInteract = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        else: interact = inter.author.id

        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2

        text = f'{int(pokes[-1])+1} ]|[ {userInteract['pokemons'][pokes]['name']} ]'
        buttons = []

        for index, item in enumerate(userInteract['pokemons'][pokes]['trait']['perk_slot']):
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label=f'{index+1}', custom_id=f'EPUFB|{users}|{pokes}|{item}', disabled=True))


        embed = disnake.Embed(description=text)
        await inter.response.edit_message(embed=embed, components=buttons)
    
    #! Выбор покемона на использование навыка
    @commands.Cog.listener('on_button_click')
    async def moveSelectPerks(self, inter: disnake.MessageInteraction):
        accList = ['PFB']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        else: interact = inter.author.id

        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2


        buttons = []
        for index, item in enumerate(userInteract['pokemons']):

            if userInteract['pokemons'][item] is None: 
                buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label=f'{index+1}', custom_id=f'SMslot{index}|{item}|{users}|{interact}', disabled=True))
                continue
            
            perks = userInteract['pokemons'][item]['trait']['perk_slot']

            Nones = False
            for item in perks:
                if perks[item] is not None: break
            else: Nones = True

            if Nones:
                buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{index+1}', custom_id=f'SMslot{index}|{item}|{users}|{interact}', disabled=True))
                continue

            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{index+1}', custom_id=f'SMslot{index}|{item}|{users}|{interact}'))
        else:
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Назад', custom_id=f'MVBF-BACKSTEP|{users}'))

        text = '```Выбор покемона с навыком```\n'
        for index, item in enumerate(userInteract['pokemons']):
            try: traits = userInteract['pokemons'][item]['trait']['perk_slot']
            except: 
                text += f'~~**{index+1} ]|[ None ]**~~'
                continue

            tt = ''
            for perks in traits:
                if traits[perks] is None: tt += f'~~`| <[ None ]>`~~\n' 
                else: tt += f'| [ {traits[perks]['name']} ]|[ {'Готов' if traits[perks]['buffer']/traits[perks]['endurance'] == 0 else 'Не готов'} ]|[ R: {traits[perks]['buffer']} ]\n'

            text += f'**{index+1} ]|[ {userInteract['pokemons'][item]['name']} ]**\n{tt}\n'

        embed = disnake.Embed(description=text)

        await inter.response.edit_message(embed=embed, components=buttons)

    @commands.Cog.listener('on_button_click')
    async def moveSelectTargetAfterSelectMoves(self, inter: disnake.MessageInteraction):
        accList = ['SelectTargetToUseMove']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        indexed, users, poke, command = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        else: interact = inter.author.id
        
        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2
        #! / / / / / / / / / / / / / /

        userInteract['move'][poke] = command
        saveObjectFight(users=users, yamls=objFile.toSave())

        #! / / / / / / / / / / / / / /
        buttons = []
        for index, item in enumerate(userInteract['pokemons']):

            if userInteract['pokemons'][item] is None: 
                buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label=f'{index+1}', custom_id=f'SelectedMOVIESPOKE|{item}|{users}|{interact}', disabled=True))
                continue

            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{index+1}', custom_id=f'SelectedMOVIESPOKE|{item}|{users}|{interact}'))
        else:
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Назад', custom_id=f'MVBF-BACKSTEP|{users}'))

        moves = ''
        for index, item in enumerate(userInteract['move']):
            if userInteract['move'][item] is None: 
                try: moves += f'**{index+1} ]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| Действие (Базовое): Атака {index+1}-го покемона`\n\n'
                except: moves += f'~~**{index+1} ]|[ None ]**~~\n\n'
            else: 
                moves += f'**{index+1}]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| {await decriptedCommandLocale(userInteract['move'][item])}`\n'
            
        text = f'```Выбранные действия покемонов```\n{moves}'

        embed = disnake.Embed(description=text)

        await inter.response.edit_message(embed=embed, components=buttons)

    #! Выбор действия для конкретного покемона
    @commands.Cog.listener('on_button_click')
    async def moveSelectMovesOnPoke(self, inter: disnake.MessageInteraction):
        accList = ['SelectedMOVIESPOKE']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, slot, users, interact = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        else: interact = inter.author.id
        
        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2

        # BUG: Перенести данную хуйню в другое место, так как реролится действия каждый раз. Это баг
        components = [disnake.SelectOption(label=f'Отменить', value=f'cannelSelectMovePonymons')]
        text = '```Доступные действия для ПоNимона```\n'
        for index, item in enumerate(listMoves):
            if 0 <= random.randint(0, 100) <= chancedDropMoves[item]:
                text += f'**`-> {movesToRu(item)}`**\n'
                components.append(
                    disnake.SelectOption(
                        label=f'{movesToRu(item)}',
                        value=f'{index}|{item}|{slot}|{users}'
                        )
                    )
        
        embed = disnake.Embed(description=text)

        view = ViewDropDownMenus(options=components, user=interact, fileID=users)
        await inter.response.edit_message(embed=embed, components=None)
        await inter.followup.edit_message(inter.message.id, view=view)
        # await inter.response.edit_message(embed=disnake.Embed(title='Выбор действия покемона'), view=view)

    #! Выбор действий для покемонов
    @commands.Cog.listener('on_button_click')
    async def moveSelectMoves(self, inter: disnake.MessageInteraction):
        accList = ['DFB']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        else: interact = inter.author.id
        
        if int(inter.author.id) == int(objFile.p1['id']): userInteract = objFile.p1
        else: userInteract = objFile.p2
        
        buttons = []
        for index, item in enumerate(userInteract['pokemons']):

            if userInteract['pokemons'][item] is None: 
                buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.danger, label=f'{index+1}', custom_id=f'SelectedMOVIESPOKE|{item}|{users}|{interact}', disabled=True))
                continue

            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'{index+1}', custom_id=f'SelectedMOVIESPOKE|{item}|{users}|{interact}'))
        else:
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Назад', custom_id=f'MVBF-BACKSTEP|{users}'))

        moves = ''
        for index, item in enumerate(userInteract['move']):
            if userInteract['move'][item] is None: 
                try: moves += f'**{index+1} ]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| Действие (Базовое): Атака {index+1}-го покемона`\n\n'
                except: moves += f'~~**{index+1} ]|[ None ]**~~\n\n'
            else: 
                try: moves += f'**{index+1}]|[ {userInteract['pokemons'][item]['name']} ]:**\n`| {await decriptedCommandLocale(userInteract['move'][item])}`\n\n'
                except: moves += f'~~**{index+1} ]|[ None ]**~~\n\n'
            
        text = f'```Выбранные действия покемонов```\n{moves}'

        embed = disnake.Embed(description=text)

        await inter.response.edit_message(embed=embed, components=buttons)

    # Прослушиватель для побега с боя
    #? Не сделано
    @commands.Cog.listener('on_button_click')
    async def escapeFromBattle(self, inter: disnake.MessageInteraction):
        accList = ['ESCBF']
        for item in accList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, users = inter.component.custom_id.split('|')
        objFile = loadObjectFight(users=users)

        if not (int(inter.author.id) == int(objFile.p1['id']) or int(inter.author.id) == int(objFile.p2['id'])):
            await inter.response.send_message('Вы не являетесь участником боя.', ephemeral=True)
            return
        
        print(objFile.Dbox)
        await inter.response.defer()

        # import pprint
        # ob = objFile.toSave()
        # pprint.PrettyPrinter(width=5).pprint(ob)

#! Форма карты предметов
# ids:{
#   name:"",
#   action:""
# }

class MainLoop:
    def __init__(self, fileUsers, data=None) -> None:

        self.EndBattle = False

        self.temporalLogs = ''
        self.log = data['log']
        self.fileUsers = fileUsers

        self.step = data['step']
        self.message_adress = data['message_adress']

        self.Dbox = data['Dbox'],
        self.Lbox = data['Lbox'],

        self.p1 = {
            "loseBool":data['p1']['loseBool'],
            "ready": data['p1']['ready'],

            "id":data['p1']['id'],
            "name":data['p1']['name'],
            "bot":data['p1']['bot'],

            "pokemons":data['p1']['pokemons'],
            "move": data['p1']['move'],

            "items":data['p1']['items'],
            "useItem":data['p1']['useItem']
            }
            
        self.p2 = {
            "loseBool":data['p2']['loseBool'],
            "ready":data['p2']['ready'],

            "id":data['p2']['id'],
            "name":data['p2']['name'],
            "bot":data['p2']['bot'],

            "pokemons":data['p2']['pokemons'],
            "move":data['p2']['move'],

            "items":data['p2']['items'],
            "useItem":data['p2']['useItem']
            }


    def toSave(self):
        data = {
            "step" : self.step,
            "log": self.log,

            "message_adress" : self.message_adress,
            "Dbox": self.Dbox[0],
            "Lbox": self.Lbox[0],

            "p1" : {
                "ready": self.p1['ready'],
                "loseBool":self.p1['loseBool'],

                "id":self.p1['id'],
                "name":self.p1['name'],
                "bot":self.p1['bot'],

                "pokemons":self.p1['pokemons'],
                "move":self.p1['move'],

                "items":self.p1['items'],
                "useItem":self.p1['useItem']
                },

            "p2" : {
                "loseBool":self.p2['loseBool'],
                "ready":self.p2['ready'],

                "id":self.p2['id'],
                "name":self.p2['name'],
                "bot":self.p2['bot'],

                "pokemons":self.p2['pokemons'],
                "move":self.p2['move'],

                "items":self.p2['items'],
                "useItem":self.p2['useItem']
                },
        }
        return data


    async def savePokemonsPVP(self, updateMap, deleteMap):
        pass

    def savePokemonsPVE(self, updateMap, deleteMap):
        pass


    async def RunAwayFromBattle(self, message,  winner,  looser):
        #? При побеге бегущие получают урон в 15% от здоровья
        #? Опыт при побеге не получается
        pass

    async def battleEnd(self, message,  winner,  looser):
        '''Учесть, что следует удалить у покемонов перед сохранением: moveCount, modifacators'''
        '''100% winner exp gained, 15% looser exp gained'''

        def paramGenerator():
            params = {
                "params":{'attack':"atk", 'healpoint':"hp", 'regen':'reg'}, 
                "curr":{'price':"price"}
                }
            firstSelect = choice(list(params.keys()))
            secondSelect = choice(list(params[firstSelect].keys()))
            return (firstSelect, secondSelect, random.randint(1, 2), params[firstSelect][secondSelect])

        pokeExpUp = ''
        updateMap = {}
        for item in winner['pokemons']:
            if winner['pokemons'][item] is None: continue

            expGen = random.randint(10, 75)
            paramGen = paramGenerator()

            pokeExpUp += f'**Winner:** _-> {winner['pokemons'][item]['name']} (+{expGen}exp / +{paramGen[2]}{paramGen[3]})_\n'

            winner['pokemons'][item]['other_param']['exp'] += expGen
            winner['pokemons'][item][paramGen[0]][paramGen[1]] += paramGen[2]

            del winner['pokemons'][item]['modifacators']
            del winner['pokemons'][item]['moveCount']

            if winner['id'] is list(updateMap.keys()):
                updateMap[winner['id']][winner['pokemons'][item]['innerID']] = {
                    'exp':expGen,
                    paramGen[0]:{paramGen[1]:paramGen[2]}
                    }
            else:
                updateMap[winner['id']] = {
                    winner['pokemons'][item]['innerID'] : {
                        'exp':expGen,
                        paramGen[0]:{paramGen[1]:paramGen[2]}
                        }
                    }

        for item in looser['pokemons']:
            if looser['pokemons'][item] is None: continue

            expGen = random.randint(1, 15)

            pokeExpUp += f'**Lose:** _-> {looser['pokemons'][item]['name']} (+{expGen}exp)_\n'

            looser['pokemons'][item]['other_param']['exp'] += expGen

            del looser['pokemons'][item]['modifacators']
            del looser['pokemons'][item]['moveCount']

            if looser['id'] is list(updateMap.keys()):
                updateMap[looser['id']][looser['pokemons'][item]['innerID']] = {
                    'exp':expGen
                    }
            else:
                updateMap[looser['id']] = {
                    looser['pokemons'][item]['innerID'] : {
                        'exp':expGen
                        }
                    }

        pokeDie = ''
        deleteMap = {}
        for item in self.Dbox[0]:
            if item is None: continue
            pokeDie += f'**DEAD:** _-> {item['name']}_\n'
            
            deleteMap 

            if item['owner'] is list(deleteMap.keys()):
                deleteMap[item['owner']].append([item['inner']])
            else:
                deleteMap[item['owner']] = []


        looseText = f'```Итоги боя```\n## Победитель: [{winner['name']}]\nПолучено: +2 репутации (-2 у проигравшего)\n\n**`<<< Покемоны получившие опыт >>>`**\n{pokeExpUp}\n**`<<< Потерянные покемоны >>>`**\n{pokeDie}'

        embed = disnake.Embed(description=looseText, colour=disnake.Color.dark_green())
        await message.edit(embed=embed, components=None)

        await setFightStatus(self.p1['id'], status=False) #? Для первого игрока
        await setFightStatus(self.p2['id'], status=False) #? Для второго игрока

        self.EndBattle = True
        if self.p2['bot']: await self.savePokemonsPVE(updateMap, deleteMap)
        else: await self.savePokemonsPVP(updateMap, deleteMap)

    
    # Обновление страницы информации, конечная точка расчетов
    async def updatePage(self, message, embed):
        self.step += 1

        self.log.append(self.temporalLogs)
        self.temporalLogs = ''

        countNones = 0
        for item in self.p1['pokemons']:
            if self.p1['pokemons'][item] is None: countNones += 1
        else:
            if countNones == 3:
                self.p1['looseBool'] = True
                await self.battleEnd(message, self.p2, self.p1)
                return

        enemyCountNones = 0
        for item in self.p2['pokemons']:
            if self.p2['pokemons'][item] is None: enemyCountNones += 1
        else:
            if enemyCountNones == 3:
                self.p2['looseBool'] = True
                await self.battleEnd(message, self.p1, self.p2)
                return


        await message.edit(embed=embed)

    # Основная функция пересчета действий, позиций и урона
    async def nextStep(self, message):
        # Первостепенно используются все действия и предметы на на защиту и увороты
        # Дальше применяются навыки поддержки и модификаций
        # В конце вычисляется атака атакующих
        # Защита → поддержка → атака
        floppySlots = ['slot0', 'slot1', 'slot2']

        plyersBox = [self.p1, self.p2]

        firstPunch = choice(plyersBox)
        plyersBox.remove(firstPunch)
        secondPunch = plyersBox[0]

        self.temporalLogs += f'**`|[ {firstPunch['name']} ]|`**\n'
        for index, item in enumerate(firstPunch['pokemons']):
            if firstPunch['move'][item] is None:
                command = 'atk'
                target = item
            else:
                command, target = str(firstPunch['move'][item]).split('-')

            if firstPunch['pokemons'][item] is None: continue

            fs = copy.copy(floppySlots)
            if secondPunch['pokemons'][target] is None: 
                for slots in fs:
                    if secondPunch['pokemons'][slots] is not None: 
                        target = slots
                        break
                else: continue


            if str(firstPunch['move'][item]).startswith('atk') or firstPunch['move'][item] is None:
                if str(secondPunch['move'][item]).startswith('deff') and firstPunch['move'][item] is None:
                    await listMoves['deff'](self, firstPunch['pokemons'][item], secondPunch['pokemons'][target], firstPunch)
                
                elif str(secondPunch['move'][item]).startswith('deff') and firstPunch['move'][item] is not None:
                    await listMoves['deff'](self, firstPunch['pokemons'][item], secondPunch['pokemons'][target], firstPunch)

                else:
                    await listMoves['atk'](self, firstPunch['pokemons'][item], secondPunch['pokemons'][target], firstPunch)
                
                if secondPunch['pokemons'][target]['other_param']['healpoint_now'] <= 0:
                    self.Dbox[0].append(secondPunch['pokemons'][target])
                    self.temporalLogs += f'`<<Покемон [{secondPunch['pokemons'][target]['name']}] был убит>>`\n'
                    secondPunch['pokemons'][target] = None

            elif str(firstPunch['move'][item]).startswith(('deff', 'env')):
                continue

            elif str(firstPunch['move'][item]).startswith('sheal'):
                await listMoves['sheal'](self, firstPunch)
        
        self.temporalLogs += f'\n**`|[ {secondPunch['name']} ]|`**\n'
        for index, item in enumerate(secondPunch['pokemons']):
            if secondPunch['move'][item] is None:
                command = 'atk'
                target = item
            else:
                command, target = str(secondPunch['move'][item]).split('-')
            
            if secondPunch['pokemons'][item] is None: continue

            fs = copy.copy(floppySlots)
            if firstPunch['pokemons'][target] is None: 
                for slots in fs:
                    if firstPunch['pokemons'][slots] is not None: 
                        target = slots
                        break
                else: continue

            if str(secondPunch['move'][item]).startswith('atk') or secondPunch['move'][item] is None:
                if str(firstPunch['move'][item]).startswith('deff') and secondPunch['move'][item] is None:
                    await listMoves['deff'](self, secondPunch['pokemons'][item], firstPunch['pokemons'][target], secondPunch)
                
                elif str(firstPunch['move'][item]).startswith('deff') and secondPunch['move'][item] is not None:
                    await listMoves['deff'](self, secondPunch['pokemons'][item], firstPunch['pokemons'][target], secondPunch)

                else:
                    await listMoves['atk'](self, secondPunch['pokemons'][item], firstPunch['pokemons'][target], secondPunch)

                if firstPunch['pokemons'][target]['other_param']['healpoint_now'] <= 0:
                    self.Dbox[0].append(secondPunch['pokemons'][target])
                    self.temporalLogs += f'`<<Покемон [{firstPunch['pokemons'][target]['name']}] был убит>>`\n'
                    firstPunch['pokemons'][target] = None

            elif str(secondPunch['move'][item]).startswith(('deff', 'env')):
                continue

            elif str(secondPunch['move'][item]).startswith('sheal'):
                await listMoves['sheal'](self, secondPunch)



        embed = updateMainText(self)
        await self.updatePage(message=message, embed=embed)


    async def attack(self, attacked, target, who):
        atk = round(attacked['params']['attack'] * (1 - (target['params']['armor'])))
        envBOOL = 1 <= random.random() <= (1 -target['params']['evasion'])

        if envBOOL:
            self.temporalLogs += f'**[{target['name']}] увернулся от атаки [{attacked['name']}]**\n'
        else:
            target['other_param']['healpoint_now'] -= atk
            self.temporalLogs += f'**[{attacked['name']}] нанес {atk} урона [{target['name']}]**\n'

        if target['other_param']['healpoint_now'] <= 0: target['other_param']['healpoint_now'] = 0

    async def deffence(self, attacked, target, who):
        
        atk = round(attacked['params']['attack'] * (1 - (target['params']['armor'] + 0.2)))
        diapATK = random.randint(round(atk*0.8), round(atk*1.2))

        atkToDown = round(attacked['params']['attack'] * (1 - (target['params']['armor'])))
        envBOOL = 1 <= random.random() <= (1 -target['params']['evasion'])

        if envBOOL:
            self.temporalLogs += f'**[{target['name']}] увернулся от атаки [{attacked['name']}]**\n'
        else:
            target['other_param']['healpoint_now'] -= diapATK
            self.temporalLogs += f'**[{attacked['name']}] нанес {diapATK} урона [{target['name']}], намеренная защита снизила урон на ({atkToDown - diapATK})**\n'
    
        if target['other_param']['healpoint_now'] <= 0: target['other_param']['healpoint_now'] = 0

    async def selfHeal(self, target):
        target['other_param']['healpoint_now'] += target['params']['regen']
        self.temporalLogs += f'_[{target}] вылечил себя на {target['params']['regen']}hp_'


    async def usePerk(toWhom, perk_slot, whoUse):
        ''' 
        toWhom= На кого применется (при all, на всех)\n
        perk_slot= ссылка на навык\n
        whoUse= Кто использует, принимает только p1/p2 в инном случае ошибка
        '''
        pass
    
    async def DefenceModifacator(toWhom, whoUse, whatUse):
        pass
    async def EvasionModifacator(toWhom, whoUse, whatUse):
        pass
    async def AttackModifacator(toWhom, whoUse, whatUse):
        pass
    async def HPModifacator(toWhom, whoUse, whatUse):
        pass
    async def SpeedModifacator(toWhom, whoUse, whatUse):
        pass



def setup(bot:commands.Bot):
    bot.add_cog(FightLoop(bot))
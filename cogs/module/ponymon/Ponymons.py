import disnake
from disnake.ext import commands

import asyncio
import json
import yaml
import time
import copy
import sqlite3
import random

from ..REQ_database import DataBase
from random import choices, choice, randrange
from .FightLoop import install

from ..RPG.System import userData

db = DataBase

async def checkHavePoke(user, ids, seq=None) -> bool:
    userBag = await giveUserBag(user)
    userWork, _ = await getWorkPokemon(user, False)
    userFighPet = await takeFightGroup(user)


    if ids not in userBag:
        for item in userFighPet:
            if str(userFighPet[item]).startswith(ids): 
                await saveFightGroup(None, user, item[-1])
        return True
    if seq not in userBag[ids]:
        for item in userFighPet:
            if str(userFighPet[item]).endswith(ids): 
                userFighPet[item] = None
                await saveFightGroup(None, user, item[-1])
        return True
    return False

async def setFightStatus(uid, status:bool):
    con = sqlite3.connect('../PonyashkaDiscord/_rpg.db')
    cur = con.cursor()
    cur.execute(f'UPDATE user_poke SET INFIGHT = {status} WHERE UID = {uid}')
    con.commit()

async def checkInFightStatus(uid):
    con = sqlite3.connect('../PonyashkaDiscord/_rpg.db')
    cur = con.cursor()

    cur.execute(f'SELECT INFIGHT FROM user_poke WHERE UID = {uid}')
    return bool(int(cur.fetchone()[0]))

async def closeEmbedMessageAfter_Interaction(message, responce, time:int):
    await asyncio.sleep(time)
    embed = disnake.Embed(description='```Окно закрыто системой.```')
    await responce.edit_message(message_id=message.id, components=None, embed=embed)
    return True
async def closeEmbedMessageAfter(message, time:int):
    await asyncio.sleep(time)
    embed = disnake.Embed(description='```Окно закрыто системой.```')
    await message.edit(components=None, embed=embed)
    return True

def associateOrderRank(rank, reverse:bool=False) -> int|str:
    order = {"?":-1,"EX":0, "S":1, "A":2, "B":3, "C":4, "D":5, "E":6, "F":7}
    orderReverse = {-1:"?", 0:"EX", 1:"S", 2:"A", 3:"B", 4:"C", 5:"D", 6:"E", 7:"F"}

    if reverse: return orderReverse[rank]
    return order[rank]

#? Main function a interaction with lotery system
async def checkButtonsLotery(countRoll) -> list:
    ''' This function return disnake.ui.Button(label='5|10')'''
    buttons = []

    if countRoll != 0: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='1', custom_id='lotery_1'))
    else: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='1', custom_id='lotery_1', disabled=True))

    if countRoll >= 5: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='5',custom_id='lotery_5'))
    else:buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='5',custom_id='lotery_5', disabled=True))

    if countRoll >= 10: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='10', custom_id='lotery_10'))
    else: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='10', custom_id='lotery_10', disabled=True))

    if countRoll >= 50: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='50', custom_id='lotery_50'))
    else: buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label='50', custom_id='lotery_50', disabled=True))

    return buttons
async def rareColor(Rank) -> disnake.Colour:
    if Rank == 'EX': return disnake.Colour.teal()
    if Rank == 'S': return disnake.Colour.red()
    if Rank == 'A': return disnake.Colour.yellow()
    if Rank == 'B': return disnake.Colour.dark_purple()
    if Rank == 'C': return disnake.Colour.blue()
    if Rank == 'D': return disnake.Colour.green()
    if Rank == 'E': return disnake.Colour.default()
    if Rank == 'F': return disnake.Colour.dark_gray()
async def RollLotery(user, freeRoll: int = 0, priceTiket=100, count:int = 1, sys:bool=False) -> map:
    if not 1 <= count <= 100: raise Exception('range count can be 1 <= count <= 100')

    if not sys:
        
        if int(freeRoll) >= int(count):
            db.Poke(user).sub(value=count, column='TIKET')

        elif int(freeRoll) == 0:
            value = count*priceTiket
            db.Money(user=user, value=value).sub()

        else:
            value = (count - freeRoll) * priceTiket
            db.Poke(user).sub(value=freeRoll, column='TIKET')
            db.Money(user=user, value=value).sub()


    with open('../PonyashkaDiscord/content/lotery/lowLotery.json', encoding='UTF-8') as file:
            load = json.load(file)
            box = load['items']
            compliments = load['compliments']
            del load

    async def getLoot(box, userBag):
        '''           ?↓   Ex↓     S↓    A↓     B↓     C↓    D↓    E↓     F↓'''
        lootChance = [0, 0.0001, 0.001, 0.005, 0.035, 0.07, 0.12, 0.199, 0.65]
        order = ["?", "EX", "S", "A", "B", "C", "D", "E", "F"]

        # Определение ранга, что выигрвывает
        rankWin = choices(order, weights=lootChance)
        rareColorRank = await rareColor(rankWin)

        # создания списка одного выиграного ранга
        associateBox = []
        for item in box:
            if box[item]['rank'] == rankWin[0]: associateBox.append(item)

        # Выборка победителя (ID)
        ids = choice(associateBox)
        
        try:
            if len(userBag[f'{ids}'])+1 > 20: selled = True
            else: selled = False

        except KeyError as error:
            selled = False

        loot = (ids, box[ids], rareColorRank, selled, box[ids]['rank'])

        del associateBox, box, ids, rankWin, rareColorRank, selled

        if not sys: DataBase.Poke(user=user).add(value=1, column='COUNTROLL')
        return loot

    listTrait = ['duplicator', 'chronojump', 'goldrained', 'deadlyluck', 'berserk', 'greenhouse', 'shield', 'armored_permove', 'mole', 'lucky', 'perk_slot']
    listProperty = ['attack', 'healpoint', 'armor', 'speed', 'evasion', 'regen']
    listCurrency = ['price', 'income']



    if count != 1:
        #? Множественный ролл

        lootEnd = []
        sellIncome = 0

        for _ in range(count):
            
            userBag = await giveUserBag(user=user)

            getPokes = await getLoot(box=box, userBag=userBag)
            loot = copy.deepcopy(getPokes[1])

            loot['price'] = randrange(loot['price'][0], loot['price'][1], 10)
            loot['income'] = randrange(loot['income'][0], loot['income'][1], 5)
            loot['countMemorySoul'] = 0

            for item in listTrait:
                if loot['trait'][item] is None: del loot['trait'][item]
            for item in listProperty:

                if item in ['armor', 'evasion']:
                    diapozone = loot['params'][item]
                    try: loot['params'][item] = randrange(round(diapozone[0]*100), round(diapozone[1]*100), 1)/100
                    except: loot['params'][item] = 0

                if item == 'speed':
                    diapozone = loot['params'][item]
                    loot['params'][item] = choice(diapozone)

                if item in ['attack', 'healpoint', 'regen']:
                    diapozone = loot['params'][item]
                    loot['params'][item] = randrange(diapozone[0], diapozone[1], 5)

            # Либо продажа, либо сохранение в инвертарь
            if getPokes[3]:
                timesSellIncome = round(loot['price'] * 0.75)
                sellIncome += timesSellIncome

                db.Money(user=user, value=timesSellIncome).add()

            else:
                savePokemon(loot=[(getPokes[0], loot, getPokes[2], getPokes[3], getPokes[4])], uid=user)
            lootEnd.append((getPokes[0], loot, getPokes[2], getPokes[3]))
            del loot


    else:
        userBag = await giveUserBag(user=user)

        getPokes = await getLoot(box=box, userBag=userBag)
        loot = copy.deepcopy(getPokes[1])

        sellIncome = 0

        loot['price'] = randrange(loot['price'][0], loot['price'][1], 10)
        loot['income'] = randrange(loot['income'][0], loot['income'][1], 5)
        loot['countMemorySoul'] = 0

        for item in listTrait:
            if loot['trait'][item] is None: del loot['trait'][item]

        for item in listProperty:

            if item in ['armor', 'evasion']:
                diapozone = loot['params'][item]
                try: loot['params'][item] = randrange(round(diapozone[0]*100), round(diapozone[1]*100), 1)/100
                except: loot['params'][item] = 0

            if item == 'speed':
                diapozone = loot['params'][item]
                loot['params'][item] = choice(diapozone)

            if item in ['attack', 'healpoint', 'regen']:
                diapozone = loot['params'][item]
                loot['params'][item] = randrange(diapozone[0], diapozone[1], 5)
        
        if getPokes[3]:
                timesSellIncome = round(loot['price'] * 0.75)
                sellIncome += timesSellIncome

                db.Money(user=user, value=timesSellIncome).add()

        else:
            savePokemon(loot=[(getPokes[0], loot, getPokes[2], getPokes[3], getPokes[4])], uid=user)

        lootEnd = [(getPokes[0], loot, getPokes[2], getPokes[3])]
    
    
    if count == 1:
        compliment = choice(compliments[f'{lootEnd[0][1]['rank']}'])
    else:
        compliment = choice(compliments['mass'])
    
    priceTiket = await GetTiketPrice(user)
    freeRoll = db.Poke(user).takeAll()[4]
    user = await userData(uid=user)
    essence = user['money']['ESSENCE']

    countToRoll = freeRoll + (essence // priceTiket)

    buttons = await checkButtonsLotery(countRoll=countToRoll)
    return {"loot":lootEnd, "compliment":compliment, "buttons":buttons, "sellIncome":sellIncome}
def savePokemon(loot, uid:int) -> None:
    '''Save without trade, for trade use other command «saveAfterTradePoke()»'''
    try:
        with open(f'../PonyashkaDiscord/content/lotery/users_bag/{uid}.json', 'r', encoding='UTF-8') as file:
            progress = json.load(file)
    except:
        progress = {}


    for item in loot:
        ids = item[0]

        # order = {"?":-1,"EX":0, "S":1, "A":2, "B":3, "C":4, "D":5, "E":6, "F":7}

        #rebuild slot perks pokemon
        rg = item[1]['trait']['perk_slot']
        item[1]['trait']['perk_slot'] = {}
        for i in range(rg):
            item[1]['trait']['perk_slot'][f'slot{i+1}'] = None
        poke = {
            "name":item[1]['name'],
            "rank":item[4],
            "trait":item[1]['trait'],
            "params":item[1]['params'],
            "other_param":{
                "lvl":0,
                "exp":0,
                "essence_drop":0,
                "timestamp_hp":0,
                "healpoint_now":item[1]['params']['healpoint'],
                
                "supports":0,
                "supports_percent_up":0,
                "countMemorySoul":item[1]['countMemorySoul']
                },
            "curr":{
                "price":item[1]['price'],
                "income":item[1]['income'],
                "power":1.0
                },
            "owner":uid,
            "holder":[uid],
            "innerID":None
            }
        try:
            count = 1
            while True: 
                if str(count) in progress[ids]:
                    count += 1
                    continue
                poke['innerID'] = f'{item[0]}-{count}'
                progress[ids][count] = poke
                break
        except:
            poke['innerID'] = f'{item[0]}-1'
            progress[ids] = {
                "1":poke
                }
            
        with open(f'../PonyashkaDiscord/content/lotery/users_bag/{uid}.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(progress, indent=2, ensure_ascii=False))


async def userHaveTicket(user) -> int:
    return db.Poke(user=user).takeAll()[4]

#? Work pokemon
async def checkValideWorkedFile(user:int):
    try:
        with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'r', encoding='UTF-8') as file: load = json.load(file)
        return load
    except:
        with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'w', encoding='UTF-8') as file: 
            slots = {"SLOT1":None, "SLOT2":None, "SLOT3":None}
            file.write(json.dumps(slots, indent=2, ensure_ascii=False))
        with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'r', encoding='UTF-8') as file: load = json.load(file)
        return load

async def checkHavePokemon_WorkFile(rankCOM_poke:str, user):
    '''Give only rankCOM (rank-order-num)'''
    workfile, cashincome = await getWorkPokemon(user=user, sys=False)

    ids, seq = rankCOM_poke.split('-')
    poke = await findMap_PokemonInDB_LikeID(ID=ids)
    
    for item in workfile:
        if workfile[item] is None: continue
        if str(poke['name'].lower()) == str(workfile[item]['name'].lower()): 
            return True, item
    return False, None
async def checkHavePokemon_UserBag(rankCOM_poke:str, user):
    '''Give only rankCOM (rank-order-num)'''
    userBag = await giveUserBag(user=user)
    rank, orde, num = rankCOM_poke.split('-')

    try:
        check = userBag[rank][orde][num]
        return True
    except:
        return False

async def giveUserBag(user) -> map:
    try:
        with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'r', encoding='UTF-8') as file:
            userBag = json.load(file)
    except:
        with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'w', encoding='UTF-8') as file:
            data = {}
            file.write(json.dumps(data, indent=2, ensure_ascii=False))
        with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'r', encoding='UTF-8') as file:
            userBag = json.load(file)
    return userBag

async def checkingPokemonAvialbility(name_or_id:str|int):
    pass

async def findID_PokemonInDB_LikeName(PokemonName:str) -> str:
    # ID == ID 
    with open('../PonyashkaDiscord/content/lotery/lowLotery.json', encoding='UTF-8') as file:
        load = json.load(file)
        pokemons = load['items']
        del load
    
    for item in pokemons:
        if PokemonName.lower() == pokemons[item]['name'].lower(): return item
    return None   
async def findMap_PokemonInUserBag_LikeName(pokemonName:str, user) -> bool:
    # ID == ID 
    '''Give a name or ID pokemon'''
    with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'r', encoding='UTF-8') as file:
        userBag = json.load(file)

    for item in userBag:
        randomSelect = userBag[item][choice(list(userBag[item].keys()))]
        if pokemonName.lower() == randomSelect['name'].lower(): return True

    return False
async def findMap_PokemonInDB_LikeID(ID:str) -> map:
    # ID 
    with open('../PonyashkaDiscord/content/lotery/lowLotery.json', encoding='UTF-8') as file:
        load = json.load(file)
        pokemons = load['items']
        del load
    return pokemons[ID]
async def findMap_PokemonInDB_LikeName(name) -> map | bool:
    with open('../PonyashkaDiscord/content/lotery/lowLotery.json', 'r', encoding='UTF-8') as file:
        load = json.load(file)
        pokemons = load['items']
        del load
    
    for ids in pokemons:
        if pokemons[ids]['name'].lower() == name.lower(): return pokemons[ids], ids
    return False

async def findPokemonInUserBag_LikeName(name) -> tuple:
    pass
async def findPokemonInUserBag_LikeID(name) -> tuple:
    pass

#! Разные сейвы файлов
def saveDelicateUserBag(poke, user):
    with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'r', encoding='UTF-8') as file: 
        userBag = json.load(file)

    ids, seq = poke['innerID'].split('-')
    userBag[ids][seq] = poke

    with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'w', encoding='UTF-8') as file: 
        file.write(json.dumps(userBag, indent=3, ensure_ascii=False))

    return True
async def saveWorkFile(workfile, user):
    with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'w', encoding='UTF-8') as file: 
        file.write(json.dumps(workfile, indent=3, ensure_ascii=False))
    return True
async def saveBagUserFile(userFile, user) -> bool:
    try:
        with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(userFile, indent=3, ensure_ascii=False))
        return True
    except: return False
async def saveFightGroup(rankCOM, user:int, slot:int):
    '''Slot take a 1|2|3 and nothing else. Pony sure.'''
    fightPet = await takeFightGroup(user=user)
    fightPet[f'slot{slot}'] = rankCOM
    with open(f'../PonyashkaDiscord/content/lotery/fightPet/{user}.json', 'w', encoding='UTF-8') as file:
        file.write(json.dumps(fightPet))

async def setWorkPokemon(rankCOM:str, user, slot:1|2|3) -> bool:

    ids, seq = rankCOM.split('-')

    workFile = await checkValideWorkedFile(user=user)
    checkHave, workFilePokes = await checkHavePokemon_WorkFile(rankCOM_poke=rankCOM, user=user)
    userPoke = await giveUserBag(user=user)

    poke = userPoke[ids][seq]

    if checkHave:
        if not workFilePokes.endswith(str(slot)): return False
        if workFile[workFilePokes]['cashIncome'] > poke['curr']['income']: return False

    workFile[f'SLOT{slot}'] = {
            "name":poke['name'],
            "time":round(time.time()),
            "cashIncome":poke['curr']['income']
        }
    await saveWorkFile(workFile, user)
    return True    

async def getWorkPokemon(user, sys:bool) -> tuple:
    workerPokemon = await checkValideWorkedFile(user=user)
    cashIncome = await calculateValueWorkPokemon(user=user, sys=sys)
    return workerPokemon, cashIncome
async def calculateValueWorkPokemon(user, sys=False):
    workFile = await checkValideWorkedFile(user)
    slotsItem = ['SLOT1', 'SLOT2', 'SLOT3']
    incomeList = {}
    timeNow = round(time.time())
    timeSleep = 0
    for item in slotsItem:
        try:
            timeSleep = (timeNow-workFile[item]['time'])//3600
            if timeSleep > 10: timeSleep = 10
            incomeList[item] = {
                "name":workFile[item]['name'],
                "pastTense":timeSleep,
                "income":timeSleep*workFile[item]['cashIncome']}
            if sys and timeSleep > 0: 
                await stampTimePokemon(user=user, slot=item[4])
        except:
            incomeList[item] = None
    slots = {
        "SLOT1":incomeList['SLOT1'],
        "SLOT2":incomeList['SLOT2'],
        "SLOT3":incomeList['SLOT3']
        }
    
    del workFile, slotsItem, incomeList, timeNow
    return slots
async def stampTimePokemon(user, slot:1|2|3):
    workfile = await checkValideWorkedFile(user=user)
    workfile[f'SLOT{slot}']['time'] = round(time.time())
    await saveWorkFile(workfile=workfile, user=user)
async def checkStrikeWork(strike) -> float:
    if 80 > strike: return 1.0
    if 170 > strike: return 2.5
    if 320 > strike: return 5.0
    if 490 > strike: return 7.5
    if 710 > strike: return 10.0
    return 15.0

#? Function what they allow sell or buy on time market pokemon
async def sellPokemon(pokemon:list, user) -> bool:
    with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'r', encoding='UTF-8') as file:
        userBag = json.load(file)
    with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'r', encoding='UTF-8') as file:
        userWorPoke = json.load(file)

    pokeCountList = []
    listCorrectSells = []
    async def sell(pokemon):
        checkHavePoke = await findPokemonInUserBag_LikeName(pokemon['name'], user=user)

        if checkHavePoke:
            pokemonCount = userBag[pokemon['name']]['count']
            del userBag[pokemon['name']]

            for item in userWorPoke:
                try:
                    if userWorPoke[item]['name'] == pokemon['name']:
                        userWorPoke[item] = None
                except: pass

            await saveBagUserFile(userFile=userBag, user=user)
            await saveWorkFile(workfile=userWorPoke, user=user)
            sellIncome = round(pokemon['price'] * 0.75) * pokemonCount
            if db.Money(user=user, value=sellIncome).add(): 
                listCorrectSells.append(True)
                return pokeCountList.append(pokemonCount)
        else: 
            listCorrectSells.append(False)
            return pokeCountList.append(None)
    
    # try:
    for item in pokemon:
        await sell(item)
    return (listCorrectSells, pokeCountList)
    # except: 
    #     print('exit 2')
    #     return (False, None)

async def getLenUserBag(userBag) -> int:
    count = 0
    for ranks in userBag:
        for numbers in userBag[ranks]:
            if numbers == 'weight': continue
            count += len(userBag[ranks][numbers])
    return count
async def GetTiketPrice(user) -> int:
    userLVL = db.Info(user_id=user).takeFromRPG(table='user_main_info')[1]
    userCountRoll = db.Info(user_id=user).takeFromRPG(table='user_poke')[3]
    userBag = await giveUserBag(user=user)

    if userLVL <= 0: userLVL = 0

    lenBag = await getLenUserBag(userBag=userBag)
    return 10000 + (100 * (userLVL//2)) + (100 * (userCountRoll//100)) + (100 * (lenBag//10))

async def takeFightGroup(user:int):
    try:
        with open(f'../PonyashkaDiscord/content/lotery/fightPet/{user}.json', 'r', encoding='UTF-8') as file:
            fightPet = json.load(file)
        return fightPet
    except:
        fightPet = {
            'slot1':None,
            'slot2':None,
            'slot3':None
            }
        with open(f'../PonyashkaDiscord/content/lotery/fightPet/{user}.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(fightPet))
        return fightPet

async def setDescriptionTextWorkGroup(user):
    workPoke, cashIncome = await getWorkPokemon(user=user, sys=False)
    text = ''
    for index, item in enumerate(workPoke):
        if not workPoke[item]:
            text += f'** `{index+1}`: `Пустой слот`**\n| —\n'
            continue
        income = cashIncome[item]
        text += f' **`{index+1}`**: **`{income['name']}`** **`({workPoke[item]['cashIncome']:,}/h)`**\n| Собрано: `({income['income']})`\n| С последнего сбора: `({time.strftime('%H:%M:%S', time.gmtime(round(time.time())-workPoke[item]['time']))})`\n'
    else:
        text += f'-# _Для сбора используйте команду !work._'
    return text
async def setButtonsWorkGroup(message, rare, user):
    buttons = [
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='1', custom_id=f'selectWorkSlot-1|{rare}|{user}'),
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='2', custom_id=f'selectWorkSlot-2|{rare}|{user}'),
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='3', custom_id=f'selectWorkSlot-3|{rare}|{user}')
            ]
    await message.edit(components=buttons)
async def setButtonsFightGroup(message, data:tuple):
    buttons = [
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='1', custom_id=f'selectFightSlot-1|{data[0]}|{data[1]}'),
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='2', custom_id=f'selectFightSlot-2|{data[0]}|{data[1]}'),
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='3', custom_id=f'selectFightSlot-3|{data[0]}|{data[1]}')
            ]
    await message.edit(components=buttons)

def DelicateInjectWorkFile(user, pokemon):
            with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'r', encoding='UTF-8') as file:
                userWorkPoke = json.load(file)
            for item in userWorkPoke:
                try:
                    if userWorkPoke[item]['name'] == pokemon['name'] and userWorkPoke[item]['cashIncome'] == pokemon['curr']['income']:
                        userWorkPoke[item] = None
                except: pass
async def endSellPokeAfterSelect(pokemon_ids:str, user, message):

    userBag = await giveUserBag(user=user)
    ids, seq = pokemon_ids.split('-')

    pokemon = userBag[ids][seq]
    
    text = f'✔ **Понимон [{pokemon['name']}] был продан за `{round(pokemon['curr']['price']*0.75)}`es** \n'

    embed = disnake.Embed(
            description=text
            ).set_footer(text='Понимон продаётся за 75% от стоимости')
    
    import copy 
    price = copy.copy(userBag[ids][seq]['curr']['price'])
    del userBag[ids][seq]
    if len(userBag[ids]) == 0: del userBag[ids]

    db.Money(user=user, value=round(price*0.75)).add()
    del price

    DelicateInjectWorkFile(user=user, pokemon=pokemon)
    await saveBagUserFile(userBag, user)
    await message.edit(embed=embed)
async def endRemPokeAfterSelect(pokemon_ids:str, user, message):

    userBag = await giveUserBag(user=user)
    ids, seq = pokemon_ids.split('-')

    pokemon = userBag[ids][seq]

    value = pokemon['other_param']['essence_drop']
    valueChanceDrop = (1 + value*1.4)/(1_000_000 + value*0.8 + random.randint(round(value*0.7), round(value*1.3)))
    rem = random.random() < valueChanceDrop
    
    text = f'✔ **Понимон [{pokemon['name']}] был переплавлен, {'оказалось зря.' if rem else f'в `1` штуку духовной памяти '}** \n'

    embed = disnake.Embed(
            description=text
            ).set_footer(text=f'{'Даже рынок рабов, нет так ужасен!' if random.random() < 0.05 else ''}')

    if rem: db.Poke(user=user).add(value=1, column='POKE_ESSENCE')
    
    del userBag[ids][seq]
    if len(userBag[ids]) == 0: del userBag[ids]

    DelicateInjectWorkFile(user=user, pokemon=pokemon)
    await saveBagUserFile(userBag, user)
    await message.edit(embed=embed)

def hardSaveBag(user, file):
    with open(f'../PonyashkaDiscord/content/lotery/users_bag/{user}.json', 'w', encoding='UTF-8') as f:
        f.write(json.dumps(file, indent=3, ensure_ascii=False))
async def confirmActions(user1, user2, rankCOM, message):
    userBag1 = await giveUserBag(user1)
    userBag2 = await giveUserBag(user2)

    ids, seq = rankCOM.split('-')
    if ids in list(userBag2.keys()):
        if list(userBag2[ids].keys()) == 20: return await message.edit(embed=disnake.Embed(description=f'**Похоже у данного пользователя нет места для данного типа понимонов.**'))

        num = 1
        keysList = list(userBag2[ids].keys())
        while True:
            if str(num) not in keysList: 
                break
            num += 1
        
        pokesEntrade = copy.deepcopy(userBag1[ids][seq])
        del userBag1[ids][seq]
        if len(userBag1[ids]) == 0: del userBag1[ids]

        pokesEntrade['owner'] = int(user2)
        pokesEntrade['holder'].append(int(user2))
        pokesEntrade['innerID'] = str(f'{ids}-{num}')

        userBag2[ids][num] = pokesEntrade

        hardSaveBag(user=user1, file=userBag1)
        hardSaveBag(user=user2, file=userBag2)

        embed= disnake.Embed(description=f'**Вы передали пользователю <@{user2}> понимона.**')
        await message.edit(embed=embed)
    else:
        pokesEntrade = copy.deepcopy(userBag1[ids][seq])

        pokesEntrade['owner'] = int(user2)
        pokesEntrade['holder'].append(int(user2))
        pokesEntrade['innerID'] = str(f'{ids}-1')
        
        del userBag1[ids][seq]
        if len(userBag1[ids]) == 0: del userBag1[ids]

        userBag2[f'{ids}'] = {
                '1':pokesEntrade
            }

        hardSaveBag(user=user1, file=userBag1)
        hardSaveBag(user=user2, file=userBag2)

        embed= disnake.Embed(description=f'**Вы передали пользователю <@{user2}> понимона.**')
        await message.edit(embed=embed)

# Just locale params and stats
async def AllockatePokemons(name:str) -> str:
    listTrait = {
        'duplicator':'Дубликатор', 'chronojump':'Хронопрыжок', 
        'goldrained':'Злато-дождь', 'deadlyluck':'Смертоудача', 
        'berserk':'Берсерк', 'greenhouse':'Тепличность', 
        'shield':'Щит', 'armored_permove':'Чешуя', 
        'mole':'Кротовик', 'lucky':'Удачливость', 
        'perk_slot':'Слотов навыков'}
    listProperty = {
        'attack':'🔪 Урон', 'healpoint':'💖 Здоровье', 
        'armor':'🛡 Броня', 'speed':'🍃 Скорость', 
        'evasion':'🦋 Уклонение', 'regen':'💞 Регенерация'}
    listCurr = {
        'price':'💵 Цена', 'income':'💹 Доход', 'power':'🔥 Усиление работы'
        }

    for item in listProperty:
        if name == item: return listProperty[item]
    for item in listTrait:
        if name == item: return listTrait[item]
    for item in listCurr:
        if name == item: return listCurr[item]
    return '`[Неизвестное]`'

def pokesToNextLvLExp(rank, lvl) -> int:
    if lvl >= 25: return False
    
    conRPG = sqlite3.connect('../PonyashkaDiscord/_rpg.db')
    curRPG = conRPG.cursor()

    curRPG.execute(f'SELECT {rank} FROM levels_pokes WHERE lvl={lvl+1}')
    return curRPG.fetchone()[0]
async def selectedCountElements(count, box, data) -> map:
    '''get a two-dimensional array, and return two-dimensional array what have a "count" elements'''

    ids, seq = data[1].split('-')
    user = data[0]

    userBag = await giveUserBag(user=user)
    poke = userBag[ids][seq]

    tempoMap = {}
    counts = 0
    while counts < count:
        select = choice(list(box.keys()))
        ended = choice(list(box[select].keys()))

        if ended == 'armor' or ended == 'evasion': 
            if poke[select][ended] >= 0.8: continue

        try:
            if ended in list(tempoMap[select].keys()): continue
            tempoMap[select][ended] = box[select][ended].to_component_dict()
        except: 
            tempoMap[select] = {
                    ended:box[select][ended].to_component_dict()
                }
        
        counts += 1
    return tempoMap


def rankedBoost(rank) -> list:
    rankedBoostMap = {
        'F':[1.2, 1.05],
        'E':[1.3, 1.05],
        'D':[1.4, 1.05],
        'C':[1.5, 1.05],
        'B':[1.6, 1.05],
        'A':[1.7, 1.05],
        'S':[2.0, 1.10]
        }
    return rankedBoostMap[rank]
def rrNeedSUP(rank:str) -> int:
    rrUpedMap = {
        'F':10,
        'E':12,
        'D':14,
        'C':16,
        'B':18,
        'A':20,
        'S':25,
        'EX':50,
        '?':10
        }
    return rrUpedMap[rank]
def rrUped(rank:str):
    rrUpedMap = {
        'F':'E',
        'E':'D',
        'D':'C',
        'C':'B',
        'B':'A',
        'A':'S',
        'S':'S'
        }
    if rank == 'EX': return 'EX'
    return rrUpedMap[rank] 
async def updateMessage(message, view):
    await message.edit(embed=disnake.Embed(description='### Какого понимона расчитаете как расходник?', colour=disnake.Color.dark_blue()), view=view)
def mapSup(supCount):
    if int(supCount) < 2: return 0.05
    return round(0.05 + ((int(supCount) // 2) * 0.05), 2)
async def EndSopportSelect(message, user, ids:list):

    userBag = await giveUserBag(user=user)

    uids, useq = ids[0].split('-')
    upPoke = userBag[uids][useq]
    mapedSuped = upPoke['other_param']['supports']
    upRank = True if int(mapedSuped)+1 == rrNeedSUP(upPoke['rank']) else False

    dids, dseq = ids[1].split('-')
    diePoke = userBag[dids][dseq]

    roll = choice(['params', 'curr'])
    mapRoll = {
        'params':{
            'attack':f'-> Атака [{upPoke['params']['attack']:.0f} -> {upPoke['params']['attack'] + round(diePoke['params']['attack'] * mapSup(str(mapedSuped))):.0f}]',
            'healpoint':f'-> Здоровье [{upPoke['params']['healpoint']:.0f} -> {upPoke['params']['healpoint'] + round(diePoke['params']['healpoint'] * mapSup(str(mapedSuped))):.0f}]',
            'armor':f'-> Броня [{upPoke['params']['armor']:.2f} -> {(upPoke['params']['armor'] + round(diePoke['params']['armor'] * mapSup(str(mapedSuped)), 2)):.2f}]',
            'evasion':f'-> Уклонение [{upPoke['params']['evasion']:.2f} -> {(upPoke['params']['evasion'] + round(diePoke['params']['evasion'] * mapSup(str(mapedSuped)), 2)):.2f}]',
            'regen':f'-> Регенерация [{upPoke['params']['regen']:.0f} -> {upPoke['params']['regen'] + round(diePoke['params']['regen'] * mapSup(str(mapedSuped))):.0f}]'
            },
        'curr':{
            'price':f'-> Цена [{upPoke['curr']['price']:.0f} -> {upPoke['curr']['price'] + round(diePoke['curr']['price'] * mapSup(str(mapedSuped))):.0f}]',
            'income':f'-> Доход [{upPoke['curr']['income']:.0f} -> {upPoke['curr']['income'] + round(diePoke['curr']['income'] * mapSup(str(mapedSuped))):.0f}]',
            'power':f'-> Усиление дохода [{upPoke['curr']['power']:.2f} -> {upPoke['curr']['power'] + round(diePoke['curr']['power'] * mapSup(str(mapedSuped)), 2):.2f}]'
            }
        }
    buttons = {
        'params':{
            'attack':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Атака', custom_id=f'SUPATK|{user}|{uids}-{useq}|{dids}-{dseq}'),
            'healpoint':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Здоровье', custom_id=f'SUPHP|{user}|{uids}-{useq}|{dids}-{dseq}'),
            'armor':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Броня', custom_id=f'SUPDEF|{user}|{uids}-{useq}|{dids}-{dseq}'),
            'evasion':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Уклонение', custom_id=f'SUPEVN|{user}|{uids}-{useq}|{dids}-{dseq}'),
            'regen':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Регенерация', custom_id=f'SUPREG|{user}|{uids}-{useq}|{dids}-{dseq}'),
            },
        'curr':{
            'price':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Цена', custom_id=f'SUPPR|{user}|{uids}-{useq}|{dids}-{dseq}'),
            'income':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Доход', custom_id=f'SUPINC|{user}|{uids}-{useq}|{dids}-{dseq}'),
            'power':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Усиление дохода', custom_id=f'SUPPINC|{user}|{uids}-{useq}|{dids}-{dseq}'),
            }
        }

    mapLocked = {}
    textRoll = ''
    for item in mapRoll[roll]:
        if diePoke[roll][item] == 1 and item == 'healpoint': 
            textRoll += f'~~{mapRoll[roll][item]}~~\n'
            mapLocked[item] = True
            continue
        if diePoke[roll][item] == 0 and item in ['attack', 'armor', 'evasion', 'regen', 'price', 'income', 'power']: 
            textRoll += f'~~{mapRoll[roll][item]}~~\n'
            mapLocked[item] = True
            continue

        if item == 'armor' and upPoke['params']['armor'] >= 0.8:
            textRoll += f'~~{mapRoll[roll][item]}~~\n'
            mapLocked[item] = True
            continue
        if item == 'evasion' and upPoke['params']['evasion'] >= 0.8:
            textRoll += f'~~{mapRoll[roll][item]}~~\n'
            mapLocked[item] = True
            continue

        mapLocked[item] = False
        textRoll += f'{mapRoll[roll][item]}\n'

    button = []
    offButtonCount = 0
    for item in buttons[roll]:
        if mapLocked[item]: 
            buttons[roll][item].disabled = True
            offButtonCount += 1
            button.append(buttons[roll][item])
            continue
        button.append(buttons[roll][item])

    if offButtonCount == len(button):
        while True:
            rollTwice = choice(['params', 'curr'])
            if roll != rollTwice: 
                roll = rollTwice
                break
        button = []

        mapLocked = {}
        textRoll = ''
        for item in mapRoll[rollTwice]:
            if diePoke[rollTwice][item] == 1 and item == 'healpoint': 
                textRoll += f'\n~~`{mapRoll[rollTwice][item]}`~~'
                mapLocked[item] = True
                continue
            if diePoke[rollTwice][item] == 0 and item in ['attack', 'armor', 'evasion', 'regen', 'price', 'income', 'power']: 
                textRoll += f'\n~~`{mapRoll[rollTwice][item]}`~~'
                mapLocked[item] = True
                continue
            mapLocked[item] = False
            textRoll += f'\n{mapRoll[rollTwice][item]}'

        button = []
        offButtonCount = 0
        for item in buttons[rollTwice]:
            if mapLocked[item]: 
                buttons[rollTwice][item].disabled = True
                offButtonCount += 1
                button.append(buttons[rollTwice][item])
                continue
            button.append(buttons[rollTwice][item])

        if offButtonCount == len(button):
            await message.edit(embed=disnake.Embed(description=f'**Похоже все соки из донора были выжаты: [{diePoke['name']}-{dseq}]\n\nПопробуйте другого.**', colour=disnake.Color.red()))
            return


    await message.edit(embed=disnake.Embed(description=f'## Кубик брошен...\n`Выбор предоставлен.` \n**Вы можете улучшить [{'параметр' if roll == 'params' else 'свойство'}] у [{upPoke['name']}]:**\n{textRoll}\n').set_footer(text=f'Модификатор количества поддержек: {mapSup(str(mapedSuped)):.0%}\n{f'Данное усиление продвинет ранг понимона до {rrUped(upPoke['rank'])}' if upRank else ''}'), components=button)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
def reduct(num) -> str:
    if num // 1_000_000_000 > 0:
        return f"{(num/1_000_000_000):.2f}T"
    if num // 1_000_000 > 0:
        return f"{(num/1_000_000):.2f}M"
    if num // 1_000 > 0:
        return f"{(num/1_000):.2f}K"
    return f"{num:.0f}"
def calculateCP(poke) -> int:
    # Форма БМ покемонов
    # (((hp+reg)*(%)def*(%)env) + (atk*2.5*0.2) + ((price*0.1+inc*0.5)*pUp)) * rank
    # ex-2, s-1.75, a-1.65, b-1.55, c-1.4, d-1.25, e-1.1, f-1
    # На потом: 
    # 1. Просчет дополнительной мощи от специальных свойств
    # 2. Просчет от количества боёв покемона

    rankBoost = {"EX":2, "S":1.75, "A":1.65, "B":1.55, "C":1.4, "D":1.25, "E":1.15, "F":1}

    # Блок с расчетом сторон жизнеспособности покемона
    param = poke['params']
    block1 = (param['healpoint'] + param['regen']) * (1 + param['armor']) * (1 + param['evasion']) 
    
    # Блок с расчетом атакующей способности покемона
    block2 = (param['attack'] * 2.5 * 0.2)
    
    # Блок с экономической мощности покемона
    curr = poke['curr']
    block3 = ((int(curr['price']) * 0.1) + (curr['income'] * 0.5)) * curr['power'] 
    
    # Финалиция вычислений БМ
    endCalc = (block1 + block2 + block3) * rankBoost[poke['rank']]

    return endCalc

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
def HPupdate(poke, user):
    '''Обновление состояния здоровья'''
    if poke['other_param']['healpoint_now'] == poke['params']['healpoint']: return poke
    if poke['other_param']['timestamp_hp'] == 0: 
        poke['other_param']['timestamp_hp'] = round(time.time())
        saveDelicateUserBag(poke, user)
        return poke

    hp = poke['other_param']['healpoint_now']
    regen = int(poke['params']['regen'] * poke['trait']['greenhouse'])
    times = round((time.time() - int(poke['other_param']['timestamp_hp'])) // 3600)

    hp += round(times * regen)
    if int(hp) > int(poke['params']['healpoint']): poke['other_param']['healpoint_now'] = poke['params']['healpoint']

    if times != 0: poke['other_param']['timestamp_hp'] = round(time.time())

    saveDelicateUserBag(poke, user)
    return poke
async def startFight(message, users, mulp):
    '''
        По факту тут происходит распоковка и обработка данных в удобоприемлеммый формат
    '''
    userID = mulp[0]
    opponentID = mulp[1]

    with open(f'../PonyashkaDiscord/content/lotery/fight/{users}.json', 'r', encoding='utf-8') as file:
        TemporalDatafightMap = json.load(file)
    
    # Подгрузка инвентарей для определния адресаций и подгрузки самих покемонов
    userBag = await giveUserBag(user=userID)
    if not TemporalDatafightMap['p2']['bot']: 
        opponentBag = await giveUserBag(user=opponentID)
    
    #? Подгрузка самих покемонов
    userPokes = {}
    opponentPokes = {}
    for index, item in enumerate(TemporalDatafightMap['p1']['pokemons']):
        try:
            ids, seq = TemporalDatafightMap['p1']['pokemons'][item].split('-')
            poke = HPupdate(userBag[ids][seq], userID)

            add = copy.deepcopy(poke)

            add['moveCount'] = 0
            add['modifacators'] = {}

            userPokes[f'slot{index}'] = add
        except:
            userPokes[f'slot{index}'] = None

    # Если второй игрок не бот
    if not TemporalDatafightMap['p2']['bot']:
        for index, item in enumerate(TemporalDatafightMap['p2']['pokemons']):
            try:
                ids, seq = TemporalDatafightMap['p2']['pokemons'][item].split('-')
                poke = HPupdate(opponentBag[ids][seq], opponentID)

                add = copy.deepcopy(poke)

                add['moveCount'] = 0
                add['modifacators'] = {}

                opponentPokes[f'slot{index}'] = add
            except:
                opponentPokes[f'slot{index}'] = None
    else:

        for index, item in enumerate(TemporalDatafightMap['p2']['pokemons']):
            try:
                poke = HPupdate(TemporalDatafightMap['p2']['pokemons'][item], TemporalDatafightMap['p1']['idp'])
                add = copy.deepcopy(poke)

                add['moveCount'] = 0
                add['modifacators'] = {}

                opponentPokes[f'slot{index}'] = add
            except:
                opponentPokes[f'slot{index}'] = None


    #? Подгрузка предметов игрока
    try:
        # Загрузка предметов P1
        with open(f'../PonyashkaDiscord/content/lotery/user_bag_items/{userID}.yaml', 'r', encoding='utf-8') as file:
            userItems = yaml.safe_load(file)
        temporalList = []
        for item in userItems:
            temporalList.append(userItems[item])
        userItemsList = list(chunks(temporalList, 20))
    except: userItemsList = None
    try:
        # Загрузка предметов P2
        with open(f'../PonyashkaDiscord/content/lotery/user_bag_items/{opponentID}.yaml', 'r', encoding='utf-8') as file:
            opponentItems = yaml.safe_load(file)
        temporalList = []
        for item in opponentItems:
            temporalList.append(opponentItems[item])
        opponentItemsList = list(chunks(temporalList, 20))
    except: opponentItemsList = None
    

    textP1 = ''
    for index, slot in enumerate(userPokes):
        item = userPokes[slot]
        if item is None: 
            textP1 += f'**{index+1} ]|[ None ]**\n'
            continue
        percentHp = item['other_param']['healpoint_now']/item['params']['healpoint']

        attack = f'{round(item['params']['attack']*0.8)}-{round(item['params']['attack']*1.2)}'
        hp = f'{item['other_param']['healpoint_now']}/{item['params']['healpoint']}'

        textP1 += f'**{index+1} ]|[ . ]|[ {item['name']} ]**\n`[ HP: {hp} ]|[ ATK: {attack} ]`\n{HPbar(percentHp)}\n'

    textP2 = ''
    for index, slot in enumerate(opponentPokes):
        item = opponentPokes[slot]
        if item is None: 
            textP2 += f'**{index+1} ]|[ None ]**\n'
            continue
        percentHp = item['other_param']['healpoint_now']/item['params']['healpoint']

        attack = f'{round(item['params']['attack']*0.8)}-{round(item['params']['attack']*1.2)}'
        hp = f'{item['other_param']['healpoint_now']}/{item['params']['healpoint']}'

        textP2 += f'**{index+1} ]|[ . ]|[ {item['name']} ]**\n`[ HP: {hp} ]|[ ATK: {attack} ]`\n{HPbar(percentHp)}\n'

    body = f'``` <-- Игрок P1: {TemporalDatafightMap['p1']['name']} --> ```\n{textP1}\n``` <-- Игрок P2: {TemporalDatafightMap['p2']['name']} --> ```\n{textP2}'

    if TemporalDatafightMap['p2']['bot']: title = "Бой против бота"
    else: title = "Бой между игроками"

    p1BOT = False
    p2BOT = bool(TemporalDatafightMap['p2']['bot'])

    if TemporalDatafightMap['p2']['bot']: BOTbutton = disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'P2', custom_id=f'RBF_P2|{opponentID}|{users}', disabled=True)

    else: BOTbutton = disnake.ui.Button(style=disnake.ButtonStyle.red, label=f'P2', custom_id=f'RBF_P2|{opponentID}|{users}')

    buttons = [
        disnake.ui.Button(style=disnake.ButtonStyle.red, label=f'P1', custom_id=f'RBF_P1|{userID}|{users}'),
        BOTbutton,
        disnake.ui.Button(style=disnake.ButtonStyle.blurple, label=f'Решения', custom_id=f'MVBF|{users}'),
        disnake.ui.Button(style=disnake.ButtonStyle.blurple, label=f'Предметы', custom_id=f'ISBF|{users}'),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label=f'Побег', custom_id=f'ESCBF|{users}')
        ]

    players = {
        "p1":(int(userID), str(TemporalDatafightMap['p1']['name'])),
        "p1_pokemons":userPokes,
        "p1_items":userItemsList,
        "p1_bot":p1BOT,

        "p2":(int(opponentID), str(TemporalDatafightMap['p2']['name'])),
        "p2_pokemons":opponentPokes,
        "p2_items":opponentItemsList,
        "p2_bot":p2BOT
        }


    embed = disnake.Embed(
        title=title,
        description=body
        ).set_footer(text='Шаг боя: 0')

    adress = (int(message.guild.id), int(message.channel.id), int(message.id))

    await setFightStatus(userID, status=True) #? Для первого игрока
    await setFightStatus(opponentID, status=True) #? Для второго игрока

    install(users=users, players=players, adress=adress)
    await message.edit(embed=embed, components=buttons)
async def fightButtonsUpdateGetReady(message, p1:bool=None, p2:bool=None):
    if p1 is not None and p2 is not None:
        buttons = [
        disnake.ui.Button(label=f'P1', custom_id=message.components[0].children[0].custom_id),
        disnake.ui.Button(label=f'P2', custom_id=message.components[0].children[1].custom_id)
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
        buttons = [
        disnake.ui.Button(style=p1, label=f'P1', custom_id=message.components[0].children[0].custom_id),
        disnake.ui.Button(style=message.components[0].children[1].style, label=f'P2', custom_id=message.components[0].children[1].custom_id)
        ]
        for index, item in enumerate(buttons):
            if item.label == 'P1': 
                if p1: style = disnake.ButtonStyle.green
                else: style = disnake.ButtonStyle.red
                buttons[index].style = style
    if p2 is not None and p1 is None:
        buttons = [
        disnake.ui.Button(style=message.components[0].children[0].style, label=f'P1', custom_id=message.components[0].children[0].custom_id),
        disnake.ui.Button(style=p2, label=f'P2', custom_id=message.components[0].children[1].custom_id)
        ]
        for index, item in enumerate(buttons):
            if item.label == 'P2': 
                if p2: style = disnake.ButtonStyle.green
                else: style = disnake.ButtonStyle.red
                buttons[index].style = style
    await message.edit(components=buttons)

async def openHellMarket() -> map:
    with open('../PonyashkaDiscord/content/lotery/deadPokeMarket.json', encoding='UTF-8') as file:
        deadMarket = json.load(file)
    return deadMarket
async def saveHellMarket_DeadFight(ponymon):
    deadMarket = await openHellMarket()
    deadMarket['dead_in_fight'].append(ponymon)
    with open('../PonyashkaDiscord/content/lotery/deadPokeMarket.json', 'w', encoding='UTF-8') as file:
        json.dump(deadMarket, file, indent=3, ensure_ascii=False)


class PokeCom(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
# unstatic load module, it`s just for simplicity
def setup(bot:commands.Bot):
    bot.add_cog(PokeCom(bot))
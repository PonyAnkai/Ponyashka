import disnake
from disnake.ext import commands
from random import randint

import asyncio
import json
import time

from ..REQ_database import DataBase
from random import choices, choice, randrange

db = DataBase

class Exception(Exception): pass

class RpgCommand(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener('on_button_click')
    async def fightListenerButtonsSwap(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == 'action_player':
            buttons = await getButtonsAction()
            await inter.response.edit_message(components=buttons)

        if inter.component.custom_id == 'item_player':
            buttons = await getButtonsItem()
            await inter.response.edit_message(components=buttons)

        if inter.component.custom_id in ['back_from_action', 'back_from_items']:
            buttons = await getButtonsFight()
            await inter.response.edit_message(components=buttons)
    
    @commands.Cog.listener('on_button_click')
    async def fightEndMovePlayer(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == 'attack_player':
            await inter.response.defer()
        if inter.component.custom_id == 'escape_player':
            await inter.response.defer()


async def createMetadata(message_id) -> dict:
    temporal = {
                "id":'S0',
                "next":"S0",
                "route_select":False,
                "exit":False,
                "message_id":message_id,

                "buffer":1
                }
    return temporal

#? Command for delete different embeds through time
async def deleteAfterEmbed(json_name:str, message:object, time:int) -> bool:
    try:
        await asyncio.sleep(time)
        with open(f"../PonyashkaDiscord/config/{json_name}", encoding='UTF-8') as file:
            data = json.load(file)
            del data[f'{message.id}']
            file.close()
        with open(f'../PonyashkaDiscord/config/{json_name}', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(data, indent=3, ensure_ascii=False))
            file.close()
        embed = disnake.Embed(title='Информация',description='```Окно закрыто системой.```')
        await message.edit(components=None, embed=embed)
        return True
    except:
        print('Code 2 >>> In method "deleteAfterEmbed" tiny problem.')

#? command for delete message after enter time
async def deleteAfter(message:object, time:int) -> None:
    await asyncio.sleep(time)
    await message.delete()

async def endDialogScene(message:int):
    await message.edit(components=None)

async def dialogWithoutSelect(text:list, tempo:int, message:object, end_button:object) -> None:
        for index, item in enumerate(text):
            if index != len(text)-1:
                embed = disnake.Embed(description=item)
                await message.edit(embed=embed, components=None)
                await asyncio.sleep(tempo)
            else:
                embed = disnake.Embed(description=item)
                await message.edit(embed=embed, components=end_button)

#? command for load dictonary user data, what need to statistic embed
async def userData(uid:int) -> dict:
    try:
        with open(f'../PonyashkaDiscord/content/user/{uid}.json', encoding='UTF-8') as file:
            userDataJ = json.load(file)
            file.close() 
    except:
        loadUserData = {
            "main_load":{
                "RANK":{},
                "ACHIVM":{},
                "TITLE":{}
                },
            "PERK":{
                "ACTIVE":{},
                "PASSIVE":{},
                "SPECIAL":{}
                }
            }
        with open(f'../PonyashkaDiscord/content/user/{uid}.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(loadUserData, indent=3, ensure_ascii=False))
            file.close()
        with open(f'../PonyashkaDiscord/content/user/{uid}.json', 'r', encoding='UTF-8') as file:
            userDataJ = json.load(file)
            file.close()
        
    
    user_CP = DataBase.Info(user_id=uid).takeFromRPG(table='user_main_info')
    user_M = DataBase.Info(user_id=uid).takeFromRPG(table='user_money')
    user_S = DataBase.Info(user_id=uid).takeFromSystem(table='user_wins_max')
    user_INV = DataBase.Info(user_id=uid).takeFromRPG(table='user_active_inventory')
    user_DIP = DataBase.Info(user_id=uid).takeFromRPG(table='user_diplomaty')
    user_PR = DataBase.Info(user_id=uid).takeFromRPG(table='user_parametr')
    user_E = DataBase.Info(user_id=uid).takeFromRPG(table='user_equipment')

    userData = {
        "main":{
            "LVL":user_CP[1],
            "EXP":user_CP[2],
            "REP":user_CP[3],
            "RANK":userDataJ["main_load"]["RANK"],
            "ACHIVM":userDataJ["main_load"]["ACHIVM"],
            "TITLE":userDataJ["main_load"]["TITLE"],
            "CLAN": user_DIP[2],
            "GROUP": user_DIP[1]
            },
        "money":{
            "ESSENCE":user_M[1],
            "SHARD":user_M[2],
            "SOUL":user_M[3],
            "CRISTALL_SOUL":user_M[4],
            "COU":user_M[5],
            "VCOIN":user_M[6],
            "ACOIN":user_M[7],
            "TCOIN":user_M[8]
            },
        "equipment":{
            "HEAD":user_E[1],
            "FINGER_1":user_E[2],
            "FINGER_2":user_E[3],
            "NEAK":user_E[4],
            "HAND_L":user_E[5],
            "HAND_R":user_E[6],
            "BODY":user_E[7],
            "LEGS":user_E[8],
            "EMP_HEAD":user_E[9],
            "EMP_CHEST":user_E[10],
            "EMP_BELLY":user_E[11],
            "EMP_RHAND":user_E[12],
            "EMP_LHAND":user_E[13]
            },
        "parametr":{
            "HP":user_PR[1],
            "ATK":user_PR[2],
            "DEF":user_PR[3],
            "STR":user_PR[4],
            "LUCK":user_PR[5],
            "CRIT":user_PR[6],
            "CCRIT":user_PR[7],
            "ULT":user_PR[8],
            "REG":user_PR[9],
            "SS":user_PR[10],
            "FLX":user_PR[11],
            "STL":user_PR[12],
            "SEN":user_PR[13],
            "VIT":user_PR[14],
            "INS":user_PR[15],
            "CTR":user_PR[16],
            "GEN":user_PR[17],
            "FR":user_PR[18],
            "ER":user_PR[19],
            "AQ":user_PR[20],
            "WD":user_PR[21],
            "HL":user_PR[22],
            "WG":user_PR[23],
            "LG":user_PR[24],
            "DR":user_PR[25],
            "ST":user_PR[26]
            },
        "inventory":{
            "SLOT1":user_INV[1],
            "SLOT2":user_INV[2],
            "SLOT3":user_INV[3],
            "SLOT4":user_INV[4],
            "SLOT5":user_INV[5]
            },
        "perk":{
            "ACTIVE":userDataJ['PERK']['ACTIVE'],
            "PASSIVE":userDataJ['PERK']['PASSIVE'],
            "SPECIAL":userDataJ['PERK']['SPECIAL']
            },
        "dip":{
            "SUNSET":user_DIP[3],
            "TAYBLASS":user_DIP[4],
            "DARKBOOK":user_DIP[5],
            "FREESOVET":user_DIP[6],
            "FAME":user_DIP[7],
            "PET":user_DIP[8]
            }
        }



    # always back 'userData' type=dict
    return userData

async def getButtonsFight():
    '''it`s a just button for fight, nothing like that'''
    buttons = [
        disnake.ui.Button(style=disnake.ButtonStyle.danger, label='Атака', custom_id='attack_player'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='Цель', custom_id='select_target'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='Действие', custom_id='action_player'),
        disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Предметы', custom_id='item_player'),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label='Побег', custom_id='escape_player')
        ]
    return buttons
async def getButtonsAction():
    # TODO: Добавить множественные проверки на наличие кнопок, по типу: Есть ли у пользователя возможности вора, по краже, или возможность целевого вампиризма. Желательно сделать это сразу, а также вывести списком возможные действия которые способен будет делать игрок
    buttons = [
        disnake.ui.Button(style=disnake.ButtonStyle.danger, label='A', custom_id='a'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='B', custom_id='b'),
        disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='C', custom_id='c'),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label='D', custom_id='d'),
        disnake.ui.Button(style=disnake.ButtonStyle.danger, label='F', custom_id='f'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='G', custom_id='g'),
        disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='I', custom_id='i'),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label='H', custom_id='h'),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label='Назад-1', custom_id='back_from_action')
        ]
    return buttons
async def getButtonsItem():
    buttons = [
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='1', custom_id='use_1_item'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='2', custom_id='use_2_item'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='3', custom_id='use_3_item'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='4', custom_id='use_4_item'),
        disnake.ui.Button(style=disnake.ButtonStyle.green, label='5', custom_id='use_5_item'),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label='Назад-2', custom_id='back_from_items')
        ]
    return buttons


async def CTX_ToDumpPickle(ctx):
    pass
async def createFightData(players:list):
    fightData = {
        "meta":{
            "itter":0
            }
        }
    for item in players:
        fightData[players.name] = {
            "move":None,
            "item":None
            }


# unstatic load module, it`s just for simplicity
def setup(bot:commands.Bot):
    bot.add_cog(RpgCommand(bot))
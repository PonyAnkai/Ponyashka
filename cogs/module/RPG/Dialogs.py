import disnake
from disnake.ext import commands
from random import randint
import asyncio
import json

from .System import *
from ...Rpg import RPG


def rep(character:str, value:int):
    pass
def command(nameCommand):
    pass

# adaptive context modefier
def mode(mode:str):
    tag_list = mode.split()

    if tag_list[0] == 'rep':
        rep(character=tag_list[1], value=tag_list[2])
    if tag_list[0] == 'stat':
        RPG.stat()
    
# ID = 1-1-00001
# open all function for RPG module
async def segment(
        fileName:str, 
        author_id:int, 
        message:object, 
        segment:str, 
        name_button:str
    ) -> None:
    
    with open(f'../PonyashkaDiscord/content/RPG/dialogs/{fileName}.json', encoding='UTF-8') as file:
        scene = json.load(file) # id(F/S/T|X-Y):{text:[], select:[], (optional)mode:[]}
        settings = scene['setting'] # tempo, image
    with open(f'../PonyashkaDiscord/content/RPG/dialogs/temporal_dialog/{author_id}.json', encoding='UTF-8') as file:
        metadata = json.load(file) # id:str, next:id+1 , message_id:int
    
    metadata['id'] = segment
    phase = scene[segment]
    buttons = []

    # try: mode = phase['mode']
    # except: mode = 0


    try: 
        metadata['exit'] = phase['exit']
        metadata['next'] = 'exit'
    except: pass
    

    if not metadata['exit']:
        route_select = not len(phase[f'route_{metadata['buffer']}']) < 2
        #? Проверка на множественность выбора
        if route_select:
            metadata['route_select'] = True
            metadata['next'] = scene[segment][f'route_{metadata['buffer']}']
        else:   
            metadata['route_select'] = False
            metadata['next'] = scene[segment][f'route_{metadata['buffer']}'][0]
        #? Создание кнопок для продолжения диалога
        for index, item in enumerate(phase[f'select_{metadata['buffer']}']):
            buttons.append(disnake.ui.Button(style=disnake.ButtonStyle.gray, label=item, custom_id=f'{name_button}{index+1}')) 

    #? Save metadata
    with open(f'../PonyashkaDiscord/content/RPG/dialogs/temporal_dialog/{author_id}.json', 'w', encoding='UTF-8') as file:
        file.write(json.dumps(metadata, indent=3, ensure_ascii=False))

    for index, item in enumerate(phase[f'text_{metadata['buffer']}']):
        embed = disnake.Embed(title=phase['header'][0], description=item).set_footer(text=f'id={metadata['id']}, next={metadata['next']}, route={metadata['route_select']}')

        if index == len(phase[f'text_{metadata['buffer']}'])-1 and not metadata['exit']:
            await message.edit('', embed=embed, components=buttons)
        else: await message.edit('', embed=embed, components=None)


        await asyncio.sleep(settings['tempo'])




class Dialogs(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener('on_button_click')
    async def first_talk_with_player(self, inter:disnake.MessageInteraction):
        if inter.component.custom_id not in ['first_talk_with_player', 'start_prologe1', 'start_prologe2', 'start_prologe3']:
            return
        with open(f'../PonyashkaDiscord/content/RPG/dialogs/temporal_dialog/{inter.author.id}.json', encoding='UTF-8') as file:
            metadata = json.load(file) # id:int, message_id:int
        
        if inter.component.custom_id in ['start_prologe1', 'start_prologe2', 'start_prologe3'] and metadata['exit']:
            await inter.response.edit_message(components=None)
            return
        if inter.component.custom_id in ['start_prologe1', 'start_prologe2', 'start_prologe3'] and not inter.response.is_done():
            await inter.response.defer()


        # 0= no select away
        # 1-4= selected user route
        if not metadata['route_select']:
            await segment(fileName='first_dialog_with_ponyashka', author_id=inter.author.id, message=inter.message, segment=metadata['next'], name_button='start_prologe') # play text
        else:
            if inter.component.custom_id == 'start_prologe1': metadata['next'] = metadata['next'][0]
            elif inter.component.custom_id == 'start_prologe2': metadata['next'] = metadata['next'][1]
            elif inter.component.custom_id == 'start_prologe3': metadata['next'] = metadata['next'][2]
            await segment(fileName='first_dialog_with_ponyashka', author_id=inter.author.id, message=inter.message, segment=metadata['next'], name_button='start_prologe') # play text
        
    
    @commands.Cog.listener('on_button_click')
    async def testingDialogs(self, inter:disnake.MessageInteraction):
        if inter.component.custom_id not in ['testDialog', 'testingDialogs1', 'testingDialogs2', 'testingDialogs3']:
            return
        with open(f'../PonyashkaDiscord/content/RPG/dialogs/temporal_dialog/{inter.author.id}.json', encoding='UTF-8') as file:
            metadata = json.load(file) # id:int, message_id:int
        
        if inter.component.custom_id in ['testingDialogs1', 'testingDialogs2', 'testingDialogs3'] and metadata['exit']:
            await inter.response.edit_message(components=None)
            return
        if inter.component.custom_id in ['testingDialogs1', 'testingDialogs2', 'testingDialogs3'] and not inter.response.is_done():
            await inter.response.defer()
        if inter.component.custom_id == 'testDialog':
            await inter.response.defer()
        

        # 0= no select away
        # 1-4= selected user route
        if not metadata['route_select']:
            await segment(fileName='testing_dialog', author_id=inter.author.id, message=inter.message, segment=metadata['next'], name_button='testingDialogs') # play text
        else:
            if inter.component.custom_id == 'testingDialogs1': metadata['next'] = metadata['next'][0]
            elif inter.component.custom_id == 'testingDialogs2': metadata['next'] = metadata['next'][1]
            elif inter.component.custom_id == 'testingDialogs3': metadata['next'] = metadata['next'][2]
            await segment(fileName='testing_dialog', author_id=inter.author.id, message=inter.message, segment=metadata['next'], name_button='testingDialogs') # play text
        

def setup(bot:commands.Bot):
    loadCog = Dialogs(bot)
    bot.add_cog(loadCog)
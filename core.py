import disnake
from disnake.ext import commands
from tqdm import tqdm

desc = 'Я всегда развиваюсь! И ты тоже начинай!'

bot = commands.Bot(command_prefix='!', 
                   intents=disnake.Intents.all(), 
                   activity= disnake.Activity(name='GFM', type= disnake.ActivityType.playing),
                   reload=True, 
                   help_command=None,
                   description=desc)

loadRange = ['Economics', 'Message', 'Events', 'Fun', 'Rpg', 'Administrator', 'Until', 'TestingEver', 'module.RPG.Dialogs', 'module.RPG.System', 'module.RPG.Shop', 'module.Views', 'module.ponymon.FightLoop', 'module.PG.pg', 'module.ponymon.Ponymons', 'module.PG.sub_PG', 'EventLogs']
for item in loadRange:
    bot.load_extension(f'cogs.{item}')

bot.run(open("token.txt", 'r').readline())  
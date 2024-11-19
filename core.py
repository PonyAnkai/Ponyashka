import disnake
from disnake.ext import commands
from tqdm import tqdm

desc = 'Я всегда развиваюсь! И ты тоже начинай!'

bot = commands.Bot(command_prefix='!', 
                   intents=disnake.Intents.all(), 
                   activity= disnake.Activity(name='fu-fu-fu', type= disnake.ActivityType.playing),
                   reload=True, 
                   help_command=None,
                   description=desc)

loadRange = ['Economics', 'Message', 'Events', 'Fun', 'Rpg', 'Administrator', 'Until', 'TestingEver', 'module.RPG.Dialogs', 'module.RPG.System', 'module.RPG.Shop', 'module.Views', 'module.ponymon.FightLoop', 'PG', 'module.PGModule', 'module.ponymon.Ponymons']
for index in range(len(loadRange)):
    bot.load_extension(f'cogs.{loadRange[index]}')

bot.run(open("token.txt", 'r').readline())  
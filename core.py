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

loadRange = ['Economics', 'Message', 'Events', 'Fun', 'Rpg', 'Administrator', 'Until', 'TestingEver', 'module.SystemDialogsRPG', 'module.SystemCommandRPG', 'module.SystemShop', 'module.SystemViews', 'module.FightLoop', 'PG', 'module.PGModule', 'module.PokemonModule', 'Var']
for index in range(len(loadRange)-1):
    bot.load_extension(f'cogs.{loadRange[index]}')

bot.run(open("token.txt", 'r').readline())  
import disnake
from disnake.ext import commands

from .module import REQ_database as Rdb

db = Rdb.DataBase

class Events(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    
    # Preparation start
    @commands.Cog.listener()
    async def on_ready(self):
        pass
        # await self.bot.get_channel(1205649033125830706).send(f'Запуск номер ``{data[2]}``')
    
    @commands.Cog.listener('on_ready')
    async def on_ready_end(self):
        db.Bot.set(column='dies', value=1).add()
        data = db.Bot().info()
        print(f'| Numbers start >>> {data[2]}')
        print('_'*60)

    @commands.Cog.listener('member_join')
    async def member_join(self, member):

        if not member.author.bot: db.Check(user_id=member.author.id, user_name=member.author.name).user()
        else: return
        print(f'On database add user: {member.author.name}')

    @commands.Cog.listener('member_remove')
    async def member_remove(self, member):

        if not member.author.bot: db.DeleteData(user_id=member.author.id).delete()
        else: return
        print(f'On database delete user: {member.author.name}')

    # Обработчик ошибок
    # # ! Добавить кастомные варианты ошибок и ответов
    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if isinstance(error, commands.MissingPermissions):
    #         await ctx.send(f"{ctx.author.mention}, у вас недостаточно прав для этой команды")
    #     elif isinstance(error, commands.CommandNotFound):
    #         print(f"Вызвана неизвестная мне команда: {error}")
    #     elif isinstance(error, commands.DiscordServerError):
    #         print(f"Опять соединение прохое... (DiscordServerError: {error})")
    #     else:
    #         print(ctx, error)


# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Events(bot))
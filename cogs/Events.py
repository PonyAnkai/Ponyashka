import disnake
from disnake.ext import commands

from .module import REQ_database as Rdb
from .EventLogs import EventsLogs as ev

db = Rdb.DataBase

class Events(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener('on_ready')
    async def on_ready_end(self):
        db.Bot.set(column='dies', value=1).add()
        data = db.Bot().info()
        print(f'Main ponyashka is ready | Numbers start >>> {data[2]}')
        print('_'*60)

    @commands.Cog.listener('member_join')
    async def member_join(self, member):

        if not member.author.bot: 
            responce = db.Check(user_id=member.author.id, user_name=member.author.name).user()
            await ev(self.bot).new_user(member.author.name, responce[1])        
        else: return

    @commands.Cog.listener('member_remove')
    async def member_remove(self, member):
        pass
        # if not member.author.bot: db.DeleteData(user_id=member.author.id).delete()
        # else: return
        # print(f'On database delete user: {member.author.name}')

    @commands.Cog.listener('on_invite_create')
    async def invite_create(self, invite):
        await ev(self.bot).invite_user(invite)

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Events(bot))
from .module import REQ_database as Rdb

import random
import time

import disnake
from disnake.ext import commands
import random

'''
# ! Приколы для будущего
import os.path
import shutil   
'''
db = Rdb.DataBase

class Fun(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    
    # ! переработать позже
    @commands.command(name='rand', aliases=['рандом', 'ранд', 'случ'])
    async def rand(self, ctx):
        
        
        
        mess = ctx.message.content.split(' ')
        elements = []
        try:
            mess_ = round(abs(int(mess[1])))
            try:
                elements.append(mess_)
            except IndexError:
                await ctx.send('Укажите хотя бы один численный аргумент')
        except ValueError:
            await ctx.send('Укажите хотя бы один численный аргумент')
            return 0

        try:
            mess_ = mess[2]
            try:
                mess_ = round(abs(int(mess_)))
                elements.append(mess_)
            except ValueError:
                elements.append(False)
        except IndexError:
            elements.append(False)

        if not elements[1]:
            await ctx.send(random.randint(0, elements[0]))
        elif elements[1]:
            await ctx.send(random.randint(elements[0], elements[1]))

    @commands.command(name='gif', aliases=['гиф', 'гифка'])
    async def gif(self, ctx):
        file = open('../PonyashkaDiscord/other_content/Gif/base.txt', mode='r')

        gifs = []
        for item in file:
            gifs.append(item.rstrip())
        file.close()

        await ctx.send(random.choice(gifs))

    @commands.command(name='gifadd', aliases=['добгиф', 'новгиф'])
    async def gifadd(self, ctx):
        file = open('../PonyashkaDiscord/other_content/Gif/base.txt', mode='r')

        try:
            gifs_user = ctx.message.content.split(' ')[1]
        except:
            await ctx.send('что-то не так')
            return

        gifs = []
        for item in file:
            gifs.append(item.rstrip())
        file.close()
        
        if gifs_user in gifs:
            await ctx.send('Такое уже есть')
            return
        else:
            await ctx.send('Добавлено в список')
            gifs.append(gifs_user)
        
        file = open('../PonyashkaDiscord/content/Gif/base.txt', mode='w')
        for i in range(len(gifs)):
            file.writelines(f'{gifs[i]}\n')
        file.close()

    @commands.command(name='russianrollete', aliases=['rr', 'рулетка', 'rollete'])
    async def russianRollete(self, ctx):

        user = ctx.message.author.id

        # Проверка на указание числового значения
        try:
            bullet = int(ctx.message.content.lower().split(' ')[1])
        except:
            embed = disnake.Embed(description='Не указано количество **пуль**')
            return await ctx.send(embed=embed)
        
        # Проверка диапазона
        if not 0 < bullet < 7:
            embed = disnake.Embed(description='Количество **пуль** должно быть 1-6')
            return await ctx.send(embed=embed)

        # Преобразования в проценты
        endGame = float('{:.2f}'.format(bullet / 6))
        chance = float('{:.2f}'.format(random.random()))

        # Взятие стриков из бд
        strick = db.Fun(user=user).get()

        # Проверка
        if chance > endGame:
            db.Fun(user=user, strick='rolete').add()
            db.Fun(user=user).maxis()
            embed = disnake.Embed(
                title=f'**Выстрела не было. \nПоздравляю** 🎉',
                color= disnake.Colour.green())
            embed.set_footer(text=f'WinSrick: {strick[3]+1}')
            return await ctx.send(embed=embed)
        else:
            db.Fun(user=user, strick='rolete').clear()
            embed = disnake.Embed(
                title=f'**Ты проиграл этой жизни** 💀',
                color= disnake.Colour.red())
            embed.set_footer(text='WinSrick: 0')
            return await ctx.send(embed=embed)

    @commands.command(name='coin', aliases=['монетка', 'монеточка', 'коин'])
    async def coin(self, ctx):

        user = ctx.message.author.id

        try:
            mess = ctx.message.content.split(' ')[1]
        except IndexError:
            await ctx.send('Укажите, орёл или решка, после команды')
            return False
        if mess == 'орёл' or mess == 'орел':
            count = 1
        elif mess == 'решка':
            count = 2
        else:
            await ctx.send('Укажите, орёл или решка, после команды')
            return False
        
        bot_var = random.randint(1, 2)
        strick = db.Fun(user=user).get()

        if bot_var == count and count == 2:
            db.Fun(user=user, strick='coin').add()
            db.Fun(user=user).maxis()
            emb = disnake.Embed(description=f'**Воу! Это оказалась ``решка``! Победа за тобой!**\nWinSrick: ``{strick[1]+1}``',
                                colour=disnake.Color.green())
            await ctx.send(embed=emb)
        elif bot_var != count and count == 1:
            db.Fun(user=user, strick='coin').clear()
            emb = disnake.Embed(description='**Лол, Это оказалась ``решка``. Приходи в следующий раз.**\nWinSrick: ``0``',
                                colour=disnake.Color.red())
            await ctx.send(embed=emb)
        elif bot_var == count and count == 1:
            db.Fun(user=user, strick='coin').add()
            db.Fun(user=user).maxis()
            emb = disnake.Embed(description=f'**Воу! Это оказался ``орёл``! Победа за тобой!**\nWinSrick: ``{strick[1]+1}``',
                                colour=disnake.Color.green())
            await ctx.send(embed=emb)
        elif bot_var != count and count == 2:
            db.Fun(user=user, strick='coin').clear()
            emb = disnake.Embed(description='**Лол, Это оказался ``орёл``. Приходи в следующий раз.**\nWinSrick: ``0``',
                                colour=disnake.Color.red())
            await ctx.send(embed=emb)

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Fun(bot))
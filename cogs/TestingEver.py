from typing import Coroutine
import disnake
from disnake.ext import commands

import json
import os
from .EventLogs import EventsLogs as el 
import asyncio


class Testing(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    async def view(self, ctx):
        if ctx.message.guild.id != 1199488197885968515:
            return
        
        ids = ctx.message.content.split()
        try:
            with open(f'../PonyashkaDiscord/content/location/{ids[1]}.json', encoding='UTF-8') as f:
                config = json.load(f)

            try:
                param = ctx.message.content.split()
                if param[2] == 'take':
                    await ctx.send('Ваш файлик!',file=disnake.File(f'../PonyashkaDiscord/content/location/{ids[1]}.json'))
                else:
                    await ctx.send(config[f'{param[2]}'])
            except:
                await ctx.send(config)
            f.close()
        except:
            try:
                # Указываем путь к директории
                directory = "../PonyashkaDiscord/content/location"
                # Получаем список файлов
                files = os.listdir(directory)
                text = ''
                if ids[1] == 'name':
                    for item in files:
                        with open(f'../PonyashkaDiscord/content/location/{item}', 'r', encoding='UTF-8') as f:
                            config = json.load(f)
                            name = item.replace('.json', '')
                            text += f'{name} — {config['name']}\n'
                    await ctx.send(text)
                else:
                    await ctx.send(f'Такой ({ids[1]}) локации нет. Либо-же в файле была ошибка.')
            except:
                # Указываем путь к директории
                directory = "../PonyashkaDiscord/content/location"
                # Получаем список файлов
                files = os.listdir(directory)

                try:
                    files.remove('desktop.ini')
                except:
                    pass
                text = ''
                for index, item in enumerate(files):
                    if index == len(files)-1:
                        text+=f'{item}'
                        continue
                    text+= f'{item}\n'
                # Выводим список файлов
                await ctx.send(text)

    @commands.command()
    async def load(self, ctx):
        if ctx.message.guild.id != 1199488197885968515:
            return
        
        try:
            atth = ctx.message.attachments
            name_atth = atth[0].filename
            url_atth = atth[0].url
            
            text= 'lol'
            if not name_atth.endswith('.json'):
                print(f'>->->->-> Попытка загрузки сторонего типа файла {name_atth}')

                return
            
            import requests
            responce = requests.get(url=url_atth)
            with open(f'../PonyashkaDiscord/content/location/{name_atth}', 'wb') as file:
                file.write(responce.content)
            file.close()

            await ctx.send(f'Успешная загрузка!')
        except:
            pass

    @commands.command()
    async def swap(self, ctx):

        m = ctx.message.content.split()
        # try:
        ids = m[1] # айди файла
        param = m[2] # Параметр для свапа
        val = m[3] # значение свапа
        with open(f'../PonyashkaDiscord/content/location/{ids}.json', 'r', encoding='UTF-8') as f:
            config = json.load(f)
            config[param] = val
            f.close()
        with open(f'../PonyashkaDiscord/content/location/{ids}.json', 'w', encoding='UTF-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.close()
        await ctx.send('Я изменила параметр! Проверяй!')
        # except:
        #     await ctx.send('Ой, что-то пошло не так, вы точно написали такой формат команды? \n``~swap <ID> <параметр> <значение>``\n\nТакже меняйте число на число, а слова на слова!')

    @commands.command()
    async def emb(self, ctx):
        if ctx.message.guild.id != 1199488197885968515:
            return
        
        if not ctx.message.attachments:
            try:
                select = ctx.message.content.split()
                embed = disnake.Embed(title='Проверка загрузки кастома')
                embed.set_image(file=disnake.File(f'../PonyashkaDiscord/content/icon/{select[1]}'))
                await ctx.send(embed=embed)
            except:
                import os
                # Указываем путь к директории
                directory = "../PonyashkaDiscord/content/icon"
                # Получаем список файлов
                files = os.listdir(directory)
                
                try: files.remove('desktop.ini')
                except: pass

                text = ''
                for index, item in enumerate(files):
                    if index == len(files)-1:
                        text+=f'{item}'
                        continue
                    text+= f'{item}\n'
                # Выводим список файлов
                await ctx.send(text)
        else:
            atth = ctx.message.attachments

            namefile = atth[0].filename.split('.')[1]
            if namefile not in ['gif', 'png', 'jpg', 'webm']:
                await ctx.send(f'Я не работаю с форматом ({namefile}), просите поня добавить его в разрешенное!')

            try:
                file = atth[0].filename.split('.')
                name_atth = f'{ctx.message.content.split()[1]}.{file[1]}'
            except:
                await ctx.send('Вы забыли указать название!')
                return
            url_atth = atth[0].url

            import requests
            responce = requests.get(url=url_atth)
            with open(f'../PonyashkaDiscord/content/icon/{name_atth}', 'wb') as file:
                file.write(responce.content)
            file.close()
            await ctx.send('Я сделять!')

    @commands.command()
    async def added(self, ctx):

        import sqlite3
        con = sqlite3.connect('../PonyashkaDiscord/_system.db')
        cur = con.cursor()
        
        threads = ctx.guild.threads
        channels = ctx.guild.channels
        read = 0
        for item in channels:
            cur.execute(f"SELECT ID FROM channel_data WHERE ID = {item.id}")
            seel = cur.fetchone()
            if seel is None:
                read += 1
                cur.execute("INSERT INTO channel_data VALUES (?, ?, ?)", (item.id, item.name, 0))
                con.commit()
        for item in threads:
            cur.execute(f"SELECT ID FROM channel_data WHERE ID = {item.id}")
            seel = cur.fetchone()
            if seel is None:
                read += 1
                cur.execute("INSERT INTO channel_data VALUES (?, ?, ?)", (item.id, item.name, 0))
                con.commit()
                

        # int(time.strftime('%d'))
        await ctx.send(f'Записала {read} записей!')

    @commands.command()
    async def chk(self, ctx):
        
        with open('../PonyashkaDiscord/other_content/RP/magic.txt', encoding='UTF-8') as f:
            magic = f.read().split(', ')
            f.close()

        v = 1
        try:
            v = int(ctx.message.content.split()[1])
        except:
            await ctx.send(f'Количество зарегестрированой магии: {len(magic)}\n-# Сотня в шаманизме')
            return
        
        if ctx.message.author.id != 374061361606688788:
            return

        from random import choice
        text = set()
        while True:
            text.add(choice(magic))
            if v == len(text):
                break
        
        embed_text = ''
        for index, item in enumerate(text):
            embed_text += f'{index+1}: {item}\n'
        embed = disnake.Embed(title='Рандомные обелиски магии', description=embed_text)
        await ctx.send(embed=embed)

    @commands.command(name='neuro')
    async def neuro(self, ctx):
        '''Идея о том, что бы сделать обращение к поняшке. Человек написал о пони и она тут как тут, даже на что-то ответить может. Только сложность в том, что потребуется реализовать систему адаптивной нейронки, что будет понимать контекст сообщения, даже с ошибками, и выдавать нужный ответ.'''
        '''Учесть прикол, что при Timeout выскакивает ошибка, которую следует обработать, дабы в чат не сралось'''
        channel = ctx.message.channel
        def check(e):
            return e.content == 'поняшка' and e.channel == channel
        msg = await self.bot.wait_for('message', check=check, timeout=15)
        await channel.send(f'Да-да?')

    @commands.command(name='test')
    async def test(self, ctx):
        responce = await el(self.bot).MoneyIncome(ctx.author, value=15)
        await ctx.send(f"{responce}")

    @commands.command(name='ck')
    async def ck(self, ctx):

        text = 'Задача 1 — {pos0}\nЗадача 2 — {pos1}\nЗадача 3 — {pos2}\n'
        checkList = [False, False, False]
        timeStop = [5, 10, 3]

        async def msg(message=None):
            if message:
                return await message.edit(text.format(
                    pos0='✅' if checkList[0] else '❌',
                    pos1='✅' if checkList[1] else '❌',
                    pos2='✅' if checkList[2] else '❌',
                    ))
            else:
                return await ctx.send(text.format(
                    pos0='✅' if checkList[0] else '❌',
                    pos1='✅' if checkList[1] else '❌',
                    pos2='✅' if checkList[2] else '❌',
                    ))
        
        mess = await msg()
        for index, item in enumerate(checkList):
            async with ctx.channel.typing():
                await asyncio.sleep(timeStop[index])
            checkList[index] = not item
            await msg(mess)
        else: 
            await ctx.send('Проверка завершена.')

def setup(bot:commands.Bot):
    bot.add_cog(Testing(bot))
from typing import Coroutine
import disnake
from disnake.ext import commands

import json
import os
import asyncio


class Listener(disnake.ui.StringSelect):
    def __init__(self, options):
        super().__init__(
            placeholder='Сортировка по...',
            min_values=1,
            max_values=1,
            options=options
            )
        
    def callback(self, interaction: disnake.MessageInteraction):
        pass
        
class ViewListener(disnake.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.add_item(Listener(options=options))


class Testing(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    #? Прослушка
    @commands.Cog.listener('on_button_click')
    async def listener(self, inter:disnake.MessageInteraction):
        if inter.component.custom_id not in ['base', 'base2', 'base3']:
            return
        
        if inter.component.custom_id == 'base':
            await inter.response.edit_message(components=None)
            await inter.response.edit_message("Вторая страничка", components=self.buttons_2)
        if inter.component.custom_id == 'base2':
            await inter.response.edit_message("Третья страничка", view=self.viewer)

    @commands.command()
    async def base(self, ctx):
        
        self.buttons_1 = [
            disnake.ui.Button(style=disnake.ButtonStyle.red, label='Page1', custom_id='base'),
            disnake.ui.Button(style=disnake.ButtonStyle.green, label='Page2', custom_id='base2')
            ]
        self.buttons_2 = [
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Назад', custom_id='base3')
            ]
        
        self.options = [
            disnake.SelectOption(label='big1', value='back2')
            ]
        
        self.viewer = ViewListener(self.options)

        await ctx.send("Первая страничка", components=self.buttons_1)

    async def lvl_set(self, ctx):
        import sqlite3
        con = sqlite3.connect('../PonyashkaDiscord/database.db')
        cur = con.cursor()

        lvl, role_id = ctx.message.content, ctx.message.raw_mentions

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
        import time
        con = sqlite3.connect('../PonyashkaDiscord/database.db')
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

    @commands.Cog.listener('on_button_click')
    async def que_button(self, inter:disnake.MessageInteraction):
        if inter.component.custom_id not in ['que_acc', 'que_quit', 'que_next']:
            return
        
        try:
            # Подгрузка файла с очередью
            with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8') as f:
                que_list_embed = json.load(f)
                f.close()

            list_j = que_list_embed[f'{inter.message.id}']
            que_list = list_j['que_list']
            # проверка на авторство и определенный ID взаимодействия, через обращение к классовому словарю TestingEver
            # Огромная зависимость на работу бота, при перезапуске весь кэш очищается
            # So sad
            if (inter.component.custom_id == 'que_next') and (inter.author.id == list_j['author']):
                try:
                    que_list.pop(0)
                except:
                    await inter.response.defer()
                    return
                # Простите, но понь в душе не ебет, как это можно без поломки пихнуть в функцию. Зависимости ебучие, а так же недостаток знаний.
                text = ''
                title = list_j['embed_base'][0]
                for index, item in enumerate(que_list):
                    text += f'`{index+1}` >>> <@{item}>\n'
                if text == '': text = list_j['embed_base'][1]
                embed = disnake.Embed(title=title, description=text)
            # Альт иной исход проверки на взаимодействие с кнопкой автора
            elif (inter.component.custom_id == 'que_next') and (inter.author.id != list_j['author']):
                await inter.response.send_message('вы не являетесь автором данной очереди.', ephemeral=True)
                return
            
            # проверка на вхождение в очередь человека
            if inter.component.custom_id == 'que_acc':
                if inter.author.id in que_list:
                    await inter.response.defer()
                    return
                que_list.append(inter.author.id)
                # Простите, но понь в душе не ебет, как это можно без поломки пихнуть в функцию. Зависимости ебучие, а так же недостаток знаний.
                text = ''
                title = list_j['embed_base'][0]
                for index, item in enumerate(que_list):
                    text += f'`{index+1}` >>> <@{item}>\n'
                if text == '': text = list_j['embed_base'][1]
                embed = disnake.Embed(title=title, description=text)
            
            if inter.component.custom_id == 'que_quit':
                if inter.author.id not in que_list:
                    await inter.response.defer()
                    return
                que_list.remove(inter.author.id)
                
                # Простите, но понь в душе не ебет, как это можно без поломки пихнуть в функцию. Зависимости ебучие, а так же недостаток знаний.
                text = ''
                title = list_j['embed_base'][0]
                for index, item in enumerate(que_list):
                    text += f'`{index+1}` >>> <@{item}>\n'
                if text == '': text = list_j['embed_base'][1]
                embed = disnake.Embed(title=title, description=text)
                
            list_j['que_list'] = que_list
            with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8', mode='w') as f:
                f.write(json.dumps(que_list_embed, indent=3, ensure_ascii=False))
                f.close()
            await inter.response.edit_message(embed=embed)
        except:
            await inter.response.edit_message(components=None)

    @commands.command()
    async def que(self, ctx):
        
        author = ctx.message.author.id
        que_list = []

        try:
            break_take = ctx.message.content.split()[1]
            title_base = ctx.message.content.replace('~que ', '')
        except:
            title_base = f'Очередь пользователя {ctx.message.author.name}'
        desc = 'Очередь пуста'
        
        embed = disnake.Embed(title=title_base, description=desc)
        button = [
            disnake.ui.Button(style=disnake.ButtonStyle.green, label='Занять', custom_id='que_acc'),
            disnake.ui.Button(style=disnake.ButtonStyle.red, label='Уйти', custom_id='que_quit'),
            disnake.ui.Button(style=disnake.ButtonStyle.gray, label='Следующий', custom_id='que_next')
            ]
        message = await ctx.send(embed=embed, components=button)
        
        try:
            with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8') as f:
                que_list_embed = json.load(f)
                f.close()
        except:
            pass

        try:
            que_list_embed[message.id] = { 
                'author':author,
                'embed_base':[title_base, desc], 
                'que_list':que_list,
                'jump_message':[
                        ctx.guild.id,
                        ctx.channel.id,
                        message.id
                        ]
                }
        except:
            que_list_embed = {
                message.id:{
                    'author':author,
                    'embed_base':[title_base, desc], 
                    'que_list':que_list,
                    'jump_message':[
                        ctx.guild.id,
                        ctx.channel.id,
                        message.id
                        ]
                    }
                }

        with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8', mode='w') as f:
            f.write(json.dumps(que_list_embed, indent=3, ensure_ascii=False))
            f.close()

    @commands.command()
    async def que_pop(self, ctx):
        if ctx.message.author.id != 374061361606688788:
            return
        

        try:
            id_mess = ctx.message.content.split()[1]
        except:
            try:
                with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8') as f:
                    que_list_embed = json.load(f)
                f.close()
                text = ''
                for item in que_list_embed:
                    gcm = que_list_embed[item]['jump_message']
                    url = f'https://discord.com/channels/{gcm[0]}/{gcm[1]}/{gcm[2]}'
                    text += f'**Name:** `{que_list_embed[item]['embed_base'][0]}` \n| {url} ← <@{que_list_embed[item]['author']}>\n'
                embed = disnake.Embed(title='Активные очереди', description=text)
                await ctx.send(embed=embed)
                return

            except:
                await ctx.send('Активные очереди отсутсвуют. Либо их большое количество.')
                return
        
        try:
            with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8') as f:
                que_list_embed = json.load(f)
                message_url = que_list_embed[id_mess]['jump_message']
            del que_list_embed[f'{id_mess}']
            f.close()
            with open('../PonyashkaDiscord/config/que_list.json', encoding='UTF-8', mode='w') as f:
                f.write(json.dumps(que_list_embed, indent=3, ensure_ascii=False))
            f.close()
            message = await self.bot.get_guild(message_url[0]).get_channel(message_url[1]).fetch_message(message_url[2])
            await message.edit(components=None)
            await ctx.send(f'Очередь с ID:{id_mess} - была закрыта.')
        except KeyError:
            await ctx.send(f'Очереди с ID:{id_mess} - не существует.')
    
    @commands.command()
    async def slideshow(self, ctx):
        import os
        from time import sleep
        # Указываем путь к директории
        directory = "../PonyashkaDiscord/content/icon/slide_show"
        # Получаем список файлов
        files = os.listdir(directory)
        try: 
            cooldown = ctx.message.content.split()[1]
            if type(cooldown) != int: cooldown = 5
        except: cooldown = 5

        embed = disnake.Embed(title=f'Файл номер= 1')
        embed.set_image(file=disnake.File(f'../PonyashkaDiscord/content/icon/slide_show/{files[0]}'))
        message = await ctx.send(embed=embed)
        sleep(5)
        for index, item in enumerate(files):
            if index == 0: continue
            embed = disnake.Embed(title=f'Файл номер= {index+1}')
            embed.set_image(file=disnake.File(f'../PonyashkaDiscord/content/icon/slide_show/{item}'))
            await message.edit(embed=embed)
            sleep(5)

    @commands.command(name='neuro')
    async def neuro(self, ctx):
        '''Идея о том, что бы сделать обращение к поняшке. Человек написал о пони и она тут как тут, даже на что-то ответить может. Только сложность в том, что потребуется реализовать систему адаптивной нейронки, что будет понимать контекст сообщения, даже с ошибками, и выдавать нужный ответ.'''
        '''Учесть прикол, что при Timeout выскакивает ошибка, которую следует обработать, дабы в чат не сралось'''
        channel = ctx.message.channel
        def check(e):
            return e.content == 'поняшка' and e.channel == channel
        msg = await self.bot.wait_for('message', check=check, timeout=15)
        await channel.send(f'Да-да?')

    @commands.command(name='emoji')
    async def emoji(self, ctx: disnake.ext):

        await ctx.send('<:huh:1300665543879168090>')

def setup(bot:commands.Bot):
    bot.add_cog(Testing(bot))
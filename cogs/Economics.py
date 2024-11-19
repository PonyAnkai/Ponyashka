import disnake
from disnake.ext import commands
from .module import REQ_database as Rdb

import json
import yaml
import pickle
import sqlite3

import time
import random

from .module.ponymon.Ponymons import *
from .module.RPG.System import *
from .module.Views import *
from .Until import Until

db = Rdb.DataBase

class AddedrMarket:
    def __init__(self):
        pass
    
    def addTiket(user, value, price):
        db.Money(user=user, value=value*price).sub()
        db.Poke(user=user).add(value=value, column='TIKET')

    def addSoul(user, value, price):
        db.Money(user=user, value=value*price, currency='SHARD').sub()
        db.Money(user=user, value=value, currency='SOUL').add()
        
    def addPokeEssence(user, value, price):
        db.Money(user=user, value=value*price).sub()
        db.Poke(user=user).add(value=value, column='POKE_ESSENCE')

class Economics(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command(name='wallet', aliases=['кошелёк', 'кошелек', 'кошель', 'wl'])
    async def wallet(self, ctx):

        user = ctx.message.author.id
        stat = await userData(uid=user)
        poke = db.Poke(user=ctx.author.id).takeAll()
        
        money = stat['money']
        text = f'## Шэкэли, что ты насобирал \n```Эссенции: {money['ESSENCE']:,}\nОсколки: {money['SHARD']:,}\nДуши: {money['SOUL']:,}``````Кристальные души: {money['CRISTALL_SOUL']:,}``````Монеты «Коширского»: {money['COU']:,}\nМонеты «Сущности»: {money['ACOIN']:,}\nМонеты «Пустоты»: {money['VCOIN']:,}\nМонеты «Истины»: {money['TCOIN']:,}``` ```Билеты: {poke[4]}\nЭссенции монстра: {poke[5]}```'

        embed = disnake.Embed(
            description=text
            ).set_thumbnail(url=ctx.message.author.avatar.url)
        
        message = await ctx.send(embed=embed)

        await closeEmbedMessageAfter(message, time=60)

    #? Добавить стриковую градацию <10/1 <25/2,5 <50/5 <75/7.5 <100/10 endless/15
    @commands.command(name='work', aliases=['работа', 'раб'])
    async def work(self, ctx):

        if db.Lock(user_id=ctx.author.id, slot=1).ready() or ctx.author.id == 374061361606688788:
            db.Check(user_id=ctx.author.id, user_name=ctx.author.name).user()
            cashIncome = await calculateValueWorkPokemon(user=ctx.author.id, sys=True)

            info = db.Poke(user=ctx.author.id).takeAll()
            strikeMulti = await checkStrikeWork(info[1])
            timestamp = (round(time.time()) - info[2])//3600
            strikeup = 24 > timestamp >= 0
            dropstrike = (strikeup//24) > 5

            text = ''
            pokemonIncome = 0
            for item in cashIncome:
                if cashIncome[item] is None:
                    continue
                if cashIncome[item]['pastTense'] > 0:
                    pokemonIncome += int(cashIncome[item]['income'])
                    text += f'[{cashIncome[item]['name']}] принес(-ла): **`{cashIncome[item]['income']}`**\n'

            cashUser = round(random.randint(15, 120) * strikeMulti)
            cash = pokemonIncome + cashUser
            embed = disnake.Embed(description=f'### Вы заработали: `{cashUser}es`\n\n{text}\nОбщая прибыль: `+{cash}es`\n`Приходите позже!`', colour=disnake.Colour.dark_green())
            embed.set_footer(text=f'Вызвал: {ctx.author.name}.   Текущий стрик: {info[1]+1} = {strikeMulti}x')
            if db.Money(user=ctx.author.id, value=cash).add():
                if strikeup and not dropstrike: 
                    db.Poke(user=ctx.author.id).update(value=round(time.time()))
                    db.Poke(user=ctx.author.id).add(value=1)
                elif dropstrike:
                    db.Poke(user=ctx.author.id).update(value=round(time.time()))
                    db.Poke(user=ctx.author.id).update(value=0, time=False)
                db.Poke(user=ctx.author.id).update(value=14_400)
                await ctx.send(embed=embed)
            else: await ctx.send('Сообщите поню, я опять сломана')
        else:
            to_formated_time = db.Lock(user_id=ctx.author.id, slot=1).info()[0] - round(time.time())
            end_time = time.strftime('%H:%M:%S', time.gmtime(to_formated_time))
            embed = disnake.Embed(description=f'### Не торопитесь так сильно\n`приходите через: {end_time}`', colour=disnake.Colour.dark_red())
            embed.set_footer(text=f'Вызвал: {ctx.author.name}')
            
            message = await ctx.send(embed=embed)

            await closeEmbedMessageAfter(message, time=60)

    @commands.Cog.listener('on_button_click')
    async def loteryListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ['lotery_1', 'lotery_5', 'lotery_10', 'lotery_50']:
            return

        def weightRank(rank):
            order = {"?":-1,"EX":0, "S":1, "A":2, "B":3, "C":4, "D":5, "E":6, "F":7}
            return order[rank]
        async def bestRoll(count, best:bool):
            priceTiket = await GetTiketPrice(inter.author.id)
            data = await RollLotery(user=inter.author.id, count=count, priceTiket=priceTiket)

            text = ''
            SortedData = sorted(data['loot'], key=lambda x: weightRank(x[1]['rank']))
            DeleteDuplicate = {
                'add':{},
                'sell':{}
                }

            for item in SortedData:
                if item[3]:
                    if item[0] in DeleteDuplicate['sell']:
                        DeleteDuplicate['sell'][item[0]]['count'] += 1
                    else:
                        DeleteDuplicate['sell'][item[0]] = {
                            'poke':item[1],
                            'count':1
                            }
                else:
                    if item[0] in DeleteDuplicate['add']:
                        DeleteDuplicate['add'][item[0]]['count'] += 1
                    else:
                        DeleteDuplicate['add'][item[0]] = {
                            'poke':item[1],
                            'count':1
                            }

            text += f'```Добавлено в инвертарь```'

            for index, item in enumerate(DeleteDuplicate['add']):

                if index+1 == len(DeleteDuplicate['add']):
                    text += f'`({DeleteDuplicate['add'][item]['poke']['rank']}:{DeleteDuplicate['add'][item]['count']}x)|{DeleteDuplicate['add'][item]['poke']['name']}`\n'
                    continue

                text += f'`({DeleteDuplicate['add'][item]['poke']['rank']}:{DeleteDuplicate['add'][item]['count']}x) {DeleteDuplicate['add'][item]['poke']['name']}`, '
                
            if len(DeleteDuplicate['sell']) != 0:
                text += f'```Продано из-за ограничение: ```'

            for index, item in enumerate(DeleteDuplicate['sell']):

                if index+1 == len(DeleteDuplicate['sell']):
                    text += f'`({DeleteDuplicate['sell'][item]['poke']['rank']}:{DeleteDuplicate['sell'][item]['count']}x)|{DeleteDuplicate['sell'][item]['poke']['name']}`'
                    continue

                text += f'`({DeleteDuplicate['sell'][item]['poke']['rank']}:{DeleteDuplicate['sell'][item]['count']}x) {DeleteDuplicate['sell'][item]['poke']['name']}`, '
                
            else:
                if len(DeleteDuplicate['sell']) != 0:
                    text += f'\n\n**Возвращено по ставке 75%:** `+{data['sellIncome']}(es)`'

            embed = disnake.Embed(
                description=f"# ```Ты выиграл в лотереи...```\n{text}\n`{data['compliment']}`\n",
                colour=disnake.Colour.dark_gold()           
                )
            embed.set_footer(text=f'Вызвал: <{inter.author.name}> | Цена за тикет = <{priceTiket}>')

            await inter.response.edit_message(embed=embed, components=data['buttons'])

        if inter.component.custom_id == 'lotery_1':
            priceTiket = await GetTiketPrice(inter.author.id)
            data = await RollLotery(user=inter.author.id, priceTiket=priceTiket)
            loots = data['loot'][0]

            text = f"# ```Ты выиграл в лотереи...```\n## → {loots[1]['name']} `({loots[0]})`\n"
            if loots[3]: text += f'>20, Продан по ставке 75%: +`{data['sellIncome']}(es)`'
            text += f'`\n{data['compliment']}`'
            embed = disnake.Embed(
                description=text,
                colour=loots[2]           
                )
            embed.set_footer(text=f'Вызвал: <{inter.author.name}> | Цена за тикет = <{priceTiket}>')

            await inter.response.edit_message(embed=embed, components=data['buttons'])
        elif inter.component.custom_id == 'lotery_5':
            await bestRoll(count=5, best=False)
        elif inter.component.custom_id == 'lotery_10':
            await bestRoll(count=10, best=False)
        elif inter.component.custom_id == 'lotery_50':
            await bestRoll(count=50, best=True)
        
    @commands.command(name='lotery', aliases=['лотерея', 'гача'])
    async def lotery(self, ctx):

        try: userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        except: userEnter = None
        if userEnter in ['?', 'help']:
            Until.helpedUser(ctx, info='lotery')
            return
        else: del userEnter

        # TODO: Добавить использование билетов, если они есть, а также подтверждение, если недостающую часть будет догонятся деньгами.
        user = await userData(ctx.author.id)
        essence = user['money']['ESSENCE']
        priceTiket = await GetTiketPrice(ctx.author.id)
        if priceTiket*5 > essence >= priceTiket:
            data = await RollLotery(user=ctx.author.id, priceTiket=priceTiket)
            loots = data['loot'][0]

            embed = disnake.Embed(
                description=f"# ```Ты выиграл в лотереи...```\n# {loots[1]['name']} `(Rank: {loots[0]})`\n## `{data['compliment']}`\n",
                colour=loots[2]         
                )
            embed.set_footer(text=f'Крутил барабан: <{ctx.author.name}> | Цена за тикет = <{priceTiket}>')

            savePokemon(loot=data['loot'], uid=ctx.author.id)

            await ctx.send(embed=embed, components=data['buttons'])
        elif essence > priceTiket*5:
            user = await userData(ctx.author.id)
            essence = user['money']['ESSENCE']
            buttons = await checkButtonsLotery(essence=essence, priceTiket=priceTiket)

            embed = disnake.Embed(
                description=f"### Сколько желаете открыть?\nПри себе у вас ({await userHaveTicket(user=ctx.author.id)}) билетов, они используются первыми, а далее деньги.\n\n**1 билет:** `{priceTiket:,}`\n**5 билетов:** `{priceTiket*5:,}`\n**10 билетов:** `{priceTiket*10:,}`\n**50 билетов:** `{priceTiket*50:,}`",
                colour=disnake.Colour.dark_orange()
                )
            embed.set_footer(text=f'Вызвал: {ctx.author.name}')

            await ctx.send(embed=embed, components=buttons)
        else:
            embed = disnake.Embed(
                description=f'```Похоже у вас не хватает средств\nСтоимость 1 крутки для вас равна {priceTiket} шекелям.```',
                colour=disnake.Colour.dark_red()
                )
            embed.set_footer(text=f'Вызвал: <{ctx.author.name}?')
            await ctx.send(embed=embed)

    async def pokemon(self, ctx):
        try:
            with open(f'../PonyashkaDiscord/content/lotery/users_bag/{ctx.author.id}.json', 'r', encoding='UTF-8') as file:
                userBag = json.load(file)

            with open(f'../PonyashkaDiscord/content/lotery/lowLotery.json', 'r', encoding='utf-8') as file:
                load = json.load(file)
                loteryItem = load['items']
        except:
            embed = disnake.Embed(description='```Похоже вы не обладаете ни одним покемонов. Возможно вы даже ещё не играли в гачу-рулетку. Попробуйте.```')
            await ctx.send(embed=embed)
            return

        text = ''
        order = ["?", "EX", "S", "A", "B", "C", "D", "E", "F"]
        mapingPokemons = {}

        # text += f'`({countPet}) {randomPet['name']}` '
        # text += f'```{itemORD} - rank ```'

        for itemORD in order:
            for item in userBag:
                try: randomPet = userBag[item][choice(list(userBag[item].keys()))]
                except: continue
                countPet = len(userBag[item])

                if randomPet['rank'] != itemORD: continue

                if randomPet['rank'] in mapingPokemons:
                    card = {"name":randomPet['name'], "count":countPet}
                    mapingPokemons[randomPet['rank']].append(card)
                else:
                    mapingPokemons[randomPet['rank']] = [{"name":randomPet['name'], "count":countPet}]
                
        for rank in order:
            if rank not in mapingPokemons: continue

            text += f'```{rank} - rank ```'
            for poke in mapingPokemons[rank]:
                text += f'`({poke['count']}) {poke['name']}` '


        if text == '': text = '**У вас тут пусто. Даже перекати поля нет.**'
        embed = disnake.Embed(
            description=f"{text}"
            )
        embed.set_footer(text=f'Вызвал: {ctx.author.name}')
        message = await ctx.send(embed=embed)
        await closeEmbedMessageAfter(message, time=60)

    @commands.Cog.listener("on_button_click")
    async def craftListener(self, inter: disnake.MessageInteraction):
        check = ['essence_soul_cf', 'shard_soul_cf']
        for item in check:
            if inter.component.custom_id.startswith(item):break
        else: return
        component = inter.component.custom_id.split('|')[0]
        user = int(inter.component.custom_id.split('|')[1])
        value = int(inter.component.custom_id.split('|')[2])
        if user != inter.author.id:
            await inter.response.send_message('Данное взаимодействие не принадлежит вам.', ephemeral=True)
            return

        # Крафт осколков душ
        # Коэффициент 400 к 1
        if component == 'essence_soul_cf':
            # Проверка наличие указаных средств у пользователя
            check = db.Money(user=user).have()
            if value > check:
                embed = disnake.Embed(description='**Недостаточно средств**', color= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)
            # Основные преобразования по формуле
            # Число выпадающих шардов
            shardValue = value//400
            # Шанс дропа шардов
            chanceDrop = float('{:.3f}'.format(value / (value+200)))
            # Не больше 80%
            if chanceDrop > 0.8: chanceDrop = 0.800

            # Создание диапазона выпадающих шардов
            minDrop = int(shardValue * 0.7)
            if minDrop <= 0: minDrop = 1
            maxDrop = int(round(shardValue * 1.3))
            if maxDrop <= 1: maxDrop = 2
            lossEssence = int(value*0.8)
            # Сколько будет потеряно в случае неудачи
            if lossEssence <= 10: lossEssence = value
            # Рандоминг чисел. Шанса и числа шардов
            randomNum= float('{:.3f}'.format(random.random()))
            ShardDrop = random.randint(minDrop, maxDrop)

            if chanceDrop > randomNum:
                # Позитивный исход
                db.Money(user=user, currency='ESSENCE', value=value).sub()
                db.Money(user=user, currency='SHARD', value=ShardDrop).add()
                embed = disnake.Embed(
                    description='**Шанс выпадения : **ㅤ `[{:.1%}]`\n**Вы получили:**ㅤㅤㅤ`[{ShardDrop}]` осколок(-ов)'.format(chanceDrop, ShardDrop= ShardDrop),
                    color= disnake.Colour.green())
                return await inter.response.edit_message(embed=embed, components=None)
            else:
                # Негативный исход
                db.Money(user=user, currency='ESSENCE', value=lossEssence).sub()
                embed = disnake.Embed(
                    description='**Шанс выпадения : **ㅤ `[{:.1%}]`\n**Вы потеряли (80%):**ㅤ`[{lossEssence}]` эссенций'.format(chanceDrop, lossEssence= lossEssence),
                    color= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)
        # Крафт душ
        # Коэффициент 1200 к 1
        elif component == 'shard_soul_cf':
            # Проверка наличие указаных средств у пользователя
            check = db.Money(user=user, currency='SHARD').have()
            if value > check:
                embed = disnake.Embed(description='**Недостаточно средств**', colour= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)
            # Основные преобразования по формуле
            # Число выпадающих шардов
            soulValue = value//1200
            # Шанс дропа шардов
            chanceDrop = float('{:.3f}'.format(value / (value+300)))
            # Не больше 80%
            if chanceDrop > 0.6: chanceDrop = 0.600

            # Создание диапазона выпадающих шардов
            minDrop = int(soulValue * 0.5)
            if minDrop <= 0: minDrop = 1
            maxDrop = int(round(soulValue * 1.8))
            if maxDrop <= 1: maxDrop = 2
            lossShard = int(value*0.5)
            # Сколько будет потеряно в случае неудачи
            if lossShard <= 10: lossShard = value
            # Рандоминг чисел. Шанса и числа шардов
            randomNum= float('{:.3f}'.format(random.random()))
            soulValue = random.randint(minDrop, maxDrop)

            if chanceDrop > randomNum:
                # Позитивный исход
                db.Money(user=user, currency='SHARD', value=value).sub()
                db.Money(user=user, currency='SOUL', value=soulValue).add()
                embed = disnake.Embed(
                    description='**Шанс выпадения : **ㅤ `[{:.1%}]`\n**Вы получили:**ㅤㅤㅤㅤ`[{soulValue}]` душ'.format(chanceDrop, soulValue= soulValue),
                    color= disnake.Colour.green())
                return await inter.response.edit_message(embed=embed, components=None)
            else:
                # Негативный исход
                db.Money(user=user, currency='SHARD', value=lossShard).sub()
                embed = disnake.Embed(
                    description='**Шанс выпадения : **ㅤ `[{:.1%}]`\n**Вы потеряли (50%):**ㅤ`[{lossShard}]` осколков'.format(chanceDrop, lossShard= lossShard),
                    color= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)

    @commands.command(name='craft', aliases=['cfs', 'крафтдуш', 'создать'])
    async def craft(self, ctx):

        user = ctx.message.author.id
        db.Check(user_id=user, user_name=ctx.message.author.name).user()

        # Проверка на наличия числового значения
        try:
            value = abs(int(ctx.message.content.lower().split(' ')[1]))
        except:
            embed = disnake.Embed(description='**Не корректно указано количество, или вовсе не указано**', color= disnake.Colour.red())
            return await ctx.send(embed=embed)
        
        components = [
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, disabled=False, label='SH', custom_id=f'essence_soul_cf|{user}|{value}'),
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, disabled=False, label='SL', custom_id=f'shard_soul_cf|{user}|{value}')
            ]
        embed = disnake.Embed(title='Что желаете скрафтить?', description='\nSH = Осколки\nSL = Души')
        embed.set_footer(text=f'Вызвал: {ctx.author.name}')

        message = await ctx.send(embed=embed, components=components)

    @commands.Cog.listener('on_button_click')
    async def uncraftListener(self, inter: disnake.MessageInteraction):
        check = ['shard_break_uncf', 'soul_break_uncf', 'cristall_break_uncf', 'item_break_uncf']
        for item in check:
            if inter.component.custom_id.startswith(item):break
        else: return
        component = inter.component.custom_id.split('|')[0]
        user = int(inter.component.custom_id.split('|')[1])
        value = int(inter.component.custom_id.split('|')[2])
        if user != inter.author.id:
            await inter.response.send_message('Данное взаимодействие не принадлежит вам.', ephemeral=True)
            return

        def randomBreak() -> bool:
            randNum = random.randint(1, 100)
            if randNum >= 70: return False
            else: return True

        # Поломка валют
        # Коэффициент 400 к 1
        if component == 'shard_break_uncf':
            # Проверка наличие указаных средств у пользователя
            check = db.Money(user=user, currency='SHARD').have()
            if value > check:
                embed = disnake.Embed(description='**Недостаточно [SH] в кошельке**', color= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)
            # Основные преобразования по формуле
            # Число выпадающих шардов
            dropEssence = 0
            breakCount = 0
            for _ in range(value):
                if randomBreak(): 
                    dropEssence += random.randrange(10, 200, 10)
                else: breakCount += 1

            db.Money(user=user, currency='SHARD', value=value).sub()
            db.Money(user=user, currency='ESSENCE', value=dropEssence).add()
            embed = disnake.Embed(
                description=f'**Разрушение `{value}` [SH] принесло: `{dropEssence}es`**\n**Пустых осколков: `{breakCount}`**',
                color= disnake.Colour.green())
            embed.set_footer(text='Шанс неудачи стабилен: 30% на ед.')
            return await inter.response.edit_message(embed=embed, components=None)
        
        # Крафт душ
        # Коэффициент 1200 к 1
        elif component == 'soul_break_uncf':
            # Проверка наличие указаных средств у пользователя
            check = db.Money(user=user, currency='SOUL').have()
            if value > check:
                embed = disnake.Embed(description='**Недостаточно [SL] в кошельке**', color= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)
            # Основные преобразования по формуле
            # Число выпадающих шардов
            dropEssence = 0
            breakCount = 0
            for _ in range(value):
                if randomBreak(): 
                    dropEssence += random.randrange(10, 100, 5)
                else: breakCount += 1

            db.Money(user=user, currency='SOUL', value=value).sub()
            db.Money(user=user, currency='SHARD', value=dropEssence).add()
            embed = disnake.Embed(
                description=f'**Разрушение `{value}` [SL] принесло: {dropEssence}sh**\n**Пустых душ: `{breakCount}`**',
                color= disnake.Colour.green())
            embed.set_footer(text='Шанс неудачи стабилен: 30% на ед.')
            return await inter.response.edit_message(embed=embed, components=None)
            
        elif component == 'cristall_break_uncf':
            # Проверка наличие указаных средств у пользователя
            check = db.Money(user=user, currency='CRISTALL_SOUL').have()[4]
            if value > check:
                embed = disnake.Embed(description='**Недостаточно [CSL] в кошельке**', color= disnake.Colour.red())
                return await inter.response.edit_message(embed=embed, components=None)
            # Основные преобразования по формуле
            # Число выпадающих шардов
            dropEssence = 0
            breakCount = 0
            for _ in range(value):
                if randomBreak(): 
                    dropEssence += random.randrange(10, 50, 1)
                else: breakCount += 1

            db.Money(user=user, currency='CRISTALL_SOUL', value=value).sub()
            db.Money(user=user, currency='SOUL', value=dropEssence).add()
            embed = disnake.Embed(
                description=f'**Разрушение `{value}` [CSL] принесло: `{dropEssence}sl`**\n**Пустых кристальных душ: `{breakCount}`**',
                color= disnake.Colour.green())
            embed.set_footer(text='Шанс неудачи стабилен: 30% на ед.')
            return await inter.response.edit_message(embed=embed, components=None)
        
        elif component == 'item_break_uncf':
           pass

    @commands.command(name='uncraft', aliases=['unc', 'сломать', 'разломать', 'разбор', 'переработать'])
    async def uncraft(self, ctx):
        user = ctx.message.author.id
        db.Check(user_id=user, user_name=ctx.message.author.name).user()

        # Проверка на наличия числового значения
        try:
            value = abs(int(ctx.message.content.lower().split(' ')[1]))
        except:
            embed = disnake.Embed(description='**Не корректно указано количество, или вовсе не указано**', color= disnake.Colour.red())
            return await ctx.send(embed=embed)
        
        components = [
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, disabled=False, label='SH', custom_id=f'shard_break_uncf|{user}|{value}'),
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, disabled=False, label='SL', custom_id=f'soul_break_uncf|{user}|{value}'),
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, disabled=False, label='CSL', custom_id=f'cristall_break_uncf|{user}|{value}')
            ]
        embed = disnake.Embed(title='Что желаете разрушить?', description='\nSH = Осколки\nSL = Души\nCSL = Кристальные души')

        message = await ctx.send(embed=embed, components=components)

    @commands.command(name='sellpoke', aliases=['продать', 'slp'])
    async def sellpoke(self, ctx):
        # Одиночная продажа имеет флаги: all, по стандарту one
        # Без подтверждения действия о продажи всех покемонов

        # Продажа по рангам, переделать, да и просто починить, дабы можно было продать несколько рангов
        # Выскакивает подтверждение на действие с описанием, что будут проданы все покемоны, а те, что работают из этого ранга, будут сняты

        name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        ranksToSell = ['?', 'EX', 'S', 'A', 'B', 'C', 'D', 'E', 'F']
        pokemonsList = name.split(', ')

        userBag = await giveUserBag(user=ctx.author.id)

        # Функция для удаления работающего покемона из списка работающих
        # Первая грубая, смотрящая только на название покемона, вторая деликатная, смотрящая ещё и на зарабаоток
        def injectWorkFile(user, pokemon):
            with open(f'../PonyashkaDiscord/content/lotery/user_pet_in_work/{user}.json', 'r', encoding='UTF-8') as file:
                userWorkPoke = json.load(file)
            for item in userWorkPoke:
                try:
                    if userWorkPoke[item]['name'] == pokemon['name']:
                        userWorkPoke[item] = None
                except: pass

        errorsInput = []
        endSelled = []
        # endSelled = (commandToSell, sellValueList, pokeHowSell)

        async def mainSellFunc(mass:bool, pokemonName):
            if type(pokemonName) == list:
                pokemon = pokemonName[0]
            else: pokemon = pokemonName

            if '-all' in pokemon or mass: flag = 'all'
            else: flag = 'one'
            pokemon = pokemon.split(' -')[0]

            rankSell = True
            if pokemon.upper() in ranksToSell: 
                rankSell = False

            else:
                pokemonID = await findID_PokemonInDB_LikeName(PokemonName=pokemon)
                if pokemonID is None:
                    if not mass:
                        errorsInput.append(pokemon)
                        return False
                    else:
                        errorsInput.append(pokemon)
                        return False

            
            if rankSell:
                # Когда указывается название покемона
                if flag == 'all':
                    # Флаг на продажу всех типов этого покемона
                    # Поиск реальности существования данного покемона
                    pokemonID = await findID_PokemonInDB_LikeName(PokemonName=pokemon)
                    
                    try: 
                        # Получение пользовательского инветаря
                        userBagPoke = userBag[pokemonID]
                        # Количество тамошних покемонов и временная переменная для продажи
                        count = len(userBagPoke)
                        timesSelled = 0
                        associate = []
                        for item in userBagPoke:
                            associate.append(item)
                        # Прочесывание стоимости
                        for item in userBagPoke:
                            timesSelled += userBagPoke[item]['curr']['price'] * 0.75
                            injectWorkFile(user=ctx.author.id, pokemon=userBagPoke[item])
                        else:
                            pokeHowSell = userBagPoke[random.choice(associate)]['name']
                        
                        commandToSell = True
                        sellValueList = (timesSelled, count)

                        del userBag[pokemonID]
                        endSelled.append((commandToSell, sellValueList, pokeHowSell, (False, None), (False, None)))
                    except:
                        pokesWhatWannaSell = await findMap_PokemonInDB_LikeID(ID=pokemonID)
                        endSelled.append((False, (0, 0), pokesWhatWannaSell['name'], (False, None), (False, None)))
                    await saveBagUserFile(userBag, ctx.author.id)
                if flag == 'one':
                    # Флаг на продажу одного покемона из этого типа.
                    # 1. Через view пользователь выбирает покемона.
                    # 2. Через флаг слеш указывается ids. <name>/<count>
                    # Поиск реальности существования данного покемона
                    # input -> rank
                    pokemonID = await findID_PokemonInDB_LikeName(PokemonName=pokemon)
                    rank = (await findMap_PokemonInDB_LikeID(ID=pokemonID))['rank']

                    options = []
                    userBagPoke = userBag[pokemonID]

                    for index, item in enumerate(userBagPoke):
                        options.append(
                            disnake.SelectOption(
                                label=f'({index+1}) {userBagPoke[item]['name']} ({userBagPoke[item]['curr']['price']} es)',
                                value=f'poke|{index+1}|{pokemonID}-{item}|{userBagPoke[item]['curr']['price']}'
                                )
                            )
                    else:
                        options.append(
                            disnake.SelectOption(
                                label=f'Отменить продажу',
                                value=f'cannelSell|null|null|999999999999999999'
                                )
                            )
                    options.sort(key=lambda x: int(x.value.split('|')[3]), reverse=True)
                    
                    view = SelectMassPokemonsViewCorrectSell(options=options, user=ctx.author.id)
                    embed = disnake.Embed(description='**Выберите из списка ваших покемонов, того что желаете продать.**').set_footer(text='Для продажи всех, одного типа, используйте флаг [-all]')
                    await ctx.send(embed=embed, view=view)
                    return True
                return False
            else:
                # Когда указывается ранг который надо продать
                pokemonRank = pokemon.upper()
                
                userBagPokes = []
                ids = []
                for item in userBag:
                    if userBag[item][choice(list(userBag[item].keys()))]['rank'] == pokemonRank: 
                        userBagPokes.append(userBag[item])
                        ids.append(item)


                if not userBagPokes:
                    endSelled.append((False, 0, None, (True, pokemon), (False, None)))
                    return False

                commandToSell = True

                timesSelled = 0
                for item in userBagPokes:
                    for pokes in item:
                        pricePokes = item[pokes]['curr']['price']

                        injectWorkFile(user=ctx.author.id, pokemon=item[pokes])
                        try:
                            timesSelled += round(pricePokes * 0.75)
                        except:
                            print(pricePokes, item[pokes]['name'])

                else:
                    sellValueList = (timesSelled, len(userBagPokes)-1)
                    commandToSell = True
                    endSelled.append((commandToSell, sellValueList, None, (False, None), (True,pokemon)))
                    for item in ids:
                        del userBag[item]
                    await saveBagUserFile(userBag, ctx.author.id)
        # В целом, скорей всего есть более элегантное решение, но мне так похуй. Лень искать, да и время жмёт.
        # Удачи будущему мне эту хуйню пытаться улучшать, для чего-то кардинально нового
        if len(pokemonsList) == 1:
            viewStart = await mainSellFunc(mass=False, pokemonName=name)
            if viewStart: return

        else:
            # Когда через запятую перечисляют ранги или покемонов
            # Проверок на продажу нет, кроме вопроса о подтверждении действия
            # Попытаться реализовать, что с рангом можно указать и название, а это будет работать
            # Мысль: Через реализацию функций из блока if == 1   
            for item in pokemonsList:
                await mainSellFunc(mass=True, pokemonName=item)

        # endSelled = (commandToSell, sellValueList, pokeHowSell, rankSelledUser, UnknowEnter, rankedSelect)
        text = ''
        endSummGain = 0
        count = 0

        for nums in endSelled:
            if nums[0]:
                endSummGain += nums[1][0]
                count += nums[1][1]
        if endSummGain != 0:
            db.Money(user=ctx.author.id, value=round(endSummGain)).add()

        for index, item in enumerate(endSelled):
            
            if item[0] and not item[4][0]:

                if item[1][1] > 1: endWords = ['и', 'ы']
                else: endWords = ['', '']

                text += f'✔ **Покемон{endWords[1]} [{item[2]}] был{endWords[0]} продан{endWords[1]} за `{round(item[1][0]):,}`es** ({item[1][1]} шт)\n'

            elif item[0] and item[4][0]:
                text += f'✔ **Покемоны ранга [{item[4][1].upper()}] проданы за `{round(item[1][0]):,}`es** ({item[1][1]} вид(-ов))\n'

            elif not item[0] and item[3][0]:
                text += f'❌ **У вас нет покемонов из ранга [{item[3][1]}].**\n'

            else:
                text += f'❌ **Вы не обладаете [{item[2]}].**\n' 

        else:
            if len(errorsInput) != 0: text += '\n'
            for item in errorsInput:
                text += f'❓ **Ошибочный или неверный ввод:** [{item}]\n'
        if endSummGain > 0:
            text += f'\n💰 _Общая выгода продажи: **`{endSummGain:.0f}`**es_'

        embed = disnake.Embed(
            description=text
            ).set_footer(text='Покемоны продаются за 75% от стоимости')
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener('on_button_click')
    async def setpokeListener(self, inter: disnake.MessageInteraction):
        check = ['selectWorkSlot-1', 'selectWorkSlot-2', 'selectWorkSlot-3']
        for item in check:
            if inter.component.custom_id.startswith(item):break
        else: return
        
        slot, rareCOM, user = inter.component.custom_id.split('|')

        if int(user) != inter.author.id: 
            await inter.response.send_message('Вызовите свою команду', ephemeral=True)
            return  
        
        slotID = slot.split('-')[1]
        embed = disnake.Embed(description=f'### Вы установили покемона на работу в {slotID} слот')
        check = await setWorkPokemon(rankCOM=rareCOM, user=int(user), slot=int(slotID))

        if not check: await inter.response.send_message(ephemeral=True, content='Только уникальные виды покемонов.\nЛибо вы можете переназначить уже работающего, на более продуктивного.')
        else: await inter.response.edit_message(embed=embed, components=None)

    @commands.command(name='setpokework', aliases=['датьроботу', 'упрячь', 'поставить', 'spw'])
    async def setpokework(self, ctx):
        # Проверка значения
        try: 
            # Введенные данные от пользователя
            enterMessage = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
            # попытка поиска, через введенное имя покемона
            foundPoke, ids = await findMap_PokemonInDB_LikeName(name=enterMessage)
            # Получение данных о боевой группе пользователя
            fightPoke = await takeFightGroup(ctx.author.id)
        except:
            print(enterMessage)
            # Исключение извещающее о отсутствии покемона или ошибке 
            embed = disnake.Embed(description='**Не указано имя покемона или его ID**') 
            await ctx.send(embed=embed)
            return
        
        # Наличие покемна у человека
        userBag = await giveUserBag(user=ctx.author.id)
        try:
            poke = userBag[ids]
        except:
            embed = disnake.Embed(description='**Вы не обладаете данным покемоном**') 
            await ctx.send(embed=embed)
            return
        
        # Получение рабочего стака покемонов у человека
        workPoke, cashIncome = await getWorkPokemon(user=ctx.author.id, sys=False)

        text = ''
        for index, item in enumerate(workPoke):
            income = cashIncome[item]

            if not workPoke[item]:
                text += f'### `{index+1}`: `Пустой слот`\n'
                continue

            try: text += f'### `{index+1}`: `{workPoke[item]['name']}` `({workPoke[item]['cashIncome']:,}/h)`\n'
            except: text += f'### `{index+1}`: `{workPoke[item]['name']}` `({income['income']})`\n'
            
        else:
            text += f'\n\n-# Нажмите на кнопку, для завершения'

        embed = disnake.Embed(
            title='На какое место желаете посадить покемона?',
            description=text,
            colour=disnake.Colour.fuchsia()
            )
        embed.set_footer(text=f'Вызвал: {ctx.author.name}. ')

        if foundPoke['rank'] == '?':
            embed = disnake.Embed(description='Покемонов ранга [?] нельзя использовать для работы.')
            await ctx.send(embed=embed)
            return
        
        # buttons = [
        #     disnake.ui.Button(style=disnake.ButtonStyle.gray, label='1', custom_id=f'slot_1|{pokeID}|{ctx.author.id}'),
        #     disnake.ui.Button(style=disnake.ButtonStyle.gray, label='2', custom_id=f'slot_2|{pokeID}|{ctx.author.id}'),
        #     disnake.ui.Button(style=disnake.ButtonStyle.gray, label='3', custom_id=f'slot_3|{pokeID}|{ctx.author.id}')
        #     ]

        text = 'Учтите, что пока покемон работает, его нельзя отправить сражаться.'
        embed = disnake.Embed(
            title='Кого вы бы хотели отправить работать?',
            description=text
            )

        options = []
        for index, item in enumerate(poke):
            options.append(
                disnake.SelectOption(
                    label=f'({index+1}) {poke[item]['name']} ({poke[item]['curr']['income']}/h)',
                    value=f'poke|{index+1}|{poke[item]['curr']['income']}|{ids}-{item}'
                    )
                )
        options.sort(key=lambda x: int(x.value.split('|')[2]), reverse=True)
        view = SelectMassPokemonsViewWorkGroup(options=options, user=ctx.author.id)

        await ctx.send(embed=embed, view=view)

    @commands.command(name='lookdivpoke', aliases=['pokediv', 'осмотрпокемонов', 'осмотрработы', 'ld', 'покеработа'])
    async def lookDivPoke(self, ctx):
        
        workPoke, cashIncome = await getWorkPokemon(user=ctx.author.id, sys=False)
        text = ''
        for index, item in enumerate(workPoke):
            timeStruct = time.gmtime(round(time.time())-workPoke[item]['time'])
            times = time.strftime(f'{timeStruct[2]-1}:%H:%M:%S', timeStruct)
            if not workPoke[item]:
                text += f'### ** `{index+1}`: `Пустой слот`**\n| —\n'
                continue
            income = cashIncome[item]
            text += f'### **`{index+1}`**: **`{income['name']}`** **`({workPoke[item]['cashIncome']:,}/h)`**\n| Собрано: `({income['income']})`\n| С последнего сбора: `({times})`\n'
        else:
            text += f'-# _Для сбора используйте команду !work._\nМаксимальный порог сбора: 10 часов'

        embed = disnake.Embed(
            description=text,
            colour=disnake.Colour.fuchsia()
            )
        embed.set_footer(text=f'Вызвал: {ctx.author.name}. ')
        await ctx.send(embed=embed)

    @commands.command(name='look', aliases=['l', 'осмотр'])
    async def look(self, ctx):
        # TODO: Сделать дополнительную возможность на просмотр навыков, характеристик и эффектов
        try:
            name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
            try: 
                foundPoke, rare = await findMap_PokemonInDB_LikeName(name=name)

            except: 
                embed = disnake.Embed(description='**Возможно где-то ошибка в названиии.**')
                await ctx.send(embed=embed)
                return

            try: crafteble = 'Да' if foundPoke['crafteble'] else 'Нет'
            except: crafteble = 'Неизвестно'

            try: desc = random.choice(foundPoke['description'])
            except: desc = '-Отсутсвует-'

            try: gif = foundPoke['gif']
            except: gif = None

            def sizeStat(stat):
                return (foundPoke['params'][stat][0]+foundPoke['params'][stat][1])/2

            priceText = f'**`Ценообразование:`**\n- Цена от _`{foundPoke['price'][0]:,}(es)`_ до _`{foundPoke['price'][1]:,}(es)`_\n- Доход от _`{foundPoke['income'][0]:,}(es/h)`_ до _`{foundPoke['income'][1]:,}(es/h)`_'
            pokeStats = f'**`Характиристики (среднее):`**\n- Здоровье: {sizeStat('healpoint'):.0f} ({sizeStat('regen'):.0f}/h)\n- Атака: {sizeStat('attack'):.0f}\n- Броня: {sizeStat('armor'):.0%}\n- Уклонение: ({sizeStat('evasion'):.0%})\n- Скорость: {1/foundPoke['params']['speed'][1]:.1f}x-{1/foundPoke['params']['speed'][0]:.1f}x'

            embed = disnake.Embed(
                title=f'[{foundPoke['name']}]|[ID:{rare}]|[Rare:{foundPoke['rank']}]',
                description=f'**`Описание:`**\n{desc}\n\n{priceText}\n\n{pokeStats}',
                )
            embed.set_thumbnail(url=gif)
            embed.set_footer(text=f'Возможность крафта: {crafteble}')
            await ctx.send(embed=embed)
            return
        except:
            embed = disnake.Embed(description='### Либо такого предмета - `нет`, либо вы неправильно написали его `название`.')
            await ctx.send(embed=embed)
            return

    @commands.Cog.listener('on_button_click')
    async def lookBagListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ['lb_next', 'lb_back', 'lb_dropStat']:
            return
        
        try:
            with open('../PonyashkaDiscord/config/lookBags.json', encoding='UTF-8') as file:
                stat_list = json.load(file)

            mess = stat_list[f'{inter.message.id}']

            if mess['author'] != inter.author.id:
                await inter.response.send_message('`Отказано в доступе. Вы не являетесь автором вызова.`', ephemeral=True)
                return
            
            if inter.component.custom_id == 'lb_next':
                if mess['index']+1 > len(mess['embeds']):
                    await inter.response.defer()
                    return
                mess['index']+= 1
                await inter.response.edit_message(embed=disnake.Embed.from_dict(mess['embeds'][f'{mess['index']}']))
            elif inter.component.custom_id == 'lb_back':
                if mess['index']-1 <= 0:
                    await inter.response.defer()
                    return
                mess['index']-= 1
                await inter.response.edit_message(embed=disnake.Embed.from_dict(mess['embeds'][f'{mess['index']}']))
            elif inter.component.custom_id == 'lb_dropStat':
                embed = disnake.Embed(title='Информация',description='```Окно закрыто пользователем.```')
                await inter.response.edit_message(embed=embed, components=None)
                return
            
            with open('../PonyashkaDiscord/config/lookBags.json', mode='w', encoding='UTF-8', ) as file:
                file.write(json.dumps(stat_list, indent=3, ensure_ascii=False))
        except:
            embed = disnake.Embed(title='Информация',description='```Активно иное окно.```')
            await inter.response.edit_message(embed=embed, components=None)

    @commands.command(name='lookbag', aliases=['lb', 'петы', 'покемоны', 'poke'])
    async def lookBag(self, ctx):

        name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        name = name.split('GOOD')

        try: names, seq = name[0].split('=')
        except: names = name[0] 

        print(names)

        PokeID = await findID_PokemonInDB_LikeName(PokemonName=names)
        if name == ctx.message.content.split(' ')[0] or PokeID is None:
            await self.pokemon(ctx)
            return

        userBag = await giveUserBag(user=ctx.author.id)
        try: 
            poke = HPupdate(userBag[PokeID][seq], ctx.author.id)
        except: poke = False


        if poke:

            pokesEXPneed = pokesToNextLvLExp(rank=poke['rank'], lvl=poke['other_param']['lvl'])

            lvls = ''
            tump = ''

            if pokesEXPneed <= poke['other_param']['exp']: 
                tump = ' **(N-UP)**'
            if int(poke['other_param']['lvl']) >= 25: 
                lvls = ' **(MAX)**'
                tump = ' **(MAX)**'

            mainInfo = f'**`Основное`**\n- Ранг: `[{poke['rank']}]`\n- Уровень: `[{poke['other_param']['lvl']}]`{lvls}\n- Опыт: `[{poke['other_param']['exp']:,}/{pokesEXPneed:,}]`{tump}\n- Поддержек: `[{poke['other_param']['supports']}]`\n- Усиление от поддержек: `[{poke['other_param']['supports_percent_up']:.0%}]`'

            priceText = f'**`Ценообразование:`**\n- Цена: `{poke['curr']['price']:,}(es)`\n- Доход: `{poke['curr']['income']:,}(es/h)`'

            pokeStats = f'**`Характиристики:`**\n- Здоровье: `[{poke['other_param']['healpoint_now']}/{poke['params']['healpoint']:.0f}]`\n- Регенерация: `[{poke['params']['regen']:.0f}]/h`\n- Атака: `[{poke['params']['attack']:.0f}]` (±20%)\n- Броня: `[{poke['params']['armor']:.0%}]`\n- Уклонение: `[{poke['params']['evasion']:.0%}]`\n- Скорость: `[{1/poke['params']['speed']:.1f}x]`'

            text = f'{mainInfo}\n\n{priceText}\n\n{pokeStats}'
            embed = disnake.Embed(
                title=f'[ {poke['name']} ]|[ ID:{PokeID} ]|[ Seq:{seq} ]',
                description=text
                )
            message = await ctx.send(embed=embed)
            await closeEmbedMessageAfter(message, time=60)

            return

        try: pokes = userBag[PokeID]
        except:
            await ctx.send(embed=disnake.Embed(description='**Похоже вы не обладаете данным типом покемонов**'))
            return
        listsEmbed = {}

        keyses = list(pokes.keys())
        chunk = list(chunks(keyses, 5))

        for i, chu in enumerate(chunk):
            text = ''
            ran = 0
            for item in chu:
                pok = HPupdate(pokes[item], ctx.author.id)
                text += f'**- - (Seq: {item})**| Уровень: `[{pok['other_param']['lvl']}]`|`[{pok['other_param']['exp']}/{pokesToNextLvLExp(rank=pok['rank'], lvl=pok['other_param']['lvl'])}]`\n| Здоровье: `[{pok['other_param']['healpoint_now']}/{pok['params']['healpoint']:.0f}]`\n| Поддержек: `[{pok['other_param']['supports']}]`\n'
                ran += 1
                if ran == 5: break
            listsEmbed[f"{i+1}"] = {
                    "title":f'[ {pokes[choice(list(pokes.keys()))]['name']} ]|[ ID:{PokeID} ]', 
                    "description":text,
                    "footer":{"text":f"Страница: {i+1}"}
                    }
        if (len(list(pokes.keys()))//5)+1 > 1:
            buttons = [
                disnake.ui.Button(style=disnake.ButtonStyle.gray, label='←', custom_id='lb_back'),
                disnake.ui.Button(style=disnake.ButtonStyle.gray, label='→', custom_id='lb_next'),
                disnake.ui.Button(style=disnake.ButtonStyle.red, label='✖', custom_id='lb_dropStat')
                ]
        else: buttons = None

        message = await ctx.send(embed=disnake.Embed.from_dict(listsEmbed['1']), components=buttons)
        
        await closeEmbedMessageAfter(message, time=60)

    #? pokemon fight between player
    @commands.Cog.listener('on_button_click')
    async def fightPokeAcceptSystem(self, inter: disnake.MessageInteraction):
        acc = ['fip1', 'fip2']
        for item in acc:
            if inter.component.custom_id.startswith(item): break
        else: return
        comm, user, user2, interact = inter.component.custom_id.split('|')

        try:
            users = f'{user}-{user2}'
            with open(f'../PonyashkaDiscord/content/lotery/fight/{users}.json', 'r', encoding='utf-8') as file:
                fightMap = json.load(file)
        except:
            users = f'{user2}-{user}'
            with open(f'../PonyashkaDiscord/content/lotery/fight/{users}.json', 'r', encoding='utf-8') as file:
                fightMap = json.load(file)

        for item in fightMap:
            if int(fightMap[item]['idp']) == int(inter.author.id) and inter.author.id == int(interact):
                fightMap[item]['ready'] = not fightMap[item]['ready']
                if item[-1] == '1':
                    await fightButtonsUpdateGetReady(inter.message, p1=fightMap[item]['ready'])
                if item[-1] == '2':
                    await fightButtonsUpdateGetReady(inter.message, p2=fightMap[item]['ready'])
        with open(f'../PonyashkaDiscord/content/lotery/fight/{users}.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(fightMap, indent=3, ensure_ascii=False))
        
        if fightMap['p1']['ready'] and (fightMap['p2']['ready'] or fightMap[item]['bot']):
            if fightMap[item]['bot']:
                embed = disnake.Embed(description='**Бой против [бота] начинается.**')
            else:
                embed = disnake.Embed(description='**Бой между [игроками] начинается.**')
            await inter.response.edit_message(embed=embed, components=None)
            await startFight(message=inter.message, users=users, mulp=(user, user2))
            return
        await inter.response.defer()

    @commands.command(name='fightpoke', aliases=['fip', 'сражение', 'боп'])
    async def fightPoke(self, ctx: disnake.ext.commands.Context):

        checkFight = await checkInFightStatus(uid=ctx.author.id)
        if checkFight:
            await ctx.send(embed=disnake.Embed(description='**Ой! Похоже вы находитесь в бою!**\n**Во время боя нельзя начинать другой бой.**'))
            return
        

        try:
            opponent = ctx.message.mentions[0]
        except:
            embed = disnake.Embed(description='Не выбран соперник, упомяните его после команды.')
            await ctx.send(embed=embed)
            return

        if opponent.id == ctx.author.id:
            embed = disnake.Embed(description='Ты не можешь сразиться сам с собой.')
            await ctx.send(embed=embed)
            return

        try:
            with open(f"../PonyashkaDiscord/content/lotery/fightPet/{ctx.author.id}.json", 'r', encoding='utf-8') as file:
                loadPokeUser = json.load(file)
        except:
            embed = disnake.Embed(description='**У вас даже не настроена боевая группа.**')
            await ctx.send(embed=embed)
            return
        
        if not opponent.bot:
            try:
                with open(f"../PonyashkaDiscord/content/lotery/fightPet/{opponent.id}.json", 'r', encoding='utf-8') as file:
                    loadPokeOppenent = json.load(file)
            except:
                embed = disnake.Embed(description='**У вызванного пользователя не организована боевая группа.**')
                await ctx.send(embed=embed)
                return

        countUserPokeFught = 0
        countOpponentPokeFight = 0
        for item in loadPokeUser:
            pass


        #! Потом удалить
        userBag = await giveUserBag(user=ctx.author.id)


        # TODO: Исключить возможность поняшки выбирать, выбранные игроком покемонов, и повторять выбор

        if opponent.bot:
            randomPoke = []
            for index in range(3):
                ids = choice(list(userBag.keys()))
                pok = userBag[ids][choice(list(userBag[ids].keys()))]
                randomPoke.append(pok)

        if opponent.bot: 
            fightMap = {
                "p1":{
                    "idp":ctx.author.id,
                    "name":ctx.author.name,
                    "ready":False,
                    "bot":False,

                    "pokemons":{
                        'slot1':loadPokeUser['slot1'],
                        'slot2':loadPokeUser['slot2'],
                        'slot3':loadPokeUser['slot3']
                        }
                    },
                "p2":{
                    "idp":opponent.id,
                    "name":opponent.name,
                    "ready":False,
                    "bot":opponent.bot,

                    "pokemons":{
                        'slot1':randomPoke[0],
                        'slot2':randomPoke[1],
                        'slot3':randomPoke[2]
                        }
                    }            
                }
        else:
            fightMap = {
                "p1":{
                    "idp":ctx.author.id,
                    "name":ctx.author.name,
                    "ready":False,
                    "bot":False,

                    "pokemons":{
                        'slot1':loadPokeUser['slot1'],
                        'slot2':loadPokeUser['slot2'],
                        'slot3':loadPokeUser['slot3']
                        }
                    },
                "p2":{
                    "idp":opponent.id,
                    "name":opponent.name,
                    "ready":False,
                    "bot":opponent.bot,

                    "pokemons":{
                        'slot1':loadPokeOppenent['slot1'],
                        'slot2':loadPokeOppenent['slot2'],
                        'slot3':loadPokeOppenent['slot3']
                        }
                    }            
                }
        # Счетчик на проверку валидности боевой группы.
        NoneCount = 0
        # Описание загрузки тектового оформления первого игрока
        summCP1 = 0
        FGP1 = ''
        for index, item in enumerate(loadPokeUser):
            opp = await giveUserBag(user=ctx.author.id)
            try:

                ids, seq = loadPokeUser[f'slot{index+1}'].split('-')
                cp = calculateCP(opp[ids][seq])
                FGP1 += f'| **`[ БМ: {reduct(cp)} ]|[ {opp[ids][seq]['name']} ]`**\n'

                summCP1 += round(cp)

            except: 
                NoneCount += 1
                FGP1 += f'| **`[ None ]`**\n'
        
        #TODO: Позже подумать о подключении конфигурационных файлов
        if NoneCount == 3:
            embed = disnake.Embed(description='**Ваша боевая группа не содержит боевых покемонов.**')
            await ctx.send(embed=embed)
            return
        
        # Счетчик на проверку валидности боевой группы.
        NoneCount = 0
        # Описание загрузки информации второго игрока на первую страницу
        summCP2 = 0
        if opponent.bot:
            # Описание алгоритма для бота
            FGP2 = ''
            for item in randomPoke:
                cp = calculateCP(item)
                FGP2 += f'| **`[ БМ: {reduct(cp)} ]|[ {item['name']} ]`**\n'

                summCP2 += round(cp)
        else:
            # Описание алгоритма для живого игрока
            FGP2 = ''
            for index, item in enumerate(loadPokeOppenent):
                opp = await giveUserBag(user=opponent.id)
                try:

                    ids, seq = loadPokeOppenent[f'slot{index+1}'].split('-')
                    cp = calculateCP(opp[ids][seq])
                    FGP2 += f'| **`[ БМ: {reduct(cp)} ]|[ {opp[ids][seq]['name']} ]`**\n'

                    summCP2 += round(cp)

                except: 
                    NoneCount += 1
                    FGP2 += f'| **`[ None ]`**\n'
        
        if NoneCount == 3:
            embed = disnake.Embed(description='**Боевая группа опонента не содержит боевых покемонов в составе.**')
            await ctx.send(embed=embed)
            return
        
        # PreStart call to accept fight
        text = f'## Готовы ли игроки к бою?\n### Первый игрок (БМ: {summCP1}): \n**[P1]** — `{ctx.author.name}`\n{FGP1}'
        buttonsPlayer = [
            disnake.ui.Button(style=disnake.ButtonStyle.red, label=f'P1', custom_id=f'fip1|{ctx.author.id}|{opponent.id}|{ctx.author.id}'),
            ]
        
        if opponent.bot:
            buttonsPlayer.append(disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'P2', custom_id=f'fip2|{ctx.author.id}|{opponent.id}|{opponent.id}', disabled=True))
            text += f'### Второй игрок (БМ: {summCP2}): \n**[БОТ]|[P2]** — `{opponent.name}`\n{FGP2}'
        else:
            buttonsPlayer.append(disnake.ui.Button(style=disnake.ButtonStyle.red, label=f'P2', custom_id=f'fip2|{ctx.author.id}|{opponent.id}|{opponent.id}'))
            text += f'### Второй игрок (БМ: {summCP2}): \n**[P2]** — `{opponent.name}`\n{FGP2}'

        embed = disnake.Embed(description=text)
        
        try:
            with open(f'../PonyashkaDiscord/content/lotery/fight/{opponent.id}-{ctx.author.id}.json', 'r', encoding='utf-8') as file: pass
            
            with open(f'../PonyashkaDiscord/content/lotery/fight/{opponent.id}-{ctx.author.id}.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(fightMap, indent=3, ensure_ascii=False))

        except:
            with open(f'../PonyashkaDiscord/content/lotery/fight/{ctx.author.id}-{opponent.id}.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(fightMap, indent=3, ensure_ascii=False))
            
        
        await ctx.send(embed=embed, components=buttonsPlayer)

    @commands.Cog.listener('on_button_click')
    async def setFightGroupLictener(self, inter: disnake.MessageInteraction):
        trustList = ['selectFightSlot-1', 'selectFightSlot-2', 'selectFightSlot-3']
        for item in trustList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, rankCOM, user = inter.component.custom_id.split('|')
        _, slot = comm.split('-')
        ids, seq = rankCOM.split('-')
        userBag = (await giveUserBag(int(user)))[ids][seq]

        if int(user) != inter.author.id: 
            await inter.response.defer()
            return
        
        await saveFightGroup(user=user, rankCOM=rankCOM, slot=slot)
        embed = disnake.Embed(description=f'**Покемон [{userBag['name']}] был установлен в {slot} слот**')

        await inter.response.edit_message(embed=embed, components=None)

    @commands.command(name='setfightgroup', aliases=['sfg', 'угу', 'установкабоеваягруппа'])
    async def setFightGroup(self, ctx):
        
        checkFight = await checkInFightStatus(uid=ctx.author.id)
        if checkFight:
            await ctx.send(embed=disnake.Embed(description='**Ой! Похоже вы находитесь в бою!**\n**Во время боя нельзя изменять боевую группу.**'))
            return
        

        # Проверка значения
        try: 
            # Введенные данные от пользователя
            enterMessage = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')

            try: 
                # первая попытка поиска, через введенное имя покемона
                foundPoke, rare = await findMap_PokemonInDB_LikeName(name=enterMessage)

            except: 
                # Вторая попытка нахождения покемона через индитификатор покемона Rank-num
                foundPoke = await findMap_PokemonInDB_LikeID(ID=enterMessage)
                rare = enterMessage.split('-')

            # Получение данных о боевой группе пользователя
            fightPoke = await takeFightGroup(ctx.author.id)
        except:
            # Исключение извещающее о отсутствии покемона или ошибке 
            embed = disnake.Embed(description='**Не указано имя покемона или его ID**') 
            await ctx.send(embed=embed)
            return

        #? Если введен конкретный адресс покемона, то сразу переходить к установки его в слот, при прохождении условий

        # Наличие покемона у человека
        userBag = await giveUserBag(user=ctx.author.id)
        try:
            poke = userBag[rare]
        except:
            embed = disnake.Embed(description='**Вы не обладаете данным покемоном**') 
            await ctx.send(embed=embed)
            return
        
        text = '**Выберите покемона из списка, которого бы вы хотели установить в боевую группу**'
        embed = disnake.Embed(description=text)

        options = []
        for index, item in enumerate(poke):
            options.append(
                disnake.SelectOption(
                    label=f'({index+1}) {poke[item]['name']} ({poke[item]['params']['healpoint']}hp) ({poke[item]['params']['attack']}atk)',
                    value=f'poke|{index}|{poke[item]['params']['healpoint']}-{poke[item]['params']['attack']}|{rare}-{item}'
                    )
                )
        options.sort(key=lambda x: round((int(x.value.split('|')[2].split('-')[0]) + int(x.value.split('|')[2].split('-')[1]))/2), reverse=True)
        view = SelectMassPokemonsViewfightGroup(options=options, user=ctx.author.id)

        await ctx.send(embed=embed, view=view)

    @commands.command(name='lookfightgroup', aliases=['lfg', 'бгу', 'боеваягруппа'])
    async def lookFightGroup(self, ctx):
        slots = await takeFightGroup(user=ctx.author.id)
        text = ''
        for index, item in enumerate(slots):
            if slots[item] is None:
                text += f'### **`{index+1}:` `Пустой слот.`**\n| <None>\n'
            else:
                ids, seq = slots[item].split('-')
                try: localUserBag = (await giveUserBag(ctx.author.id))[ids][seq]
                except:
                    slots[item] = None
                    text += f'### **`{index+1}:` `Пустой слот.`**\n| <None>\n'
                    await saveFightGroup(rankCOM=None, user=ctx.author.id, slot=index+1)
                    continue
                localParams = localUserBag['params']
                text += f'### **`{index+1}:` `{localUserBag['name']}` `({localUserBag['other_param']['lvl']}) lvl`**\n| Здоровье: `[{localParams['healpoint']:,}]` `[{localParams['regen']}/h]`\n| Атака: `[{localParams['attack']:,}]`\n| Процент защиты: `[{localParams['armor']:.0%}]`\n| Шанс уклонения: `[{localParams['evasion']:.0%}]`\n| Скорость: `[{(1/localParams['speed']):.0%}]`\n'

        embed = disnake.Embed(description=text, colour=disnake.Colour.dark_red())
        await ctx.send(embed=embed)

    @commands.command(name='tradepoke', aliases=['trp', 'передать'])
    async def tradepoke(self, ctx):
        
        checkFight = await checkInFightStatus(uid=ctx.author.id)
        if checkFight:
            await ctx.send(embed=disnake.Embed(description='**Ой! Похоже вы находитесь в бою!**\n**Во время боя нельзя торговать понимонами.**'))
            return

        try:
            # Получение упоминания пользователя которому добавляется покемон
            mentionedUser = ctx.message.mentions[0]
        except:
            ErrorEmbed = disnake.Embed(description='**Форма команды: !trp <пользователь> <покемон>**')
            await ctx.send(embed=ErrorEmbed)
            return

        try:
            # Получение названия или ID покемона
            sennedPokemon = ctx.message.content.split()[2]
        except:
            ErrorEmbed = disnake.Embed(description='**Форма команды: !trp <пользователь> <покемон>**')
            await ctx.send(embed=ErrorEmbed)
            return
        
        try:
            try: 
                    # первая попытка поиска, через введенное имя покемона
                    foundPoke, rare = await findMap_PokemonInDB_LikeName(name=sennedPokemon)
            except: 
                # Вторая попытка нахождения покемона через индитификатор покемона Rank-num
                foundPoke = await findMap_PokemonInDB_LikeID(ID=sennedPokemon)
                rare = sennedPokemon.split('-')
        except:
            ErrorEmbed = disnake.Embed(description='**Возможно вы неверно указали либо ID покемона, либо название.**')
            await ctx.send(embed=ErrorEmbed)
            return

        try:
            userPokemons = await giveUserBag(user=ctx.author.id)
            SelectedPokes = userPokemons[rare]
        except:
            embed = disnake.Embed(description='**Упс, похоже вы не обладаете данным видом.**')
            await ctx.send(embed = embed)
            return

        # Формат [trade|rankCOM|user-ment]
        options = []
        for index, item in enumerate(SelectedPokes):
            options.append(
                disnake.SelectOption(
                    label=f'({index+1}) {SelectedPokes[item]['name']} ({SelectedPokes[item]['curr']['income']}/h)',
                    value=f'trade|{index+1}|{rare}-{item}|{ctx.author.id}-{mentionedUser.id}'
                    )
                )

        embed = disnake.Embed(description=f'**Выберите покемона, которого вы хотели бы передать.**')

        view = SelectMassPokemonsViewSelectPoke(options=options, user=ctx.author.id)
        await ctx.send(embed=embed, view=view)

    # Покемонов можно продать не только в стоковом магазине, но и на аукционе, между игроками.
    @commands.command(name='bidding', aliases=['bid', 'аукцион', 'аук', 'торги'])
    async def bidding(self, ctx):
        '''
        1. Вопрос пользователю о том, что снимать с аукциона после продажного цикла(2 недели), или же продлять из кармана.
        Если пополнить не удалось, то лот снимается.
        Стоимость держания лота: 2%, 5%, 10% от цены покемона
        Стоимость обозначает приоритет лота.
        2. Аукцион автономен. Не требует подтверждения на передачу, работает как обычная покупка.
        3. 
        '''
        pass

    @commands.Cog.listener('on_button_click')
    async def supportEndSelect(self, inter:disnake.MessageInteraction):
        trustList = ['SUPATK', 'SUPHP', 'SUPDEF', 'SUPEVN', 'SUPREG', 'SUPPR', 'SUPINC', 'SUPPINC']
        for item in trustList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, user, uid, did = inter.component.custom_id.split('|')
        userBag = await giveUserBag(user=user)

        if inter.author.id != int(user): 
            await inter.response.send_message(embed=disnake.Embed(title='Данное взаимодействие не является вашим.'), ephemeral=True)

        uids, useq = uid.split('-')
        upPoke = userBag[uids][useq]
        oldPoke = copy.deepcopy(upPoke)

        mapedSuped = upPoke['other_param']['supports']
        upRank = True if int(mapedSuped)+1 == 10 else False

        dids, dseq = did.split('-')
        diePoke = userBag[dids][dseq]

        upPoke = HPupdate(upPoke, inter.author.id)
        diePoke = HPupdate(diePoke, inter.author.id)

        maximus = ''
        if comm == 'SUPATK':
            upPoke['params']['attack'] += round(diePoke['params']['attack'] * mapSup(str(mapedSuped)))
            diePoke['params']['attack'] = 0
        if comm == 'SUPHP':
            upPoke['params']['healpoint'] += round(diePoke['params']['healpoint'] * mapSup(str(mapedSuped)))
            diePoke['params']['healpoint'] = 1
        if comm == 'SUPDEF':
            upPoke['params']['armor'] += round(diePoke['params']['armor'] * mapSup(str(mapedSuped)), 3)
            if upPoke['params']['armor'] > 0.8:
                upPoke['params']['armor'] = 0.8
                maximus = 'MAX'
            diePoke['params']['armor'] = 0
        if comm == 'SUPEVN':
            upPoke['params']['evasion'] += round(diePoke['params']['evasion'] * mapSup(str(mapedSuped)), 3)
            if upPoke['params']['evasion'] > 0.8:
                upPoke['params']['evasion'] = 0.8
                maximus = 'MAX'
            diePoke['params']['evasion'] = 0
        if comm == 'SUPREG':
            upPoke['params']['regen'] += round(diePoke['params']['regen'] * mapSup(str(mapedSuped)))
            diePoke['params']['regen'] = 0

        # Цена
        if comm == 'SUPPR':
            upPoke['curr']['price'] += round(diePoke['curr']['price'] * mapSup(str(mapedSuped)))
            diePoke['curr']['price'] = 0
        # Доход
        if comm == 'SUPINC':
            upPoke['curr']['income'] += round(diePoke['curr']['income'] * mapSup(str(mapedSuped)))
            diePoke['curr']['income'] = 0
        # Мощность
        if comm == 'SUPPINC':
            upPoke['curr']['power'] += round(diePoke['curr']['power'] * mapSup(str(mapedSuped)), 2)
            diePoke['curr']['power'] = 0

        if upRank and upPoke['rank'] != 'S':
            upPoke['params']['attack'] = round(upPoke['params']['attack'] * (rankedBoost(upPoke['rank']))[0])
            upPoke['params']['healpoint'] = round(upPoke['params']['healpoint'] * (rankedBoost(upPoke['rank']))[0])

            upPoke['params']['armor'] = round(upPoke['params']['armor'] * (rankedBoost(upPoke['rank']))[1], 2)
            if upPoke['params']['armor'] > 0.8:
                upPoke['params']['armor'] = 0.8
                maximus = 'MAX'
            upPoke['params']['evasion'] = round(upPoke['params']['evasion'] * (rankedBoost(upPoke['rank']))[1], 2)
            if upPoke['params']['evasion'] > 0.8:
                upPoke['params']['evasion'] = 0.8
                maximus = 'MAX'

            upPoke['params']['regen'] = round(upPoke['params']['regen'] * (rankedBoost(upPoke['rank']))[0])
            upPoke['curr']['price'] = round(upPoke['curr']['price'] * (rankedBoost(upPoke['rank']))[0])
            upPoke['curr']['income'] = round(upPoke['curr']['income'] * (rankedBoost(upPoke['rank']))[0])
            upPoke['curr']['power'] = round(upPoke['curr']['power'] * (rankedBoost(upPoke['rank']))[0])

            upPoke['rank'] = rrUped(upPoke['rank'])
            
        text = f'### |[ {upPoke['name']} ]|\n'
        for item in upPoke['params']:
            if upPoke['params'][item] != oldPoke['params'][item]: text += f'- **{await AllockatePokemons(item)}:** `[{oldPoke['params'][item]} -> {upPoke['params'][item]}]` {maximus}\n'
        for item in upPoke['curr']:
            if upPoke['curr'][item] != oldPoke['curr'][item]: text += f'- **{await AllockatePokemons(item)}:** `[{oldPoke['curr'][item]} -> {upPoke['curr'][item]}]`\n'
        
        
        if upRank:
            text += f'\nПокемон претерпел эволюцию: `[{oldPoke['rank']} -> {upPoke['rank']}]`\n'

            upPoke['other_param']['supports'] = 0
        else: upPoke['other_param']['supports'] += 1
        
        diePoke['other_param']['supports'] -= 1
        diePoke['other_param']['supports_percent_up'] -= 0.01

        upPoke['other_param']['supports_percent_up'] += 0.01
        text += f'- Поддержек: `[→{upPoke['other_param']['supports']}]`\n- Усиление от поддержки: `[→{upPoke['other_param']['supports_percent_up']:.0%}]`'

        await saveBagUserFile(userBag, user)
        message = await inter.response.edit_message(embed=disnake.Embed(title='Итоги усиления', description=text, colour=disnake.Color.purple()), components=None)
        await closeEmbedMessageAfter(message, time=60)
        return

    @commands.command(name='support', aliases=['пдж', 'поддержка', 'sup'])
    async def support(self, ctx):        
        name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        if name == ctx.message.content.split(' ')[0]:
            await ctx.send(embed=disnake.Embed(description='Не введено ничего. Для дополнительной справке по использованию, обратитесь к справке. Команда: `[!help поддержка]`'))
            return
        
        try: SupPoke, diePoke = name.split(' : ')
        except: 
            await ctx.send(embed=disnake.Embed(description='Введено либо некорректная форма, либо больше двух значений.'))
            return
        
        findSupPokes = await findID_PokemonInDB_LikeName(PokemonName=SupPoke)
        if findSupPokes is None:
            await ctx.send(embed=disnake.Embed(description=f'Покемон `[{SupPoke}]` - не был обнаружен. Вы правильно ввели его название?'))
            return
        findDiePokes = await findID_PokemonInDB_LikeName(PokemonName=diePoke)
        if findDiePokes is None:
            await ctx.send(embed=disnake.Embed(description=f'Покемон `[{diePoke}]` - не был обнаружен. Вы правильно ввели его название?'))
            return
        
        userBag = await giveUserBag(user=ctx.author.id)
        SupPokes = userBag[findSupPokes]

        optionsSupPoke = []
        for index, item in enumerate(SupPokes):
            optionsSupPoke.append(
                disnake.SelectOption(
                    label=f'({index+1}) {SupPokes[item]['name']} ({SupPokes[item]['other_param']['supports']} sup)',
                    value=f'poke|{index+1}|{SupPokes[item]['other_param']['lvl']}|{findSupPokes}-{item}'
                    )
                )
        optionsSupPoke.sort(key=lambda x: int(x.value.split('|')[2]), reverse=True)
        
        view = ViewSelectToSupPoke(options=optionsSupPoke, user=ctx.author.id, userBag=userBag, diePokes=findDiePokes)
        await ctx.send(embed=disnake.Embed(description='### Какого покемона вы желаете улучшить?', colour=disnake.Color.dark_green()), view=view)

    @commands.Cog.listener('on_button_click')
    async def upPokeLictener(self, inter: disnake.MessageInteraction):
        trustList = ['UPPPATK', 'UPPPHP', 'UPPPDEF', 'UPPPEVN', 'UPPPREG', 'UPPPR', 'UPPINC', 'UPPPINC']
        for item in trustList:
            if inter.component.custom_id.startswith(item): break
        else: return

        comm, user, pid = inter.component.custom_id.split('|')
        userBag = await giveUserBag(user=user)

        try:
            with open('../PonyashkaDiscord/config/tempoUppPoke.json', 'r', encoding='utf-8') as file:
                listButtons = json.load(file)
            inner = listButtons[f'{inter.message.id}']
        except:
            await inter.response.edit_message(embed=disnake.Embed(title='Активно иное окно улучшения.', description=''), components=None)
            return

        if inter.author.id != int(user): 
            await inter.response.send_message(embed=disnake.Embed(title='Данное взаимодействие не является вашим.'), ephemeral=True)
            return
        
        ids, seq = pid.split('-')
        poke = userBag[ids][seq]
        
        if poke['other_param']['lvl'] == 25: 
            await inter.response.edit_message(embed=disnake.Embed(title='Покемон достиг максимального уровня.', description=''), components=None)
            return

        if comm == 'UPPPATK':
            text = f'Улучшение параметра урона: `[{poke['params']['attack']} -> {round(poke['params']['attack'] * 1.1)}]`' 
            poke['params']['attack'] = round(poke['params']['attack'] * 1.1)

        if comm == 'UPPPHP':
            text = f'Улучшение параметра здоровья: `[{poke['params']['healpoint']} -> {round(poke['params']['healpoint'] * 1.1)}]`'
            poke['params']['healpoint'] = round(poke['params']['healpoint'] * 1.1)

        if comm == 'UPPPDEF':
            text = f'Улучшение параметра защиты: `[{poke['params']['armor']} -> {round(poke['params']['armor'] * 1.1, 2)}]`'
            poke['params']['armor'] = round(poke['params']['armor'] * 1.1, 2)

            if poke['params']['armor'] >= 0.8:
                poke['params']['armor'] = 0.8
                text = f'Параметр защиты достиг максимума: `[{poke['params']['armor']} -> 0.8 (MAX)]`'

        if comm == 'UPPPEVN':
            text = f'Улучшение параметра уворота: `[{poke['params']['evasion']} -> {round(poke['params']['evasion'] * 1.1, 2)}]`'
            poke['params']['evasion'] = round(poke['params']['evasion'] * 1.1, 2)

            if poke['params']['evasion'] >= 0.8:
                poke['params']['evasion'] = 0.8
                text = f'Параметр уворота достиг максимума: `[{poke['params']['evasion']} -> 0.8 (MAX)]`'

        if comm == 'UPPPREG':
            text = f'Улучшение параметра регенерации: `[{poke['params']['regen']} -> {round(poke['params']['regen'] * 1.1)}]`'
            poke['params']['regen'] = round(poke['params']['regen'] * 1.1)

        # Цена
        if comm == 'UPPPR':
            text = f'Улучшение параметра цены: `[{poke['curr']['price']} -> {round(poke['curr']['price'] * 1.1)}]`'
            poke['curr']['price'] = round(poke['curr']['price'] * 1.1)

        # Доход
        if comm == 'UPPINC':
            text = f'Улучшение параметра дохода: `[{poke['curr']['income']} -> {round(poke['curr']['income'] * 1.1)}]`'
            poke['curr']['income'] = round(poke['curr']['income'] * 1.1)

        # Мощность
        if comm == 'UPPPINC':
            text = f'Улучшение параметра мощи: `[{poke['curr']['power']} -> {round(poke['curr']['power'] * 1.1, 2)}]`'
            poke['curr']['power'] = round(poke['curr']['power'] * 1.1, 2)

        poke['other_param']['exp'] -= pokesToNextLvLExp(rank=poke['rank'], lvl=poke['other_param']['lvl'])
        poke['other_param']['lvl'] += 1

        await saveBagUserFile(userBag, int(user))

        countUppes = len(inner['butt'])

        if inner['butt']:
            zup = inner['butt'][0]
            button = []

            for item in zup:
                for cax in zup[item]:
                    button.append(disnake.ui.Button(style=disnake.ButtonStyle(value=zup[item][cax]['style']), label=zup[item][cax]['label'], custom_id=zup[item][cax]['custom_id']))
            else: inner['butt'].pop(0)

            await inter.response.edit_message(embed=disnake.Embed(title=f'Улучшение {poke['name']}',description=text, colour=disnake.Color.purple()).set_footer(text=f'Количество возможныхулучшений: {countUppes}'), components=button)
        else:

            text2 = f'{text}\nНа этом все.'
            await inter.response.edit_message(embed=disnake.Embed(title=f'Улучшение [{poke['name']}]',description=text2, colour=disnake.Color.purple()).set_footer(text=f'Больше нет доступных улучшений.'), components=None)

        with open('../PonyashkaDiscord/config/tempoUppPoke.json', 'w', encoding='utf-8') as file:
            json.dump(listButtons, file, indent=3, ensure_ascii=False)

    @commands.command(name='upgradepoke', aliases=['upp', 'улучшение'])
    async def upPoke(self, ctx):
        '''Улучшение покемона по достижению предела опыта'''
        name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        if name == ctx.message.content.split(' ')[0]:
            await ctx.send(embed=disnake.Embed(description='Не введено ничего. Для дополнительной справке по использованию, обратитесь к help. Команда: `[!help улучшение]`', colour=disnake.Color.dark_red()))
            return
        
        try: pokeName, seq = name.split('=')
        except: 
            await ctx.send(embed=disnake.Embed(description='Введена некорректная форма. \nКорректная форма: !upp `<name>=<seq>`', colour=disnake.Color.dark_red()))
            return
        
        idsPoke = await findID_PokemonInDB_LikeName(PokemonName=pokeName)
        if idsPoke is None:
            await ctx.send(embed=disnake.Embed(description=f'`Возможно вы ошиблись в названии покемона. Система не обнаружила: [{pokeName}]`', colour=disnake.Color.dark_red()))
            return
        
        try:
            poke = (await giveUserBag(user=ctx.author.id))[idsPoke][seq]
        except:
            await ctx.send(embed=disnake.Embed(description=f'`Похоже вы не обладаете: [{pokeName}-{seq}]`', colour=disnake.Color.dark_red()))
            return

        poke = HPupdate(poke, ctx.author.id)
        
        countUppes = 0

        exLvl = copy.copy(poke['other_param']['lvl'])
        exExp = copy.copy(poke['other_param']['exp'])
        
        for i in range(25):
            if exLvl == 25: break
            response = pokesToNextLvLExp(rank=poke['rank'], lvl=exLvl)
            if response <= exExp:
                countUppes += 1
                exExp -= response
                exLvl += 1
            else: continue
        else: del exLvl, exExp

        if countUppes == 0:
            await ctx.send(embed=disnake.Embed(description=f'**Похоже ваш покемон ещё не достаточно накопил сил, для микро-эволюции.**\n', colour=disnake.Color.purple()))
            return
        
        buttons = {
        'params':{
            'attack':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Атака', custom_id=f'UPPPATK|{ctx.author.id}|{idsPoke}-{seq}'),
            'healpoint':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Здоровье', custom_id=f'UPPPHP|{ctx.author.id}|{idsPoke}-{seq}'),
            'armor':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Броня', custom_id=f'UPPPDEF|{ctx.author.id}|{idsPoke}-{seq}'),
            'evasion':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Уклонение', custom_id=f'UPPPEVN|{ctx.author.id}|{idsPoke}-{seq}'),
            'regen':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Регенерация', custom_id=f'UPPPREG|{ctx.author.id}|{idsPoke}-{seq}'),
            },
        'curr':{
            'price':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Цена', custom_id=f'UPPPR|{ctx.author.id}|{idsPoke}-{seq}'),
            'income':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Доход', custom_id=f'UPPINC|{ctx.author.id}|{idsPoke}-{seq}'),
            'power':disnake.ui.Button(style=disnake.ButtonStyle.blurple, label='Усиление дохода', custom_id=f'UPPPINC|{ctx.author.id}|{idsPoke}-{seq}'),
            }
        }

        message = await ctx.send(embed=disnake.Embed(title=f'Улучшение {poke['name']}', description='Улучшение покемона происходит на каждом уровне. \nОднако может быть улучшен только один из трех предложенных параметров.', colour=disnake.Color.purple()).set_footer(text=f'Количество возможных улучшений: {countUppes}'))

        try:
            with open('../PonyashkaDiscord/config/tempoUppPoke.json', 'r', encoding='utf-8') as file:
                listButtons = json.load(file)
                
                for item in listButtons:
                    if ctx.author.id == listButtons[item]['author']: del listButtons[item]
                
                listButtons[f'{message.id}'] = {
                        'author':ctx.author.id,
                        'butt':[]
                    }
        except:
            listButtons = {
                f'{message.id}':{
                    'author':ctx.author.id,
                    'butt':[]
                    }
                }

        for i in range(countUppes):
            listButtons[f'{message.id}']['butt'].append(await selectedCountElements(3, buttons, (ctx.author.id, f'{idsPoke}-{seq}')))

        else: 
            zup = listButtons[f'{message.id}']['butt'][0]
            button = []
            for item in zup:
                for cax in zup[item]:
                    button.append(disnake.ui.Button(style=disnake.ButtonStyle(value=zup[item][cax]['style']), label=zup[item][cax]['label'], custom_id=zup[item][cax]['custom_id']))

            await message.edit(components=button)
            
            listButtons[f'{message.id}']['butt'].pop(0)


        with open('../PonyashkaDiscord/config/tempoUppPoke.json', 'w', encoding='utf-8') as file:
            json.dump(listButtons, file, indent=3, ensure_ascii=False)

        


        # import pprint
        # pprint.PrettyPrinter(width=5).pprint(self.buttonsToUpper)

        # cup = disnake.ui.Button(style=disnake.ButtonStyle(value=1), label='12', custom_id='22')
        # butt = cup.to_component_dict()
        # print(butt)
        # print(cup)
        # print(disnake.ui.Button(style=disnake.ButtonStyle(value=butt['style']), label=butt['label'], custom_id=butt['custom_id']))

    @commands.command(name='remelting', aliases=['плавка', 'переплавка', 'rem'])
    async def remelting(self, ctx):

        

        name = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        if name == ctx.message.content.split(' ')[0]:
            await ctx.send(embed=disnake.Embed(description='Не введено ничего. Для дополнительной справке по использованию, обратитесь к pokedex. Команда: `[!pokedex улучшение]`', colour=disnake.Color.dark_red()))
            return
        
        # Форма конкретного покемона list<<name>-<seq>>
        async def oncePoke():
            try: pokeName, seq = name.split('-')
            except: 
                return ctx.send(embed=disnake.Embed(description='Введена некорректная форма. \nКорректная форма: !upp `<name>-<seq>`', colour=disnake.Color.dark_red()))
            
            idsPoke = await findID_PokemonInDB_LikeName(PokemonName=pokeName)
            if idsPoke is None:
                return ctx.send(embed=disnake.Embed(description=f'`Возможно вы ошиблись в названии покемона. Система не обнаружила: [{pokeName}]`', colour=disnake.Color.dark_red()))
            poke = (await giveUserBag(user=ctx.author.id))[idsPoke][seq]

        # Форма по типу list<name>
        async def oneTypePoke():
            pass

        # Форма по рангу list<rank>
        async def rankedRem():
            pass

    @commands.command(name='marketpoke', aliases=['mp', 'магаз', 'магазин'])
    async def marketPoke(self, ctx):
        
        try:
            with open('../PonyashkaDiscord/content/lotery/market.yaml', 'r', encoding='utf-8') as file:
                market = yaml.safe_load(file)
        except:
            market = {
                "config":{
                    "timestamp":0
                    },
                "items":{}
                }
            with open('../PonyashkaDiscord/content/lotery/market.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(market, file)


        try:
            comm = ctx.message.content.split()
            comm.pop(0)

            listComm = []
            for item in comm:
                if '-' in item:
                    listComm.append((item.split('-')[0], item.split('-')[1]))
        except:
            comm = None

        buying = False

        listBuy = []

        if comm is not None:
            for command in listComm:
                keys = market['items'].keys()

                for item in keys:
                    noItem = False
                    # Проверка на релевантность покупки, если там есть указанные товары
                    if market['items'][item]['name'].lower() == command[0].lower():
                        
                        if command[1].isdigit():
                            if int(command[1]) > 0: value = int(command[1])
                            else: value = 1
                        else: value = 1

                        count = market['items'][item]['count']
                        if count - value < 0: value = int(count)
                        if value == 0: 
                            buy = False
                            noItem = True

                        price = market['items'][item]['price']
                        userCurr = db.Money(user=ctx.author.id, currency=market['items'][item]['curr']).have()
                        if value * price > userCurr or noItem: 
                            buy = False 
                        else: 
                            buy = True
                        
                        if buy:
                            # Загрузка функции
                            func = pickle.loads(market['items'][item]['added'])
                            func(user=ctx.author.id, value=value, price=market['items'][item]['price'])
                            market['items'][item]['count'] -= value

                            #TODO: Потом учесть, что предметы имеют иной метод добавления. Однако также и имеют флаг о том, что это предмет.

                            with open('../PonyashkaDiscord/content/lotery/market.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(market, file)
                        

                        buying = True
                        listBuy.append((market['items'][item]['name'], value, market['items'][item]['price'], (buy, userCurr, market['items'][item]['curr_r'], noItem)))

        if buying:
            text = ''
            for index, item in enumerate(listBuy):
                if item[3][0]:
                    text += f'**({index+1}) Куплен предмет: `[{item[0]}]` \n| `[{item[1]}/шт]` по цене `({item[2]:,}/штука)`**\n\n'
                elif item[3][3]:
                    text += f'**({index+1}) Предмета [{item[0]}] — Ожидайте завоз.**\n'
                else:
                    text += f'**({index+1}) Недостаточно денег для [{item[0]}], требуется `[{(item[1]*item[2]):,} {item[3][2]}]`, у вас `[{item[3][1]:,} {item[3][2]}]`**'
            embed = disnake.Embed(description=text)
            await ctx.send(embed=embed)
            return

        timestamp = market['config']['timestamp'] - round(time.time())

        if timestamp < 0: 
            updateStamp = True
        else: 
            updateStamp = False
            timeStruct = time.gmtime(timestamp)
            times = time.strftime(f'{timeStruct[2]-1}:%H:%M:%S', timeStruct)

        mainText = ''
        if updateStamp:
            associateItems = {
                    "1":{
                        "name":"Билет",
                        "desc":"Совершенно обычный на вид игровой тикет, такой же, как выдают в аркадных автоматах, когда выиграл достаточно. На самом билете написано: «Высоко в небе, ваша удача». Торговец говорит, что этот билет можно использовать в лотереи.",
                        "rank":"GRAY",

                        "added":pickle.dumps(AddedrMarket.addTiket),

                        "count":random.randrange(50, 200, 5),
                        "price":random.randrange(3500, 17500, 500),
                        "curr":"ESSENCE", "curr_r":"es"
                        },
                    "2":{
                        "name":"Душа",
                        "desc":"Душа сильного существа. Частый метод для получения души, это переплавка очень дорогих и сильных монстров под определенные критерии. Но этот процесс очень дорогой и долгий, однако... Откуда торговец берет их? Не ясно, но многие поговаривают, что тут пахнет обманом.",
                        "rank":"GREEN",

                        "added":pickle.dumps(AddedrMarket.addSoul),

                        "count":random.randrange(200, 700, 10),
                        "price":random.randrange(50, 300, 10),
                        "curr":"SHARD", "curr_r":"sh"
                        },
                    "3":{
                        "name":"Духовная память",
                        "desc":"Духовная память переплавленного монстра. Некогда этот монстр прошел множество битв, ради того что быть переплавленным в довольно простой зеленый кристаллик. Откуда торговец их берет, не сильно ясно.",
                        "rank":"GREEN",

                        "added":pickle.dumps(AddedrMarket.addPokeEssence),

                        "count":random.randrange(200, 700, 10),
                        "price":random.randrange(50, 750, 10),
                        "curr":"SHARD", "curr_r":"sh"
                        }
                }

            #TODO: Тут расположить метод для добавления стороних предметов в магазин, а также их рандомизация. Также учесть адресацию: <color>-ids, example -> GRAY-3
            #? Предметы априори нельзя улучшать в межранговом векторе. Почти все предметы = расходники.
            #? Расходники всегда одного уровня, хоть и сила разная, так как при ids=CUSTOM учитывается только определенные уже системой свойства.

            for index, item in enumerate(associateItems):
                if index == 5: break

                tere = associateItems[item]

                mainText += f'### {index+1}. {tere['name']} ({tere['count']}/{tere['count']})\n| `Описание:` {tere['desc']}\n| `Стоимость:` **{tere['price']}**{tere['curr_r']} / one\n'

                market['items'][item] = {
                    "name":tere['name'],
                    "desc":tere['desc'],
                    "added":tere['added'],

                    "max_count":tere['count'],
                    "count":tere['count'],

                    "price":tere['price'],
                    "curr":tere['curr'], 
                    "curr_r":tere['curr_r']
                    }
            else:
                market['config']['timestamp'] = round(time.time()) + 259200


                with open('../PonyashkaDiscord/content/lotery/market.yaml', 'w', encoding='utf-8') as file:
                    yaml.dump(market, file)

        else:
            with open('../PonyashkaDiscord/content/lotery/market.yaml', 'r', encoding='utf-8') as file:
                loadMarket = yaml.safe_load(file)
            
            for index, item in enumerate(loadMarket['items']):
                if index == 5: break

                tere = loadMarket['items'][item]

                mainText += f'### {index+1}. {tere['name']} ({tere['count']}/{tere['max_count']})\n| `Описание:` {tere['desc']}\n| `Стоимость:` **{tere['price']}**{tere['curr_r']} / one\n'


        embed = disnake.Embed(
            title='Шайтан магазин дряхлого {Санди}',
            description=mainText
            )
        
        if updateStamp:
            embed.set_footer(text='При вас торговец раставил новые товары.\nДля покупки: !mp <товар>-<количество>')
        else:
            embed.set_footer(text=f'До завоза нового товара: [{times}]\nДля покупки: !mp <товар>-<количество>')


        await ctx.send(embed=embed)    

    # TODO: Не забыть добавить эту наглядную команду для награждения
    @commands.command(name='buggift', aliases=['bg'])
    async def buggift(self, ctx):
        ment = ctx.message.mentions[0]

        await ctx.send(ment.id)
    
    #? Для разного рода маленьких проверок
    @commands.command(name='tt')
    async def tte(self, ctx):   
        await ctx.send(await checkInFightStatus(uid=ctx.author.id))

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Economics(bot))
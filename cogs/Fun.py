import disnake
from disnake.ext import commands
from disnake.errors import HTTPException

import random
import time
import random
import math
import pymorphy3
import requests

from .module import REQ_database as Rdb


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

    @commands.command(name='brainfuck', aliases=['fuck', 'bf'])
    async def brainFuck(self, ctx):

        operators = {
            '+':[10, 100_000], 
            '-':[10, 100_000], 
            '*':[2, 1000], 
            '//':[10_000, 1_000_000]}
        SO = random.choice(list(operators.keys()))

        # if SO == '/':
        #     firstNum = random.randint(operators[SO][0], operators[SO][1]-1)
        #     secondNum = random.randint(operators[SO][0], firstNum-1)
        if SO == '-':
            firstNum = random.randint(operators[SO][0], operators[SO][1])
            secondNum = random.randint(operators[SO][0], firstNum-1)
        elif SO == '//':
            firstNum = random.randint(operators[SO][0], operators[SO][1])
            secondNum = random.randint(operators[SO][0], firstNum)
        elif SO == '+':
            firstNum = random.randint(operators[SO][0], operators[SO][1])
            secondNum = random.randint(operators[SO][0], operators[SO][1])
        else:
            firstNum = random.randint(operators[SO][0], operators[SO][1]-1)
            secondNum = random.randint(firstNum+1, operators[SO][1])
        
        operNum = eval(f'{firstNum}{SO}{secondNum}')
        beforeNum = operNum
        lastSides = None

        # Цвета
        colorNum = {'черный':0, 'красный':1,'оранжевый':2, 'желтый':3, 'зеленый':4, 'голубой':5, 'синий':6, 'серый':7, 'фиолетовый':8, 'белый':9}
        reverseColorNum = {0:'черный', 1:'красный', 2:'оранжевый', 3:'желтый', 4:'зеленый', 5:'голубой', 6:'синий', 7:'серый', 8:'фиолетовый', 9:'белый'}

        # Стороны свет + день/ночь
        worldSides = {0:'север', 1:'северо-восток', 2:'восток', 3:'юго-восток', 4:'юг', 5:'юго-запад', 6:'запад', 7:'северо-запад', 8:'ночь', 9:'день'}
        reverseWorldSide = {'север':0, 'северо-восток':1, 'восток':2, 'юго-восток':3, 'юг':4, 'юго-запад':5,'запад':6,'северо-запад':7, 'ночь':8, 'день':9}

        # Руны
        # погодные условия
        # Регионы
        # Имена

        #! Функции для вопросов
        def countColor(enter, up_down, sys=False):
            if up_down == 'up':
                colors = [0]*10
                for item in str(operNum):
                    colors[int(colorNum[reverseColorNum[int(item)]])] += 1
                return enter.lower() == reverseColorNum[colors.index(max(colors))]
            else:
                colors = [0]*10
                for item in str(operNum):
                    colors[int(colorNum[reverseColorNum[int(item)]])] += 1
                return enter.lower() == reverseColorNum[colors.index(min(colors, key=lambda e: e if e != 0 else 10))]
        def nextNumInON(enter):
            if int(enter.split()[1]) == -1: return (enter.split())[0].lower() == 'никакая'
            return int((enter.split())[0]) == int((enter.split())[1])
        def summ(enter):
            nums = [int(item) for item in list(str(operNum))]
            return int(enter) == sum(nums)
        def lineColors(enter):
            line = enter.split()
            lineOper = [f'{reverseColorNum[int(num)]}' for num in str(operNum)]
            for i, item in enumerate(lineOper):
                if line[i].lower() != item: return False
            return True
        def YES_NO(bool_):
            if bool_: return 'да'
            return 'нет'
        def MORE_LESS(num1, num2):
            if num1 == num2: return 'равно'
            if num1 > num2: return 'больше'
            return 'меньше'
        def simpleNum(enter):
            nums = [int(item) for item in list(str(operNum))]
            count = 0
            for item in nums:
                count += 1 if item in [2, 3, 5, 7] else 0 
            return int(enter) == int(count)
            
        # lvl= easy, medium, high, hell
        toRuTags = {
            'easy':'Простое', 'medium':'Среднее', 'high':'сложное', 'hell':'адское',
            'calculate':'вычисления', 'value':'значение', 'thisNum':'текущее число',
            'definition':'определение', 'digit':'цифра', 'color':'цвет', 'firstNum':'первое число',
            'count':'количество', 'more':'больше', 'less':'меньше', 'fullNum':'полное число',
            'reference':'справка', 'n-num':'n-ая цифра', 'after':'после', 'summ':'сумма',
            'dispatcher':'диспетчер', 'chain':'цепочка', 'comparison':'сравнение',
            'simple':'простые цифры', 'side':'стороны', 'minus':'разница', 'multi':'умножение',
            'factorial':'факториал', 'lastNum':'последняя цифра'
                    }
        question = {
            'q1':[
                'Чему равняется ваше текущее число?', 
                lambda enter: int(enter) == operNum,
                ['easy', 'calculation', 'value', 'thisNum']
                ],
            'q2':[
                'Какой цвет обозначет первая цифра, текущем числе?', 
                lambda enter: colorNum[enter.lower()] == int(str(operNum)[0]),
                ['easy', 'definition', 'firstNum', 'digit', 'color', 'thisNum']
                ],
            'q3':[
                'Какого цвета больше всего в текущем числе?', 
                lambda enter: countColor(enter, 'up'),
                ['medium', 'calculate', 'count', 'more', 'color', 'thisNum']
                ],
            'q4':[
                'Какой цвет обозначает цифра ({num})?', 
                lambda enter: (enter.split())[0].lower() == reverseColorNum[int((enter.split())[1])],
                ['easy', 'definition', 'color', 'refence']
                ],
            'q5':[
                'Какая цифра обозначает ({num}) цвет?', 
                lambda enter: int((enter.split())[0]) == colorNum[reverseColorNum[int((enter.split())[1])]] ,
                ['easy', 'definition', 'digit', 'reference']
                ],
            'q6':[
                'Какой цвет обозначает {num}-я цифра из текущего числа?', 
                lambda enter: (enter.split())[0].lower() == reverseColorNum[int(str(operNum)[int((enter.split())[1])])],
                ['medium', 'definition', 'n-num', 'color', 'thisNum']
                ],
            'q7':[
                'Какая цифра идёт после первой цифры обозначающей ({num}) в текущем числе?', 
                lambda enter: nextNumInON(enter),
                ['medium', 'definition', 'digit', 'after', 'color', 'thisNum']
                ],
            'q8':[
                'Какого цвета меньше всего в текущем числе?', 
                lambda enter: countColor(enter, 'down'),
                ['medium', 'calculate', 'count', 'less', 'color', 'thisNum']
                ],
            'q9':[
                'Какова сумма всех цифр текущего числа?', 
                lambda enter: summ(enter),
                ['medium', 'calculate', 'summ', 'digit', 'thisNum']
                ],
            'q10':[
                'Какое будет число, если сложить ({num1}-ю) цифру текущего числа с ({num2}-ой) цифрой числа диспетчера', 
                lambda enter: int((enter.split())[0]) == (int((enter.split())[1]))+int((enter.split())[2]),
                ['high', 'calculate', 'summ', 'digigt', 'thisNum', 'dispatcher']
                ],
            'q11':[
                'Как выглядит цепочка цветов текущего числа?', 
                lambda enter: lineColors(enter),
                ['medium', 'difinition', 'chain', 'thisNum']
                ],
            'q12':[
                'Какой цвет будет у последней цифры числа, если сложить ({num1}-ю) цифру текущего числа с ({num2}-ой) цифрой числа диспетчера', 
                lambda enter: enter.split()[0].lower() == reverseColorNum[ int(str( int(enter.split()[1]) + int(enter.split()[2]) )[-1]) ],
                ['high', 'calculate', 'summ', 'digit', 'definition', 'color', 'thisNum', 'dispatcher']
                ],
            'q13':[
                '({num1}-я) цифра текущего числа больше ({num2}-й) цифры числа диспетчера?', 
                lambda enter: (enter.split())[0].lower() == YES_NO((enter.split())[1] > (enter.split())[2]),
                ['medium', 'comparison', 'digit', 'more', 'thisNum', 'dispatcher']
                ],
            'q14':[
                '({num1}-я) цифра текущего числа меньше ({num2}-й) цифры числа диспетчера?', 
                lambda enter: (enter.split())[0].lower() == YES_NO((enter.split())[2] > (enter.split())[1]),
                ['medium', 'comparison', 'digit', 'less', 'thisNum', 'dispatcher']
                ],
            'q15':[
                'Если разделить текущее число на составные, то сколько в нем простых цифр?', 
                lambda enter: simpleNum(enter),
                ['medium', 'definition', 'count', 'digit', 'simple', 'thisNum']
                ],
            'q16':[
                'Какая будет последняя цифра после суммирования всех цифр числа диспетчера?', 
                lambda enter: int(enter) == int((str(sum([int(item) for item in str(secondNum)])))[-1]),
                ['medium', 'calculate', 'summ', 'digit', 'definition', 'thisNum']
                ],
            'q17':[
                'Какая будет сумма после суммирования всех цифр числа диспетчера?',
                lambda enter: int(enter) == sum([int(item) for item in str(secondNum)]),
                ['easy', 'digit', 'summ', 'calculate']
                ],
            'q18':[
                'Какому направлению определена цифра {num}?',
                lambda enter: (enter.split())[0].lower() == worldSides[int((enter.split())[1])],
                ['easy', 'digit', 'definition', 'side']
                ],
            'q19':[
                'Пройдя на {side}, а после умножив текущее число на значение данной стороны, какое число вы наблюдаете?',
                lambda enter: int((enter.split())[0]) == (int((enter.split())[1]) * operNum),
                ['easy', 'side', 'thisNum', 'calculate']
                ],
            'q20':[
                'Какой цвет соответсвует ночи?',
                lambda enter: enter.lower() == reverseColorNum[8],
                ['easy', 'definition', 'color', 'side']
                ],
            'q21':[
                'Если ({num1}-я) цифра текущего числа меньше ({num2}-ей) цифры числа диспетчера, то поделив текущее число на разницу между ними, каким будет ваше текущее число? В ином случае напишите значение текущего числа.',
                lambda enter: int(enter.split()[0]) == (operNum//abs(int(enter.split()[1])-int(enter.split()[2])) if int(enter.split()[1]) < int(enter.split()[2]) else operNum),
                ['medium', 'comparison', 'less', 'calculate', 'minus', 'n-num', 'thisNum', 'dispatcher', 'value']
                ],
            'q22':[
                'Если ({num1}-я) цифра текущего числа больше ({num2}-ей) цифры числа диспетчера, то умножив текущее число на сумму между ними, каким будет ваше текущее число? В ином случае напишите значение текущего числа.',
                lambda enter: int(enter.split()[0]) == (operNum*(int(enter.split()[1])+int(enter.split()[2])) if int(enter.split()[1]) > int(enter.split()[2]) else operNum),
                ['medium', 'comparison', 'more', 'calculate', 'summ', 'n-num', 'thisNum', 'dispatcher', 'value']
                ],
            'q23':[
                'Если взять ({num1}-ю) цифру текущего числа, ({num2}-ю) цифру числа диспетчера и перемножить их, то будет ли это число больше или меньше факториала последней цифры текущего числа?',
                lambda enter: (enter.split()[0]).lower() == MORE_LESS((int(enter.split()[1])*int(enter.split()[2])), math.factorial(int(str(operNum)[-1]))),
                ['high', 'comparison', 'more', 'less', 'calculate', 'multi', 'factorial', 'lastNum', 'thisNum', 'dispatcher']
                ],
            'q24':[
                'Если бы вас попросили бы смешать цвета ({color1}), то как бы вы записали итоговое число, попроси вас добавить ещё {color2}, в конец числа?',
                lambda enter: int(enter.split()[0]) == int(enter.split()[1]),
                ['medium', 'definition', 'color', 'count', 'calculate']
                ],
            'q25':[
                'Какой цвет соответсвует дню?',
                lambda enter: enter.lower() == reverseColorNum[9],
                ['easy', 'definition', 'color', 'side']
                ],
            'q26':[
                'Если бы вас попросили бы сопоставить цвета ({color1}), то как бы вы записали итоговое число, попроси вас добавить ещё {color2}, в конец числа?',
                lambda enter: int(enter.split()[0]) == int(enter.split()[1]),
                ['medium', 'definition', 'color', 'count', 'calculate']
                ],
            }
        
        #! Функции для усложнения
        def reverseNum(upp):
            toRevs = list(str(upp))
            toRevs.reverse()
            text = ''
            for item in toRevs:
                text += item
            return int(text)
        def whereTags(tag):
            respoce = []
            for key in list(question.keys()):
                if tag in question[key][2]: respoce.append(int((key.split('q'))[1])-1)
            return respoce
        def downChancedINTOvalue(listChanced, value, q):
            index = int((q.split('q'))[1])-1
            listChanced[index] -= value
            if listChanced[index] < 0: listChanced[index] = 0 
            return listChanced
        def uppChance(listChanced, tag):
            responce = whereTags(tag)
            for index in responce:
                listChanced[index] += 35
                if listChanced[index] < 0: listChanced[index] = 0 
            return listChanced
        def downChance(listChanced, tag):
            responce = whereTags(tag)
            for index in responce:
                listChanced[index] -= 35
                if listChanced[index] < 0: listChanced[index] = 0 
            return listChanced
        def summSimpleNumMultiThisNum(thisNum):
            nums = [int(item) for item in list(str(operNum))]
            value = 0
            for item in nums:
                value += item if item in [2, 3, 5, 7] else 0 
            return int(thisNum) * int(value)
        def replaceN_num(upp):
            listOper = list(str(operNum))
            listOper[upp[0]] = str(secondNum)[upp[1]]
            num = ''
            for item in listOper:
                num += f'{item}'
            return int(num)

        complication = {
            'c1':['Текущее число умножено на ({num})\n`До перерасчета.`', lambda upp: abs(operNum * upp)],
            'c2':['В текущее число было добавлено число ({num})\n`До перерасчета.`', lambda upp: abs(operNum + upp)],
            'c3':['Текущее число целочисленно поделено на ({num})\n`До перерасчета.`', lambda upp: operNum // upp if abs(operNum // upp) > 0 else 1],
            'c4':['Из текущего числа было вычтено число ({num})\n`До перерасчета.`', lambda upp: abs(operNum - upp)],
            'c5':['Ваше текущее число теперь записано обратным порядком\n`До перерасчета.`', lambda upp: reverseNum(upp)],
            'c6':['Увеличен шанс на вопросы про вычисления.\n`На сессию.`', lambda upp: uppChance(upp, 'calculate')],
            'c7':['Уменьшен шанс на простые вопросы.\n`На сессию.`', lambda upp: downChance(upp, 'easy')],
            'c8':['Уменьшен шанс на вопросы про правила\n`На сессию.`', lambda upp: downChance(upp, 'definition')],
            'c9':['Возмите все простые цифры в вашем текущем числе и суммируйте их, а после умножте на текущее число, теперь это ваше новое текущее число.', lambda upp: summSimpleNumMultiThisNum(upp)],
            'c10':['{num1}-я цифра цифра текущего числа заменена на {num2}-ю цифру диспетчера.', lambda upp: replaceN_num(upp)]

            }
        textBase = f'Напоминание: Игра идёт потоком, на каждый ответ у вас будет 45 секунд, потому исключите иные сообщения кроме ответов на вопросы. Также помните, игра требует точности ответа. Удачи вам.\n## Запомните и вычислите:\n**Оператор:** `{SO}`\n\n**Ваше число:** `{firstNum}`\n**Число диспетчера:** `{secondNum}`'
        message = await ctx.send(embed=
                disnake.Embed(description=textBase, colour=disnake.Color.yellow()),
            components=disnake.ui.Button(style=disnake.ButtonStyle.green, label='Начать', custom_id='startBrainFuck'))

        def start(e):
            return (e.author.id == ctx.author.id) and (e.component.custom_id == 'startBrainFuck')
        def check(e):
            return e.author.id == ctx.author.id

        try: startQ = await self.bot.wait_for('button_click', check=start, timeout=60)
        except TimeoutError:
            await message.edit(components=None) 
            return await ctx.send('Время для принятия истекло')
        
        textBase = f'## игра началась:\n**Оператор:** `{'?'}`\n\n**Ваше число:** `{'?'*len(str(firstNum))}`\n**Число диспетчера:** `{'?'*len(str(secondNum))}`'
        await message.edit(embed=disnake.Embed(description=textBase))
        await startQ.response.edit_message(components=None)

        points = 0
        chanced = [100] * len(list(question.keys()))
        player = f'{ctx.author.name}'

        for i in range(100):
            if i == 0: enterMess = '## Игра начинается\n\n'
            else: enterMess = ''

            if random.random() < 0.65 and i >= 3: 
                compli = random.choice(list(complication.keys()))
                diap = {'c1':[2, 100], 'c2':[100, 10_000], 'c4':[100, 10_000], 'c3':[10_000, 100_000]}
                
                if compli in ['c1', 'c2', 'c3', 'c4']:
                    RCnum = random.randint(diap[compli][0], diap[compli][1])
                    await ctx.send(f'Введено дополнительное усложнение [+1 доп. очко].\nУсложнение: {complication[compli][0]}'.format(num=RCnum))
                    operNum = complication[compli][1](RCnum)
                    points += 1
                elif compli in ['c5', 'c9']:
                    await ctx.send(f'Введено дополнительное усложнение [+1 доп. очко].\nУсложнение: {complication[compli][0]}')
                    operNum = complication[compli][1](operNum)
                    points += 1
                elif compli in ['c6', 'c7', 'c8']:
                    await ctx.send(f'Введено дополнительное усложнение [+1 доп. очко].\nУсложнение: {complication[compli][0]}')
                    chanced = complication[compli][1](chanced)
                    points += 1
                elif compli in ['c10']:
                    RCnum = random.choice([int(item) for item in str(operNum)])
                    IRCnum = str(operNum).index(str(RCnum))
                    RCnum2 = random.choice([int(item) for item in str(secondNum)])
                    IRCnum2 = str(secondNum).index(str(RCnum2))
                    await ctx.send(f'Введено дополнительное усложнение [+1 доп. очко].\nУсложнение: {complication[compli][0]}'.format(num1=IRCnum+1, num2=IRCnum2+1))
                    operNum = complication[compli][1]((IRCnum, IRCnum2))
                    points += 1


            quest = random.choices(list(question.keys()), weights=chanced)[0]
            if quest in ['q4', 'q5']:
                Rnum = random.randint(0, 9)
                if quest == 'q4': await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(num=Rnum))
                else: await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(num=reverseColorNum[Rnum]))
            elif quest == 'q6':
                Rnum = str(operNum).index(random.choice(str(operNum)))
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(num=int(Rnum)+1))
            # have {num}
            elif quest == 'q7':
                RN = random.choice(list(set(list(str(operNum)))))
                Inum = str(operNum).index(RN)
                Rnum = str(operNum)[Inum + 1] if len(str(operNum))-1 != Inum else -1
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(num=reverseColorNum[int(RN)]))
            # have {num1} and {num2}
            elif quest in ['q10', 'q12', 'q13', 'q14', 'q21', 'q22', 'q23']:
                Rnum = random.choice(str(operNum))
                Inum = str(operNum).index(Rnum)
                Rnum2 = random.choice(str(secondNum))
                Inum2 = str(secondNum).index(Rnum2)
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(num1=int(Inum)+1, num2=int(Inum2)+1))
            # have {num} and rand(0, 7)
            elif quest in ['q18']:
                Rnum = random.randint(0, 7)
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(num=Rnum))
            # have {side}
            elif quest in ['q19']:
                side = worldSides[random.randint(0, 7)]
                Rnum = reverseWorldSide[side]
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(side=side))
            elif quest in ['q24']:
                randomColor = [random.choice(list(reverseColorNum.keys())) for i in range(0, random.randint(1, 6))]
                appendRandomColor = random.choice(list(reverseColorNum.keys()))
                apeendText = ''
                Rnum = 0
                for item in randomColor:
                    apeendText += f'{reverseColorNum[item]} '
                    Rnum += item
                else: Rnum = int(f'{Rnum}{appendRandomColor}')
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(color1=apeendText, color2=appendRandomColor))
            elif quest in ['q26']:
                randomColor = [random.choice(list(reverseColorNum.keys())) for i in range(0, random.randint(2, 6))]
                appendRandomColor = random.choice(list(reverseColorNum.keys()))
                apeendText = ''
                Rnum = ''
                for index, item in enumerate(randomColor):
                    if index != len(randomColor)-1: apeendText += f'{reverseColorNum[item]} '
                    else: apeendText += f'{reverseColorNum[item]}'
                    Rnum += f'{item}'
                else: Rnum += f'{appendRandomColor}'
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}'.format(color1=apeendText, color2=appendRandomColor))
            else:
                await ctx.send(f'{enterMess}**{i+1} вопрос [{player}]:** {question[quest][0]}')
            chanced = downChancedINTOvalue(chanced, 20, quest)

            try: responce =  await self.bot.wait_for('message', check=check, timeout=45)
            except: return await ctx.send('Увы, но время на ответ закончилось.')
            request = responce.content

            # if need append 1 argument
            if quest in ['q4', 'q5', 'q6', 'q7', 'q18', 'q19', 'q24', 'q26']: request += f' {Rnum}'
            # if need apeend 2 argument
            elif quest in ['q10', 'q12', 'q13', 'q14', 'q21', 'q22', 'q23']: request += f' {Rnum} {Rnum2}'

            try:
                if question[quest][1](request): 
                    points += 1
                    await ctx.send('### ✔ **< Верно >** ✔')
                else: 
                    await ctx.send('### ❌ **< Неверно >** ❌')
                    break
            except ValueError: 
                await ctx.send('### ❌ **< Неверно >** ❌')
                break
            except KeyError: 
                await ctx.send('### ❌ **< Неверно >** ❌')
                break
        await ctx.send(embed=disnake.Embed(description=f'## Итоговое количество баллов [{player}]: `{points}`\n\nОператор: `{SO}`\nЧисло игрока: `{firstNum}`\nЧисло диспетчера: `{secondNum}`\nТекущее число: `{operNum}`', color=disnake.Color.green()))

    @commands.command(name='world', aliases=['wd', 'ворлд'])
    async def wordl(self, ctx):

        userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        if len(userEnter.split()) >= 1:
            if userEnter.split()[0] == 'add':
                listEntered = userEnter.split()
                try: listEntered.remove(ctx.message.content.split(' ')[0])
                except: pass

                with open('./content/WORLD/dataSet.txt', 'r', encoding='UTF-8') as f:
                    wordsData = f.read()
                    
                addCount = 0
                rejectCount = 0

                for item in listEntered:
                    threshold = 0.50

                    morph = pymorphy3.MorphAnalyzer()
                    p = morph.parse(item.lower())
                    score = p[0].score

                    if score >= threshold and item.lower() not in wordsData.split():
                        wordsData += f' {item.lower()}'
                        addCount += 1
                    else: rejectCount += 1
                
                with open('./content/WORLD/dataSet.txt', 'w', encoding='UTF-8') as f:
                    f.write(wordsData)
                return await ctx.send(f'Слов добавлено: {addCount}\nслов откланено: {rejectCount}')
            elif userEnter == 'count':
                with open('./content/WORLD/dataSet.txt', 'r', encoding='UTF-8') as f:
                    wordsData = f.read()
                return await ctx.send(f'Всего слов: {len(wordsData.split())}')


        with open('./content/WORLD/dataSet.txt', 'r', encoding='UTF-8') as f:
            wordsData = (f.read()).split()

        word = random.choice(wordsData)
        countTry = len(word)//3 + 4
        enteredWord = ['⬛'*len(word)]*countTry
        def getText():
            text = ''
            for item in enteredWord:
                text += f'{item}\n'
            return text
        
        openWord = ['- ']*len(word)
        maybeWord = []
        def getMaybeWord():
            openW = ''
            maybeW = ''
            for item in openWord: openW += f'{item} '
            for item in maybeWord: maybeW += f'{item} '
            else: 
                if maybeW == '': maybeW = 'Нет'

            return f'Открытое: {openW}'


        def check(e):
            return e.author.id == ctx.author.id

        originalMessage = await ctx.send(embed=disnake.Embed(title='Слово задано', description=f'На каждую попытку: 180 секунд.\nСлово обладает: {len(word)} буквами.\nНапишите **стоп**, для завершения\n\n{getText()}').set_footer(text=getMaybeWord()))

        tryEnter = 0
        win = False
        while True:
            await originalMessage.edit(embed=disnake.Embed(title='Слово задано', description=f'На каждую попытку: 3 минуты.\nСлово обладает: {len(word)} буквами.\nНапишите **стоп**, для завершения\n\n{getText()}').set_footer(text=getMaybeWord()))

            if win: return await ctx.send(embed=disnake.Embed(description=f'## Победа!\nДа, это было действительно слово: [{word}]', color=disnake.Color.green()))
            elif tryEnter == countTry and not win:
                return await ctx.send(embed=disnake.Embed(description=f'## Вы проиграли...\nЗагаданным словом было: [{word}]', color=disnake.Color.red()))
            
            try: responce =  await self.bot.wait_for('message', check=check, timeout=180)
            except TimeoutError: return await ctx.send(embed=disnake.Embed(description=f'Время закончилось. \nЭтим словом было: "{word}"', color=disnake.Color.dark_blue())) 
            request = responce.content

            if request.lower() in ['закончить', 'стоп']:
                return await ctx.send(embed=disnake.Embed(description=f'Игра была закончена пользователем. Словом было: {word}'))

            brc = False
            for key in request:
                if len(request)//2 < request.count(key): brc = True
            if brc: continue

            if len(request) == len(word):
                listReq = list(request.lower())
                listWord = list(word.lower())
                checkWord = ''

                if request.lower() == word.lower(): 
                    win = True

                for index, item in enumerate(listWord):
                    if listReq[index] == item:
                        checkWord += '🟩'
                        openWord[index] = f'[{listReq[index]}] '
                    elif listReq[index] in listWord:
                        checkWord += '🟨'
                        if listReq[index] not in maybeWord: maybeWord.append(f'[{listReq[index]}]')
                    else:
                        checkWord += '🟥'
                enteredWord[tryEnter] = checkWord
                tryEnter += 1

    @commands.command(name='r34')
    async def rule34(self, ctx):
        try: 
            if ctx.channel.guild:
                if not ctx.channel.nsfw and ctx.channel.id != 1205649033125830706:
                    return await ctx.send('Только ЛС или в NSFW канале.')
        except: pass
        
        nameEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
        name = nameEnter.split()[0]

        try:
            if name == ctx.message.content.split(' ')[0]:
                pid = random.randint(1, 200)
                url = 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index'
                params = {
                    "json":1,
                    "limit":50,
                    "pid":pid,
                    "tags":"-gay -ai_generated -yaoi -ambiguous_gender -hyper_muscles -armpit_hair -hyper_penis -hyper -male/male -fart -fart_fetish -fat -foot_fetish -overweight -trap -futanari"
                    }
                response = requests.get(f'{url}', params=params).json()
                select = random.choice(range(len(response)-1))
            elif name.lower() == 'gif':
                pid = random.randint(1, 200)
                url = 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index'
                params = {
                    "json":1,
                    "limit":50,
                    "pid":pid,
                    "tags":"-gay -ai_generated -yaoi -ambiguous_gender -hyper_muscles -armpit_hair -hyper_penis -hyper -male/male -fart -fart_fetish -fat -foot_fetish -overweight -trap -futanari gif -video"
                    }
                response = requests.get(f'{url}', params=params).json()
                select = random.choice(range(len(response)-1))
            elif name.lower() == "video":
                pid = random.randint(1, 200)
                url = 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index'
                params = {
                    "json":1,
                    "limit":50,
                    "pid":pid,
                    "tags":"-gay -ai_generated -yaoi -ambiguous_gender -hyper_muscles -armpit_hair -hyper_penis -hyper -male/male -fart -fart_fetish -fat -foot_fetish -overweight -trap -futanari video"
                    }
                response = requests.get(f'{url}', params=params).json()
                select = random.choice(range(len(response)-1))
            else:
                pid = random.randint(1, 200)
                url = 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index'
                params = {
                    "json":1,
                    "limit":50,
                    "pid":pid,
                    "tags":"-gay -ai_generated -yaoi -ambiguous_gender -hyper_muscles -armpit_hair -hyper_penis -hyper -male/male -fart -fart_fetish -fat -foot_fetish -overweight -trap -futanari"
                    }
                response = requests.get(f'{url}', params=params).json()
                select = random.choice(range(len(response)-1))
            # responseFile = requests.get(response[select]['file_url'])
            # extension = response[select]['file_url'].split('.')[-1]

            # with open(f'./content/TEMPR34FILE/randomImage.{extension}', 'wb') as f:
            #     f.write(responseFile.content)

            await ctx.send(f'{response[select]['file_url']}')
        except:
            await ctx.send('Похоже лимит сайта немного превышен. Попробуйте чуть позже.')

    @commands.command(name='dice')
    async def dice(self, ctx):
        try:
            userEnter = ctx.message.content.replace(f'{ctx.message.content.split(' ')[0]} ', '')
            if userEnter == ctx.message.content.split(' ')[0]:
                return await ctx.send(embed=disnake.Embed(
                    description='```Доступные варианты дайсов: ```\n-> `cdn`\n c — количество кубов, n — сторон (1-n)'
                    ))
            dices = str(userEnter).split()
            text_output = ''
            for item in dices:
                try:
                    out = []
                    count, value = item.split('d')
                    for index in range(int(count)):
                        out.append(random.randint(1, int(value)))
                    t_out = ''
                    for i, v in enumerate(out): 
                        if len(out)-1 != i: t_out += f'{v}, '
                        else: t_out += f'{v}'
                    text_output += f'**[{item}]** -> `{t_out}`\n'
                except:
                    text_output += f'**[{item}]** i> ошибочный ввод\n'

            await ctx.send(embed=disnake.Embed(description=text_output))
        except HTTPException:
            await ctx.send(embed=disnake.Embed(description='Превышен лимит символов. \nУменьшите запросы.', colour=disnake.Color.dark_red()))

# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Fun(bot))
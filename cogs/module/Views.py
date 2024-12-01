import disnake
from disnake.ext import commands
from .ponymon.Ponymons import *

# Заглушка для динамической подгрузки
class Cock(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot


#! Слушающий класс для выбора покемонов из категории боевых групп.
class SelectMassPokemonsViewfightGroup(disnake.ui.View):
    def __init__(self, options:list, user:int):
        super().__init__(timeout=None)
        self.add_item(SelectMassPokemonsMenuFightGroup(options, user))
class SelectMassPokemonsMenuFightGroup(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int):
        self.index = 0
        self.user = user

        super().__init__(
            placeholder=f'Выбрать из {len(options)}',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        _, index, hp_atk, rankCOM = inter.data.values[0].split('|')
        ids, seq = rankCOM.split('-')


        userBag = (await giveUserBag(self.user))[ids][seq]
        params = userBag['params']
        pokes = f'**`>>` `{userBag['name']}` `({userBag['other_param']['lvl']}) lvl`**\n| 💖 Здоровье: `[{params['healpoint']:,}]` `[{params['regen']}/h]`\n| 🔪 Атака: `[{params['attack']:,}]`\n| 🛡 Процент защиты: `[{params['armor']:.0%}]`\n| 🦋 Шанс уклонения: `[{params['evasion']:.0%}]`\n| 🍃 Скорость: `[{(1/params['speed']):.0%}]`\n'

        slots = await takeFightGroup(user=self.user)
        text = ''
        for index, item in enumerate(slots):
            if slots[item] is None:
                text += f'**`{index+1}:` `Пустой слот.`**\n| <None>\n'
            else:
                localIds, localSeq = slots[item].split('-')
                try: localUserBag = (await giveUserBag(self.user))[localIds][localSeq]
                except:
                    text += f'**`{index+1}:` `Пустой слот.`**\n| <None>\n'
                    await saveFightGroup(rankCOM=None, user=self.user, slot=item[-1])
                    continue
                localParams = localUserBag['params']

                text += f'**`{index+1}:` `{localUserBag['name']}` `({localUserBag['other_param']['lvl']}) lvl`**\n| 💖 Здоровье: `[{localParams['healpoint']:,}]` `[{localParams['regen']}/h]`\n| 🔪 Атака: `[{localParams['attack']:,}]`\n| 🛡 Процент защиты: `[{localParams['armor']:.0%}]`\n| 🦋 Шанс уклонения: `[{localParams['evasion']:.0%}]`\n| 🍃 Скорость: `[{(1/localParams['speed']):.0%}]`\n\n'

        embed = disnake.Embed(description=f'```Выбранный покемон:``` {pokes}\n```Слоты```\n{text}', colour=disnake.Colour.dark_red())

        await inter.response.edit_message(embed=embed, view=None)
        await setButtonsFightGroup(message=inter.message, data=(rankCOM, self.user))

#! Слушатель для команды работы покемонов 
class SelectMassPokemonsViewWorkGroup(disnake.ui.View):
    def __init__(self, options:list, user:int):
        super().__init__(timeout=None)
        self.add_item(SelectMassPokemonsMenuWorkGroup(options, user))
class SelectMassPokemonsMenuWorkGroup(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int):
        self.index = 0
        self.user = user

        super().__init__(
            placeholder=f'Выбрать из {len(options)}',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        _, index, hp_atk, rankCOM = inter.data.values[0].split('|')
        text = await setDescriptionTextWorkGroup(user=inter.author.id)

        embed = disnake.Embed(
            title='На какой из 3-х слотов вы желаете его поставить?',
            description=text,
            colour=disnake.Colour.fuchsia()
            )

        await inter.response.edit_message(embed=embed, view=None)
        await setButtonsWorkGroup(message=inter.message, rare=rankCOM, user=inter.author.id)
        
#! Слушатель для продажи одного покемона
class SelectMassPokemonsViewCorrectSell(disnake.ui.View):
    def __init__(self, options:list, user:int):
        super().__init__(timeout=None)
        self.add_item(SelectMassPokemonsMenuCorrectSell(options, user))
class SelectMassPokemonsMenuCorrectSell(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int):
        self.index = 0
        self.user = user

        super().__init__(
            placeholder=f'Выбрать из {len(options)-1}',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        command, index, rankCOM, price = inter.data.values[0].split('|')

        if command == 'cannelSell':
            embed = disnake.Embed(description='**Процесс продажи был отменен.**')
            await inter.response.edit_message(embed=embed, view=None)
            return
        else:
            
            await inter.response.edit_message(view=None)
            await endSellPokeAfterSelect(pokemon_ids=rankCOM, user=self.user, message=inter.message)

#! Для переплавки покемона
class SelectMassPokemonsViewCorrectRemelting(disnake.ui.View):
    def __init__(self, options:list, user:int):
        super().__init__(timeout=None)
        self.add_item(SelectMassPokemonsMenuCorrectRemelting(options, user))
class SelectMassPokemonsMenuCorrectRemelting(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int):
        self.index = 0
        self.user = user

        super().__init__(
            placeholder=f'Выбрать из {len(options)-1}',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        command, index, rankCOM, price = inter.data.values[0].split('|')

        if command == 'cannelRem':
            embed = disnake.Embed(description='**Процесс переплавки был отменен.**')
            await inter.response.edit_message(embed=embed, view=None)
            return
        else:
            
            await inter.response.edit_message(view=None)
            await endRemPokeAfterSelect(pokemon_ids=rankCOM, user=self.user, message=inter.message)

#! Слушатель для трейдов между игроками
class SelectMassPokemonsViewSelectPoke(disnake.ui.View):
    def __init__(self, options:list, user:int):
        super().__init__(timeout=None)
        self.add_item(SelectMassPokemonsMenuSelectPoke(options, user))
class SelectMassPokemonsMenuSelectPoke(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int):
        self.index = 0
        self.user = user

        super().__init__(
            placeholder=f'Выбрать из {len(options)}х',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        command, index, rankCOM, users = inter.data.values[0].split('|')

        user1, user2 = users.split('-')

        await inter.response.edit_message(view=None)
        await confirmActions(user1=user1, user2=user2, rankCOM=rankCOM, message=inter.message)
 
#! Слушатель для улучшаемого покемона
class ViewSelectToSupPoke(disnake.ui.View):
    def __init__(self, options:list, user:int, userBag, diePokes:str):
        super().__init__(timeout=None)
        self.add_item(SelectToSupPoke(options, user, userBag, diePokes))
class SelectToSupPoke(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int, userBag, diePokes):
        self.index = 0
        self.user = user
        self.userBag = userBag
        self.diePoes = diePokes

        super().__init__(
            placeholder=f'Выбрать из {len(options)}',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        _, index, lvl, upPoke = inter.data.values[0].split('|')

        ids, seq = upPoke.split('-')
        sups = self.userBag[ids][seq]
        if sups['rank'] in ['S', 'EX'] and sups['other_param']['supports'] == rrNeedSUP(sups['rank']):
            return await inter.response.send_message(embed=disnake.Embed(description='**Увы, но покемон на пике. Дальше некуда**'), ephemeral=True)

        diePokes = self.userBag[self.diePoes]

        options = []
        for index, item in enumerate(diePokes):
            ardDiePoke = f'{self.diePoes}-{item}'
            if upPoke == ardDiePoke: continue
            options.append(
                disnake.SelectOption(
                    label=f'({index+1}) {diePokes[item]['name']} ({diePokes[item]['other_param']['supports']} sup)',
                    value=f'poke|{index+1}|{diePokes[item]['other_param']['lvl']}|{ardDiePoke}|{upPoke}'
                    )
                )
        options.sort(key=lambda x: int(x.value.split('|')[2]), reverse=True)
        if len(options) == 0:
            return await inter.response.edit_message(embed=disnake.Embed(description=f'**Похоже, вы не обладаете иными понимонами, из этой категории [{sups['name']}]**'), components=None)

        view = ViewSelectToDiePoke(options=options, user=inter.author.id)
        await inter.response.edit_message(view=None)
        await updateMessage(inter.message, view)

#! Слушатель для уничтожаемого покемона
class ViewSelectToDiePoke(disnake.ui.View):
    def __init__(self, options:list, user:int):
        super().__init__(timeout=None)
        self.add_item(SelectToDiePoke(options, user))
class SelectToDiePoke(disnake.ui.StringSelect):
    def __init__(self, options:list, user:int):
        self.index = 0
        self.user = user

        super().__init__(
            placeholder=f'Выбрать из {len(options)}',
            min_values=1,
            max_values=1,
            options=options
            )
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id: return

        _, index, hp_atk, diePoke, upPoke = inter.data.values[0].split('|')

        userBag = await giveUserBag(user=self.user)

        if upPoke == diePoke: await inter.response.send_message(ephemeral=True, embed=disnake.Embed(description='**Нельзя выберать того же покемона.**'))

        await inter.response.defer()
        await EndSopportSelect(message=inter.message, user=inter.author.id, ids=[upPoke, diePoke])

#! Слушатель для лидерборда
class DropDownViewLeader(disnake.ui.View):
    def __init__(self, map: map, user:int, time:float):
        super().__init__(timeout=None)
        self.add_item(DropDownMenuLeader(map, user, time))
class DropDownMenuLeader(disnake.ui.StringSelect):
    def __init__(self, map:map, user:int, time:float):
        self.index = 0
        self.map = map
        self.user= user
        self.time= time

        # disnake.SelectOption(label='Аркады', value='arcade', description='Сортировка по самому большому винстрику')
        options = [
            disnake.SelectOption(label='Опыт', value='exp', description='Сортировка по свободному опыту'),
            disnake.SelectOption(label='Валюта', value='money', description='Сортировка по валюте [1sl = 3200es, 1sh = 400es]'),
            disnake.SelectOption(label='Характиристикам', value='stat', description='Топ 1, по каждой характиристике')
            ]
        super().__init__(
            placeholder='Сортировка по...',
            min_values=1,
            max_values=1,
            options=options
            )
        
        if map is None:
            raise 'Not have map: [components] [embed]'
        
        
    async def callback(self, inter: disnake.MessageInteraction):
        if self.user != inter.author.id:
            await inter.response.send_message('Не вы вызвали таблицу', ephemeral=True)
        if self.values[0] == 'exp':
            embed= self.map[0]
        elif self.values[0] == 'money':
            embed= self.map[1]
        # elif self.values[0] == 'arcade':
        #     embed= self.map[2]
        elif self.values[0] == 'stat':
            embed= self.map[2]


        if self.time < time.time():
            embed = disnake.Embed(description='**Вышло время взаимодействия**', colour=disnake.Color.red())
            await inter.response.edit_message(embed=embed, view=None)
            return
        else:
            await inter.response.edit_message(embed=embed)



# unstatic load module, it`s just for simplicity
def setup(bot:commands.Bot):
    bot.add_cog(Cock(bot))
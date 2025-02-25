import disnake
from disnake.ext import commands
import random
import time
import json
import sqlite3
from time import sleep

from .module import REQ_database as Rdb

db = Rdb.DataBase

def banList(UID:int) -> bool:
    with open('../PonyashkaDiscord/config/message_cfg.json') as file:
        config = json.load(file)
        file.close()
        if UID in config['BanList']:
            return False
        return True
    
class Message(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Установка главных переменных
        user = message.author.id
        user_name = message.author.name
        timeMessage = time.strftime('%H:%M', time.gmtime(round(time.time() + 36000)))
        
        # Проверка на ботовость того, кто отправил сообщение
        if not message.author.bot: db.Check(user_id=user, user_name=user_name).user()
        else: return
            
        try:
            con = sqlite3.connect('../PonyashkaDiscord/_system.db')
            cur = con.cursor()
            cur.execute(f"UPDATE channel_data SET count = count + 1 WHERE ID = {message.channel.id}")
            con.commit()
        except:
            pass

        # Проверка на упоминание пользователя и инкремент при правде
        mentioned = message.raw_mentions
        if (mentioned is not None):
            try:
                ment= message.raw_mentions[0]
                user_data = db.Info(user_id=user).user()
                if (user_data[2] < round(time.time())) and ment != user:
                    db.User(user_id=ment, value=1, column='mentions').upParam()
                    db.User(user_id=user, value=30).lockMent()
            except:
                pass
        # Проверка на личные сообщения
        if message.guild is None:
            if message.author.id != 374061361606688788: 
                print(f'<< Сообщение от {message.author.name} >> [{message.content}]')
                return
            else: return



        # Проверка актуальности уровня
        userExpNow= db.Info(user_id=user).takeFromRPG(table='user_main_info')[2]
        userLvlNow= db.Info(user_id=user).takeFromRPG(table='user_main_info')[1]
        userLvl = db.Info().positionLVL(exp=userExpNow)

        if userLvl != userLvlNow:
            db.User(column='lvl', user_id=user, value=userLvl).setParam()
            embed = disnake.Embed(
            title=f'Изменение силы души у: \n``{message.author.name}`` | ``{message.author.nick}``',
            description=f'Сила души изменилась\n```с {userLvlNow} до {userLvl}```',
            colour=disnake.Color.dark_gold()
            )
            embed.set_thumbnail(url=message.author.avatar)
            print(f'Code 1 >>> Обновление уровня у пользователя {message.author.name} ({userLvlNow}→{userLvl})')
            await self.bot.get_channel(992673176448417792).send(embed=embed)

        # Загрузки конфигурацции
        with open(f'../PonyashkaDiscord/config/levels/{message.guild.id}.json') as file:
            configLVL = json.load(file)
            level_config = configLVL['levels']

        range_item_lvl = []
        range_item_lvl_bool = []
        user_role = []

        # Заполнение списка ролями пользователя
        for item in message.author.roles: user_role.append(item.id)
        # Разбиваем ключи на список связанных чисел, для проверки диапазона
        for item in level_config: range_item_lvl.append(item.split('-'))
        # Проверка диапазона по связанным ключам
        for item in range_item_lvl: range_item_lvl_bool.append(int(item[0]) <= userLvl <= int(item[1]))
        else: del range_item_lvl

        # from .Message import banList
        ban_list = banList(user)

        # Изменение ролей
        if ban_list:
            for index, item in enumerate(level_config):
                try:
                    if not level_config[item] in user_role and range_item_lvl_bool[index]:
                        await message.author.add_roles(self.bot.get_guild(message.guild.id).get_role(level_config[item]))
                    elif level_config[item] in user_role and not range_item_lvl_bool[index]:
                        await message.author.remove_roles(self.bot.get_guild(message.guild.id).get_role(level_config[item]))
                except:
                    print('\t\t< ↓ Error ↓ >\t\t')
                    print(f'authorError={message.author.name}')
                    print(f'level_config[{item}]({type(level_config[item])}) = {level_config[item]}')
                    print('\t\t< ↑ Error ↑ >\t\t')

        # Загрузка конфигов
        with open('../PonyashkaDiscord/config/message_cfg.json') as file:
            config = json.load(file)
        # Буффер сообщений.
        with open('../PonyashkaDiscord/config/buffer.json', encoding='UTF-8') as file:
            buffer = json.load(file)

        # Проверка на создателя
        if message.author.id != 374061361606688788:
            # Выпадения опыта ~30% и денег с шансом ~10%
            # Шанс выпадения шарда с шансом 0,005%
            valueRandomXP = random.randint(1, 1000)
            valueRandomM = random.randint(1, 1000)
            valuePupet = random.randint(1,5)

            def check_over_buffer():
                if buffer['bufferSpam'].count(message.author.id) == 3: return False
                else: return True
            def append_buffer(buffer_cfg):
                if len(buffer_cfg['bufferSpam']) < 3:
                    buffer['bufferSpam'].append(message.author.id)
                else:
                    buffer['bufferSpam'].pop(0)
                    buffer['bufferSpam'].append(message.author.id)
                with open('../PonyashkaDiscord/config/buffer.json', 'w', encoding='UTF-8') as file:
                    json.dump(buffer_cfg, file)

            checkOverBuffer = check_over_buffer()
            if valueRandomXP <= config['exp'] and checkOverBuffer:  # Выпадение опыта ')
                db.Exp(user_id=user, value=valuePupet).add()
                db.Bot(value=10).lock()
                append_buffer(buffer)
                return
            elif valueRandomM <= config['money'] and checkOverBuffer:  # Выпадение денег
                val = random.randint(0, 1000)
                if val <= config['super_money']:
                    db.Money(user=user, currency='SHARD', value=valuePupet).add()
                    return
                db.Money(user=user, value=valuePupet).add()
                db.Bot(value=10).lock()
                append_buffer(buffer)
                return
        

        # Проверка таймера реакций
        if db.Bot(self).checkLock():
            return
            
            
        # Проверка на разрешенный канал
        file = open(f"../PonyashkaDiscord/acesses/{message.guild.id}.txt", mode='a+')
        file.seek(0)
        susc = []
        for item in file:
            susc.append(item.rstrip())
        file.close()
        # Проверка на канал в котором произошел ивент
        if str(message.channel.id) not in susc:
            return
        

        # Исключение частых символов
        simbol = '/.,&?!()'
        content = message.content
        for item in simbol:
            content = content.replace(item, '')
        # простые слова-реакции
        file = open('../PonyashkaDiscord/React_text/Base_react_pony.txt', mode='r', encoding='utf-8')
        num = random.randint(1, 1000)
        mass_react = []
        for ent in file:
            mass_react.append(ent.rstrip())
        file.close()
        

        # Случайные реакции поняшки
        if num <= config['text_react_chance']:
            await message.channel.send(f"_{random.choice(mass_react)}_")
            db.Bot(value=config['text_react_timer']).lock()
            return
        if num <= config['emoji_react_chance']:
            emoji = message.guild.emojis
            await message.channel.send(random.choice(emoji))
            db.Bot(value=config['emoji_react_timer']).lock()
            return
        # if num <= config['reaction_react_chance']:
        #     emoji = message.guild.emojis
        #     await message.add_reaction(random.choice(emoji))
        #     db.Bot(value=config['reaction_react_timer']).lock()
        #    return

        
        # Слова на которые откликается бот
        react_role = config['reaction_word']
        if message.author.id == 374061361606688788:
            return
        # Отклик поняшки на слова, что указаны в config.json["reaction_word"]
        for content in content.split(' '):
            for react in react_role:
                if content.lower() == react:
                    choice = random.randint(1, 4)
                    emoji = message.guild.emojis
                    if choice == 1:
                        await message.channel.send(f"_{random.choice(mass_react)}_")
                        db.Bot(value=30).lock()
                        return
                    # elif choice == 2:
                    #     await message.channel.send(random.choice(emoji))
                    #     db.Bot(value=20).lock()
                    #     return
                    # elif choice == 3:
                    #     await message.add_reaction(random.choice(emoji))
                    #     db.Bot(value=20).lock()
                    #     return


# Загрузка кога в основное ядро по команде
def setup(bot:commands.Bot):
    bot.add_cog(Message(bot))
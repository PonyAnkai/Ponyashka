import disnake
from disnake.ext import commands

import sqlite3
import time

con = sqlite3.connect('../PonyashkaDiscord/_system.db')
conRPG = sqlite3.connect('../PonyashkaDiscord/_rpg.db')
cur = con.cursor()
curRPG = conRPG.cursor()

class DataBase:
    class Check:
        # Передать id пользователя и name пользователя
        def __init__(self, user_id, user_name=None):
            self.user_id = user_id
            self.user_name = user_name
            
        def user(self):
            num = 0
            
            #! Основная таблица юзера в таблицах системы и не РПГ модуле
            cur.execute(f"SELECT * FROM user_ment WHERE uid = {self.user_id}")
            if cur.fetchone() is None:
                num+= 1
                cur.execute("INSERT INTO user_ment VALUES (?, ?, ?)", (self.user_id, 0, 0))
            cur.execute(f'SELECT uid FROM user_wins WHERE uid = {self.user_id}')
            if cur.fetchone() is None:
                num+= 1
                cur.execute("INSERT INTO user_wins VALUES (?, ?, ?, ?)", (self.user_id, 0, 0, 0))
            cur.execute(f'SELECT uid FROM user_wins_max WHERE uid = {self.user_id}')
            if cur.fetchone() is None:
                num+= 1
                cur.execute("INSERT INTO user_wins_max VALUES (?, ?, ?, ?)", (self.user_id, 0, 0, 0))


            #? Pokefile
            curRPG.execute(f'SELECT * FROM user_poke WHERE UID = {self.user_id}')
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f"INSERT INTO user_poke (UID) VALUES ({self.user_id})")


            #? RPG module
            curRPG.execute(f'SELECT * FROM user_active_inventory WHERE UID = {self.user_id}')
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f"INSERT INTO user_active_inventory (UID) VALUES ({self.user_id})")
            curRPG.execute(f'SELECT * FROM user_diplomaty WHERE UID = {self.user_id}')
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f"INSERT INTO user_diplomaty (UID) VALUES ({self.user_id})",)
            curRPG.execute(f'SELECT * FROM user_equipment WHERE UID = {self.user_id}')
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f"INSERT INTO user_equipment (UID) VALUES ({self.user_id})")
            curRPG.execute(f"SELECT * FROM user_main_info WHERE UID = {self.user_id}")
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f"INSERT INTO user_main_info (UID) VALUES ({self.user_id})")
            curRPG.execute(f"SELECT * FROM user_money WHERE UID = {self.user_id}")
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f'INSERT INTO user_money (UID) VALUES ({self.user_id})')
            curRPG.execute(f"SELECT * FROM user_parametr WHERE UID = {self.user_id}")
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f'INSERT INTO user_parametr (UID) VALUES ({self.user_id})')
            curRPG.execute(f'SELECT * FROM user_blocktime WHERE UID = {self.user_id}')
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f'INSERT INTO user_blocktime (UID) VALUES ({self.user_id})')
            curRPG.execute(f'SELECT * FROM user_terms WHERE UID = {self.user_id}')
            if curRPG.fetchone() is None:
                num+=1
                curRPG.execute(f'INSERT INTO user_terms (UID) VALUES ({self.user_id})')
            curRPG.execute(f'SELECT * FROM user_ds_info WHERE UID = {self.user_id}')
            names_update = curRPG.fetchone()
            if not names_update:
                num+=1
                curRPG.execute('INSERT INTO user_ds_info VALUES (?, ?)', (self.user_id, self.user_name))
            elif names_update:
                if names_update[1] != self.user_name:
                    num+=1
                    curRPG.execute(f"UPDATE user_ds_info SET NAME = '{self.user_name}' WHERE UID = '{self.user_id}'")
            # curRPG.execute(f'SELECT * FROM user_reputation WHERE UID = {self.user_id}')
            # if curRPG.fetchone() is None:
            #     num+=1
            #     curRPG.execute(f"INSERT INTO user_reputation (UID) VALUES ({self.user_id})")


            conRPG.commit()
            con.commit()
            if num!= 0:
                print(f'Create new record {self.user_id} / Update poss: {num}')
                return False
            return True
        
        def bot(self):
            cur.execute('SELECT * FROM bot')
            if cur.fetchone() is None:
                cur.execute("INSERT INTO bot VALUES (?, ?, ?, ?)", (0, 0, 0, 0))
                con.commit()
                return True
            else:
                return False
            
    class Money:
        # Передать id пользователя по которому и будут совершаться дальнейшие операции
        def __init__(self, *, user: int, currency= 'ESSENCE', value= 0):
            self.user= user
            self.currency= currency
            self.value= value

        # essence, shard, soul, cristall
        def add(self) -> bool:
            if self.currency in ["ESSENCE", "SHARD", "SOUL", "CRISTALL_SOUL", "COU", "VCOIN", "ACOIN", "TCOIN"]:
                curRPG.execute(f'UPDATE user_money SET {self.currency} = {self.currency} + {self.value} WHERE UID = {self.user}')
            else: return False
            conRPG.commit()
            return True
        
        def sub(self) -> bool:
            if self.currency in ["ESSENCE", "SHARD", "SOUL", "CRISTALL_SOUL", "COU", "VCOIN", "ACOIN", "TCOIN"]:
                curRPG.execute(f'SELECT {self.currency} FROM user_money WHERE UID = {self.user}')
                if curRPG.fetchone()[0] - self.value >= 0: 
                    curRPG.execute(f'UPDATE user_money SET {self.currency} = {self.currency} - {self.value} WHERE UID = {self.user}')
                else: return False
            else: return False
            conRPG.commit()
            return True
        def update(self) -> bool:
            if self.currency in ["ESSENCE", "SHARD", "SOUL", "CRISTALL_SOUL", "COU", "VCOIN", "ACOIN", "TCOIN"]:
                curRPG.execute(f'UPDATE user_money SET {self.currency} = {self.value} WHERE UID = {self.user}')
            else: return False
            conRPG.commit()
            return True
        
        def have(self) -> int:
            curRPG.execute(f'SELECT {self.currency} FROM user_money WHERE UID = {self.user}')
            return curRPG.fetchone()[0]
        
    class Info:
        def __init__(self, user_id= None):
            self.user_id= user_id
        def takeFromRPG(self, table:str) -> tuple:
            if self.user_id is None:
                curRPG.execute(f'SELECT * FROM {table}')
                return curRPG.fetchall()
            curRPG.execute(f'SELECT * FROM {table} WHERE UID = {self.user_id}')
            return curRPG.fetchone()    
        
        def takeFromSystem(self, table:str) -> tuple:
            if self.user_id is None:
                cur.execute(f'SELECT * FROM {table}')
                return cur.fetchall()
            cur.execute(f'SELECT * FROM {table} WHERE UID = {self.user_id}')
            return cur.fetchone()

        def positionLVL(self, exp:int) -> int:
            curRPG.execute(f'SELECT max(lvl) FROM levels WHERE expTotal - {exp} <= 0')
            lvl = curRPG.fetchone()[0]
            if lvl is None:
                return 0
            return lvl
        def user(self):
            cur.execute(f'SELECT * FROM user_ment WHERE uid = {self.user_id}')
            return cur.fetchone()
    
    class Poke:
        def __init__(self, user:int) -> None:
            self.user = user

        def add(self, value, column='STRIKE') -> bool:
            curRPG.execute(f'UPDATE user_poke SET {column} = {column} + {value} WHERE UID = {self.user}')
            conRPG.commit()
            return True
        def sub(self, value, column='STRIKE') -> bool:
            curRPG.execute(f'SELECT {column} FROM user_poke WHERE UID = {self.user}')
            if curRPG.fetchone()[0] - self.value >= 0: 
                curRPG.execute(f'UPDATE user_poke SET {column} = {column} - {value} WHERE UID = {self.user}')
            else: return False
            conRPG.commit()
            return True
        def update(self, value=0, time_bool:bool=True) -> bool:
            if time_bool: curRPG.execute(f'UPDATE user_poke SET TIMESTAMP = {round(time.time())} + {value} WHERE UID = {self.user}')
            else: curRPG.execute(f'UPDATE user_poke SET STRIKE = {value} WHERE UID = {self.user}')
            conRPG.commit()
            return True
        
        def takeAll(self) -> tuple:
            curRPG.execute(f'SELECT * FROM user_poke WHERE UID = {self.user}')
            return curRPG.fetchone()

    class Bot:
        def __init__(self, value=0):
            self.value = value
        
        def lock(self) -> bool:
            cur.execute(f'UPDATE bot SET lock_tmreact = {round(time.time() + self.value)}')
            con.commit()
            return True

        def checkLock(self) -> bool:
            cur.execute(f'SELECT lock_tmreact FROM bot')
            if round(time.time()) > cur.fetchone()[0]: return False
            else: return True
        
        def info(self):
            cur.execute('SELECT * FROM bot')
            return cur.fetchone()
        
        class set:
            def __init__(self, column=None, value=0):
                self.column = column
                self.value = value
            def add(self):
                cur.execute(f'UPDATE bot SET {self.column} = {self.column} + {self.value}')
                con.commit()
                return True
            def sub(self):
                cur.execute(f'UPDATE bot SET {self.column} = {self.column} - {self.value}')
                con.commit()
                return True
            def update(self):
                cur.execute(f'UPDATE bot SET {self.column} = {self.value}')
                con.commit()
                return True
            
    class User:
        def __init__(self, column=None, user_id=None, value=0):
            self.user_id = user_id
            self.value = value
            self.column = column

        def setParam(self):
            curRPG.execute(f'UPDATE user_main_info SET {self.column} = {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
            return True
        
        def upParam(self):
            curRPG.execute(f'UPDATE user_main_info SET {self.column} = {self.column} + {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
            return True
        
        def downParam(self):
            curRPG.execute(f'UPDATE user_main_info SET {self.column} = {self.column} - {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
            return True
        
        def lockMent(self):
            times = round(time.time()) + self.value
            cur.execute(f'UPDATE user_ment SET MentTimer = {times} WHERE uid = {self.user_id}')
            conRPG.commit()
            return True

    class Fun:
        def __init__(self, user: int, strick=None):
            self.user = user
            self.strick = strick
        
        def add(self):
            if self.strick == 'coin':
                cur.execute(f'UPDATE user_wins SET coin_str = coin_str + 1 WHERE uid = {self.user}')
                con.commit()
                return True
            elif self.strick == 'casino':
                cur.execute(f'UPDATE user_wins SET casino_str = casino_str + 1 WHERE uid = {self.user}')
                con.commit()
                return True
            elif self.strick == 'rolete':
                cur.execute(f'UPDATE user_wins SET RusRolete = RusRolete + 1 WHERE uid = {self.user}')
                con.commit()
                return True
            return False
        
        def clear(self):
            if self.strick == 'coin':
                cur.execute(f'UPDATE user_wins SET coin_str = 0 WHERE uid = {self.user}')
                con.commit()
                return True
            elif self.strick == 'casino':
                cur.execute(f'UPDATE user_wins SET casino_str = 0 WHERE uid = {self.user}')
                con.commit()
                return True
            elif self.strick == 'rolete':
                cur.execute(f'UPDATE user_wins SET RusRolete = 0 WHERE uid = {self.user}')
                con.commit()
                return True
            return False
        
        def get(self):
            cur.execute(f'SELECT * FROM user_wins WHERE uid = {self.user}')
            return cur.fetchone()
        
        def maxis(self):
            ls = ('coin_str_max', 'casino_str_max', 'RusRolete_max')

            cur.execute(f'SELECT * FROM user_wins_max WHERE uid = {self.user}')
            max_str = list(cur.fetchone())
            max_str.pop(0)
            cur.execute(f'SELECT * FROM user_wins WHERE uid = {self.user}')
            user_str = list(cur.fetchone())
            user_str.pop(0)

            for i in range(len(max_str)):
                if max_str[i] < user_str[i]:
                    cur.execute(f'UPDATE user_wins_max SET {ls[i]} = {user_str[i]} WHERE uid = {self.user}')
    
    class Exp:
        def __init__(self, user_id:int, value:int) -> None:
            self.user_id = user_id
            self.value = value
        
        def add(self) -> bool:
            curRPG.execute(f'UPDATE user_main_info SET EXP = EXP + {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
            return True
        def sub(self) -> bool:
            curRPG.execute(f'SELECT EXP FROM user_main_info WHERE UID = {self.user_id}')
            if curRPG.fetchone() - self.value < 0:
                return False
            curRPG.execute(f'UPDATE user_main_info SET EXP = EXP - {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
            return True
        def update(self) -> bool:
            if self.value < 0:
                return False
            curRPG.execute(f'UPDATE user_main_info SET EXP = {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
            return True

    class RPG:
        def __init__(self) -> None:
            pass
        def info(self, user_id:int, table:str):
            curRPG.execute(f'SELECT * FROM {table} WHERE UID = {user_id}')
            return curRPG.fetchone()
        
        def changeUser(self, user_id:int, table:str, column:str, value):
            try:
                curRPG.execute(f'UPDATE {table} SET {column} = {value} WHERE UID = {user_id}')
                curRPG.commit()
                return True
            except:
                return False

        def addRecord(self, table:str, dict:dict):
            pass
            
    class Lock:
        '''
        Slot: 1-5
        Value: second
        '''
        def __init__(self, user_id:int, slot:int, value:int=0):
            self.user_id = user_id
            self.slot = slot
            self.value = value

        def lock(self):
            curRPG.execute(f'UPDATE user_blocktime SET SLOT_LOCk{self.slot} = {round(time.time())} + {self.value} WHERE UID = {self.user_id}')
            conRPG.commit()
        def info(self):
            if self.slot is None: curRPG.execute(f'SELECT * FROM user_blocktime WHERE UID = {self.user_id}')
            else: curRPG.execute(f'SELECT SLOT_LOCK{self.slot} FROM user_blocktime WHERE UID = {self.user_id}')
            return curRPG.fetchone()
        def ready(self):
            if self.info()[0] > round(time.time()):
                return False
            return True


    # TODO: Releaze function what can delet record from db. this need for delete data leave user.
    class DeleteData:
        def __init__(self, user_id:int):
            self.user_id = id
        
        def delete(self):
            list_rpg = ['user_money', 'user_active_inventory', 'user_blocktime', 'user_diplomaty', 'user_ds_info', 'user_equipment', 'user_main_info', 'user_parametr', 'user_reputation', 'user_terms', 'user_poke']
            list_system = ['user_ment', 'user_wins', 'user_wins_max']

            try:
                for item in list_rpg:
                    curRPG.execute(f'DELETE FROM {item} WHERE UID = {self.user_id}')
                else: conRPG.commit()
                
                for item in list_system:
                    cur.execute(f'DELETE FROM {item} WHERE UID = {self.user_id}')
                else: con.commit()
                return True
            except: return False
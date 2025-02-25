from ..base import Base
import json

from random import choice, randint

with open('../PonyashkaDiscord/content/RPG/fight/data/namingEnemy.json', 'r') as file: 
    namingEnemy = json.load(file)
with open('../PonyashkaDiscord/content/RPG/fight/enemy_content/lowEnemy.json') as file:
    assets = json.load(file)

class Goblin(Base):
    def __init__(self):
        super().__init__()

        gob = namingEnemy['Goblin']

        #? Механики монстра
        self.name = f'{gob[f'{choice(range(1, len(gob)))}']}'
        self.live = True

        #? Определение гобу особых хар-тик
        self.HP = randint(5, 15)
        self.ATK = randint(2, 5)
    
    def __str__(self) -> str:
        return f'Я {self.name}'
        
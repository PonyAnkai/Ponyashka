

chancedDropMoves = {
    'atk':100,
    'deff':80,
    'sheal':80
    }


listMoves = {
    'atk':lambda self, attack, target, who: self.attack(attack, target, who),
    'deff':lambda self, attack, target, who: self.deffence(attack, target, who),
    'sheal':lambda self, target: self.heal(target)
    }


def movesToRu(text:str) -> str:
    locale = {
        #? Стандартные действия
        'atk':'[#] Прямая атака',
        'deff':'[#] Комплексная защита',
        'sheal':'[#] Самолечение'
        }
    return locale[text]

async def decriptedCommandLocale(command) -> str:
    #? В некоторых случаях, при применении действия на себе target == None
    command, target = command.split('-')

    if command == 'atk':
        return f'{movesToRu(command)} ({int(target[-1])+1}-го противника)'
    if command == 'deff':
        return f'{movesToRu(command)} (Снижение входящего урона)'
    if command == 'sheal':
        return f'{movesToRu(command)} (Лечение 10% здоровья)'
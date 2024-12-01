
# От скорости больше х2, может появилтся двойной удар
# От медлительности больше 0.5х может появится заряженный удар, или сверх-удар судьбы, при 0.25х
chancedDropMoves = {
    'atk':100,
    'deff':100,
    'sheal':100
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
        return f'{movesToRu(command)} (Лечение здоровья)'
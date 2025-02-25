import json

def rare_glory_content(lvl, text):
    # Gray
    if lvl == 0: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(80, 80, 80), rgb(160, 160, 160), rgb(80, 80, 80));">{text}</div>', 0)
    # Green
    if lvl == 1: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(0, 140, 0), rgb(0, 255, 0), rgb(0, 140, 0));">{text}</div>', 1)
    # Cyan
    if lvl == 2: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(0, 140, 140), rgb(0, 255, 255), rgb(0, 140, 140));">{text}</div>', 2)
    # Blue
    if lvl == 3: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(0, 70, 140), rgb(0, 140, 255), rgb(0, 70, 140));">{text}</div>', 3)
    # Purple
    if lvl == 4: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(140, 0, 140), rgb(255, 0, 255), rgb(140, 0, 140));">{text}</div>', 4)
    # Gold
    if lvl == 5: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(140, 140, 0), rgb(255, 255, 0), rgb(140, 140, 0));">{text}</div>', 5)
    # Orange
    if lvl == 6: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(140, 52, 0), rgb(255, 144, 0), rgb(140, 52, 0));">{text}</div>', 6)
    # Red
    if lvl == 7: return (f'<div class="chif" style="background-image: linear-gradient(30deg,rgb(140, 40, 40), rgb(255, 0, 0), rgb(190, 0, 0), rgb(255, 0, 0), rgb(140, 40, 40));">{text}</div>', 7)
    # Rainbow
    if lvl == 8: return (f'<div class="chif" style="background-image: linear-gradient(30deg, rgb(64, 64, 64), rgb(255, 40, 40), rgb(255, 144, 0), rgb(255, 255, 0), rgb(0, 255, 0), rgb(0, 255, 255), rgb(0, 120, 255), rgb(255, 0, 255), rgb(255, 255, 255));">{text}</div>', 8)
    # Metal
    if lvl == 9: return (f'<div class="chif" style="background-image: linear-gradient(30deg, rgb(140, 140, 140), rgb(255, 255, 255), rgb(140, 140, 140), rgb(255, 255, 255), rgb(140, 140, 140));">{text}</div>', 9)

def get_title(UID):
    with open('./content/LP/user_infos.json', encoding='UTF-8') as f:
        infos = json.load(f)
    if str(UID) in infos['title'].keys(): return infos['title'][str(UID)]
    return ''

def glory_content(UID) -> str:
    with open('./content/LP/user_infos.json', encoding='UTF-8') as f:
        infos = json.load(f)
    if str(UID) not in infos['glory'].keys(): return ''
    text_box = []
    for glory in infos['glory'][str(UID)]:
        text_box.append(rare_glory_content(glory['rank'], glory['name']))
    text_box.sort(key=lambda e: e[1], reverse=True)
    text = ''
    for item in text_box:
        text += f'{item[0]}'
    return text

def rank_colored(rank:int) -> str:
    if rank == 1: return '<h1>1</h1>'
    if rank == 2: return '<h2>2</h2>'
    if rank == 3: return '<h3>3</h3>'
    return f'{rank}'
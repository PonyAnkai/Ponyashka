import json

def loadJson(path, encoding='utf-8') -> json:
    with open(path, 'r', encoding=encoding) as f:
        return json.load(f)

def saveJson(path, file=None, encoding='utf-8'):
    if file is not None:
        with open(path, 'w', encoding=encoding) as f:
            json.dump(file, f)
    else:
        with open(path, 'r', encoding=encoding) as f:
            loadJson = json.load(f)

        toSave = loadJson | file
        
        with open(path, 'w', encoding=encoding) as f:
            json.dump(toSave, f)
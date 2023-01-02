import json
import os


_dir = os.path.dirname(__file__)
info_file = os.path.join(_dir,"info.json")


def info_get():
    with open(info_file, 'r', encoding='utf_8') as f:
        info = json.loads(f.read())
    return info


async def info_update(key: str, value):
    with open(info_file, 'r', encoding='utf_8') as f:
        info = json.loads(f.read())
    info[key] = value
    with open(info_file, 'w', encoding='utf_8') as f:
        f.write(json.dumps(info, indent=4, ensure_ascii=False))
import sqlite3
import os
import random
import re


_dir = os.path.dirname(__file__)
conn = os.path.join(_dir,"cards.db")


def get_card(idx: str):
    db = sqlite3.connect(conn)
    xka = db.cursor()
    if idx == "-1":
        xka.execute("SELECT * FROM cardinfo")
        result = xka.fetchall()
        xka.close()
        res = random.choice(result)
        idx = res[0]
        url = res[1]
        content = f"你抽到了 [CQ:image,file={url}]\n--------------\n 卡号：{idx}"
    else:
        xka.execute('''SELECT * FROM cardinfo WHERE idx = ("%s")''' % idx)
        result = xka.fetchone()
        xka.close()
        if result == None:
            db.close()
            return None
        url = result[1]
        qq = result[2]
        content = f"卡号：{idx}\n上传者:{qq} [CQ:image,file={url}]"
    db.close()
    return content 


def card_increase(imgs: str, qq: str):
    cnt = 0
    image_url = re.search(r"\[CQ:image,file=(.*?)url=(.*?)\]", imgs)
    db = sqlite3.connect(conn)
    while image_url != None:
        cnt += 1
        url = image_url.group(2)
        sql = '''INSERT INTO cardinfo (url,qq) VALUES ("%s","%s")''' % (url,qq)
        db.execute(sql)
        db.commit()
        imgs = imgs.replace(image_url.group(), "")
        image_url = re.search(r"\[CQ:image,file=(.*?)url=(.*?)\]", imgs)
    db.close()
    return cnt


def card_decrease(idx: str):
    db = sqlite3.connect(conn)
    xka = db.cursor()
    xka.execute('''SELECT * FROM cardinfo WHERE idx = ("%s")''' % idx)
    result = xka.fetchone()
    if result == None:
        return None
    qq = result[2]
    xka.execute('''DELETE FROM cardinfo WHERE idx = ("%s")''' % idx)
    db.commit()
    xka.close()
    db.close()
    return qq


def qq_decrease(qq: str):
    db = sqlite3.connect(conn)
    sql = '''DELETE FROM cardinfo WHERE qq = ("%s")''' % qq
    db.execute(sql)
    db.commit()
    db.close()

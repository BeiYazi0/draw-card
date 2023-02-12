import hoshino
from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
from nonebot.exceptions import CQHttpError
import asyncio
from .draw_card import*
from .info_rw import*


sv_help = '''
[抽卡] 随机抽取一张卡
[洗入+图片(多张)] 向卡池洗入若干张图片(或用洗入回复某条消息)
[举办卡号+xxx] 向维护组举办指定卡号的图片
[查库存] 查看卡片总数
'''.strip()
sv = Service('sp抽卡', help_=sv_help, bundle='娱乐')


info = info_get()
w_model = info["white"]
b_model = info["black"]
white_groups = set(info["white_groups"])
black_qq = set(info["black_qq"])
contributor = info["contributor"]
withdraw = 30 # 撤回时间


max_notice = 3
lmt = DailyNumberLimiter(max_notice)
refuse_notice = f'您今天已经举报过{max_notice}次了，请明天再来吧！'


@sv.on_fullmatch('抽卡')
async def card_choice(bot, ev: CQEvent):
    card,index = get_card("-1")
    try:
        msg = await bot.send(ev, card, at_sender = True)
        if withdraw > 0:
            await asyncio.sleep(withdraw)
            await bot.delete_msg(message_id=msg['message_id'])
    except CQHttpError:
        await bot.send(ev, f"糟糕，卡号为【{index}】的图片发不出去力...快向维护组举办吧～")


@sv.on_keyword('洗入')
async def card_update(bot, ev: CQEvent):
    uid = str(ev.user_id)
    gid = str(ev.group_id)
    if (b_model and uid in black_qq) or (w_model and gid not in white_groups):
        return
    p = ev.message.extract_plain_text().replace("洗入","").strip()
    if p != "":
        return
    if ev.message[0].type == "reply":
        tmsg = await bot.get_msg(message_id=int(ev.message[0].data['id']))
        ev.message = tmsg["message"]
    imgs = str(ev.message)
    cnt = card_increase(imgs, uid)
    if cnt == 0:
        await bot.send(ev, "你的图片呢？", at_sender = True)
        return
    uid = str(uid)
    global contributor
    if contributor.get(uid) == None:
        contributor[uid] = cnt
    else:
        contributor[uid] += cnt
    await info_update("contributor", contributor)
    await bot.send(ev, f"洗入成功，共洗入{cnt}张图片", at_sender = True)


@sv.on_prefix('举办卡号')
async def card_against(bot, ev: CQEvent):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.send(ev, refuse_notice, at_sender=True)
        return
    sp = hoshino.config.SUPERUSERS[0]
    idx = ev.message.extract_plain_text()
    if not idx:
        await bot.send(ev, "你的卡号呢？", at_sender=True)
    else:
        lmt.increase(uid)
        card,index = get_card(idx)
        if card == None:
            await bot.send(ev, "错误的卡号", at_sender=True)
            return
        await bot.send_private_msg(self_id=ev.self_id, user_id=sp, message=f'收到Q{uid}@群{ev.group_id}的举报\n{card}')
        await bot.send(ev, f'您的反馈已发送至维护组！', at_sender=True)


@sv.on_prefix('删除卡号')
async def card_delete(bot, ev: CQEvent):
    uid = ev.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    idx = ev.message.extract_plain_text()
    if not idx:
        await bot.send(ev, "你的卡号呢？", at_sender=True)
        return
    qq = card_decrease(idx)
    if qq == None:
        await bot.send(ev, f"卡号{idx}不存在")
        return
    global contributor
    contributor[qq] -= 1
    await info_update("contributor", contributor)
    await bot.send(ev, f"删除卡号{idx}成功")


@sv.on_prefix('删除qq')
async def qq_delete(bot, ev: CQEvent):
    uid = ev.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    qq = ev.message.extract_plain_text()
    global contributor
    if contributor.get(qq, 0) == 0:
        await bot.send(ev, f"没有由Q{qq}洗入的卡牌")
        return
    qq_decrease(qq)
    contributor[qq] = 0
    await info_update("contributor", contributor)
    await bot.send(ev, f"已删除所有由Q{qq}洗入的卡牌")


@sv.on_prefix('查看卡号')
async def card_check(bot, ev: CQEvent):
    uid = ev.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    idx = ev.message.extract_plain_text()
    if not idx:
        await bot.send(ev, "你的卡号呢？", at_sender=True)
        return
    card,index = get_card(idx)
    if card == None:
        await bot.send(ev, "错误的卡号", at_sender=True)
    else:
        try:
            msg = await bot.send(ev, card)
            if withdraw > 0:
                await asyncio.sleep(withdraw)
                await bot.delete_msg(message_id=msg['message_id'])
        except CQHttpError:
            await bot.send(ev, f"糟糕，卡号为【{index}】的图片发不出去力...")


@sv.on_fullmatch('查看卡池贡献者')
async def card_check(bot, ev: CQEvent):
    uid = ev.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    res = '卡池贡献榜单'
    global contributor
    keys = sorted(contributor, key=lambda x:contributor[x], reverse=True)
    for qq in keys:
        if contributor[qq] == 0:
            continue
        res += f"\n{qq}：{contributor[qq]}"
    await bot.send(ev, res)
    

async def card_setting(target: str, model: int, value):
    global w_model, b_model, white_groups, black_qq
    if model == 1:
        value = set(value.split(" "))
        if target == 0:
            black_qq = black_qq | value
            await info_update("black_qq", list(black_qq))
        else:
            white_groups = white_groups | value
            await info_update("white_groups", list(white_groups))
    elif model == 0:
        if target == 0:
            b_model = value
            await info_update("b_model", b_model)
        else:
            w_model = value
            await info_update("w_model", w_model)
    else:
        value = set(value.split(" "))
        if target == 0:
            black_qq = black_qq - value
            await info_update("black_qq", list(black_qq))
        else:
            white_groups = white_groups - value
            await info_update("white_groups", list(white_groups))


@sv.on_prefix('抽卡设置')
async def card_set(bot, ev: CQEvent):
    uid = ev.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    setting = ev.message.extract_plain_text().strip()
    if len(setting) < 5:
        return
    wb = setting[0:3]
    setting = setting[3:]
    if wb == "白名单":
        target = 1
        model = setting[0:2]
        value = setting[2:].strip()
        if model in ["增加", "新增", "添加"]:
            model = 1
        elif model in ["删除", "减少", "移除"]:
            model = -1
        elif model == "启用":
            model = 0 
            value = True
        elif model == "禁用":
            model = 0 
            value = False
        else:
            return
    elif wb == "黑名单":
        target = 0
        model = setting[0:2]
        value = setting[2:].strip()
        if model in ["增加", "新增", "添加"]:
            model = 1
        elif model in ["删除", "减少", "移除"]:
            model = -1
        elif model == "启用":
            model = 0 
            value = True
        elif model == "禁用":
            model = 0 
            value = False
        else:
            return
    await card_setting(target, model, value)
    await bot.send(ev, "设置成功")


@sv.on_prefix('抽卡状态')
async def card_set(bot, ev: CQEvent):
    uid = ev.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    content = ev.message.extract_plain_text().strip()
    if content == "":
        if w_model == True:
            statu1 = "白名单已启用"
        else:
            statu1 = "白名单未启用"
        if b_model == True:
            statu2 = "黑名单已启用"
        else:
            statu2 = "黑名单未启用"
        statu = f"{statu1}\n{statu2}"
    elif content.isdigit():
        if content in white_groups:
            statu1 = f"群{content}在白名单中"
        else:
            statu1 = f"群{content}未在白名单中"
        if content in black_qq:
            statu2 = f"Q{content}在黑名单中"
        else:
            statu2 = f"Q{content}未在黑名单中"
        statu = f"{statu1}\n{statu2}"
    else:
        return
    await bot.send(ev, statu)


@sv.on_fullmatch('查库存')
async def info(bot, ev: CQEvent):
    stock = total()
    await bot.send(ev, f"当前图库总库存为 {stock} 张~")

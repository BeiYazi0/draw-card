# draw-card

基于HoshinoBot v2的本地抽卡插件，卡池中图片源自于用户上传。

## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/BeiYazi0/draw-card`
2. 在 `config/__bot__.py`的模块列表里加入 `draw-card`
3. 重启HoshinoBot

## 配置文件详细说明

  - `white` : 白名单模式, 仅允许位于白名单中的群向卡池洗入图(默认禁用)
  - `black` : 黑名单模式, 不允许黑名单中的用户向卡池洗入图片(默认启用)
  - `white_groups` : 白名单
  - `black_qq` : 黑名单
  - `contributor`: 卡池贡献者

## 指令说明

【抽卡】

随机抽取一张卡

【洗入+图片(多张)】

向卡池洗入若干张图片(或用洗入回复包含图片的消息)

【举办卡号+xxx】 

举办指定卡号的图片(举报信息将私聊发给超级用户)

【查库存】

查看数据库中卡片的总数

### 以下指令仅限超级用户使用

【删除卡号+xxx】

删除指定卡号的图片

【删除qq+xxx】

删除由用户xxx上传的所有图片

【查看卡号+xxx】

查看指定卡号的图片及上传者

【查看卡池贡献者】

查看卡池中所有贡献者及其上传的图片数量

【抽卡设置 白名单/黑名单 启用/禁用】

启用或禁用 黑名单/白名单 模式

【抽卡设置 白名单/黑名单 增加/新增/添加/删除/减少/移除 群号/qq号】

向 黑名单/白名单 中添加或移除 群号/qq号(若有多个请用空格隔开)

【抽卡状态(+群号/qq号)】

若加上 群号/qq号 则查询其是否在  黑名单/白名单 中，否则查询 黑名单/白名单 模式开启情况

## 效果

抽卡
![image](https://github.com/BeiYazi0/draw-card/blob/main/test/card_choice.png)

洗入
![image](https://github.com/BeiYazi0/draw-card/blob/main/test/card_update.png)

查看卡号
![image](https://github.com/BeiYazi0/draw-card/blob/main/test/card_check.png)

收到举办信息
![image](https://github.com/BeiYazi0/draw-card/blob/main/test/card_against.png)

## 备注

cards.db是准备好的数据库，如果不需要，可以直接删除，并在首次启用前在`draw_card.py`文件第9行添加以下代码。
```powershell
db = sqlite3.connect(conn)
db.execute("""CREATE TABLE if not exists cardinfo (
idx INTEGER primary key autoincrement,
url VARCHAR(20),
qq VARCHAR(20))""")
db.close()
```
将`info.json`文件中的contributor修改为空字典，重启HoshinoBot并成功运行后删去上述代码即可。

举办卡号主要针对失效的图片以及不健康图片。

## 更新信息

2023-2-12 感谢[@XiaoFuOS](https://github.com/XiaoFuOS)提供的代码，添加【查库存】指令，查看卡片的总数。

2023-2-8 感谢[@XiaoFuOS](https://github.com/XiaoFuOS)提供的代码，对于失效的图片，对用户发送提示及卡号。

2023-1-23 感谢[@XiaoFuOS](https://github.com/XiaoFuOS)提供的代码，增加了撤回的功能，withdraw为撤回时间，若为0则不撤回。

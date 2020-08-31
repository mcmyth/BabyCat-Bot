from module.command import *
from module.cqEncoder import *
from config.configManager import *
from module.timer import RepeatingTimer
from ccsun.main import *
configManager = Config()
CQEncoder = CQEncoder()
Log = Log()
#运行命令
qq = configManager.config["user"]["qq"]
authKey = configManager.config["user"]["authKey"]
mirai_api_http_locate = configManager.config["user"]["httpapi"]
app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

ccsunGroup = ccsunConfig["group"]

i = 0
async def hello():
    global i
    if i > 0:
        timeNow = time.strftime('%H:%M', time.localtime(time.time()))
        if timeNow == "00:00":
            #CCSUN流量统计
            await app.sendGroupMessage(ccsunGroup, getBandwidth(True))
            #维基日图
            try:
                wikipic = await getWikipic(['wikipic'])
                sendMessage = wikipic["sendText"]
                await app.sendGroupMessage(971058508, sendMessage)
                if os.path.exists(wikipic["imagePath"]):
                    os.remove(wikipic["imagePath"])
            except:pass
    if i == 0:i += 1
t = RepeatingTimer(60, hello)
t.start()

#运行指令
async def run_command(type: str, data: dict):
    app = data[Mirai]
    qq = configManager.config["user"]["qq"]
    if type == "group":
        group = data[Group]
        member = data[Member]
        source = data[Source]
        message = data[MessageChain]
        # if group.id == 570727901:
        Log.write(member.id, group.id, "[↓]群组消息", CQEncoder.messageChainToCQ(message))
        cqMessage = CQEncoder.messageChainToCQ(message)
        sendMessage = ""
        print(f"[{dateTime.timestampToDateTime()}]{cqMessage}")
        if (cqMessage[0:4].lower() == "/cat"):
            if (cqMessage.lower() == "/cat"):
                sendMessage = "啪！"
                Log.write(qq, group.id, "[↑]群组消息", sendMessage)
                await app.sendGroupMessage(group, sendMessage, quoteSource=source)
            command = commandDecode(cqMessage[5:])
            print(command)
            if (len(command) > 0):
                command[0] = command[0].lower()
                if (command[0] == "hi"):
                    sendMessage = "啪！"
                    await app.sendGroupMessage(group, sendMessage, quoteSource=source)
                if (command[0] == "ocr"):
                    if (len(command) > 1):
                        await app.sendGroupMessage(group, await tencent_ocr(command[1], (member.id, group.id)),
                                                   quoteSource=source)
                    else:
                        sendMessage = "参数不足"
                        await app.sendGroupMessage(group, sendMessage)
                if (command[0] == "info"):
                    sendMessage = getInfo(qq, group)
                    await app.sendGroupMessage(group, sendMessage)
                if (command[0] == "set"):
                    if len(command) >= 4:
                        sendMessage = [At(member.id), Plain(set(command, member, group))]
                        await app.sendGroupMessage(group, sendMessage)
                    else:
                        sendMessage = [At(member.id), Plain("参数不足")]
                        await app.sendGroupMessage(group, sendMessage)
                if (command[0] == "wikipic"):
                    wikipic = await getWikipic(command)
                    sendMessage = wikipic["sendText"]
                    await app.sendGroupMessage(group, sendMessage)
                    if os.path.exists(wikipic["imagePath"]):
                        os.remove(wikipic["imagePath"])
                    return
                if command[0] == "testt":
                    await app.sendGroupMessage(group, CQEncoder.cqToMessageChain(command[1]))
                if isinstance(sendMessage, list):
                    Log.write(qq, group.id, "[↑]群组消息", CQEncoder.messageChainToCQ(sendMessage))
                else:
                    Log.write(qq, group.id, "[↑]群组消息", sendMessage)
        if group.id == ccsunGroup:
            cqMessage = CQEncoder.messageChainToCQ(message)
            command = commandDecode(cqMessage)
            if cqMessage == "流量":
                await app.sendGroupMessage(ccsunGroup, getBandwidth())
            if cqMessage == "订阅":
                await app.sendGroupMessage(ccsunGroup, getSub())
            if cqMessage == "更新数据":
                await app.sendGroupMessage(ccsunGroup, getBandwidth(True))
            if command[0] == "/ccsun":
                if len(command) >= 1:
                    if command[1] == "update":
                        await app.sendGroupMessage(ccsunGroup, getBandwidth(True))


    if type == "friend":
        pass
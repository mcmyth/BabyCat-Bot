from module.command import *
from module.cqEncoder import *
from config.configManager import *
from module.timer import RepeatingTimer
from ccsun.main import *
from module.help import *
configManager = Config()
CQEncoder = CQEncoder()
Log = Log()
#运行命令
qq = configManager.config["user"]["qq"]
authKey = configManager.config["user"]["authKey"]
mirai_api_http_locate = configManager.config["user"]["httpapi"]
app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

ccsunGroup = ccsunConfig["group"]
sent = False
async def Timer1():
    global sent
    timeNow = time.strftime('%H:%M', time.localtime(time.time()))
    if timeNow == "00:00" and sent == False:
        sent = True
        try:
            # CCSUN流量统计
            await app.sendGroupMessage(ccsunGroup, getBandwidth(True))
            #月结日重置总计流量
            if resetTotal():
                await app.sendGroupMessage(ccsunGroup, "流量已重置")
            # 维基日图
            wikipic = await getWikipic(['wikipic'])
            sendMessage = wikipic["sendText"]
            await app.sendGroupMessage(971058508, sendMessage)
            if os.path.exists(wikipic["imagePath"]):
                os.remove(wikipic["imagePath"])
        except:pass
    if timeNow != "00:00" and sent == True:
        sent = False
t = RepeatingTimer(3, Timer1)
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
        if ocrQueueCheck(group.id,member.id):
            if cqMessage[:9] == "[CQ:image" and message.__root__[1].type == "Image":
                sendMessage = await tencent_ocr(cqMessage, (member.id, group.id))
                await app.sendGroupMessage(group,sendMessage ,quoteSource=source)
        head = "/cat"
        if (cqMessage[0:4].lower() == head):
            if (cqMessage.lower() == head):
                sendMessage = f"Hi,想查询命令菜单请输入{head} help 或 {head} menu"
                Log.write(qq, group.id, "[↑]群组消息", sendMessage)
                await app.sendGroupMessage(group, sendMessage, quoteSource=source)
            command = commandDecode(cqMessage[5:])
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
                        sendMessage = ocrQueue(group.id, member.id)
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
                if (command[0] == "say"):
                    result = await say(app,command, (member.id, group.id))
                    msg = result.get("msg")
                    status = result.get("status")
                    if status:
                        sendMessage = msg
                    else:
                        await app.sendGroupMessage(group, msg,quoteSource=source)
                if (command[0] == "shutup"):
                    await app.sendGroupMessage(group, await shutup(), quoteSource=source)
                if (command[0] == "i"):
                    await app.sendGroupMessage(group, checkMe(member.id), quoteSource=source)
                if (command[0] == "check"):
                    await app.sendGroupMessage(group, checkUser(command,member.id), quoteSource=source)
                if (command[0] == "web"):
                    #todo Web screenshot
                    pass
                if (command[0] == "help" or command[0] == "menu"):
                    await app.sendGroupMessage(group, getMenu(command), quoteSource=source)
                    pass
                if command[0] == "testt":
                    await app.sendGroupMessage(group,str(ocrQueueCheck(group.id,member.id)))
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
            if cqMessage[:2] == "图表":
                if len(cqMessage) >= 2:
                    day = cqMessage[2:]
                    if not is_number(day):day = "7"
                if int(day) > 180:
                    day = "180"
                    await app.sendGroupMessage(ccsunGroup, "最大查询过去180天的数据", quoteSource=source)
                imagePath =  getChart(source.id,day)
                await app.sendGroupMessage(ccsunGroup,[Image.fromFileSystem(imagePath)])
                os.remove(imagePath)
            if command[0] == "/ccsun":
                if len(command) >= 1:
                    if command[1] == "update":
                        await app.sendGroupMessage(ccsunGroup, getBandwidth(True))


    if type == "friend":
        pass
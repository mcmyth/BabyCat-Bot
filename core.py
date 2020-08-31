from module.command import *
from module.cqEncoder import *
from config.configManager import *
configManager = Config()
CQEncoder = CQEncoder()
Log = Log()

#运行命令
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
    if type == "friend":
        pass
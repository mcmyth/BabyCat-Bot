from core import *
Log.write("", "", "[i]系统消息", f"QQ:{qq}启动成功.")
@app.receiver("FriendMessage")
async def event_gm(app: Mirai, friend: Friend, message: MessageChain):
    cqMessage = CQEncoder.messageChainToCQ(message)
    # print(cqMessage)
    await app.sendFriendMessage(friend, Image(imageId="/1440126177-1174332322-BB3BEC5F9394B4B426F687DFDC933AC4"))

@app.receiver("MemberJoinEvent")
async def join_event(app: Mirai, event: MemberJoinEvent):
    await app.sendGroupMessage(event.member.group.id, [At(event.member.id), Plain("Welcome!")])

@app.receiver("GroupMessage")
async def event_gm(app: Mirai, message: MessageChain, group: Group, member: Member,source: Source):
    await run_command("group", {
        Mirai: app,
        Group: group,
        Member: member,
        MessageChain: message,
        Source: source
    })

if __name__ == "__main__":
    app.run()

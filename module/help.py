head = "/cat"
help = {
    f"{head}":"呼叫机器人",
    f"{head} ocr":"识别图片中的文字\n"
                   "命令使用方法：\n"
                   f"{head}ocr <图片> 或先输入 {head}ocr,再回复1张图片\n"
                  f"例:{head}ocr <此处填入一个图片>",
    f"{head} info":"查询系统信息\n"
                   "例:/info",
    f"{head} set":"设置权限组(需要超级管理员)\n"
                  "命令使用方法：\n"
                  f"{head} set <user> <add|del|level|admin> <this|qq|At>\n"
                  f"例:{head} set user add this",
    f"{head} check": "查询权限组(查询他人需要超级管理员)\n"
                   "命令使用方法：\n"
                   f"{head} check <this|qq|At>\n"
                   f"例:{head} check this",
    f"{head} wikipic": "获取维基日图\n"
                       "命令使用方法:\n"
                       f"{head}wikipic [日期]\n"
                       f"例:{head}wikipic 20200101",
    f"{head} say": "发送消息(非超级管理员最多3次且不能指定其他群)\n"
                   "命令使用方法:\n"
                   f"(1){head} say <this|group> text count\n"
                   f"(2){head} say <text>\n"
                   f"例:{head} say test",
    f"{head} shutup": "终止复读\n"
                   "命令使用方法:\n"
                   f"{head} shutup ",

}
def getHelp(command):
    command = head + " " + command.lower().strip().replace("\n","")
    if command in help.keys():
        return help[command]
    else:
        return "找不到该命令的帮助！"

def getMenu(command=None):
    print(command)
    if command != None and len(command) > 1:
        return  getHelp(command[1])
    else:
        text="命令列表:\n"
        keys = list(help.keys())
        print(keys)
        i = 0
        for x in keys:
            i += 1
            text += str(i) + "." + x + "  " + help[x].splitlines()[0] +"\n"
        return text[:-1]

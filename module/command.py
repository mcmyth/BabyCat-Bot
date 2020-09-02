import aiohttp
import json

from database.databaseAdapter import *
from module.cqEncoder import *
from module.wikiPic import WikiPic
from module.timer import asyncioInterval

ocrText = ""
CQEncoder = CQEncoder()
SystemInfo = SystemInfo()
User = User()


def commandDecode(command):
    regex = r'(\\s*(".+?"|[^:\s])+((\s*:\s*(".+?"|[^\s])+)|)|("(\D|\d)+?^|"(\D|\d)+?"|"+|[^"\s])+)'
    pattern = re.compile(regex)
    c1 = re.findall(pattern, command, flags=0)
    c2 = []
    i = 0
    for x in c1:
        if x[0][0] == '"' and x[0][-1:] == '"':
            c2.append(x[0][1:-1])
        else:
            c2.append(x[0])
        i = i + 1
    return (c2)


async def tencent_ocr(cqImage, source):  # aiohttp必须放在异步函数中使用
    asyncLog = Log()
    imgLink = CQEncoder.getCQattr(cqImage, "url")
    if (imgLink != ""):
        async with aiohttp.request('GET',
                                   'https://ai.qq.com/cgi-bin/appdemo_imagetranslate?image_url=' + imgLink) as resp:
            json = await resp.json()
            str = ""
            i = 0
            for x in json["data"]["image_records"]:
                str = str + json["data"]["image_records"][i]["source_text"] + "\n"
                i = i + 1
            if (str == ""):
                return "未在图中找到文本"
            else:

                asyncLog.write(source[0], source[1], "[↑]群组消息", str[:-1])
                return str[:-1]
    else:
        return "解析失败！"


def getInfo(qq, group):
    str = "[机器人信息]\n"
    str += "[机器人内核]Mirai\n"
    str += f"[当前登入QQ]{qq}\n"
    str += f"[当前QQ群]{group.name}({group.id})\n"
    str += f"[CPU使用]{SystemInfo.getCpuLoad()}%\n"
    str += f"[系统内存]{SystemInfo.getMemoryInfo()}"
    return str


def set(command, qq, group):
    if (User.user_check(qq.id, "admin") == False):
        return "权限不足"
    if command[1] == "user":
        if command[2] == "add":
            if len(command) < 5: command.append("this")
            if command[4] == "this": command[4] = str(group.id)
            if command[3] == "this" or command[3] == "": command[3] = str(qq.id)
            if User.userManager("add", CQEncoder.atToQQ(command[3]), command[4]):
                return "成功添加用户"
            else:
                return "添加用户失败，该用户可能已存在"
        if command[2] == "del":
            if len(command) < 5: command.append("this")
            if command[4] == "this": command[4] = str(group.id)
            if command[3] == "this" or command[3] == "": command[3] = str(qq.id)
            if User.userManager("del",CQEncoder.atToQQ(command[3]), command[4]):
                return "成功删除用户"
            else:
                return "删除用户失败"
        if command[2] == "level":
            if len(command) >= 6:
                if command[4] == "this": command[4] = str(qq.id)
                if command[5] == "this": command[5] = str(group.id)
                if User.userManager("level", command[4], command[5], command[6]):
                    return "已成功更新用户等级"
                else:
                    return "更新用户等级失败"
            else:
                return "参数不足"
        if command[2] == "admin":
            print(command[3])
            command[3] = CQEncoder.atToQQ(command[3])
            if command[3] == "this": command[3] = str(qq.id)
            if len(command) >= 4 and len(command) < 5:
                command.append("")
            return User.global_user(command[3], "admin", command[4])
    return "语法错误或出现未知错误。"


async def getWikipic(command):
    imagePath = ""
    DateTimeGenerator_obj = DateTimeGenerator()
    if not len(command) > 1:
        wikiPicDate = datetime.strptime(DateTimeGenerator_obj.timestampToDateTime(), '%Y-%m-%d %H:%M:%S').strftime(
            '%Y-%m-%d')
    else:
        wikiPicDate = command[1]
    wikiPic_obj = WikiPic()
    try:
        source = await wikiPic_obj.asyncGetWikiPic(wikiPicDate)
    except:
        ret = {"sendText": "发生错误，请检查输入日期是否正确", "imagePath": imagePath}
        return ret
    wikiPicJson = json.loads(source)
    if len(wikiPicJson) == 0:
        ret = {"sendText": "暂未查询到" + DateTimeGenerator_obj.strDateToChinese(command[1]) + "的维基日图",
               "imagePath": imagePath}
        return ret
    date = wikiPicJson[0]["date"]
    text = wikiPicJson[0]["text"]
    small = wikiPicJson[0]["small"]
    large = wikiPicJson[0]["large"]
    imagePath = "temp/" + getNetworkImage(small)
    sendText = [Plain(text=f'{date}维基日图\n'), Image.fromFileSystem(imagePath),
                Plain(text=f"\n{text}\n小:{small}\n大:{large}")]
    print("imageFilename:" + imagePath)
    ret = {"sendText": sendText, "imagePath": imagePath}
    return ret


def ocrQueue(qq_group, qq_number):
    if User.joinQueue("ocr", qq_group, qq_number):
        return "请发送一个图片进行OCR识别,发送任意文字取消本次操作。"
    else:
        return "请求加入队列失败"


def ocrQueueCheck(qq_group, qq_number):
    queue = User.searchQueue("ocr", qq_group, qq_number)
    if len(queue) > 0:
        id = queue[0][0]
        User.deleteQueue(id)
        return True
    else:
        return False


asyncioInterval = asyncioInterval()
async def repeat(app, text, count,object):
    shutupPath = "temp/.shutup"
    for i in range(count):
        await app.sendGroupMessage(object, CQEncoder.cqToMessageChain(text))
        time.sleep(1)
        if os.path.isfile(shutupPath):
            break

async def say(app, command, source):
    # /cat say object text count

    if len(command) <= 1: return {"status": False, "msg": "参数不足"}
    if len(command) <= 2:command.insert(1,source[1])
    object = command[1]
    if is_number(command[1]):object = int(command[1])
    if object == "this":object =  source[1]
    print(command)
    if object != "this" and is_number(command[1]) == False and len(command) > 1:return {"status": False, "msg": "语法错误"}
    text = command[2]
    if len(command) <= 3:
        count = 1
    else:
        try:
            count = int(command[3])
        except:
            count = 1

    if User.user_check(source[0], "admin") == False and count > 3:return {"status": False, "msg": "非超级管理员复读不能大于3次"}
    if count > 1:
        asyncioInterval.call_later(0.1, repeat, app, text, count,object)
    else:
        print(object)
        await app.sendGroupMessage(object,  CQEncoder.cqToMessageChain(text))
    return {"status": True, "msg": f"发送了{count}次'{text}'"}


async def shutup():
    shutupPath = "temp/.shutup"
    if os.path.isfile(shutupPath):
        os.remove(shutupPath)
        return "已允许复读"
    else:
        with open(shutupPath, 'w') as file_object:
            file_object.write("")
            return "已禁止复读"

def checkMe(qq):return User.userInfo(qq)

def checkUser(command,member):
    if User.user_check(member, "admin") == True:
        if len(command) >= 1:
            return User.userInfo(CQEncoder.atToQQ(command[1]))
        else:
            return "缺少参数"
    else:
        return "您没有权限执行该命令"
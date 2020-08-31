import aiohttp
import json

from database.databaseAdapter import *
from module.cqEncoder import *
from module.wikiPic import WikiPic

ocrText = ""
CQEncoder = CQEncoder()
SystemInfo = SystemInfo()
User = User()
def commandDecode(command):
    regex = r'(\\s*(".+?"|[^:\s])+((\s*:\s*(".+?"|[^\s])+)|)|(".+?"|[^"\s])+)'
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

async def tencent_ocr(cqImage,source):  # aiohttp必须放在异步函数中使用
    asyncLog = Log()
    imgLink = CQEncoder.getCQattr(cqImage,"url")
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
    if(User.user_check(qq.id,"admin")==False):
        return "权限不足"
    if command[1] == "user":
        if command[2] == "add":
            if len(command) < 5: command.append("this")
            if command[4] == "this": command[4] = str(group.id)
            if command[3] == "this" or command[3] == "": command[3] = str(qq.id)
            qqNumber = command[3]
            command[3] = CQEncoder.getCQattr(qqNumber,"qq")
            if command[3] == None: command[3] = qqNumber
            if User.userManager("add", command[3], command[4]):
                return "成功添加用户"
            else:
                return "添加用户失败，该用户可能已存在"
        if command[2] == "del":
            if len(command) < 5: command.append("this")
            if command[4] == "this": command[4] = str(group.id)
            if command[3] == "this" or command[3] == "": command[3] = str(qq.id)
            qqNumber = command[3]
            command[3] =  CQEncoder.getCQattr(command[3],"qq")
            if command[3] == None: command[3] = qqNumber
            if User.userManager("del", command[3], command[4]):
                return "成功删除用户"
            else:
                return "删除用户失败"
        if command[2] == "level":
            if len(command) >= 6:
                if command[4] == "this": command[4] = str(qq.id)
                if command[5] == "this" : command[5] = str(group.id)
                if User.userManager("level", command[4], command[5], command[6]):
                    return "已成功更新用户等级"
                else:
                    return "更新用户等级失败"
            else:
                return "参数不足"
        if command[2] == "admin":
            qqNumber = command[3]
            command[3] =  CQEncoder.getCQattr(command[3],"qq")
            if command[3] == None: command[3] = qqNumber
            if command[3] == "this": command[3] = str(qq.id)
            print(command[3])
            if len(command) >=4  and  len(command) < 5:
                command.append("")
            return User.global_user(command[3],"admin",command[4])
    return "语法错误或出现未知错误。"


async def getWikipic(command):
    imagePath = ""
    DateTimeGenerator_obj = DateTimeGenerator()
    if not len(command) > 1:
        wikiPicDate = datetime.strptime(DateTimeGenerator_obj.timestampToDateTime(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    else:
        wikiPicDate = command[1]
    wikiPic_obj = WikiPic()
    try:
        source = await wikiPic_obj.asyncGetWikiPic(wikiPicDate)
    except:
        ret = {"sendText":"发生错误，请检查输入日期是否正确","imagePath":imagePath}
        return ret
    wikiPicJson = json.loads(source)
    if len(wikiPicJson) == 0:
        ret = {"sendText":"暂未查询到" + DateTimeGenerator_obj.strDateToChinese(command[1]) + "的维基日图","imagePath":imagePath}
        return ret
    date = wikiPicJson[0]["date"]
    text = wikiPicJson[0]["text"]
    small = wikiPicJson[0]["small"]
    large = wikiPicJson[0]["large"]
    imagePath = "temp/" + getNetworkImage(small)
    sendText =  [Plain(text=f'{date}维基日图\n'),Image.fromFileSystem(imagePath),Plain(text=f"\n{text}\n小:{small}\n大:{large}")]
    print("imageFilename:" + imagePath )
    ret = {"sendText":sendText,"imagePath":imagePath}
    return ret
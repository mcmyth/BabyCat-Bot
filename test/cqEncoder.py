import asyncio
from aiohttp import *
from module.cqEncoder import *
#
# async def main(imglink):  # aiohttp必须放在异步函数中使用
#     async with aiohttp.request('GET',
#                                'https://ai.qq.com/cgi-bin/appdemo_imagetranslate?image_url='+ imglink) as resp:
#         json = await resp.json()
#         # print(json["data"]["image_records"][0]["source_text"])
#         str = ""
#         i = 0
#         for x in json["data"]["image_records"]:
#             str = str + json["data"]["image_records"][i]["source_text"] + "\n"
#             i = i + 1
#         return (str)
#
# def tecent_ocr(img):
#     imglink = cqimage_decode(img)
#     print (imglink)
#     if(imglink == ""):
#         return "参数错误，该指令应为/ocr <图片>"
#     else:
#         loop = asyncio.get_event_loop()
#         get_future = asyncio.ensure_future(main(imglink))  # 相当于开启一个future
#         loop.run_until_complete(get_future)  # 事件循环
#         print(get_future.result())
#         return (get_future.result())
# print(tecent_ocr("[CQ:image,url=https://img.it610.com/image/info5/664ff08906a641dcafbb1b3489e02ab7.jpg]"))

#
# class Employee:
#     '所有员工的基类'
#     empCount = 0
#
#     def __init__(self, name, salary):
#         self.name = name
#         self.salary = salary
#         Employee.empCount += 1
#
#     def displayCount(self):
#         print("Total Employee %d" % Employee.empCount)
#
#     def displayEmployee(self):
#         print( "Name : ", self.name, ", Salary: ", self.salary)
#
#
#
# Employee("Manni", 5000).displayEmployee()
# print("Total Employee %d" % Employee.empCount)

# 解析消息：
# a[CQ:face,id=13,name=ciya][CQ:face,id=13,name=ciya]
# __root__=[Source(type=<MessageComponentTypes.Source: 'Source'>, id=10234, time=datetime.datetime(2020, 8, 5, 9, 33, 11, tzinfo=datetime.timezone.utc)),
# Plain(type=<MessageComponentTypes.Plain: 'Plain'>, text='a'), Face(type='Face', faceId=13, name='ciya')]
#\[CQ:(.+?)\]

# __root__=[Source(type=<MessageComponentTypes.Source: 'Source'>, id=10249, time=datetime.datetime(2020, 8, 5, 10, 35, 37, tzinfo=datetime.timezone.utc)),
# Plain(type=<MessageComponentTypes.Plain: 'Plain'>, text='a'), Face(type='Face', faceId=13, name='ciya'),
# Plain(type=<MessageComponentTypes.Plain: 'Plain'>, text='a')]



def cq_attr(cqcode,attr):
    v = getmidstring(cqcode,attr + "=",",")
    if v == None:
        v = getmidstring(cqcode, attr + "=", "]")
    return v
def cq_type(cqcode):
    return getmidstring(cqcode,"[CQ:", ",")

def cqcodeParsing(str):
    regex = r'(\[CQ:(.+?)\])'
    pattern = re.compile(regex)
    return re.findall(pattern, str)

def getmidstring(str, start_str, end_str):
    start = str.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = str.find(end_str, start)
        if end >= 0:
            return str[start:end].strip()

def replace_char(string, char, start,end):
    string = list(string)
    del(string[start:end])
    #print( ''.join(string))
    string.insert(start,char)
    return ''.join(string)


def getCQIndex(text):
    cqIndex = []
    cqIndex.clear()
    p = re.compile("(\[CQ:(.+?)\])")
    for m in p.finditer(text):
        #print(m.start(), m.group())
        cqIndex.append((m.start(), m.end()))
    cqIndex.append((len(text), len(text)))
    return cqIndex




#text = 'aaa[CQ:face,id=13,name=ciya][CQ:face,id=14,name=222]bbb[CQ:face,id=13,name=ciya]ccc'


# getCQIndex(text)
# print(cqIndex)
# print(text[0:cqIndex[0][0]])
# text = replace_char(text, "啊啊", 0, cqIndex[0][0])
# print(text)

#
#
# getCQIndex(text)
# print(cqIndex)
# print(text[cqIndex[0][1]:cqIndex[1][0]])
# text = replace_char(text, "啊啊", cqIndex[0][1], cqIndex[1][0])
# print(text)

#
#
# getCQIndex(text)
# print(cqIndex)
# text = replace_char(text, "啊啊", cqIndex[1][1], cqIndex[2][0])
# print(text)
#
# getCQIndex(text)
# print(cqIndex)
# text = replace_char(text, "啊啊", cqIndex[2][1], cqIndex[3][0])
# print(text)
def plainToCQ(text):
    i = 0
    j = 0
    k = 0
    cqIndex = getCQIndex(text)
    while i < len(cqIndex):
        if(i > 0):
            if(i == 1):
                k = k + 1
            else:
                j = j + 1
        if i > 0:
            getCQIndex(text)
            source_text = text[cqIndex[j][k]:cqIndex[j + 1][0]]
            if(source_text != ""):
                text = replace_char(text,f"[CQ:plain,text={source_text}]", cqIndex[j][k], cqIndex[j + 1][0])
        else:
            getCQIndex(text)
            source_text = text[0:cqIndex[0][0]]
            if (source_text != ""):
                text = replace_char(text, f"[CQ:plain,text={source_text}]" , 0, cqIndex[0][0])
        i = i + 1
    return text


def cqToMessageChain(text):
    text = plainToCQ(text)
    cqlist = cqcodeParsing(text)
    chain = []
    for x in cqlist:
        if cq_type(x[0]) == "face":
            chain.append(Face(faceId = cq_attr(x[0],"id")))
        elif cq_type(x[0]) == "plain":
            chain.append(Plain(text=cq_attr(x[0], "text")))
        else:
            chain.append(Plain("unknown"))
    return chain
# print(cqToMessageChain("aaa[CQ:face,id=13,name=ciya][CQ:face,id=14,name=222]啊啊啊"))

# t = "2646574948-D2A35040ED81A91088D3BB262F15E7B2"
# t = t[t.rfind('-')+1:]
# t = list(t)
# t.insert(7, '/')
# t = ''.join(t)
# print(t)


#print(cqToMessageChain())
# text = "aa=a"
#print(plainToCQ("abc[CQ:face,id=13,name=ciya][CQ:face,id=14,name=222]ddsa"))

# for x in cqIndex:
    #print(text[textIndex:x[0]])
    #if text[textIndex:x[0]]!= "":
    #text = replace_char(text,"",textIndex ,x[0])
    #     pass
    #text= replace_char(text, "哈哈", textIndex)

    # textIndex = x[1]

#print(text)


# def replace_char(string, char, index):
#     string = list(string)
#     string[index] = char
#     string = list(string)
#     del (string[index:len(char) - 1])
#     return ''.join(string)

#print(replace_char(text,"",52,55))



def getImageURL(imgConfigPath,fileName):
    if imgConfigPath[-1] != "\\" : imgConfigPath += "\\"
    try:
        f = open(imgConfigPath+fileName, 'r')
        print(getmidstring(f.read(),"url=","\n"))
    finally:
        if f:
            f.close()


#getImageURL(r"C:\Users\14401\Desktop\image",r"000B1CA3DE163EF2385653A3CCAE7196.jpg.cqimg")



#print(CQEncoder.messageChainToCQ("[CQ:image,url=https://gchat.qpic.cn/gchatpic_new/1445957253/3968399804-3189988963-0000733726B26BB5B711F1C76024E25C/0?term=2]"))




async def get_source(url_):
    try:
        async with ClientSession( ) as session:
            async with session.get(url_) as response:
                source = await response.read( )
                print(source)
    except asyncio.CancelledError:
        raise
async def main():
    tasks = [asyncio.ensure_future(get_source("https://lxns.org/"))for i in range(1, 2)]
    await asyncio.wait(tasks)



if __name__ == "__main__":
    event_loop = asyncio.get_event_loop( )
    # ------------------------------------------------

        # 用这个协程启动循环，协程返回时这个方法将停止循环。
    event_loop.run_until_complete(main())

from uuid import UUID
from mirai import *
import re
import struct


# 在Mirai-Python对消息链和CQ码互相转换
# 消息链转CQ码messageChainToCQ()
# CQ码转消息链cqToMessageChain()
class CQEncoder:
    friend = False

    # 将UTF32转换为字符
    def utf32ToChar(self, n):
        n = int(n)
        return struct.pack('<I', n).decode('utf-32')

    # 取出前后两个文本之间的文本
    def getMidString(self, text, StartStr, EndStr):
        start = text.find(StartStr)
        if start >= 0:
            start += len(StartStr)
            end = text.find(EndStr, start)
            if end >= 0:
                return text[start:end].strip()

    # 获取CQ码中属性的值
    def getCQattr(self, cqCode, cqAttr):
        v = self.getMidString(cqCode, cqAttr + "=", ",")
        if v == None:
            v = self.getMidString(cqCode, cqAttr + "=", "]")
        return v

    #将At CQ码转换为QQ号码，如转换失败则返回原始文本
    def atToQQ(self, cqCode):
        source = cqCode
        try:
            qqNumber = self.getCQattr(cqCode, "qq")
        except:
            qqNumber = None
        if qqNumber == None: qqNumber = source
        return qqNumber

    # 获取CQ码的类型
    def getCQtype(self, cqcode):
        return self.getMidString(cqcode, "[CQ:", ",")

    # 将CQ码存入List中
    def cqCodeParsing(self, text):
        regex = r'(\[CQ:(.+?)\])'
        pattern = re.compile(regex)
        # print(re.findall(pattern, text))
        return re.findall(pattern, text)

    def replaceChar(self, string, char, start, end):
        string = list(string)
        del (string[start:end])
        string.insert(start, char)
        return ''.join(string)

    # 获得文本中每一个CQ码的起始和结束位置
    def getCQIndex(self, text):
        cqIndex = []
        cqIndex.clear()
        p = re.compile("(\[CQ:(.+?)\])")
        for m in p.finditer(text):
            cqIndex.append((m.start(), m.end()))
        cqIndex.append((len(text), len(text)))
        return cqIndex

    # 转义中括号
    def escapeChar(self, text, isEscape=True):
        if isEscape:
            text = text.replace("&", "&amp;")
            text = text.replace(" ", "&nbsp;")
            text = text.replace("[", "&lt;")
            text = text.replace("]", "&gt;")
        else:
            text = text.replace("&lt;", "[")
            text = text.replace("&gt;", "]")
            text = text.replace("&nbsp;", " ")
            text = text.replace("&amp;", "&")
        return text

    # 将CQ码以外的文本转换成类型为“plain”的CQ码
    def plainToCQ(self, text):
        i = j = k = 0
        cqIndex = self.getCQIndex(text)
        while i < len(cqIndex):
            if i > 0:
                if i == 1:
                    k = k + 1
                else:
                    j = j + 1
            if i > 0:
                cqIndex = self.getCQIndex(text)
                source_text = text[cqIndex[j][k]:cqIndex[j + 1][0]]
                if source_text != "":
                    source_text = self.escapeChar(source_text)
                    text = self.replaceChar(text, f"[CQ:plain,text={source_text}]", cqIndex[j][k], cqIndex[j + 1][0])
            else:
                cqIndex = self.getCQIndex(text)
                source_text = text[0:cqIndex[0][0]]
                if (source_text != ""):
                    source_text = self.escapeChar(source_text)
                    text = self.replaceChar(text, f"[CQ:plain,text={source_text}]", 0, cqIndex[0][0])
            i = i + 1
        return text

    # 取CQ码配置文件中URL的值
    def getImageURL(self, imgConfigPath, fileName):
        if imgConfigPath[-1] != "\\": imgConfigPath += "\\"
        try:
            # print(imgConfigPath + fileName+".cqimg")
            f = open(imgConfigPath + fileName + ".cqimg", 'r')
            return self.getMidString(f.read(), "url=", "\n")
        finally:
            if f:
                f.close()

    # 将CQ码转为消息链
    # 填入图片配置路径默认进入读取配置文件的模式
    def cqToMessageChain(self, text, imgConfigPath=""):
        text = self.plainToCQ(text)
        cqList = self.cqCodeParsing(text)
        chain = []
        for x in cqList:
            if self.getCQtype(x[0]) == "face":
                chain.append(Face(faceId=self.getCQattr(x[0], "id")))
            elif self.getCQtype(x[0]) == "plain":
                plain = self.getCQattr(x[0], "text")
                plain = self.escapeChar(plain, False)
                chain.append(Plain(text=plain))
            elif self.getCQtype(x[0]) == "at":
                chain.append(At(self.getCQattr(x[0], "qq")))
            elif self.getCQtype(x[0]) == "emoji":
                chain.append(Plain(self.utf32ToChar(self.getCQattr(x[0], "id"))))
            elif self.getCQtype(x[0]) == "image":
                if self.friend == False:
                    cqImg = x[0]
                    if imgConfigPath != "":
                        cqImg = "[CQ:image,url=" + self.getImageURL(imgConfigPath, self.getCQattr(x[0], "file")) + "]"
                    imgid = self.getMidString(self.getCQattr(cqImg, "url"), "-", "/0")
                    if imgid != None:
                        imgid = imgid[imgid.rfind('-') + 1:]
                        if len(imgid) == 32:
                            imgid = str(UUID(imgid))
                            chain.append(Image(url=self.getCQattr(cqImg, "url"), imageId=imgid.upper()))

                        else:
                            print("UUID格式不正确!")
                    else:
                        print("找不到图片UUID!")
                else:
                    imgid = "/" + self.getMidString(self.getCQattr(x[0], "url")[7:], "//", "/0")
                    chain.append(Image(url=self.getCQattr(x[0], "url"), imageId=imgid.upper()))
            else:
                chain.append(Plain("unknown"))
        return chain

    def __init__(self, f=None):
        if f == True: self.friend = True

    # 将消息链转换成CQ码（不完善，部分特殊消息没做处理）
    # cqimg配置文件已被弃用，默认将URL填入CQ码中的url属性中
    def messageChainToCQ(self, messagChain):
        try:
            messageChainList = ([*(msg for msg in messagChain.__root__[1:])])
        except:
            messageChainList = messagChain
        ret = ""
        for x in messageChainList:
            type = x.type
            if type == "MessageComponentTypes.Plain":
                ret = ret + x.text
            if type == "Face":
                ret = ret + "[CQ:face,id=" + str(x.faceId) + ",name=" + x.name + "]"
            elif type == "Image":
                ret = ret + "[CQ:image,url=" + x.url + "]"
            elif type == "At":
                ret = ret + "[CQ:at,qq=" + str(x.target) + "]"
            elif type == "AtAll":
                ret = ret + "[CQ:at,qq=all]"
            elif type == "Source":
                ret = ret + ""
            elif type == "Quote":
                ret = ret + ""
            elif type == "FlashImage":
                ret = ret + ""
            elif type == "Unknown":
                ret = ret + ""
            elif type == "App":
                x = "暂不支持该消息"
            elif str(x.type) == "MessageComponentTypes.Plain":
                ret = ret + str(x.text)
            else:
                try:
                    ret = ret + "[CQ:unknown]"
                    pass
                except IOError:
                    ret = ret + "[CQ:error]"
                    print("解析消息失败：" + str(IOError))
        # print("解析消息：\n" + str(ret))
        return ret

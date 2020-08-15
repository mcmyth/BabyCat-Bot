#更新于2020/08/14 20:13 By MC_Myth

import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import sys
import urllib.parse
import datetime
from datetime import datetime
class WikiPic:

    year:str
    month: str
    day:str
    #获取网页
    async def fetch(self,session, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'accept-language':'zh-CN,zh;q=0.9'
        }
        #国内网络请配合代理食用，只支持http代理,暂不支持socks，如需支持Sock代理需要配合aiosocks
        async with session.get(url,headers=headers,proxy='') as response:
            return await response.text(encoding='utf8')

    # 处理网页
    async def download(self,url):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, url)
            soup = BeautifulSoup(html, "lxml")
            table = soup.select("div.mw-parser-output table td",)[1:]
            imageHTMLList = []
            for x in table:
                if x.get("valign")== 'top':
                    imageHTMLList.append(x)
            imageList= []
            for i in range(len(imageHTMLList)):
                date =  imageHTMLList[i].find_all('span',class_='mw-headline')[0].get('id')[:-4]
                if self.day != None:
                    if date != f"{self.year}年{self.month}月{self.day}日": continue
                text = imageHTMLList[i].select("div.gallerytext")[0].get_text().replace('\n','')
                small = 'https:' + imageHTMLList[i].select("div.thumb img")[0].get('src')
                large = small.replace('/thumb','')[:small.rfind("/")]
                large = large[:large.rfind("/")]
                imageList.append({"date": date,"text": text, "small": small, "large": large})
            #print(json.dumps(imageList))
            return json.dumps(imageList)
    #对多种不同格式的日期进行转换
    def strDateToChinese(self,date_time_str):
        date_time_obj = None
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y/%m/%d').strftime('%Y年%m月%d日').replace('月0', '月').replace('年0', '年')
        except:
            pass
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d').strftime('%Y年%m月%d日').replace('月0', '月').replace('年0', '年')
        except:
            pass
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y年%m月%d日').strftime('%Y年%m月%d日').replace('月0', '月').replace('年0', '年')
        except:
            pass
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y%m%d').strftime('%Y年%m月%d日').replace('月0', '月').replace('年0', '年')
        except:
            pass

        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y/%m').strftime('%Y年%m月').replace('年0', '年')
        except:
            pass
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m').strftime('%Y年%m月').replace('年0', '年')
        except:
            pass
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y年%m月').strftime('%Y年%m月').replace('年0', '年')
        except:
            pass
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y%m').strftime('%Y年%m月').replace('年0', '年')
        except:
            pass

        return date_time_obj

    # 取出前后两个文本之间的文本
    def getMidString(self,text, StartStr, EndStr):
        start = text.find(StartStr)
        if start >= 0:
            start += len(StartStr)
            end = text.find(EndStr, start)
            if end >= 0:
                return text[start:end].strip()
    #获取维基日图JSON，支持"2020-01-01"或"2020-01"，可单独指定某天或者某月
    def getWikiPic(self,date=None):
        date = self.strDateToChinese(date)
        self.year = date[0:date.rfind('年', 1)]
        self.month = self.getMidString(date,"年","月")
        self.day = self.getMidString(date, "月", "日")
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        url = "https://zh.wikipedia.org/wiki/Wikipedia:%E6%AF%8F%E6%97%A5%E5%9B%BE%E7%89%87/" + urllib.parse.quote(f"{self.year}年{self.month}月", safe='')
        return loop.run_until_complete(self.download(url))

#demo
# wikiPic_obj = WikiPic()
# print(wikiPic_obj.getWikiPic("20200310"))
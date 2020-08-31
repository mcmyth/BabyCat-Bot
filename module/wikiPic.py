import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import sys
import urllib.parse
from module.cqEncoder import *
from module.dateParse import *

class WikiPic:

    year:str
    month: str
    day:str

    async def fetch(self,session, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'accept-language':'zh-CN,zh;q=0.9'
        }
        #修改为正确的代理地址，仅支持HTTP代理，不需要代理可删除proxy或留空
        async with session.get(url,headers=headers,proxy="") as response:
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

    def getWikiPic(self,date=None):
        self.DateTimeGenerator = DateTimeGenerator()
        if date == None:date = self.DateTimeGenerator.timestampToDateTime()
        self.CQEncoder = CQEncoder()
        date = self.DateTimeGenerator.strDateToChinese(date)
        self.year = date[0:date.rfind('年', 1)]
        self.month = self.CQEncoder.getMidString(date,"年","月")
        self.day = self.CQEncoder.getMidString(date, "月", "日")
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        url = "https://zh.wikipedia.org/wiki/Wikipedia:%E6%AF%8F%E6%97%A5%E5%9B%BE%E7%89%87/" + urllib.parse.quote(f"{self.year}年{self.month}月", safe='')
        return loop.run_until_complete(self.download(url))

    async def asyncGetWikiPic(self,date=None):
        self.DateTimeGenerator = DateTimeGenerator()
        if date == None: date = self.DateTimeGenerator.timestampToDateTime()
        self.CQEncoder = CQEncoder()
        date = self.DateTimeGenerator.strDateToChinese(date)
        self.year = date[0:date.rfind('年', 1)]
        self.month = self.CQEncoder.getMidString(date, "年", "月")
        self.day = self.CQEncoder.getMidString(date, "月", "日")

        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        url = "https://zh.wikipedia.org/wiki/Wikipedia:%E6%AF%8F%E6%97%A5%E5%9B%BE%E7%89%87/" + urllib.parse.quote(
            f"{self.year}年{self.month}月", safe='')
        return await self.download(url)



if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



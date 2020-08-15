import json
import time
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup

# table表格用于储存书本信息
table = []


# 获取网页（文本信息）
async def fetch(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'accept-language':'zh-CN,zh;q=0.9'
    }
    async with session.get(url,headers=headers) as response:
        return await response.text(encoding='utf8')


# 解析网页
async def parser(html):
    # 利用BeautifulSoup将获取到的文本解析成HTML
    soup = BeautifulSoup(html, "lxml")
    # 获取网页中的畅销书信息
    book_list = soup.find('ul', class_="bang_list clearfix bang_list_mode")('li')

    for book in book_list:
        info = book.find_all('div')

        # 获取每本畅销书的排名，名称，评论数，作者，出版社
        rank = info[0].text[0:-1]
        name = info[2].text
        comments = info[3].text.split('条')[0]
        author = info[4].text
        date_and_publisher = info[5].text.split()
        publisher = date_and_publisher[1] if len(date_and_publisher) >= 2 else ''

        # 将每本畅销书的上述信息加入到table中
        table.append([rank, name, comments, author, publisher])


# 处理网页
async def download(url):
    async with aiohttp.ClientSession() as session:


        html = await fetch(session, url)
        soup = BeautifulSoup(html, "lxml")
        table = soup.select("div.mw-parser-output table td",)[1:]
        imageHTMLList = []
        for x in table:
            if x.get("valign")== 'top':
                imageHTMLList.append(x)
        i = 0
        imageList= []
        for x in imageHTMLList:
            date =  imageHTMLList[i].find_all('span',class_='mw-headline')[0].get('id')[:-4]
            text = imageHTMLList[i].select("div.gallerytext")[0].get_text().replace('\n','')
            small = 'https:' + imageHTMLList[i].select("div.thumb img")[0].get('src')
            large = small.replace('/thumb','')[:small.rfind("/")]
            large = large[:large.rfind("/")]
            imageList.append({"date": date,"text": text, "small": small, "large": large})
            i += 1
        print(json.dumps(imageList))



# 全部网页
urls = ['https://zh.wikipedia.org/wiki/Wikipedia:%E6%AF%8F%E6%97%A5%E5%9B%BE%E7%89%87/2020%E5%B9%B48%E6%9C%88']
# 统计该爬虫的消耗时间
# print('#' * 50)
t1 = time.time()  # 开始时间

# 利用asyncio模块进行异步IO处理
loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(download(url)) for url in urls]
tasks = asyncio.gather(*tasks)
loop.run_until_complete(tasks)


from module.wikiPic import *
from module.dateParse import *
import json
import aiohttp
import aiofiles
import urllib.request 
async def downloadNetworkFile(url,filename=None):
    async with aiohttp.ClientSession() as session:
        if filename == None:
            filename = url[url.rfind("/")+1:]
        async with session.get(url,proxy='') as resp:
            if resp.status == 200:
                f = await aiofiles.open('../temp/' + filename, mode='wb')
                await f.write(await resp.read())
                await f.close()
        return filename

def getNetworkImage(url,filename=None):
    if filename == None:
        filename = url[url.rfind("/") + 1:]
    f = urllib.request .urlopen(url)
    data = f.read()
    with open("../temp/" + filename, "wb") as code:
        code.write(data)
    return filename

wikiPicDate = "20200108"
wikiPic_obj = WikiPic()
wikiPicJson = json.loads(wikiPic_obj.getWikiPic(wikiPicDate))
date = wikiPicJson[0]["date"]
text = wikiPicJson[0]["text"]
small = wikiPicJson[0]["small"]
large = wikiPicJson[0]["large"]
sendText = f"{date}维基日图\n[Image]\n{text}\n小:{small}\n大:{large}"
print("imageFilename:" + getNetworkImage(small))
print(sendText)
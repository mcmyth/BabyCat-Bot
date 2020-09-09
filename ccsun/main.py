import datetime
import time
import os
import json
import sqlite3
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
path = "ccsun/"


def loadConfig():
    f = open(f'{path}ccsun.json', 'r')
    config = json.loads(f.read())
    return config


ccsunConfig = loadConfig()
currenProduct = ccsunConfig["user"]["product"]
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}


def getMidString(text, StartStr, EndStr):
    start = text.find(StartStr)
    if start >= 0:
        start += len(StartStr)
        end = text.find(EndStr, start)
        if end >= 0:
            return text[start:end].strip()


def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday


def saveConfig():
    f = open(f'{path}ccsun.json', 'w')
    f.write(str(json.dumps(ccsunConfig, sort_keys=True, indent=2)))
    f.close()


def updateData(date, upload, download, uploaded, downloaded):
    conn = sqlite3.connect(f'{path}ccsun.db')
    cur = conn.cursor()
    cur.execute('insert into `ccsun`(`date`, `upload`, `download`, `uploaded`, `downloaded`) VALUES(?,?,?,?,?)',
                (date, upload, download, uploaded, downloaded))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        return False
    else:
        conn.close()
        return True


def Login():
    session = requests.session()
    url = 'https://z96w.win/dologin.php'
    res = session.post(url, data=ccsunConfig["login"], headers=headers, verify=False, allow_redirects=False)
    cookies = res.cookies
    cookie = requests.utils.dict_from_cookiejar(cookies)
    ccsunConfig["cookie"] = cookie
    print("ccsun重新登陆" + str(cookie))
    saveConfig()
    return cookie


def getBandwidth(update=False):
    session = requests.session()
    url = 'https://z96w.win/clientarea.php?action=productdetails&id=' + currenProduct
    try:
        res = session.get(url, headers=headers, cookies=ccsunConfig["cookie"], verify=False, allow_redirects=False)
    except Exception as e:
        return str(e)
    # with open('1.html', 'wb') as f:
    #     f.write(res.content)
    html = res.content.decode('utf-8')
    total = getMidString(res.content.decode('utf-8'), "使用报表 (流量：", "GB)")
    if (total == None):
        Login()
        res = session.get(url, headers=headers, cookies=ccsunConfig["cookie"], verify=False, allow_redirects=False)
        html = res.content.decode('utf-8')
        total = getMidString(html, "使用报表 (流量：", "GB)")
        if (total == None):
            return "数据异常,请联系管理员。"

    if "GB" in getMidString(html, "上传 (", ")"):
        upload = round(float(getMidString(html, "上传 (", "GB)")), 2)
    else:
        upload = round(float(getMidString(html, "上传 (", "MB)")) / 1024, 2)

    if "GB" in getMidString(html, "上传 (", ")"):
        download = round(float(getMidString(html, "下载 (", "GB)")), 2)
    else:
        download = round(float(getMidString(html, "下载 (", "MB)")) / 1024, 2)

    yesterdayDownload = ccsunConfig["yesterday"]["download"]
    yesterdayUpload = ccsunConfig["yesterday"]["upload"]
    usedDownload = round(download - yesterdayDownload, 2)
    usedUpload = round(upload - yesterdayUpload, 2)

    text = f'''[使用报表 {str(round(download + upload, 2))}/200 GB]
总计已用:↑{str(upload)}GB  ↓{str(download)}GB
当天已用:↑{str(usedUpload)}GB  ↓{str(usedDownload)}GB'''

    if (update == True):
        isUpdate = updateData(getYesterday(), usedUpload, usedDownload, upload, download)
        ccsunConfig["yesterday"]["download"] = download
        ccsunConfig["yesterday"]["upload"] = upload
        saveConfig()
        if isUpdate:
            text = f'''昨日流量详情:
[使用报表 {str(round(download + upload, 2))}/200 GB]
总计已用:↑{str(upload)}GB  ↓{str(download)}GB
昨日已用:↑{str(usedUpload)}GB  ↓{str(usedDownload)}GB'''
        else:
            text = f'''昨日流量详情(数据库更新失败):
[使用报表 {str(round(download + upload, 2))}/200 GB]
总计已用:↑{str(upload)}GB  ↓{str(download)}GB
昨日已用:↑{str(usedUpload)}GB  ↓{str(usedDownload)}GB'''
    return text


def getSub():
    session = requests.session()
    url = 'https://z96w.win/clientarea.php?action=productdetails&id=' + currenProduct
    try:
        res = session.get(url, headers=headers, cookies=ccsunConfig["cookie"], verify=False, allow_redirects=False)
    except Exception as e:
        return str(e)
    html = res.content.decode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    if len(soup.select("div.panel-body table")) == 0:
        Login()
        session = requests.session()
        url = 'https://z96w.win/clientarea.php?action=productdetails&id=' + currenProduct
        res = session.get(url, headers=headers, cookies=ccsunConfig["cookie"], verify=False, allow_redirects=False)
        html = res.content.decode('utf-8')
        soup = BeautifulSoup(html, "lxml")
    table = soup.select("div.panel-body table")[1]
    copyBtn = table.select("button")
    text = f'''常规:{copyBtn[0]["data-params"]}
备用:{copyBtn[1]["data-params"]}
Q:{copyBtn[2]["data-params"]}
QX:{copyBtn[3]["data-params"]}
C:{copyBtn[4]["data-params"]}'''
    return text


def getChart(messageid, day="7"):
    with os.popen(f'node module\js\ccsun.js {str(messageid)}.jpg {day}', 'r') as f:
        text = f.read()
    print(text)  # 打印cmd输出结果
    return "temp/" + str(messageid) + ".jpg"


def resetTotal():
    day = time.strftime('%d', time.localtime(time.time()))
    if day == ccsunConfig["user"]["settlement_day"]:
        ccsunConfig["yesterday"]["download"] = "0"
        ccsunConfig["yesterday"]["upload"] = "0"
        saveConfig()
        return True
    else:
        return False

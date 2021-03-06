import ctypes
import hashlib
import json
import os
import urllib.request
import requests
from module.dateParse import *

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

    def __init__(self):
        # have to initialize this to the size of MEMORYSTATUSEX
        self.dwLength = ctypes.sizeof(self)
        super(MEMORYSTATUSEX, self).__init__()


class SystemInfo(MEMORYSTATUSEX):
    def getMemoryInfo(self):
        stat = MEMORYSTATUSEX()
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        return (str(round((stat.ullTotalPhys / 1048576) - (stat.ullAvailPhys / 1048576))) + "MB / " + str(
            round(stat.ullTotalPhys / 1048576)) + "MB")

    def getCpuLoad(self):
        """ Returns a list CPU Loads"""
        result = []
        cmd = "WMIC CPU GET LoadPercentage "
        response = os.popen(cmd + ' 2>&1', 'r').read().strip().split("\r\n")[0]
        CpuUsed = numOnly(response)
        return (CpuUsed)


def numOnly(num):
    number = ""
    for x in list(filter(str.isdigit, num)):
        number += x
    return number


def getNetworkImage(url,filename=None):
    if filename == None:
        filename = url[url.rfind("/") + 1:]
    f = urllib.request .urlopen(url)
    data = f.read()
    with open("temp/" + filename, "wb") as code:
        code.write(data)
    return filename


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
DateTimeGenerator = DateTimeGenerator()
def getShortUrl(originalUrl):
    timestamp = DateTimeGenerator.dateTimeToTimestamp()
    session = requests.session()
    confingPath = "config/config.json"
    f = open(confingPath, 'r')
    config = json.loads(f.read())
    apiKey = config["shorturl_key"]
    postData = {
        "url": originalUrl,
        "signature": hashlib.md5((str(timestamp) + apiKey).encode('utf-8')).hexdigest(),
        "timestamp": timestamp,
        "action": "shorturl",
        "format": "json"
    }
    res = session.post("https://6lu.cc/yourls-api.php", data=postData)
    content = res.content.decode('utf-8')
    try:
        result = json.loads(content)
        shortUrl = result["shorturl"]
    except:
        shortUrl = ""
        print("获取短网址失败！")
    return shortUrl

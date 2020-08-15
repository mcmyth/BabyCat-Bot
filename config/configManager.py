import json
import os
class Config:
    config = {}
    def saveConfig(self):
        f= open('config/config.json', 'w')
        f.write(str(json.dumps(self.config, sort_keys=True, indent=2)))
        f.close()

    def loadConfig(self):
        if os.path.isfile("config/config.json") == False:
            self.newConfig()
            print("配置文件不存在，已生成到config/config.json，请打开该文件填写配置信息")
            return
        try:
            f = open('config/config.json', 'r')
            self.config = json.loads(f.read())
            return f.read()
        except:
            print("配置文件格式错误，请正确填写")
        finally:
            if f:
                f.close()
            try:
                self.config["user"]["qq"]
                self.config["user"]["qq"]
                self.config["user"]["authKey"]
                self.config["user"]["httpapi"]
            except:
                print("配置文件信息缺失，请正确填写")
    def newConfig(self):
        self.config["user"] = {}
        self.config["user"]["qq"] = None
        # httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.
        self.config["user"]["authKey"] = ""
        self.config["user"]["httpapi"] = ""
        self.saveConfig()

    def __init__(self):
        self.loadConfig()


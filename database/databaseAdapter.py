import sqlite3
from module.functions import *
from module.dateParse import *

dateTime = DateTimeGenerator()
class DatabaseAdapter:
    path = "database/"
    #path = ""
    conn = None
    cur = None

    def __init__(self):
        self.newDatabase()

    def newDatabase(self):
        #if os.path.isfile("data.db"): return
        if os.path.isfile(f"{self.path}data.db"):
            self.conn = sqlite3.connect(f'{self.path}data.db')
            self.cur = self.conn.cursor()
            return
        self.conn = sqlite3.connect(f'{self.path}data.db')
        self.cur = self.conn.cursor()
        self.cur.execute('''
        CREATE TABLE "main"."user" (
        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
         "qq_number" integer(20) NOT NULL,
        "qq_group" integer(20),
        "level" integer(20)
        );''')
        self.cur.execute('''
         CREATE TABLE "main"."global_user" (
      "int" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
      "qq" integer(20),
      "status" text(20),
      "desc" integer(20)
    );''')

        self.cur.execute('''
CREATE TABLE "log" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "time" INTEGER,
  "member" INTEGER,
  "group" INTEGER,
  "type" TEXT,
  "message" TEXT
);
''')
        self.conn.commit()
        print("数据库不存在，已自动创建")


class User(DatabaseAdapter):
    def userManager(self,type, qq, group="", level=""):
        qq = numOnly(qq)
        group = numOnly(group)
        level = numOnly(level)
        if level == "": level = "1"
        type = type.lower()
        if qq == "":
            print("qq参数异常")
            return False
        if type == "add":
            if self.userExist(qq, group):
                print("用户已存在。")
                return False
            self.cur.execute(f'''
            INSERT INTO "main"."user"("qq_number", "qq_group", "level") VALUES ('{qq}', '{group}', '{level}')
            ''')
        if type == "del":
            self.cur.execute(f'DELETE FROM "main"."user" WHERE qq_number={qq} and qq_group={group}')
        self.conn.commit()
        if type == "level":
            self.cur.execute(f'UPDATE "main"."user" SET "level" = {level} WHERE qq_number={qq} and qq_group={group}')

        if self.cur.rowcount == 0:
            print("更新数据没有成功")
            return False
        self.conn.commit()
        return True


    def userExist(self,qq, group,global_user=False):
        if global_user == False:
            user = list(self.cur.execute(f"SELECT qq_number,qq_group  from user where qq_number={qq} and qq_group={group}"))
            if len(user) > 0:
                return True
            else:
                return False
        else:
            user = list(self.cur.execute("SELECT qq  from global_user where qq = ? ",(qq,)))
            if len(user) > 0:
                return True
            else:
                return False


    def global_user(self,qq, status, desc):
        if self.userExist(qq,"",True):
            self.cur.execute('DELETE FROM "main"."global_user" WHERE qq= ? ',(qq,))
            self.conn.commit()
            if self.cur.rowcount == 0:
                print("更新数据没有成功")
                return "更新数据没有成功"
            return f"已删除({qq})管理员"

        else:
            self.cur.execute('''
            INSERT INTO "main"."global_user"("qq", "status", "desc") VALUES (?, ?, ?)
            ''', (qq, status, desc))
            self.conn.commit()
            if self.cur.rowcount == 0:
                return "更新数据没有成功"
        return f"已将({qq})设为管理员"

    def user_check(self,qq, status):
        if status == "admin":
            user = list(self.cur.execute("SELECT qq,status  from global_user where qq= ? and status= 'admin'",(qq,)))
            if len(user) > 0:
                return True
            else:
                return False

class Log(DatabaseAdapter):
    def write(self,member,group,type,message):
        self.cur.execute('INSERT INTO "main"."log"("time", "member", "group", "type", "message") VALUES (?,?,?,?,?)',(dateTime.dateTimeToTimestamp(),member,group,type,message))
        self.conn.commit()
        if self.cur.rowcount == 0:
             print("写入日志失败")




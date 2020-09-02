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

        self.cur.execute('''
CREATE TABLE "main"."queue" (
  "id" INTEGER NOT NULL,
  "type" integer(20),
  "qq_group" integer(20),
  "qq_number" INTEGER(20),
  "create_date" text,
  PRIMARY KEY ("id")
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
            return f"已将({qq})从{status}权限组移除"
        else:
            self.cur.execute('''
            INSERT INTO "main"."global_user"("qq", "status", "desc") VALUES (?, ?, ?)
            ''', (qq, status, desc))
            self.conn.commit()
            if self.cur.rowcount == 0:
                return "更新数据没有成功"
        return f"已将({qq})添加到{status}权限组"

    def user_check(self,qq, status):
        user = list(self.cur.execute("SELECT qq,status  from global_user where qq= ? and status= ?",(qq,status)))
        self.conn.commit()
        if len(user) > 0:
            return True
        else:
            return False
    def userInfo(self,qq):
        permissionList = list(self.cur.execute("SELECT qq,status  from global_user where qq= ?",(qq,)))
        self.conn.commit()
        if len(permissionList) > 0:
            permission = str(qq) + "的权限列表:\n"
            for x in permissionList:
                permission += x[1] + ","
            return permission[:-1]
        else:
            return f"QQ({str(qq) })没有在任何一个权限组中"
    def joinQueue(self,type,qq_group, qq_number, create_date=None):
        if create_date == None:create_date = dateTime.timestampToDateTime()
        sql = "INSERT INTO `queue` (`type`, `qq_group`, `qq_number`, `create_date`) VALUES (?, ?, ?, ?)"
        self.cur.execute(sql, (type,qq_group, qq_number, create_date))
        self.conn.commit()
        if not self.cur.rowcount == 0:
             return True
        else:
            return False

    def searchQueue(self,type,qq_group, qq_number):
        sql = "SELECT id,type,qq_group,qq_number  from queue where type= ? and qq_group=? and qq_number=?"
        result = tuple(self.cur.execute(sql, (type,qq_group, qq_number)))
        self.conn.commit()
        return result

    def deleteQueue(self,id):
        sql = "DELETE FROM queue WHERE id = ?"
        self.cur.execute(sql,(id,))
        self.conn.commit()
        if not self.cur.rowcount == 0:
            return False
        else:
            return True

class Log(DatabaseAdapter):
    def write(self,member,group,type,message):
        self.cur.execute('INSERT INTO "main"."log"("time", "member", "group", "type", "message") VALUES (?,?,?,?,?)',(dateTime.dateTimeToTimestamp(),member,group,type,message))
        self.conn.commit()
        if self.cur.rowcount == 0:
             print("写入日志失败")




from dateutil.parser import parse
import time
import datetime
from datetime import datetime
class DateTimeGenerator:
    def timestampToDateTime(self,timestamp=None):
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if timestamp == None: return time_now
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        return time_now

    def dateTimeToTimestamp(self,datetime=None):
        time_now = time.mktime(time.strptime(self.timestampToDateTime(), '%Y-%m-%d %H:%M:%S'))
        if datetime == None: return int(time_now)
        time_now = time.mktime(time.strptime(datetime, '%Y-%m-%d %H:%M:%S'))
        return int(time_now)

    def timeFormtter_TimeStamp(self,dt):
        datestr = self.chineseDateParse(dt)
        dt = parse(dt,default=datetime.datetime(2000, 1, 1),dayfirst=True)  # 解析日期时间
        print(dt)
        timeArray = dt.timetuple()
        timeStamp = int(time.mktime(timeArray))
        # 转换为时间戳
        return timeStamp

    def timeFormtter(self,timeStampArray, format='%Y-%m-%d %H:%M:%S'):
        timeArray = []
        if not isinstance(timeStampArray, str):
            for dt in timeStampArray:
                timeArray.append(time.strftime(format, time.localtime(self.timeFormtter_TimeStamp(dt))))
            return timeArray
        else:
            timeStampArray = [timeStampArray]
            for dt in timeStampArray:
                timeArray.append(time.strftime(format, time.localtime(self.timeFormtter_TimeStamp(dt))))
            return timeArray[0]

    def chineseDateParse(self,datestr):
        datestr = datestr.replace(u'年', '-')
        datestr = datestr.replace(u'月', '-')
        datestr = datestr.replace(u'日', '-')
        datestr = datestr.replace(u'时', ':')
        datestr = datestr.replace(u'分', ':')
        datestr = datestr.replace(u'秒', '')
        return datestr

    # def isValidDay(self,datestr):
    #     datestr = self.chineseDateParse(datestr)
    #     a:bool
    #     b:bool
    #     try:
    #         self.timeFormtter(datestr)
    #     except:
    #         a =  True
    #     else:
    #         a = False
    #
    #     try:
    #         date.fromisoformat(datestr)
    #     except:
    #         b =  False
    #     else:
    #         b =  True
    #
    #     if(a or b):
    #         try:
    #             self.timeFormtter(datestr)
    #         except:
    #             return False
    #         else:
    #             return True
    #     else:
    #         return False
    #

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

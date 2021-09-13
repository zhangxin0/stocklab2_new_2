"""
止盈 & 止损通知
1. web接口将代码、买入价、止盈位、止损位录入db；重复的symbol进行状态更新，else 写入
2. 定时任务通知，通知完成后状态置为0（status=1有效，0无效）

"""
import sys

sys.path.append('/stocklab2_new_2')
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from web.controllers.notification.notify import Message
import urllib.request
from web.controllers.compute.common.WriteDb import WriteDb
from web.controllers.compute.common.ReadDb import ReadDb


class SendMessage(object):
    def send_message(self):
        # 在开市后进行:
        time = datetime.now()
        start_time = datetime(time.year, time.month, time.day, 9, 25)
        end_time = datetime(time.year, time.month, time.day, 15, 0)
        # 非开市时间 return
        if not (time >= start_time and time <= end_time):
            return
        table = 'sale_point_notify'
        sql = f'select * from {table} where status=1'
        readDb = ReadDb(sql)
        sale_points = readDb.read()
        for sale_point in sale_points:
            symbol = sale_point[1]
            user_id = sale_point[2]
            status = sale_point[3]
            buy_price = sale_point[4]
            profit_point = sale_point[5]
            cut_point = sale_point[6]
            sql_user = f'select * from user where uid={user_id}'
            readUser = ReadDb(sql_user)
            user = readUser.read()[0]
            phone = user[2]
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
            send = Message()
            if status:
                operation = self.get_operation(symbol, buy_price, profit_point, cut_point)
                if operation:
                    send.notify(symbol, operation, phone)
                    # 写入数据库:
                    sql = f"update {table} set status=0,modify_time='{time}' where symbol='{symbol}' and user_id={user_id}"
                    writeDb = WriteDb(sql)
                    writeDb.write()

    def get_operation(self, symbol, buy_price, profit_point, cut_point):
        price = self.get_current_price(symbol)
        rate = (price - buy_price) / buy_price * 100
        if rate >= profit_point:
            operation = 'SUCCESS'
        elif rate <= -cut_point:
            operation = 'FAILED'
        else:
            operation = None
        return operation

    def get_current_price(self, symbol):
        if symbol[-1] == 'Z':
            symbol = 'sz' + symbol[0:6]
        elif symbol[-1] == 'S':
            symbol = 'sh' + symbol[0:6]
        # url = f'http://q.stock.sohu.com/hisHq?code=cn_{symbol1}&start={start_date}&end={end_date}&stat=1&order=D&period=d'
        urlData = f'http://hq.sinajs.cn/list={symbol}'
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(urlData, headers=hdr)
        webURL = urllib.request.urlopen(req)
        # “股票名称、今日开盘价、昨日收盘价、当前价格、今日最高价、今日最低价..
        price = webURL.read().decode('latin-1').split('=')[1].split(',')[3]
        # 保留2位小数
        price = float(price[:-1])
        return price

    def main(self):
        print('开始定时更新任务，每15s更新是否发信息.')
        scheduler = BlockingScheduler()
        scheduler.add_job(self.send_message, 'interval', seconds=15)
        try:
            scheduler.start()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    update = SendMessage()
    update.main()

"""
Update database on 1800 seconds intervals.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from web.controllers.compute.common.ReadCursor import ReadCursor
from web.controllers.compute.common.WriteDb import WriteDb
from web.controllers.compute.common.ReadDb import ReadDb
import web.controllers.compute.Predict as Predict
import web.controllers.compute.GetData as getData


class Update():
    # nh_result, gold_cross_result
    def predict_nh(self):
        # 计算选股结果:
        table = 'nh_result'
        readDb = ReadDb(f'select * from {table} order by {table}.date desc limit 1')
        get_res = readDb.read()
        if not get_res:
            result_date = '19930624'
        else:
            # id | symbol    | date     | price
            result_date = readDb.read()[0][2]
        # 更改date = 数据库里最新的日期，如果数据库更新，要执行选股操作
        readCursor = ReadCursor()
        db_date = ('').join(readCursor.read().split('-'))
        dates = []
        symbols = []
        prices = []
        names = []
        if result_date and result_date >= db_date:
            print('粘合选股已更新！')
            return
        else:
            # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
            res = Predict.predict(0,'nh')
            count = 0
            for item in res:
                count += 1
                # 设定发送上限为7个选出股：
                if count > 7:
                    break
                names.append(ReadDb(f"select * from stock_info where symbol='{item[0]}' limit 1").read()[0][3])
                dates.append(('').join(item[1].trade_date[0].split('-')))
                symbols.append(item[0])
                # 买入价格按照单日收盘价计算
                prices.append(item[1].close[0])
            ## 添加至选股数据库：
            for i in range(len(symbols)):
                date = dates[i]
                symbol = symbols[i]
                price = prices[i]
                name = names[i]
                try:
                    # 写入数据库:
                    sql = f"insert into {table} (symbol,name,date,price) values ('{symbol}','{name}','{date}',{price})"
                    writeDb = WriteDb(sql)
                    writeDb.write()
                except Exception as e:
                    print('predict result write to db error!',e)

    def predict_gold_cross(self):
        # 计算选股结果:
        table = 'gold_cross_result'
        readDb = ReadDb(f'select * from {table} order by {table}.date desc limit 1')
        get_res = readDb.read()
        if not get_res:
            result_date = '19930624'
        else:
            # id | symbol    | date     | price
            result_date = readDb.read()[0][2]
        # 更改date = 数据库里最新的日期，如果数据库更新，要执行选股操作
        readCursor = ReadCursor()
        db_date = ('').join(readCursor.read().split('-'))
        dates = []
        symbols = []
        prices = []
        names = []
        if result_date and result_date >= db_date:
            print('金叉选股已更新！')
            return
        else:
            # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
            res = Predict.predict(0,'gold_cross')
            count = 0
            for item in res:
                count += 1
                # 设定发送上限为7个选出股：
                if count > 7:
                    break
                names.append(ReadDb(f"select * from stock_info where symbol='{item[0]}' limit 1").read()[0][3])
                dates.append(('').join(item[1].trade_date[0].split('-')))
                symbols.append(item[0])
                # 买入价格按照单日收盘价计算
                prices.append(item[1].close[0])
            ## 添加至选股数据库：
            for i in range(len(symbols)):
                date = dates[i]
                symbol = symbols[i]
                price = prices[i]
                name = names[i]
                try:
                    # 写入数据库:
                    sql = f"insert into {table} (symbol,name,date,price) values ('{symbol}','{name}','{date}',{price})"
                    writeDb = WriteDb(sql)
                    writeDb.write()
                except Exception as e:
                    print('predict result write to db error!',e)


    def update(self):
        getData.main()

    def main(self):
        self.update()
        print('开始定时更新任务，每0.5小时更新数据库和选股结果.')
        scheduler = BlockingScheduler()
        scheduler.add_job(self.predict_nh, 'interval', hours=0.5)
        scheduler.add_job(self.predict_gold_cross, 'interval', hours=0.5)
        scheduler.add_job(self.update, 'interval', hours=0.5)
        scheduler.start()


if __name__ == '__main__':
    update = Update()
    update.main()

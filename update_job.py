"""
Update database on 1800 seconds intervals.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from web.controllers.compute.common.ReadCursor import ReadCursor
from web.controllers.compute.common.WriteDb import WriteDb
from web.controllers.compute.common.ReadDb import ReadDb
import web.controllers.compute.Predict as Predict
import web.controllers.compute.GetData as getData
import datetime


class Update():
    # nh_result, gold_cross_result
    def predict_base(self, table, option):
        # 计算选股结果:
        readDb = ReadDb(f'select * from {table} order by {table}.date desc limit 1')
        get_res = readDb.read()
        if not get_res:
            result_date = '19930624'
        else:
            # id | symbol | name   | date     | price
            result_date = readDb.read()[0][3]
        # 更改date = 数据库里最新的日期，如果数据库更新，要执行选股操作
        readCursor = ReadCursor()
        db_date = ('').join(readCursor.read().split('-'))
        dates = []
        symbols = []
        prices = []
        names = []
        if result_date and result_date >= db_date and not (datetime.datetime.now().hour>=14 and datetime.datetime.now().minute>=30):
            print(f'{option}选股结果已更新！')
            return
        else:
            # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
            res = Predict.predict(0, option)
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
                    print('predict result write to db error!', e)
            # 如果没有结果，也写入数据库
            try:
                # 写入数据库:
                if not len(symbols):
                    sql = f"insert into {table} (date) values ('{db_date}')"
                    writeDb = WriteDb(sql)
                    writeDb.write()
            except Exception as e:
                print('predict result write to db error!', e)

    def predict_nh(self):
        # 计算选股结果:
        table = 'nh_result'
        option = 'nh'
        self.predict_base(table,option)

    def predict_nh_pre(self):
        table = 'nh_result_pre'
        option = 'nh'
        self.predict_base(table,option)

    def predict_gold_cross(self):
        # 计算选股结果:
        table = 'gold_cross_result'
        option = 'gold_cross'
        self.predict_base(table, option)

    def predict_gold_cross_pre(self):
        # 计算选股结果:
        table = 'gold_cross_result_pre'
        option = 'gold_cross'
        self.predict_base(table, option)

    def predict_second_up(self):
        # 计算选股结果:
        table = 'second_up_result'
        option = 'second_up'
        self.predict_base(table, option)

    def predict_second_up_pre(self):
        # 计算选股结果:
        table = 'second_up_result_pre'
        option = 'second_up'
        self.predict_base(table, option)

    def update(self):
        getData.main()

    def update_pre(self):
        getData.main_pre()

    def main(self):
        print('开始定时更新任务，每天18点更新数据库和19点更新选股结果.')
        scheduler = BlockingScheduler()
        scheduler.add_job(self.update, 'cron', hour=18, minute=0)
        scheduler.add_job(self.predict_nh, 'cron', hour=18, minute=10)
        scheduler.add_job(self.predict_gold_cross, 'cron', hour=18, minute=20)
        scheduler.add_job(self.predict_second_up, 'cron', hour=18, minute=30)
        # 下午14：30 开始，更新数据库，预测出收盘价=cur_price和成交量=cur_vol*1.125:
        scheduler.add_job(self.update_pre, 'cron', hour=14, minute=30)
        # 14:40 前选出当天的股票:
        scheduler.add_job(self.predict_nh_pre, 'cron', hour=14, minute=35)
        scheduler.add_job(self.predict_gold_cross_pre, 'cron', hour=14, minute=35)
        scheduler.add_job(self.predict_second_up_pre, 'cron', hour=14, minute=35)

        try:
            scheduler.start()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    update = Update()
    update.main()
    # update.update()
    # update.predict_nh()
    # update.predict_gold_cross()
    # update.predict_second_up()
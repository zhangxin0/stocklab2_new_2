
from web.controllers.compute.common.WriteDb import WriteDb
from web.controllers.compute.common.ReadDb import ReadDb
from web.controllers.compute.common.ReadCursor import ReadCursor
import web.controllers.compute.Predict as Predict


def predict():
    # 计算选股结果:
    readDb = ReadDb('select * from result order by result.date desc limit 1')
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
    if result_date and result_date >= db_date:
        return
    else:
        # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
        res = Predict.predict(0)
        count = 0
        for item in res:
            count += 1
            # 设定发送上限为7个选出股：
            if count > 7:
                break
            dates.append(('').join(item[1].trade_date[0].split('-')))
            symbols.append(item[0])
            # 买入价格按照单日收盘价计算
            prices.append(item[1].close[0])
        ## 添加至选股数据库：
        for i in range(len(symbols)):
            date = dates[i]
            symbol = symbols[i]
            price = prices[i]
            try:
                # 写入数据库:
                sql = f"insert into result (symbol,date,price) values ('{symbol}','{date}',{price})"
                writeDb = WriteDb(sql)
                writeDb.write()
            except Exception as e:
                print('predict result write to db error!', e)

predict()
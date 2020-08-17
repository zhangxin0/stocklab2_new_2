"""
算法HTTP服务：回测/预测 选股
此文件可独立flask 框架sqlachemy运行，方便调试
This file is to pre-process data
Input: stock symbol, cur_date
Output: algorithm indexes
"""
import numpy as np
from web.controllers.compute.GetData import GetData
from web.controllers.compute.common.ReadDb import ReadDb


def predict(cur):
    class ComputeIndex():
        # select stock symbol from cur(date), if cur ==0 , from now or from history.
        def __init__(self, symbol, cur):
            # name, open, close, low, trade_date, high, vol
            self.symbol = symbol
            self.cur = cur
            self.name = []
            self.open = []
            self.close = []
            self.train_close = []
            self.test_close = []
            self.low = []
            self.train_low = []
            self.test_low = []
            self.trade_date = []
            self.train_trade_date = []
            self.test_trade_date = []
            self.high = []
            self.train_high = []
            self.test_high = []
            self.vol = []
            self.train_vol = []
            self.test_vol = []
            self.initializer(cur)

        def initializer(self, cur):
            # data [()]  --> [(id0,symbol1,trade_date2,name3,open4,close5,high6,low7,vol8),(..),...]
            sql = f"SELECT * FROM stock_info WHERE stock_info.symbol = '{self.symbol}' ORDER BY stock_info.trade_date DESC"
            readDb = ReadDb(sql)
            query_set = readDb.read()
            for data in query_set:
                self.name.append(data[3])
                self.open.append(data[4])
                self.close.append(data[5])
                self.low.append(data[7])
                self.trade_date.append(data[2])
                self.high.append(data[6])
                self.vol.append(data[8])

            # train: cur .... old 当前历史数据
            self.train_close = self.close[cur:]
            self.train_open = self.open[cur:]
            self.train_high = self.high[cur:]
            self.train_vol = self.vol[cur:]
            self.train_low = self.low[cur:]
            # test: now ... cur
            self.test_open = self.open[:cur]
            self.test_close = self.close[:cur]
            self.test_high = self.high[:cur]
            self.test_vol = self.vol[:cur]
            self.test_low = self.low[:cur]

        # pre 表示基于当前时间cur， pre天前的值
        def MA(self, num, pre):
            sum = 0
            # train_close 基于当前时间为起点
            for i in range(pre, pre + num):
                sum += self.train_close[i]
            return sum / num

        def VOL(self, num):
            return self.train_vol[num]

        # 空头向下 k10 and k5 向下不能太陡
        def k(self, num):
            ma = self.MA(num, 0)
            ma_pre3 = self.MA(num, 3)
            return (ma - ma_pre3) / ma

        def fall(self):
            if self.k(5) < -0.04 or self.k(10) < -0.05:
                return True
            return False

        # 连续两天close < MA5:
        def lower_ma5(self):
            if self.train_close[1] < self.MA(5, 1) and self.train_close[2] < self.MA(5, 2):
                return True
            return False

        # 涨停基因
        def gene(self):
            res = False
            for i in range(1,60):
                rate = (self.train_close[i] - self.open[i])/self.open[i]*100
                if rate >= 9.9:
                    res = True
            return res

        def gold_cross(self):
            # 均线粘合
            w1 = (self.MA(20, 0) - self.MA(5, 0)) / self.MA(5, 0)
            # 股价站上5日线
            w2 = self.train_close[0] > self.MA(5, 0)
            # 前一天和今天不能死叉
            #w3 = self.MA(5,1) > self.MA(20,1) or self.MA(10,1) > self.MA(20,1)
            # w1 from 0.03 to 0.02
            if self.MA(5, 0) < self.MA(20, 0) and w1 <= 0.03 and w2 and \
                    self.MA(10, 0) < self.MA(20, 0) and self.MA(60, 0) < self.MA(20, 0):
                return True
            else:
                return False

        def mv(self, n):
            # increasing rate
            L = []
            K = []
            for i in range(3):
                K.append((self.MA(n, i) - self.MA(n, i + 1)) / self.MA(n, i + 1))
                L.append(self.VOL(i))
            V_20 = 0
            for i in range(20):
                V_20 += self.VOL(i)
            V_20 = V_20 / 20
            return (np.dot(K, L) / V_20)

        # A 当日涨幅小于5% B 22日上涨<27% C 13日下跌<15%
        def Max(self, a, b):
            return a if a > b else b

        def Min(self, a, b):
            return a if a < b else b

        def trend_good(self):
            # 当日<4.9%
            close = self.train_close[0]
            open = self.train_open[0]
            increase = (close - open) / open * 100
            w1 = increase < 4.9
            # 22日上涨 < 27%
            # 先找到最高点，再从左边找最低点，表示上升
            max = float('-inf')
            max_point = 0
            for i in range(23):
                high_today = self.Max(self.train_close[i], self.train_open[i])
                if high_today > max:
                    max = high_today
                    max_point = i
            min = max
            for i in range(max_point, 23):
                low_today = self.Min(self.train_close[i], self.train_open[i])
                if low_today < min:
                    min = low_today
            w2 = (max - min) / min * 100 < 27
            # 先找到最高点，从最高点右边找最低，表示下降
            max = float('-inf')
            max_point = 0
            for i in range(14):
                high_today = self.Max(self.train_close[i], self.train_open[i])
                if high_today > max:
                    max = high_today
                    max_point = i
            min = max
            for i in range(max_point):
                low_today = self.Min(self.train_close[i], self.train_open[i])
                if low_today < min:
                    min = low_today
            w3 = (max - min) / max * 100 < 15
            return w1 and w2 and w3

        def is_pressure_line(self):
            # calulate if there are 144 or 233 or other type of average line over in 3% range
            pass

        def select(self):
            # data filtering:
            if len(self.train_close) < 100:
                return False
            # re-define thredshold by more data
            if self.mv(20) > -0.004 and self.gold_cross() and self.mv(5) < 0.025 and self.gene():
                return True

    def predict_profit(symbol, cur):
        computeIndex = ComputeIndex(symbol, cur)
        max_price = float('-inf')
        day = 0
        # 这里test应该从最后面（old）开始数 |n-1| 个
        # choose highest from the future n days
        n = -6
        for i in range(-1, n, -1):
            if computeIndex.test_high[i] > max_price:
                max_price = computeIndex.test_high[i]
                day = i
        # day 表示几天后达到最大利润
        return day, (max_price - computeIndex.train_close[0]) / computeIndex.train_close[0] * 100

    # 选股，cur表示当前位置 cur=0 表示今天， cur=n, n 天前
    def predict(symbols, cur):
        res = []
        count = 0
        print("开始选股...")
        for symbol in symbols:
            computeIndex = ComputeIndex(symbol, cur)
            if computeIndex.select():
                count += 1
                # print(f"Number {count}:", symbol)
                res.append((symbol, computeIndex, cur))
        # sort res by (mv20,-mv5): use w1*mv20 - w2*mv5
        # 修改：早期版本只选取mv20-mv5最大的一只股票
        # 修改后：将所有当天符合条件的股票按照mv20-mv5倒序排序，将列表返回，以便按照板块进行选择买入：
        if res:
            # 修改前：
            # res.sort(key=lambda x: (x[1].mv(20) - x[1].mv(5)))
            # 修改后：
            res.sort(key=lambda x: -(x[1].mv(20) - x[1].mv(5)))
            # print best result
            #print(res[-1])
            #res = res[-1]
            print(res[0])
        # 返回结果列表
        return res

    getData = GetData()
    symbols = getData.symbol
    # 0 predict for future
    res = predict(symbols, cur)
    return res


print(predict(0))



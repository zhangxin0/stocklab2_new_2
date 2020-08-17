'''
根据symbol，cur
获取历史数据
cur=0 表示以train和test数据以当前为基点
默认使用完全数据，eg: ComputeIndex(symbol,0).close --> [今日close，昨日，...]
'''

import numpy as np
from web.controllers.compute.common.ReadDb import ReadDb

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

    def gold_cross(self):
        # 均线粘合
        w1 = (self.MA(20, 0) - self.MA(5, 0)) / self.MA(5, 0)
        # 股价站上5日线
        w2 = self.train_close[0] > self.MA(5, 0)
        # 前一天和今天不能死叉
        # w3 = self.MA(5,1) > self.MA(20,1) or self.MA(10,1) > self.MA(20,1)
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
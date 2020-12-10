"""
Alert ***
==>核心算法文件
1. 读取预测需要的原始数据
2.筛选算法：动量、金叉形态、涨停基因
==> 供回测和预测功能使用
"""

import numpy as np
import logging
from web.controllers.compute.common.ReadDb import ReadDb


class ComputeIndex():
    # select stock symbol from cur(date), if cur ==0 , from now or from history.
    def __init__(self, symbol, cur=0, option=None):
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
        self.option = option

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
    def gene(self, day):
        res = False
        for i in range(0, day):
            rate = (self.train_close[i] - self.train_close[i + 1]) / self.train_close[i + 1] * 100
            if rate >= 9.9:
                return True
        return res

    # 14日内3连板 改为2连板+涨幅超过30%
    def floor_3(self):
        count = 0
        max = 0
        res = False
        for i in range(0, 30):
            rate = (self.train_close[i] - self.train_close[i + 1]) / self.train_close[i + 1] * 100
            if rate >= 9.9:
                count += 1
            else:
                count = 0
            if count > max:
                max = count
        # 计算最大涨幅
        # max_price = self.train_high[0]
        # min_price = self.train_low[0]
        # for i in range(13, -1, -1):
        #     if self.train_high[i] > max_price:
        #         max_price = self.train_high[i]
        #     if self.train_low[i] < min_price:
        #         min_price = self.train_low[i]
        # rate = (max_price - min_price) / min_price * 100
        if max >= 3:
            res = True
        return res

    # 14日内涨停板数量>2
    def floor_2(self):
        count = 0
        res = False
        for i in range(0, 14):
            rate = (self.train_close[i] - self.train_close[i + 1]) / self.train_close[i + 1] * 100
            if rate >= 9.9:
                count += 1
        if count >= 2:
            res = True
        return res

    # 没有出现过二次反弹
    def no_second_up(self):
        res = True
        # 找到最高点
        max = 0
        day_max = 0
        index_80 = 14
        for i in range(14, -1, -1):
            if self.train_high[i] > max:
                max = self.train_high[i]
                day_max = i
        # 计算从最高点下跌20%后的index
        for i in range(day_max, -1, -1):
            if self.train_low[i] / max <= 0.8:
                index_80 = i
                break
        # 计算max1 以及index_max1
        index_max1 = index_80
        max1 = 0
        for i in range(index_80, -1, -1):
            if self.train_high[i] > max1:
                max1 = self.train_high[i]
                index_max1 = i
        # 计算min1
        min1 = self.train_low[index_80]
        for i in range(index_80, index_max1, -1):
            if self.train_low[i] < min1:
                min1 = self.train_low[i]
        # 计算反弹涨幅
        raise_rate = (max1 - min1) / min1 * 100
        if raise_rate >= 8:
            res = False
        return res

    # 前一天的收盘价高于前2天1%以上 并且当天最高价>0%(上涨） 第二天以0.5%的价格买入
    def close_high(self):
        res = False
        rate = (self.train_close[1] - self.train_close[2]) / self.train_close[2] * 100
        rate_today = (self.train_high[0] - self.train_close[1]) / self.train_close[1] * 100
        # 实盘中没有以下，回测使用，实盘人为判断是否买入，涨到0.5%
        # rate_buy = (self.test_high[-1] - self.train_close[0]) / self.train_close[0] * 100
        # if rate >= 1 and rate_buy >= 0.5:
        if rate >= 1 and rate_today >= 0:
            res = True
        return res

    # 最低股价没有跌破14日内第一个涨停的最低点:
    def no_drop_broken(self):
        res = True
        min_start = 0
        # 找到最高点
        max = 0
        day_max = 0
        for i in range(13, -1, -1):
            if self.train_high[i] > max:
                max = self.train_high[i]
                day_max = i
        # 计算min
        min = max
        for i in range(day_max, -1, -1):
            if self.train_low[i] < min:
                min = self.train_low[i]
        for i in range(0, 14):
            rate = (self.train_close[i] - self.train_close[i + 1]) / self.train_close[i + 1] * 100
            if rate >= 9.9:
                # 最低价不跌破第一个涨停的开盘价
                min_start = self.train_open[i]
            # 改最低价不跌破第一个涨停前一日的最高价
            # min_start = self.train_high[i + 1]
            # if min_start < self.train_open[i]:
            #     min_start = self.train_open[i]
        if min <= min_start:
            res = False
        return res

    # 选出前一日内跌幅在20%以上
    def drop_80(self):
        res = False
        # 找到最高点
        max = 0
        day_max = 0
        for i in range(13, -1, -1):
            if self.train_high[i] > max:
                max = self.train_high[i]
                day_max = i
        # 计算min
        min = max
        for i in range(day_max, -1, -1):
            if self.train_low[i] < min:
                min = self.train_low[i]
        # 计算跌幅
        drop_rate = self.train_low[0] / max
        if drop_rate < 0.8:
            return True
        return res

    def get_max(self, a, b, c, d):
        res = a
        if b > res:
            res = b
        if c > res:
            res = c
        if d > res:
            res = d
        return res

    def get_min(self, a, b, c):
        res = a
        if b < res:
            res = b
        if c < res:
            res = c
        return res

    # 30 日内，3个连续交易日涨幅<17%
    def day_15(self):
        res = True
        for i in range(29, 2, -1):
            rate = (self.get_max(self.train_close[i - 1], self.train_close[i - 2],
                                 self.train_close[i - 3], self.train_open[i - 3]) - self.get_min(
                self.train_close[i], self.train_close[i + 1], self.train_open[i])) / self.get_min(
                self.train_close[i], self.train_close[i + 1], self.train_open[i]) * 100
            rate_max = (self.get_max(self.train_high[i - 1], self.train_high[i - 2],
                                     self.train_high[i - 3], 0) - self.get_min(
                self.train_close[i], self.train_close[i + 1], self.train_open[i])) / self.get_min(
                self.train_close[i], self.train_close[i + 1], self.train_open[i]) * 100
            if rate > 15 or rate_max >= 20:
                return False
        return res

    # 没有144 233 和 377 日均线压力，close与均线的距离小于2.5%
    def no_pressure_line(self):
        # calulate if there are 144 or 233 or other type of average line over in 3% range
        res = True
        ma = []
        if len(self.train_close) >= 144:
            ma144 = self.MA(144, 0)
            ma.append(ma144)
        if len(self.train_close) >= 233:
            ma233 = self.MA(233, 0)
            ma.append(ma233)
        if len(self.train_close) >= 377:
            ma377 = self.MA(377, 0)
            ma.append(ma377)
        for element in ma:
            rate = abs(element - self.train_close[0]) / self.train_close[0] * 100
            # 均线距离过近，表明进入均线压力区
            if rate < 3:
                return False
                # 没有均线在股价上方
            if element > self.train_high[0]:
                return False
        return res

    # 20 个交易日内无缺口
    def no_gap(self):
        res = True
        for i in range(30, 0, -1):
            li = self.train_low[i]
            hi = self.train_high[i]
            li_1 = self.train_low[i - 1]
            hi_1 = self.train_high[i - 1]
            if li_1 - hi >= 0.02 or li - hi_1 >= 0.02:
                return False
        return res

    # 20 个交易日内无放量大阴线
    def no_drop(self):
        res = True
        vol_0 = self.train_vol[0]
        for i in range(20, 0, -1):
            open = self.train_open[i]
            close = self.train_close[i]
            down_rate = (open - close) / close * 100
            vol = self.train_vol[i]
            vol_rate = vol / vol_0
            if vol_rate >= 3 and down_rate >= 5:
                return False
            elif vol_rate >= 1.5 and down_rate >= 7:
                return False
        return res

    # 20个交易日内无天线
    def no_skyline(self):
        res = True
        vol_0 = self.train_vol[0]
        for i in range(20, 0, -1):
            high = self.train_high[i]
            close = self.train_close[i]
            line_height = (high - close) / close * 100
            vol = self.train_vol[i]
            vol_rate = vol / vol_0
            if vol_rate >= 1.5 and line_height >= 3:
                return False
        return res

    # 20个交易日内无跌停
    def no_drop_floor(self):
        res = True
        vol_0 = self.train_vol[0]
        for i in range(20, 0, -1):
            open = self.train_open[i]
            close = self.train_close[i]
            close1 = self.train_close[i + 1]
            if close <= close1 * 0.9:
                return False
        return res

    # 开盘大跌3%的排除
    def no_drop_open(self):
        res = True
        rate = (self.train_close[1] - self.train_open[0]) / self.train_close[1] * 100
        if rate >= 3:
            res = False
        return res

    # 量跌至14日内最高的40%一下：
    def vol_drop(self):
        res = False
        vol_0 = self.train_vol[0]
        vol_max = 0
        for i in range(14, 0, -1):
            if self.train_vol[i] > vol_max:
                vol_max = self.train_vol[i]
        if vol_0 / vol_max <= 0.4:
            res = True
        return res

    def nh(self):
        # 均线粘合
        w1 = (self.MA(20, 0) - self.MA(5, 0)) / self.MA(5, 0)
        # 股价站上5日线
        w2 = self.train_close[0] > self.MA(5, 0)
        # 前一天和今天不能死叉
        # w3 = self.MA(5,1) > self.MA(20,1) or self.MA(10,1) > self.MA(20,1)
        # w1 from 0.03 to 0.02
        if self.MA(5, 0) < self.MA(20, 0) and w1 <= 0.03 and \
                w2 and self.MA(10, 0) < self.MA(20, 0) and self.MA(60, 0) < self.MA(20, 0):
            return True
        else:
            return False

    # second up 均线形态
    def second_up(self):
        dis = (self.MA(10, 0) - self.MA(5, 0)) / self.MA(5, 0)
        if self.MA(5, 0) < self.MA(10, 0) and self.MA(20, 0) < self.MA(5, 0) and dis < 0.035:
            return True
        return False

    # 均线金叉
    def gold_cross_up(self):
        # 均线粘合
        w1 = (self.MA(5, 0) - self.MA(20, 0)) / self.MA(20, 0)
        # 股价站上5日线
        w2 = self.train_close[0] > self.MA(5, 0)
        # 前一天和今天不能死叉
        # w3 = self.MA(5,1) > self.MA(20,1) or self.MA(10,1) > self.MA(20,1)
        # w1 from 0.03 to 0.02
        # 上穿要求昨天小于今天刚好大于
        if self.MA(5, 0) > self.MA(20, 0) and self.MA(5, 1) <= self.MA(20, 1) and \
                w2 and self.MA(10, 0) < self.MA(20, 0) and self.MA(60, 0) < self.MA(20, 0):
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

    def select(self):
        # 短期内停过牌的股票，暂时不考虑进入：
        if len(self.train_close)< 70 or 0 in self.train_close[:32]:
            print(self.symbol)
            return False
        # re-define thredshold by more data
        if self.option == 'gold_cross':
            if self.mv(20) > -0.004 and self.gold_cross_up() and self.mv(
                    5) < 0.025 and self.gene(30):
                return True
        elif self.option == 'nh':
            if self.mv(20) > -0.004 and self.nh() and self.mv(
                    5) < 0.025 and self.gene(60):
                return True
        elif self.option == 'second_up':
            if self.floor_3() and self.drop_80() and self.no_drop_broken() and self.close_high() and self.no_second_up():
                return True
        # and self.floor_2() and self.day_15() and self.no_pressure_line() and self.no_gap() and self.no_drop_floor()
        return False

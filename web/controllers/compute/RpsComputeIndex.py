import numpy as np
from web.controllers.compute.common.ReadDb import ReadDb


class RpsComputeIndex():
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
        sql = f"SELECT * FROM stock_info WHERE stock_info.symbol = '{self.symbol}' ORDER BY stock_info.trade_date DESC limit 22"
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
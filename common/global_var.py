# coding:utf-8
from web.controllers.compute.GetData import GetData
from web.controllers.compute.RpsComputeIndex import RpsComputeIndex

class GlobalVar(object):
    global_dict = {}
    symbols = GetData().symbol
    close_21_dict = {}
    for symbol in symbols:
        # 可以把每只股票的computeIndex都加载到内存中（5-10MB）
        computeIndex = RpsComputeIndex(symbol, 0, None)
        close = computeIndex.train_close
        close_21_dict[symbol] = close
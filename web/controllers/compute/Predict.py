"""
算法HTTP服务：回测/预测 选股
此文件可独立flask 框架sqlachemy运行，方便调试
This file is to pre-process data
Input: stock symbol, cur_date
Output: algorithm indexes
"""

from web.controllers.compute.GetData import GetData
from web.controllers.compute.ComputeIndex import ComputeIndex


def predict(cur,option):
    # 选股，cur表示当前位置 cur=0 表示今天， cur=n, n 天前
    def predict_2(symbols, cur):
        res = []
        count = 0
        print("开始选股...")
        for symbol in symbols:
            computeIndex = ComputeIndex(symbol, cur, option)
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
            print(res[0])
        # 返回结果列表
        return res

    getData = GetData()
    symbols = getData.symbol
    # 0 predict for future
    res = predict_2(symbols, cur)
    return res


# print(predict(0, 'up_limit_failed'))

#print(predict(3,'second_up'))

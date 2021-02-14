"""
算法HTTP服务：回测/预测 选股
此文件可独立flask 框架sqlachemy运行，方便调试
This file is to pre-process data
Input: stock symbol, cur_date
Output: algorithm indexes
"""
import csv
import random
from web.controllers.compute.GetData import GetData
from web.controllers.compute.ComputeIndex import ComputeIndex

def back_predict():
    #计算最大利润
    def predict_profit(symbol, cur, win_rate):
        computeIndex = ComputeIndex(symbol, cur)
        max_price = float('-inf')
        # 记录几天后达到最大利润
        max_day = 0
        # 持有的时长，如果第一天卖出，则持有1天
        hold_time = 0
        # test[base on now, ..., the day after cur]
        # train[cur, cur-1:the day before cur, cur-2]
        n = -9
        # 从-1开始，第0天可以卖（今天下午选出，第二天开盘可以卖：提前选出算法）
        for i in range(-1, n, -1):
            # 记录盈利超过win_rate%的时间：
            if computeIndex.test_high[i] >= computeIndex.train_close[0]*(1 + win_rate/100):
                hold_time = -i
            # 记录8天内的最大盈利:
            # test数据new-->old, -1-->-9按时间顺序，基于当前时间向未来推移
            if computeIndex.test_high[i] > max_price:
                max_price = computeIndex.test_high[i]
                max_day = i
        # day 表示几天后达到最大利润
        return hold_time, max_day, (max_price - computeIndex.train_close[0]) / computeIndex.train_close[0] * 100

    # Input test period, predict past(period_start,period) ago. Note: data[new-->old]
    def back_prediction(symbols, period_start, period, option, win_rate):
        record = []  # 存储过去（period_start,period)选出的最佳股票
        # res中记录过去8天到period时间段符合条件的股票
        # i表示日期的时间位置：第i天前
        for i in range(period_start, period):
            res = []
            count = 0
            print("开始选股...")
            for symbol in symbols:
                computeIndex = ComputeIndex(symbol, i, option=option)
                try:
                    if computeIndex.select():
                        count += 1
                        # res: (symbol, mv20, mv5, day, profit) -> analyze mv20 and mv5 with profit [day: the peak in which day]
                        # res：符合一级筛选，存储所有的数据； 二级可以对指标和profit的关系进行分析
                        hold_time, day, profit = predict_profit(symbol, i, win_rate)
                        # i 表示从几天前作为当前日
                        res.append((computeIndex.trade_date[i],symbol, computeIndex.mv(20), computeIndex.mv(5), day, hold_time, profit))
                except Exception as e:
                    print(e.message)
            # sort res by (mv20,-mv5): use w1*mv20 - w2*mv5
            if not res:
                #打印出当前时间：
                print(f"Period: {i}: No satisfied result.")
                continue
            # mv5：corr -0.49, mv20:0.068   --> recalculate need
            # mv20 - mv5 越大越好，下面采用倒序排列：-(x[2] - x[3])，因此第一个最好
            # 对照实验暂时去掉
            res.sort(key=lambda x: -(x[2] - x[3]))
            # id = random.randint(0,len(res)-1)
            # 打印出日期时间的选股结果：
            print(f"Period: {i}: (date,symbol, mv20, mv5, day, hold_time, profit)", res[0])
            # record.append(res[-1])
            record.append(res[0])
        return record

    # 选股，cur表示当前位置 cur=0 表示今天， cur=n, n 天前
    # 获取历史数据 & 股票列表
    getData = GetData()
    symbols = getData.symbol
    # return '预测完成！'
    # 1 prediction verification: 预测过去6到period天数的5天内盈利
    """
    在这里设定回测的参数
    @:param option: nh, gold_cross, second_up
    @:param period_start: 选股开始日期，15表示：从15天前作为当前位置
    @:param period: 测试天数
    @:param win_rate: 选股成功的涨幅
    
    statics:
    @:param hold_time_all: 累计持有天数
    @:param count_0_10: 0-10% 最大涨幅分布
    """
    option = 'second_up'
    period_start = 32
    period = 200
    print(f'{option}算法{period_start}-{period}区间回测开始..')
    win_rate = 5
    record = back_prediction(symbols, period_start=period_start, period=period, option=option, win_rate=5)  # (symbol, mv20, mv5, day, profit)
    hold_time_all = 0
    sum = 0
    min = float('inf')
    max = float('-inf')
    failed = 0
    count_0_10 = 0
    count_10_20 = 0
    count_20_30 = 0
    count_30 = 0
    for pf in record:
        hold_time_all += pf[5]
        sum += pf[6]
        if pf[6] < 4:
            failed += 1
        if pf[6] < min:
            min = pf[6]
        if pf[6] > max:
            max = pf[6]
        if pf[6] < 10:
            count_0_10 +=1
        elif pf[6] < 20:
            count_10_20 += 1
        elif pf[6] < 30:
            count_20_30 += 1
        else:
            count_30 +=1
    print("粘合+动量+genge:")
    print("平均持有天数：", hold_time_all/len(record))
    print("选出数量:", len(record))
    print("失败数量:",failed)
    print(f"大于{win_rate}%的比例:{100-failed/len(record)*100}")
    print("平均盈利:", sum / (len(record)))
    print(f"count0_10={count_0_10},rate:{count_0_10/len(record)},count10_20={count_10_20},rate:{count_10_20/len(record)},count20_30={count_20_30},rate:{count_20_30/len(record)},count_30={count_30},rate:{count_30/len(record)}")
    print("最大盈利:", max)
    print("最小盈利:", min)
    print("选股记录:", record)
    with open('data.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for value in record:
            spamwriter.writerow(value)
    return '回测完成！'


back_predict()
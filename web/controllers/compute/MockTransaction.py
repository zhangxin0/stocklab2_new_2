'''
模拟交易，策略制定和验证
使用情景： 头一天晚上选出结果，第二天早上买入
'''

from flask import Blueprint
import web.controllers.compute.Predict as Predict

route_mockTransaction = Blueprint('mockTransaction', __name__)


def MA(num, stock_info, current_time):
    sum = 0
    for i in range(num):
        sum += stock_info.close[current_time + i]
    return sum / num


def overtime(Balance, buy_point, open):
    return Balance * open / buy_point


def dead_cross(stock_info, current_time):
    # MA5
    ma5 = MA(5, stock_info, current_time)
    ma5_pre = MA(5, stock_info, current_time + 1)
    ma10 = MA(10, stock_info, current_time)
    ma10_pre = MA(10, stock_info, current_time + 1)
    ma20 = MA(20, stock_info, current_time)
    ma20_pre = MA(20, stock_info, current_time + 1)
    # MA5 cross MA10:
    if ma5_pre > ma10_pre and ma5 <= ma10:
        return True
    # MA5 cross MA20:
    if ma5_pre > ma20_pre and ma5 <= ma20:
        return True
    return False


def k(num, stock_info, current_time):
    ma = MA(num, stock_info, current_time)
    ma_pre3 = MA(num, stock_info, current_time + 3)
    return (ma - ma_pre3) / ma


@route_mockTransaction.route('/mockTransaction')
def mockTransaction():
    Balance = 10000
    clean_time = 0
    #Single_buy = 10000
    Single_buy = Balance
    Balance_init = Balance
    Stock_Balance = 0
    start_period = 100
    # 持续时间
    test_period = 96
    buy_dict = {}
    stock_list = []
    cur = 0
    T1_limit_list = []
    prevent_lose = 10

    for time in range(test_period):
        # 每天全仓
        # cur 标记当前天位置
        cur = start_period - time
        print(f"第{cur}天前..")
        print(f"当前余额:{Balance},Single_buy:{Single_buy}")
        # 选出股票
        today_list = []
        # stock_select:(symbol,computeIndex,cur)
        # computeIndex 存储了symbol所有的历史info
        if Balance >= Single_buy:   # 因为全仓，Single_buy 每次卖出后都更新为当前Balance
            # 选出之后，假设已经买入，其实是明天以今天收盘价买入
            stock_select = Predict.predict(cur)
            # 假设不考虑重复购买相同股票
            if stock_select and (stock_select[0] not in buy_dict):
                Balance -= Single_buy
                print(f"日期{stock_select[1].trade_date[cur]}，明天开盘买入股票{stock_select[0]}，当前余额{Balance}")
                print(
                    f"k5:{k(5, stock_select[1], cur)},k10:{k(10, stock_select[1], cur)},k20:{k(20, stock_select[1], cur)}")
                stock_list.append(stock_select)
                # time + 1 ，今天选出，第二天开盘价买入
                buy_dict[stock_select[0]] = (stock_select[1].open[cur - 1], time + 1)
                today_list.append(stock_select[0])
        # 检测是否有卖出
        print('检测是否有卖出')
        for i in range(len(stock_list) - 1, -1, -1):
            stock = stock_list[i]
            date = stock[1].trade_date[cur]
            symbol = stock[0]
            buy_point = buy_dict[symbol][0]
            buy_time = buy_dict[symbol][1]
            # 到目前，已经持有天数:
            hold_time = time - buy_time
            sale_point = 5
            if hold_time > 5 and hold_time <= 8:
                sale_point = (40 - 5 * hold_time) / 3
            elif hold_time > 8:
                sale_point = -1
            if symbol not in T1_limit_list and symbol not in today_list:
                high = stock[1].high[cur]
                open = stock[1].open[cur]
                low = stock[1].low[cur]
                # 盈利卖出，制定动态sale_point
                # 持有超过8天，强制卖出
                if sale_point == -1:
                    Balance += overtime(Single_buy, buy_point, open)  # 获取当时价格售出
                    Single_buy = Balance
                    stock_list.pop(i)
                    buy_dict.pop(symbol)
                    print(f'日期{date},持有超过8天，强制卖出，盈利：{(open - buy_point) / buy_point * 100}%')
                elif (high - buy_point) / buy_point * 100 >= sale_point:
                    sold_point = sale_point if sale_point > (open - buy_point) / buy_point * 100 else (
                                                                                                                  open - buy_point) / buy_point * 100
                    Balance += Single_buy * (1 + sold_point / 100)
                    Single_buy = Balance
                    print(f"日期{date},恭喜您，盈利卖出{symbol}!盈利:{sold_point}%. 持有天数{hold_time}，账户余额:{Balance}")
                    # remove
                    stock_list.pop(i)
                    buy_dict.pop(symbol)
                # 没有形成金叉： 买入后3天MA5没有上穿MA20, 第二天以开盘价卖出
                # elif hold_time >= 3 and MA(5, stock[1], cur) < MA(20, stock[1], cur):
                #     rate = (stock[1].open[cur - 1] - buy_point) / buy_point
                #     Balance += Single_buy * (1 + rate)
                #     print(f"日期{date},未金叉第二天以开盘价卖出{symbol}，盈利{rate * 100}%, 持有天数{hold_time}")
                #     # remove
                #     stock_list.pop(i)
                #     buy_dict.pop(symbol)
                # 死叉，第二天以开盘价卖出
                elif dead_cross(stock[1], cur):
                    rate = (stock[1].open[cur - 1] - buy_point) / buy_point
                    Balance += Single_buy * (1 + rate)
                    Single_buy = Balance
                    print(f"日期{date},死叉第二天以开盘价卖出{symbol}，盈利{rate * 100}%, 持有天数{hold_time}")
                    # remove
                    stock_list.pop(i)
                    buy_dict.pop(symbol)
                # 止损卖出
                elif (buy_point - low) / buy_point * 100 >= prevent_lose:
                    Balance += Single_buy * (1 - prevent_lose / 100)
                    Single_buy = Balance
                    print(f"日期{date},止损卖出{symbol}!账户余额:{Balance}，持有天数{hold_time}")
                    stock_list.pop(i)
                    buy_dict.pop(symbol)
                # 阶段清仓
                elif time > 0 and time % 16 == 0:
                    clean_time += 1
                    rate = (stock[1].open[cur] - buy_point) / buy_point
                    Balance += Single_buy * (1 + rate)
                    Single_buy = Balance
                    print(f"日期{date},第{clean_time}次清仓，当前清理股票{symbol}，盈利{rate * 100}%, 持有天数{hold_time}")
                    # remove
                    stock_list.pop(i)
                    buy_dict.pop(symbol)

        T1_limit_list = today_list

    # 计算证券余额
    print('计算证券余额')
    for stock in stock_list:
        Stock_Balance += Single_buy + Single_buy * (stock[1].close[cur] - buy_dict[stock[0]][0]) / buy_dict[stock[0]][0]
    print(f'{test_period}天后账户余额:', Balance)
    print(f'{test_period}天后证券余额:', Stock_Balance)
    print("盈利率：", (Balance + Stock_Balance - Balance_init) / Balance_init * 100, '%')
    return "模拟交易完毕"

# 模拟交易log(珍贵数据，误删除）
# I period 过去（14 - 30）天交易结果：
# 策略1， 按照平均盈利判定是否卖出 卖点:7.8%
# 实验1: 总周期16天
# 无止损模式
# 16天后账户余额: 780.0
# 16天后证券余额: 46045.75056927983
# 盈利率： -6.348498861440341 %

# 策略2， 按照平均盈利判定是否卖出 卖点:3%
# period 过去（14 - 30）天交易结果：
# 实验1: 总周期16天
# 无止损模式
# 16天后账户余额: 2400.0
# 16天后证券余额: 49047.601512414054
# 盈利率： 2.895203024828108 %


# 止损模式 3%
# 计算证券余额
# 16天后账户余额: 30000.0
# 16天后证券余额: 20257.35294117647
# 盈利率： 0.5147058823529369 %

# 策略3， 卖点:5% period(14,30)
# 16天后账户余额: 3500.0
# 16天后证券余额: 48894.946627377365
# 盈利率： 4.78989325475473 %

# 卖点5% + 动态出手:
# 计算证券余额
# 16天后账户余额: 23567.79661016949
# 16天后证券余额: 29996.6415426316
# 盈利率： 7.128876305602186 % 


# II period 过去（4 - 20）天交易结果： sale_point = 5%

# 计算证券余额
# 16天后账户余额: 15000.0
# 16天后证券余额: 40243.768395043786
# 盈利率： 10.487536790087573 %

# 动态出手
# 计算证券余额
# 16天后账户余额: 24059.36073059361
# 16天后证券余额: 30517.740997783512
# 盈利率： 9.154203456754244 %


# III period 过去（10 - 40）天交易结果：
# 计算证券余额
# 30天后账户余额: 16500.0
# 30天后证券余额: 39366.568172295316
# 盈利率： 11.733136344590632 %
# 动态出手
# 计算证券余额
# 30天后账户余额: 15106.263757916822
# 30天后证券余额: 39545.21177070376
# 盈利率： 9.302951057241167 %
# 没有及时止损，提高了风险
# 止损设定为6%
# 检测是否有卖出
# 计算证券余额
# 30天后账户余额: 14271.061528059501
# 30天后证券余额: 39545.21177070376
# 盈利率： 7.632546597526526 %
# 止损设定为10%
# 计算证券余额
# 30天后账户余额: 15681.506261794479
# 30天后证券余额: 39545.21177070376
# 盈利率： 10.45343606499648 %
# 止损10% + 死叉止损
# 计算证券余额
# 30天后账户余额: 16144.78309795267
# 30天后证券余额: 39545.21177070376
# 盈利率： 11.379989737312862 %


# IV period 过去（10 - 100）天交易结果：
# 计算证券余额
# 90天后账户余额: 11500.0
# 90天后证券余额: 47705.6962521572
# 盈利率： 18.411392504314396 %
# 动态出手


# V period 过去（10 - 190）天交易结果：
# 计算证券余额
# 180天后账户余额: 15000.0
# 180天后证券余额: 42832.16345623264
# 盈利率： 15.664326912465288 %
# 动态出手


# ******************************************************
# 单仓位21000实验结果
# period (40,10)
# 计算证券余额
# 30天后账户余额: 6000.0
# 30天后证券余额: 20073.715714115668
# 盈利率： 24.160551019598415 %

# IV period 过去（10 - 100）天交易结果：
# 计算证券余额
# 90天后账户余额: 2708.8465256102427
# 90天后证券余额: 20073.715714115668
# 盈利率： 8.48839161774243 %
# 计算证券余额
# period(84,100)
# 16天后账户余额: 200.4219409282723
# 16天后证券余额: 19215.215622457283
# 盈利率： -7.544583031497348 %
# period(68,84)
# 检测是否有卖出
# 计算证券余额
# 16天后账户余额: 1849.6740780426826
# 16天后证券余额: 19648.662839165663
# 盈利率： 2.3730329390873695 %
# period(36,52)
# 16天后账户余额: 2833.333333333334
# 16天后证券余额: 19681.041466167237
# 盈利率： 7.211308569050328 %

# period(20,36)
# 16天后账户余额: 20803.832576903682
# 16天后证券余额: 0
# 盈利率： -0.9341305861729432 %

# period(4,20)
# 计算证券余额
# 16天后账户余额: 24833.333333333336
# 16天后证券余额: 0
# 盈利率： 18.253968253968267 %

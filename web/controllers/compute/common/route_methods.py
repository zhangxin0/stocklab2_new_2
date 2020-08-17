'''
Store methods used in controllers
'''

def MA(num, stock_info, current_time):
    sum = 0
    for i in range(num):
        sum += stock_info.close[current_time + i]
    return sum / num


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
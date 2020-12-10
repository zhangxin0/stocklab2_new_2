'''
获取和更新股票数据
'''
import tushare as ts
from datetime import datetime
from datetime import timedelta
import aiohttp
import json
import asyncio
import time
# 异步connection to mysql
from aiomysql import create_pool
from web.controllers.compute.common.ReadCursor import ReadCursor
import mysql


# Step 1: Get stock list and stock name from Tushare API in init
class GetData:
    """
        通过ts获取股票数据：
        name：list of all stocks' name
        symbol: list of all stocks' code
    """

    def __init__(self):
        self.cur_date = datetime.now().strftime('%Y%m%d')
        self.name = []
        self.symbol = []
        self.dict_symbol_name = {}
        ts.set_token('ada6b004ecd3db66563e9f5987722d3d5ca4013ac8f0a0901d63ea3b')
        pro = ts.pro_api()
        # 查询当前所有正常上市交易的股票列表 从tushare 至 数据库
        # data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        connection = mysql.connector.connect(host='localhost', port=3306,
                                 user='root', password='Zx1993624!',
                                 database='stock_ai')
        sql_select_Query = "select distinct symbol,name from stock_info"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        data = cursor.fetchall()
        # 查询当前所有正常上市交易的股票列表 --> 转换为list
        symbol = []
        name = []
        for obj in data:
            symbol.append(obj[0])
            name.append(obj[1])
        # 创建 symbol-name dict:
        for i in range(len(symbol)):
            self.dict_symbol_name[symbol[i]] = name[i]
        self.name = name
        self.symbol = symbol


"""
更新股票数据
爬取方法: 协程 
API: 搜狐
优点：JSON数据结果容易处理；获取速度快。 
缺点：每次只能获取100个节点的数据；API经常变动。  
方法1：http://q.stock.sohu.com/hisHq?code=[股票市场和代码]8&start=[开始日期]&end=[结束日期]&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp   
返回结果：JSON；时间段内的100个数据节点。
例如，http://q.stock.sohu.com/hisHq?code=cn_300228&start=20130930&end=20131231&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp，返回30022股票20130930到20131231时间段内的日线数据。    
"""

"""
res : 所有symbol的start到end的数据
remain: 丢包股票list
"""
# Step 2: Download history k-data from souhu finance url by co-routine
res = {}
remain = []
coroutine_num = 500
getData = GetData()


# 2.1 download data for 1 symbol
async def download_year(dict, i):  # dict {symbol : url}
    global remain
    url = list(dict.values())[0]
    symbol = list(dict.keys())[0]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = json.loads(await resp.text())
                print(f"下载数据中..stock symbol: {symbol}, stock number: {i}")
                # {} is not None
                if len(data) > 0:
                    # list of list: [[trade_date，open, close, high, low, vol]] (index:0，1，2，6，5，7)
                    res[symbol] = data[0]['hq']  # res[symbol] is all the hq(history quotes) of this symbol
                else:
                    print(f"{symbol}数据为空:{url}")
    except Exception as e:
        remain.append(dict)
        print(f"访问下载接口失败: {url}! Error:", e)

async def download_day_pre(dict, i):  # dict {symbol : url}
    global remain
    import urllib.request
    url = list(dict.values())[0]
    symbol = list(dict.keys())[0]
    try:
        resp = {}
        urlData = url
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(urlData, headers=hdr)
        print(f"下载数据中..stock symbol: {symbol}, stock number: {i}")
        webURL = urllib.request.urlopen(req)
        # “股票名称、今日开盘价、昨日收盘价、当前价格、今日最高价、今日最低价..成交量股（[8], /100 --> db）
        close = webURL.read().decode('latin-1').split('=')[1].split(',')[3]
        # 保留2位小数
        trade_date = datetime.now().date().strftime('%Y-%m-%d')
        webURL = urllib.request.urlopen(req)
        open = webURL.read().decode('latin-1').split('=')[1].split(',')[1]
        webURL = urllib.request.urlopen(req)
        high = webURL.read().decode('latin-1').split('=')[1].split(',')[4]
        webURL = urllib.request.urlopen(req)
        low = webURL.read().decode('latin-1').split('=')[1].split(',')[5]
        webURL = urllib.request.urlopen(req)
        # 2:30成交量等比例放大预测为3：00后的量，目前只对下午进行计算：
        TOTAL_SECONDS = float(4*60*60)
        cur_time = datetime.now()
        close_time = datetime(cur_time.year,cur_time.month,cur_time.day,15,0,0)
        base = 1
        if cur_time >=close_time:
            base = 1
        elif cur_time.hour>=13 and cur_time.hour<=15:
            diff = close_time - cur_time
            base = TOTAL_SECONDS/(TOTAL_SECONDS-diff.seconds)
        # 按照成交量平均增长速度进行放大：
        vol = float(webURL.read().decode('latin-1').split('=')[1].split(',')[8])*base/100
        # 组一个 hq 的结构:[[trade_date，open, close, high, low, vol]] (index:0，1，2，6，5，7)
        res[symbol] = [[trade_date,open,close,3,4,low,high,vol]]
    except Exception as e:
        remain.append(dict)
        print(f"访问下载接口失败: {url}! Error:", e)

# 2.2 start co-routine
async def download_all(sites, start):
    # for missing package: if 0 missing, then return.
    if not sites:
        return
    end = start + 500 if start + 500 <= len(sites) else len(sites)
    # tasks 没有限定并发数，会导致connect error
    tasks = [asyncio.create_task(download_year(sites[i], i)) for i in range(start, end)]
    await asyncio.gather(*tasks)
    return end

async def download_all_pre(sites, start):
    # for missing package: if 0 missing, then return.
    if not sites:
        return
    end = start + 500 if start + 500 <= len(sites) else len(sites)
    # tasks 没有限定并发数，会导致connect error
    tasks = [asyncio.create_task(download_day_pre(sites[i], i)) for i in range(start, end)]
    await asyncio.gather(*tasks)
    return end


# Main Function for step 2: Download data using co-routine
def coro_run():
    sites = []
    end_date = datetime.now().strftime('%Y%m%d')
    readCursor = ReadCursor()
    start_date = ('').join(readCursor.read().split('-'))
    # if start_date >= end_date:
    #     print("数据库已更新！")
    #     return -1
    for i in range(len(getData.symbol)):
        # for i in range(1) : #debug symbol:"000938.SZ"
        symbol = getData.symbol[i]
        dict = {}
        symbol1 = symbol.split('.')[0]
        url = f'http://q.stock.sohu.com/hisHq?code=cn_{symbol1}&start={start_date}&end={end_date}&stat=1&order=D&period=d'
        dict[symbol] = url
        sites.append(dict)
    start = 0
    while start < len(sites):
        start = asyncio.run(download_all(sites, start))

# Main Function for step 2: Download data using co-routine
# 在两点半之前，透过sina接口，预测收盘价格与成交量写入数据库:
def coro_run_pre():
    sites = []
    end_date = datetime.now().strftime('%Y%m%d')
    readCursor = ReadCursor()
    start_date = ('').join(readCursor.read().split('-'))
    # if start_date >= end_date:
    #     print("数据库已更新！")
    #     return -1
    for i in range(len(getData.symbol)):
        # for i in range(1) : #debug
        symbol = getData.symbol[i]
        req = symbol
        dict = {}
        if req[-1] == 'Z':
            req = 'sz' + req[0:6]
        elif req[-1] == 'S':
            req = 'sh' + req[0:6]
        #url = f'http://q.stock.sohu.com/hisHq?code=cn_{symbol1}&start={start_date}&end={end_date}&stat=1&order=D&period=d'
        url = f'http://hq.sinajs.cn/list={req}'
        dict[symbol] = url
        sites.append(dict)
    start = 0
    while start < len(sites):
        start = asyncio.run(download_all_pre(sites, start))


# 2.3: scraping again for missing package
def coro_remain():
    global remain
    sites = remain
    remain = []
    start = 0
    count = 0
    while start < len(sites):
        start = asyncio.run(download_all(sites, start))


# func： sql 异步读写， 将res中所有symbol对应的cursor_date -> now 的数据异步写入数据库中
# para： res 所有股票 cursor_date -> now 的数据
async def write_all(loop):
    pool = await create_pool(host='localhost', port=3306,
                             user='root', password='Zx1993624!',
                             db='stock_ai', loop=loop)
    count = 0
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # 执行sql语句的时候可以挂起
            iter_num = 1
            # 更新前，现将现有数据删除
            trade_date = datetime.now().date().strftime("%Y-%m-%d")
            delete_sql = f"delete from stock_info where trade_date='{trade_date}'"
            await cur.execute(delete_sql)
            for symbol in getData.symbol:
                if symbol in res:
                    # res_a: stock data of symbol from start_date to end_date
                    res_a = res[symbol]
                    # 把symbol cursor_date -> cur_date的数据更新：
                    for data in res_a:
                        sql = f"insert into stock_info(symbol, trade_date, name, open, close, high, low, vol) values('{symbol}', '{data[0]}', '{getData.dict_symbol_name[symbol]}', {data[1]}, {data[2]}, {data[6]}, {data[5]}, {data[7]});"
                        try:
                            await cur.execute(sql)  # execute co-routine use await.
                        except Exception as e:
                            count += 1
                            print(f"duplicate data:{count}, {e}")
                        # print("Number of rows affected by statement '{}': {}".format(
                        #     result.statement, result.rowcount))
                print(f"数据写入中..股票number:{iter_num}, symbol:{symbol}")
                iter_num += 1

            # 解决方案：缺少提交操作。Python操作数据库时，如果对数据表进行修改/删除/添加等控制操作，系统会将操作保存在内存，只有执行commit()，才会将操作提交到数据库。
            await conn.commit()
    pool.close()
    await pool.wait_closed()


"""
主函数: MAIN FUNCTION
    func1: 下载从 cursor_date - > cur_date的数据，并储存至res中
    func2: 将res更新至数据库中，并更新cursor_date
"""


# Step 3: * Main function
# update_time: 更新的次数，比如： update_time = 3, 第一次更新完之后，上次更新失败的remain[]再更新一次
def main():
    start_time = time.perf_counter()
    # 开启更新 of step 3 main function:
    res_up = coro_run()
    if res_up != -1:
        iteration = 0
        while remain:
            coro_remain()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(write_all(loop))
    print("数据库更新成功！")
    end_time = time.perf_counter()
    print(f"数据库更新时间: {end_time - start_time}s")

def main_pre():
    start_time = time.perf_counter()
    # 开启更新 of step 3 main function:
    res_up = coro_run_pre()
    if res_up != -1:
        iteration = 0
        while remain:
            coro_remain()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(write_all(loop))
    print("数据库更新成功！")
    end_time = time.perf_counter()
    print(f"数据库更新时间: {end_time - start_time}s")

if __name__=='__main__':
    #main_pre()
    main()
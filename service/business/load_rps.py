# coding:utf-8
"""
Update database on 1800 seconds intervals.
作废的定时任务，但是主进程进行引用
因为，两个进程中，创建的类不可共享：进程间的通信问题
"""
from common.global_var import GlobalVar
import urllib.request
from apscheduler.schedulers.blocking import BlockingScheduler
from web.controllers.compute.common.ReadCursor import ReadCursor
from web.controllers.compute.common.WriteDb import WriteDb
from web.controllers.compute.common.ReadDb import ReadDb
import web.controllers.compute.Predict as Predict
import web.controllers.compute.GetData as getData
import logging

global_dict = GlobalVar.global_dict

class LoadRps(object):
    """
    rds 表示特定周期内股票涨幅在stock list中的排名
        需要明确是历史最大涨幅，还是当前最大涨幅 or 相对特定收盘价的涨幅
    """
    def load_rps(self):

        SIGN_CHUANG = '3'
        SIGN_SHANG = '6'
        SIGN_SHEN = '0'

        for sign in [SIGN_CHUANG, SIGN_SHANG, SIGN_SHEN]:
            # symbols = GetData().symbol
            symbols = GlobalVar.symbols
            result_day = {}
            result_week = {}
            result_month = {}
            print(f"计算rps for sign {sign}...")
            for symbol in symbols:
                if symbol[0] == sign:
                    # 可以把每只股票的computeIndex都加载到内存中（5-10MB）
                    # computeIndex = ComputeIndex(symbol, 0, None)
                    close = GlobalVar.close_21_dict[symbol]
                    # get price for symbol
                    req = symbol
                    if req[-1] == 'Z':
                        req = 'sz' + req[0:6]
                    elif req[-1] == 'S':
                        req = 'sh' + req[0:6]
                    urlData = f'http://hq.sinajs.cn/list={req}'
                    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
                    req = urllib.request.Request(urlData, headers=hdr)
                    webURL = urllib.request.urlopen(req)
                    # “股票名称、今日开盘价、昨日收盘价、当前价格、今日最高价、今日最低价..
                    price = webURL.read().decode('latin-1').split('=')[1].split(',')[3]
                    # 保留2位小数
                    price = float(price[:-1])

                    # 如果价格没有变化，采用昨天的数据 bug: close[1]=0, reason:个别symbol最近采集到的收盘价为0，可能是退市
                    if 0 in close[:22]:
                        continue
                    rps_close_day = (price - close[1])/close[1]  # cur_price - 昨日收盘价

                    rps_close_week = (price - close[4])/close[4]

                    rps_close_month = (price - close[21])/close[21]


                    result_day[symbol] = rps_close_day
                    result_week[symbol] = rps_close_week
                    result_month[symbol] = rps_close_month

            # 降序排列，涨幅高的，rank 低，排名靠前
            sort_list_day = sorted(result_day.items(),key=lambda item:-item[1])
            sort_list_week = sorted(result_week.items(), key=lambda item: -item[1])
            sort_list_month = sorted(result_month.items(), key=lambda item: -item[1])

            global_dict[f'result_day_{sign}'] = result_day
            global_dict[f'result_week_{sign}'] = result_week
            global_dict[f'result_month_{sign}'] = result_month

            global_dict[f'rds_day_list_{sign}'] =  sort_list_day
            global_dict[f'rds_week_list_{sign}'] = sort_list_week
            global_dict[f'rds_month_list_{sign}'] = sort_list_month


    def main(self):
        print('开始定时更新任务，每天18点更新数据库和19点更新选股结果.')
        scheduler = BlockingScheduler()
        self.load_rps()
        scheduler.add_job(self.load_rps, 'cron', hour=18, minute=0)
        try:
            scheduler.start()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    update = LoadRps()
    update.load_rps()
    update.main()

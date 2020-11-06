# coding:utf-8
from common.global_var import GlobalVar
import urllib.request

class GetRps(object):
    """
    rds 表示特定周期内股票涨幅在stock list中的排名
        需要明确是历史最大涨幅，还是当前最大涨幅 or 相对特定收盘价的涨幅
    """
    def get_price(self, symbol):
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
        return price

    def get_rps(self, stock):
        # 如果未开市，则返回内存储存的value:
        stock_price = self.get_price(stock)
        stock_close = GlobalVar.close_21_dict[stock]
        global_dict = GlobalVar.global_dict
        sign = stock[0]

        if stock_price == stock_close[0]:
            rank_day = global_dict[f'rds_day_list_{sign}'].index((stock,global_dict[f'result_day_{sign}'][stock]))
            rank_week = global_dict[f'rds_week_list_{sign}'].index((stock,global_dict[f'result_week_{sign}'][stock]))
            rank_month = global_dict[f'rds_month_list_{sign}'].index((stock,global_dict[f'result_month_{sign}'][stock]))
            rps_day = {"rps":round((1 - rank_day / len(global_dict[f'rds_day_list_{sign}'])) * 100, 2),"rank":rank_day,"num":len(global_dict[f'rds_day_list_{sign}'])}
            rps_week = {"rps": round((1 - rank_week / len(global_dict[f'rds_week_list_{sign}'])) * 100, 2), "rank": rank_week,
                       "num": len(global_dict[f'rds_week_list_{sign}'])}
            rps_month = {"rps": round((1 - rank_month / len(global_dict[f'rds_month_list_{sign}'])) * 100, 2), "rank": rank_month,
                       "num": len(global_dict[f'rds_month_list_{sign}'])}
            return rps_day, rps_week, rps_month
        # symbols = GetData().symbol
        symbols = GlobalVar.symbols
        result_day = {}
        result_week = {}
        result_month = {}
        sign = stock[0]
        for symbol in symbols:
            if symbol[0] == sign:
                # 可以把每只股票的computeIndex都加载到内存中（5-10MB）
                # computeIndex = ComputeIndex(symbol, 0, None)
                close = GlobalVar.close_21_dict[symbol]
                # get price for symbol
                price = self.get_rps(symbol)
                rps_close_day = (price - close[0])/close[0]  # cur_price - 昨日收盘价
                rps_close_week = (price - close[4])/close[4]
                rps_close_month = (price - close[21])/close[21]

                result_day[symbol] = rps_close_day
                result_week[symbol] = rps_close_week
                result_month[symbol] = rps_close_month

        sort_list_day = sorted(result_day.items(), key=lambda item: item[1])
        sort_list_week = sorted(result_week.items(), key=lambda item: item[1])
        sort_list_month = sorted(result_month.items(), key=lambda item: item[1])

        global_dict[f'result_day_{sign}'] = result_day
        global_dict[f'result_week_{sign}'] = result_week
        global_dict[f'result_month_{sign}'] = result_month

        global_dict[f'rds_day_list_{sign}'] = sort_list_day
        global_dict[f'rds_week_list_{sign}'] = sort_list_week
        global_dict[f'rds_month_list_{sign}'] = sort_list_month

        rank_day = global_dict[f'rds_day_list_{sign}'].index((stock, global_dict[f'result_day_{sign}'][stock]))
        rank_week = global_dict[f'rds_week_list_{sign}'].index((stock, global_dict[f'result_week_{sign}'][stock]))
        rank_month = global_dict[f'rds_month_list_{sign}'].index((stock, global_dict[f'result_month_{sign}'][stock]))

        rps_day = {"rps": round((1 - rank_day / len(global_dict[f'rds_day_list_{sign}'])) * 100, 2), "rank": rank_day,
                   "num": len(global_dict[f'rds_day_list_{sign}'])}
        rps_week = {"rps": round((1 - rank_week / len(global_dict[f'rds_week_list_{sign}'])) * 100, 2), "rank": rank_week,
                    "num": len(global_dict[f'rds_week_list_{sign}'])}
        rps_month = {"rps": round((1 - rank_month / len(global_dict[f'rds_month_list_{sign}'])) * 100, 2),
                     "rank": rank_month,
                     "num": len(global_dict[f'rds_month_list_{sign}'])}

        return rps_day, rps_week, rps_month




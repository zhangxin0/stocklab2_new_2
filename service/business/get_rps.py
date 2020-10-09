# coding:utf-8
from common.global_var import GlobalVar
import urllib.request

class GetRps(object):
    """
    rds 表示特定周期内股票涨幅在stock list中的排名
        需要明确是历史最大涨幅，还是当前最大涨幅 or 相对特定收盘价的涨幅
    """
    def get_rps(self, stock,time):
        # symbols = GetData().symbol
        symbols = GlobalVar.symbols
        result = {}
        sign = stock[0]
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
                if time == 'day':
                    rps_close = (price - close[0])/close[0]  # cur_price - 昨日收盘价

                elif time =='week':
                    rps_close = (price - close[4])/close[4]

                elif time == 'month':
                    rps_close = (price - close[21])/close[21]


                result[symbol] = rps_close

        sort_list = sorted(result.items(),key=lambda item:item[1])
        rank = sort_list.index((stock,result[stock]))
        return round((1 - rank/len(sort_list))*100,2),rank,len(sort_list)




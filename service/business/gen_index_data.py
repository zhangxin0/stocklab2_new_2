# coding: utf-8
import logging
from flask import app,g,request,jsonify
from common.models.UserInfo import UserInfo
from common.models.TransactionHistory import TransactionHistory
from web.controllers.compute.common.ReadCursor import ReadCursor
from common.models.NhResult import NhResult
from web.controllers.compute.common.ComputeIndex import ComputeIndex
from common.models.StockInfo import StockInfo
from common.models.GoldCrossResult import GoldCrossResult
from common.models.SecondUpResult import SecondUpResult


class GenIndexDataService(object):

    @classmethod
    def get_resp_data(cls, request_method='GET'):
        try:
            hold_list = UserInfo.query.filter_by(user_id=g.current_user.uid).order_by(UserInfo.buy_date).all()
            if hasattr(g,'uid'):
                symbol = g.uid['symbol']
            else:
                # 如果symbol为空，从持股列表中读取，再为空，设定为default
                if not hold_list:
                    symbol = '000938.SZ'
                else:
                    symbol = hold_list[-1].hold_stock
            # 将空的global-symbol赋值，这样get_price就可以获取到当下symbol的值:
            g.uid = {'symbol':symbol}
            readCursor = ReadCursor()
            db_date = ('').join(readCursor.read().split('-'))
            page = 1
            limit = 10
            history_list = TransactionHistory.query.filter_by(uid=g.current_user.uid).order_by(TransactionHistory.date.desc()).offset((page-1)*limit).limit(limit).all()
            nh_result_list = NhResult.query.filter_by(date=db_date).all() or []
            gold_cross_result_list = GoldCrossResult.query.filter_by(date=db_date).all() or []
            second_up_result_list = SecondUpResult.query.filter_by(date=db_date).all() or []

            data = StockInfo.query.filter_by(symbol=symbol).order_by(StockInfo.trade_date).all()
            data0 = []
            data0 = []
            for element in data:
                # 数据意义：trade_date,开盘(open)，收盘(close)，最低(lowest)，最高(highest)
                values = [element.trade_date, element.open, element.close, element.low, element.high, element.vol]
                data0.append(values)
            # 计算股票持有时间，并添加到user_info.hold_time:
            for item in hold_list:
                stock_info = ComputeIndex(item.hold_stock, 0)
                # 买入当天为0
                try:
                    buy_date = item.buy_date[0:4] + '-' + item.buy_date[4:6] + '-' + item.buy_date[6:]
                    hold_time = stock_info.trade_date.index(buy_date) - 1
                    item.hold_time = hold_time
                except Exception as e:
                    logging.info(e)
                    hold_time = 0
            # 生成selector的html:
            html_nh = ''
            html_gold_cross = ''
            html_second_up = ''
            for i in range(0, len(nh_result_list)):
                if len(nh_result_list[i].name) == 4:
                    html_nh += "<li id='nh_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + \
                               nh_result_list[
                                   i].symbol + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + nh_result_list[
                                   i].name + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + nh_result_list[i].date + "</span></li>"
                elif len(nh_result_list[i].name) == 3:
                    html_nh += "<li id='nh_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + \
                               nh_result_list[
                                   i].symbol + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + nh_result_list[
                                   i].name + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + nh_result_list[
                                   i].date + "</span></li>"

            for i in range(0, len(gold_cross_result_list)):
                if len(gold_cross_result_list[i].name) == 4:
                    html_gold_cross += "<li id='gold_cross_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + \
                                       gold_cross_result_list[
                                           i].symbol + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + gold_cross_result_list[
                                           i].name + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + gold_cross_result_list[
                                           i].date + "</span></li>"
                elif len(gold_cross_result_list[i].name) == 3:
                    html_gold_cross += "<li id='gold_cross_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + \
                                       gold_cross_result_list[
                                           i].symbol + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + gold_cross_result_list[
                                           i].name + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + \
                                       gold_cross_result_list[
                                           i].date + "</span></li>"

            for i in range(0, len(second_up_result_list)):
                if len(second_up_result_list[i].name) == 4:
                    html_second_up += "<li id='second_up_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + \
                                      second_up_result_list[
                                          i].symbol + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + second_up_result_list[
                                          i].name + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + second_up_result_list[
                                          i].date + "</span></li>"
                elif len(second_up_result_list[i].name) == 3:
                    html_second_up += "<li id='second_up_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + \
                                      second_up_result_list[
                                          i].symbol + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + second_up_result_list[
                                          i].name + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + \
                                      second_up_result_list[
                                          i].date + "</span></li>"

            resp_data = {}
            resp_data['html_nh'] = html_nh if html_nh else "<li id='nh_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>今天没有符合条件的股票哦～～</span></li>"
            resp_data['html_gold_cross'] = html_gold_cross if html_gold_cross else "<li id='nh_select_result'><span>今天没有符合条件的股票哦～～</span></li>"
            resp_data['html_second_up'] = html_second_up if html_second_up else "<li id='nh_select_result'><span>今天没有符合条件的股票哦～～</span></li>"
            if request_method == 'POST':
                resp_data['code'] = 200
                return jsonify(resp_data)
            resp_data['data0'] = data0
            resp_data['name'] = data[0].name
            resp_data['symbol'] = data[0].symbol
            resp_data['hold_list'] = hold_list
            resp_data['nh_result_list'] = nh_result_list
            resp_data['history_list'] = history_list
            find_obj = UserInfo.query.filter(UserInfo.user_id == g.current_user.uid, UserInfo.hold_stock == symbol).first()
            user_info = UserInfo.query.filter_by(user_id=g.current_user.uid).first()
            sale_point = user_info.sale_point or 4 if user_info else 4
            if find_obj:
                resp_data['buy_price'] = round(find_obj.buy_price, 2)
                resp_data['goal_price'] = round(find_obj.buy_price * (100+sale_point)/100, 2)
        except Exception as e:
            app.logger.error(e)
        return resp_data


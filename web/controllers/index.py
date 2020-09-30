# -*- coding: utf-8 -*-
import logging
from flask import Blueprint, render_template, g, request, make_response, jsonify
from common.libs.Helper import ops_render, iPagination
from flask import Blueprint
from common.models.StockInfo import StockInfo
from common.models.User import User
from common.models.NhResult import NhResult
from common.models.GoldCrossResult import GoldCrossResult
from common.models.SecondUpResult import SecondUpResult
from common.models.StockList import StockList
from common.models.TransactionHistory import TransactionHistory
from web.controllers.compute.common.ReadCursor import ReadCursor
import datetime
import web.controllers.compute.GetData as getData
import web.controllers.compute.Predict as Predict
from application import app, db, redis_client
from common.models.UserInfo import UserInfo
from common.models.Notify import Notify
from web.controllers.compute.common.ComputeIndex import ComputeIndex
import urllib.request
import web.controllers.compute.common.route_methods as route_methods
from web.controllers.jobs.update import Update
from web.controllers.notification.notify import Message
from service.business.view_utils import ViewUtils
from web.base.view import restful

route_index = Blueprint('index_page', __name__)
global_dict = {'uid': {'symbol': '', 'hold_stock': []}}


@route_index.route("/", methods=["GET", "POST"])
@restful
def index():
    hold_list = UserInfo.query.filter_by(user_id=g.current_user.uid).order_by(UserInfo.buy_date).all()
    if g.current_user.uid in global_dict:
        symbol = global_dict[g.current_user.uid]['symbol']
    else:
        global_dict[g.current_user.uid] = {}
        # 如果symbol为空，从持股列表中读取，再为空，设定为default
        if not hold_list:
            symbol = '000938.SZ'
        else:
            symbol = hold_list[-1].hold_stock
    # 将空的global-symbol赋值，这样get_price就可以获取到当下symbol的值:
    global_dict[g.current_user.uid]['symbol'] = symbol
    readCursor = ReadCursor()
    db_date = ('').join(readCursor.read().split('-'))
    history_list = TransactionHistory.query.filter_by(uid=g.current_user.uid).order_by(TransactionHistory.date).all()
    nh_result_list = []
    gold_cross_result_list = []
    second_up_result_list = []
    try:
        nh_result_list = NhResult.query.filter_by(date=db_date).all()
        gold_cross_result_list = GoldCrossResult.query.filter_by(date=db_date).all()
        second_up_result_list = SecondUpResult.query.filter_by(date=db_date).all()
    except Exception as e:
        app.logger.error(e)
        db.session.rollback()
    data = StockInfo.query.filter_by(symbol=symbol).order_by(StockInfo.trade_date).all()
    data0 = []
    # 分页
    # req = request.values  # in url path after ?
    # page = int(req['p']) if ('p' in req and req['p']) else 1
    # page_params = {
    #     'total':history_list.count(),
    #     'page_size': app.config['PAGE_SIZE'],
    #     'page': page,
    #     'display': app.config['PAGE_DISPLAY'],
    #     'url': request.full_path.replace("&p={}".format(page), "")
    # }
    # pages = iPagination(page_params)
    # offset = (page - 1) * (app.config['PAGE_SIZE'])
    # limit = app.config['PAGE_SIZE'] * page
    # history_list = history_list.all()[offset:limit]
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
            app.logger.error(e)
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
    if request.method == 'POST':
        resp_data['code'] = 200
        return jsonify(resp_data)
    resp_data['data0'] = data0
    resp_data['name'] = data[0].name
    resp_data['symbol'] = data[0].symbol
    resp_data['hold_list'] = hold_list
    resp_data['nh_result_list'] = nh_result_list
    resp_data['history_list'] = history_list
    # resp_data['pages'] = pages
    find_obj = UserInfo.query.filter(UserInfo.user_id == g.current_user.uid, UserInfo.hold_stock == symbol).first()
    user_info = UserInfo.query.filter_by(user_id=g.current_user.uid).first()
    sale_point = user_info.sale_point
    if find_obj:
        resp_data['buy_price'] = round(find_obj.buy_price, 2)
        # sale_point = calculate_goal_price(global_dict[g.current_user.uid]['symbol'])+1
        resp_data['goal_price'] = round(find_obj.buy_price * (100+sale_point)/100, 2)
    return ops_render("index/index.html", resp_data)


@route_index.route('/update')
@restful
def update():
    getData.main()
    return '数据更新完成'


# 预测获取 股票symbol 交易日期 买入价格（当日收盘）
"""
粘合选股预测

Parameters：
    result_date : 最新日期 -- 选股结果
    db_date     : 最新日期 -- 数据库股票数据
    data        : 返回的选股结果别表 {dates:日期列表 symbols:股票代码列表 prices:价格列表 names:名称列表}
    
    
Return：
    resp        : 选股结果html -- json 序列化成类的格式， 前端通过resp.html调用
    
Raises：
    写入数据库异常
"""
@route_index.route('/nh_predict')
@restful
def nh_predict():
    data = {}
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    get_res = NhResult.query.order_by(NhResult.date.desc()).first()
    if not get_res:
        result_date = '19930624'
    else:
        result_date = NhResult.query.order_by(NhResult.date.desc()).first().date
        result = NhResult.query.filter_by(date=result_date).all()
    readCursor = ReadCursor()
    db_date = ('').join(readCursor.read().split('-'))
    dates = []
    symbols = []
    prices = []
    names = []
    # 选股结果最新 -- 不需要更新：
    if result_date and result_date >= db_date:
        count = 0
        resp['code'] = -1
        for item in result:
            count += 1
            if count > 7:
                break
            # 如果选股结果为空 -- 提示今天没有选股 date:20200719 symbol: prices: names:
            # 空不一定是None
            if not item.symbol:
                html = "<li id='nh_select_result'><span>今天没有符合条件的股票哦~~</span></li>"
                resp['html'] = html
                return jsonify(resp)
                # break
            symbols.append(item.symbol)
            dates.append(item.date)
            prices.append(item.price)
            names.append(item.name)
    # 否则 -- 运行选股算法进行更新：
    else:
        # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
        res = Predict.predict(0, 'nh')
        count = 0
        for item in res:
            count += 1
            # 设定发送上限为7个选出股：
            if count > 7:
                break
            dates.append(('').join(item[1].trade_date[0].split('-')))
            symbols.append(item[0])
            # 买入价格按照单日收盘价计算
            prices.append(item[1].close[0])
            # 添加name
            name = StockInfo.query.filter_by(symbol=item[0]).first().name
            names.append(name)
        # 添加至选股数据库：
        for i in range(len(symbols)):
            result = NhResult()
            result.date = dates[i]
            result.symbol = symbols[i]
            result.price = prices[i]
            result.name = names[i]
            try:
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                app.logger.info(e)
        # 如果选股结果为空 -- 数据库中添加选股结果为空
        if not res:
            result = NhResult()
            result.date = db_date # 记录选股日期为最新日期
            # .. symbol price name 默认为空
            try:
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                app.logger.info(e)
    data['symbol'] = symbols
    data['date'] = dates
    data['price'] = prices
    data['name'] = names
    resp['data'] = data
    html = ''  # <li id="nh_select_result"><span><i class="fa fa-plus plus-list" id="plus"></i>{{item.symbol}}</span></li>
    for i in range(0, len(symbols)):
        if len(names[i]) == 4:
            html += "<li id='nh_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + symbols[
                i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + names[i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dates[
                        i] + "</span></li>"
        elif len(names[i]) == 3:
            html += "<li id='nh_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + symbols[
                i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + names[
                        i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dates[i] + "</span></li>"
    if len(symbols) == 0:
        html += "<li id='nh_select_result'><span>今天没有符合条件的股票哦~~</span></li>"
    resp['html'] = html
    return jsonify(resp)


"""
金叉选股预测

Parameters：
    result_date : 最新日期 -- 选股结果
    db_date     : 最新日期 -- 数据库股票数据
    data        : 返回的选股结果别表 {dates:日期列表 symbols:股票代码列表 prices:价格列表 names:名称列表}


Return：
    resp        : 选股结果html -- json 序列化成类的格式， 前端通过resp.html调用

Raises：
    写入数据库异常
"""
@route_index.route('/gold_cross_predict')
@restful
def gold_cross_predict():
    data = {}
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    get_res = GoldCrossResult.query.order_by(GoldCrossResult.date.desc()).first()
    if not get_res:
        result_date = '19930624'
    else:
        result_date = GoldCrossResult.query.order_by(GoldCrossResult.date.desc()).first().date
        result = GoldCrossResult.query.filter_by(date=result_date).all()
    # 更改date = 数据库里最新的日期，如果数据库更新，要执行选股操作
    readCursor = ReadCursor()
    db_date = ('').join(readCursor.read().split('-'))
    dates = []
    symbols = []
    prices = []
    names = []
    # 选股结果最新 -- 不需要更新：
    if result_date and result_date >= db_date:
        count = 0
        resp['code'] = -1
        # 如果选股结果为空 -- 提示今天没有选股 date:20200719 symbol: prices: names:
        # 空不一定是None -- ''
        for item in result:
            count += 1
            if count > 7:
                break
            if not item.symbol:
                html = "<li id='nh_select_result'><span>今天没有符合条件的股票哦~~</span></li>"
                resp['html'] = html
                return jsonify(resp)
            symbols.append(item.symbol)
            dates.append(item.date)
            prices.append(item.price)
            names.append(item.name)
    # 否则 -- 运行选股算法进行更新：
    else:
        # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
        res = Predict.predict(0, 'gold_cross')
        count = 0
        for item in res:
            count += 1
            # 设定发送上限为7个选出股：
            if count > 7:
                break
            dates.append(('').join(item[1].trade_date[0].split('-')))
            symbols.append(item[0])
            # 买入价格按照单日收盘价计算
            prices.append(item[1].close[0])
            # 添加name
            name = StockInfo.query.filter_by(symbol=item[0]).first().name
            names.append(name)
        # 添加至选股数据库：
        for i in range(len(symbols)):
            result = GoldCrossResult()
            result.date = dates[i]
            result.symbol = symbols[i]
            result.price = prices[i]
            result.name = names[i]
            try:
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                app.logger.info(e)
        # 如果选股结果为空 -- 数据库中添加选股结果为空
        if not res:
            result = GoldCrossResult()
            result.date = db_date  # 记录选股日期为最新日期
            # .. symbol price name 默认为空
            try:
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                app.logger.info(e)
    data['symbol'] = symbols
    data['date'] = dates
    data['price'] = prices
    data['name'] = names
    resp['data'] = data
    html = ''  # <li id="nh_select_result"><span><i class="fa fa-plus plus-list" id="plus"></i>{{item.symbol}}</span></li>
    for i in range(0, len(symbols)):
        if len(names[i]) == 4:
            html += "<li id='gold_cross_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + symbols[
                i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + names[i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dates[
                        i] + "</span></li>"
        elif len(names[i]) == 3:
            html += "<li id='gold_cross_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + symbols[
                i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + names[
                        i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dates[i] + "</span></li>"
    if len(symbols) == 0:
        html += "<li id='gold_cross_select_result'><span>今天没有符合条件的股票哦~~</span></li>"
    resp['html'] = html
    return jsonify(resp)


@route_index.route('/second_up_predict')
@restful
def second_up_predict():
    data = {}
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    get_res = SecondUpResult.query.order_by(SecondUpResult.date.desc()).first()
    if not get_res:
        result_date = '19930624'
    else:
        result_date = SecondUpResult.query.order_by(SecondUpResult.date.desc()).first().date
        result = SecondUpResult.query.filter_by(date=result_date).all()
    # 更改date = 数据库里最新的日期，如果数据库更新，要执行选股操作
    readCursor = ReadCursor()
    db_date = ('').join(readCursor.read().split('-'))
    dates = []
    symbols = []
    prices = []
    names = []
    # 选股结果最新 -- 不需要更新：
    if result_date and result_date >= db_date:
        count = 0
        resp['code'] = -1
        for item in result:
            count += 1
            if count > 7:
                break
            # 如果选股结果为空 -- 提示今天没有选股 date:20200719 symbol: prices: names:
            # 空不一定是None
            if not item.symbol:
                html = "<li id='nh_select_result'><span>今天没有符合条件的股票哦~~</span></li>"
                resp['html'] = html
                return jsonify(resp)
            symbols.append(item.symbol)
            dates.append(item.date)
            prices.append(item.price)
            names.append(item.name)
    # 否则 -- 运行选股算法进行更新：
    else:
        # res 格式 [(symbol, computeIndex, cur),(symbol,.,.),...,...]
        res = Predict.predict(0, 'second_up')
        count = 0
        for item in res:
            count += 1
            # 设定发送上限为7个选出股：
            if count > 7:
                break
            dates.append(('').join(item[1].trade_date[0].split('-')))
            symbols.append(item[0])
            # 买入价格按照单日收盘价计算
            prices.append(item[1].close[0])
            # 添加name
            name = StockInfo.query.filter_by(symbol=item[0]).first().name
            names.append(name)
        # 添加至选股数据库：
        for i in range(len(symbols)):
            result = SecondUpResult()
            result.date = dates[i]
            result.symbol = symbols[i]
            result.price = prices[i]
            result.name = names[i]
            try:
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                app.logger.info(e)
        # 如果选股结果为空 -- 数据库中添加选股结果为空
        if not res:
            result = SecondUpResult()
            result.date = db_date  # 记录选股日期为最新日期
            # .. symbol price name 默认为空
            try:
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                app.logger.info(e)
    data['symbol'] = symbols
    data['date'] = dates
    data['price'] = prices
    data['name'] = names
    resp['data'] = data
    html = ''  # <li id="nh_select_result"><span><i class="fa fa-plus plus-list" id="plus"></i>{{item.symbol}}</span></li>
    for i in range(0, len(symbols)):
        if len(names[i]) == 4:
            html += "<li id='second_up_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + symbols[
                i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + names[i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dates[
                        i] + "</span></li>"
        elif len(names[i]) == 3:
            html += "<li id='second_up_select_result'><span><i class='fa fa-plus plus-list' id='plus'></i>" + symbols[
                i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + names[
                        i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + dates[i] + "</span></li>"
    if len(symbols) == 0:
        html += "<li id='second_up_select_result'><span>今天没有符合条件的股票哦~~</span></li>"
    resp['html'] = html
    return jsonify(resp)


# 为搜索提供数据接口
@route_index.route('/search', methods=['GET', 'POST'])
@restful
def search():
    resp = {'code': 200, 'msg': 'success', 'data0': {}}
    req = request.values
    symbol = req['symbol']
    # 添加后缀:
    symbol = symbol[0:6]
    if symbol[0] == '6':
        symbol += '.SS'
    else:
        symbol += '.SZ'
    symbols = []
    data0 = []
    stock_list = StockList.query.all()
    for element in stock_list:
        symbols.append(element.symbol)
    if symbol not in symbols:
        resp['code'] = -1
    else:
        find_obj = UserInfo.query.filter(UserInfo.user_id == g.current_user.uid, UserInfo.hold_stock == symbol).first()
        if find_obj:
            resp['buy_price'] = find_obj.buy_price
        global_dict[g.current_user.uid]['symbol'] = symbol
        # 制作数据接口:
        data = StockInfo.query.filter_by(symbol=symbol).order_by(StockInfo.trade_date).all()
        for element in data:
            # 数据意义：trade_date,开盘(open)，收盘(close)，最低(lowest)，最高(highest)
            values = [element.trade_date, element.open, element.close, element.low, element.high, element.vol]
            data0.append(values)
        resp['data0'] = data0
        resp['name'] = data[0].name
        resp['symbol'] = data[0].symbol
    return jsonify(resp)


@route_index.route('/add_list', methods=['GET', 'POST'])
@restful
def add_list():
    req = request.values
    symbol = req['symbol']
    resp = {'code': 200, 'msg': 'success', 'data': ''}
    # id, hold_stock, user_id, buy_price,sold_price,strategy,buy_date,sale_date
    info = UserInfo()
    info.hold_stock = symbol
    info.user_id = g.current_user.uid
    ## 因为，默认选出的股票为当前最新数据库日期下：//判断结果是否为空
    # 该股最新收盘价(数据库不能为空）
    result_date = NhResult.query.order_by(NhResult.date.desc()).first().date
    result = NhResult.query.filter(NhResult.date == result_date, NhResult.symbol == symbol).first()
    if not result:
        result_date = GoldCrossResult.query.order_by(GoldCrossResult.date.desc()).first().date
        result = GoldCrossResult.query.filter(GoldCrossResult.date == result_date,
                                              GoldCrossResult.symbol == symbol).first()
        if not result:
            result_date = SecondUpResult.query.order_by(SecondUpResult.date.desc()).first().date
            result = SecondUpResult.query.filter(SecondUpResult.date == result_date,
                                                  SecondUpResult.symbol == symbol).first()
    info.buy_price = result.price
    info.buy_date = result.date
    info.name = result.name
    try:
        db.session.add(info)
        db.session.commit()
    except Exception as e:
        app.logger.info(e)
    html = ViewUtils.refresh_stocklist()
    resp['data'] = html
    return jsonify(resp)


@route_index.route('/user_defined_add_list', methods=['GET', 'POST'])
@restful
def user_defined_add_list():
    req = request.values
    symbol = req['symbol']
    # 添加后缀:
    symbol = symbol[0:6]
    if symbol[0] == '6':
        symbol += '.SS'
    else:
        symbol += '.SZ'
    date = req['date']
    price = float(req['price'])
    resp = {'code': 200, 'msg': 'success', 'data': ''}
    # 如果输入的symbol错误，则返回-1状态码：
    symbols = []
    stock_list = StockList.query.all()
    for element in stock_list:
        symbols.append(element.symbol)
    if symbol not in symbols:
        resp['code'] = -1
    else:
        # id, hold_stock, user_id, buy_price,sold_price,strategy,buy_date,sale_date
        name = StockInfo.query.filter_by(symbol=symbol).first().name
        info = UserInfo()
        info.hold_stock = symbol
        info.user_id = g.current_user.uid
        info.buy_price = price
        info.buy_date = date
        info.name = name
        try:
            db.session.add(info)
            db.session.commit()
        except Exception as e:
            app.logger.info(e)
    html = ViewUtils.refresh_stocklist()
    resp['data'] = html
    return jsonify(resp)

@route_index.route('/user_defined_set_sale_point', methods=['GET', 'POST'])
@restful
def user_defined_set_sale_point():
    req = request.values
    resp = {'code': 200, 'msg': 'success', 'data': ''}
    try:
        sale_point = float(req['sale_point'])
    except Exception as e:
        app.logger.info(e)
        resp['code'] = -1
        return jsonify(resp)
    user_infos = UserInfo.query.filter_by(user_id=g.current_user.uid).all()
    for user_info in user_infos:
        user_info.sale_point = sale_point
    db.session.commit()
    return jsonify(resp)




@route_index.route('/delete_list', methods=['GET', 'POST'])
@restful
def delete_list():
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    req = request.values
    symbol = req['symbol']
    # id, hold_stock, user_id, buy_price,sold_price,strategy,buy_date,sale_date
    info = UserInfo.query.filter_by(user_id=g.current_user.uid, hold_stock=symbol).first()
    db.session.delete(info)
    db.session.commit()
    html = ViewUtils.refresh_stocklist()
    resp['data'] = html
    return jsonify(resp)


@route_index.route('/get_price', methods=['GET', 'POST'])
@restful
def get_price():
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    req = ''
    if g.current_user.uid in global_dict:
        req = global_dict[g.current_user.uid]['symbol']
    else:
        req = '000938.SZ'
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
    price = price[:-1]
    resp['data'] = price
    return resp


@route_index.route('/get_strategy', methods=['GET', 'POST'])
@restful
def get_strategy():
    # 对于所有的持股列表，检测是否到达卖出点
    hold_list = UserInfo.query.filter_by(user_id=g.current_user.uid).all()
    phone = User.query.filter_by(uid=g.current_user.uid).first().mobile
    # 盈利位，止损位
    prevent_lose = 10
    resp = {'code': -1, 'msg': 'success', 'data': '', 'phone': '', 'symbol': '', 'operation': ''}
    resp['phone'] = phone
    for element in hold_list:
        # 用来判断是否需要写入历史数据库
        flag = True
        # 每一只股充值sale_point，否则延续上一次修改的sale_point
        user_info = UserInfo.query.filter_by(user_id=g.current_user.uid).first()
        sale_point = user_info.sale_point
        symbol = element.hold_stock
        if symbol[-1] == 'Z':
            symbol_url = 'sz' + symbol[0:6]
        elif symbol[-1] == 'S':
            symbol_url = 'sh' + symbol[0:6]
        buy_price = element.buy_price
        buy_date = element.buy_date
        buy_date = buy_date[0:4] + '-' + buy_date[4:6] + '-' + buy_date[6:]
        # 获取买入价格
        urlData = f'http://hq.sinajs.cn/list={symbol_url}'
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(urlData, headers=hdr)
        webURL = urllib.request.urlopen(req)
        # “股票名称、今日开盘价、昨日收盘价、当前价格、今日最高价、今日最低价..
        cur_price = float(webURL.read().decode('latin-1').split('=')[1].split(',')[3])
        if cur_price == 0:
            # cur_price 读取为0时，置为买入价，表示无策略
            cur_price = buy_price - 0.0001
        # 持有时间: 读取trade_date, 持有天数为: Index - 1,eg: 当天选出未买入 hold_time = -1, 买入当天: 0
        # 强制卖出位置
        stock_info = ComputeIndex(symbol, 0)
        try:
            hold_time = stock_info.trade_date.index(buy_date) - 1
        except Exception as e:
            app.logger.error(e)
            hold_time = 0
        # 有误：因为实际情况计算的是第二天的卖点，所以整体向前1天
        # 选股历史：记录选出的股票并写入transaction_history table
        # if hold_time >= 5 and hold_time <= 8:
        #     sale_point = (40 - 5 * (hold_time)) / 3
        if hold_time > 12:
            sale_point = -1
        # 如果已买入，写入选股历史数据库：
        transaction_history = TransactionHistory()
        transaction_history.uid = g.current_user.uid
        transaction_history.hold_time = hold_time
        transaction_history.date = buy_date
        transaction_history.symbol = symbol
        transaction_history.name = StockInfo.query.filter_by(symbol=symbol).first().name
        # 止盈位
        if (cur_price - buy_price) / buy_price * 100 >= sale_point:
            resp['data'] += f"恭喜您，{symbol}到达目标价位，可以盈利卖出！ <br />"
            resp['symbol'] += symbol + ','
            resp['operation'] += 'YingLi,'
            resp['code'] = 200
            transaction_history.status = '盈利'
        # 强制卖出点
        elif sale_point == -1:
            resp['data'] += f"{symbol}持有时间过长，明天开盘强制卖出！<br />"
            resp['symbol'] += symbol + ','
            resp['operation'] += 'QiangZhi,'
            resp['code'] = 200
            transaction_history.status = '强制'
        # 死叉位
        elif route_methods.dead_cross(stock_info, 0):
            if hold_time == -1:
                resp['data'] += f"{symbol}死叉形成，不建议购买！<br />"
            else:
                resp['data'] += f"{symbol}死叉形成，明天开盘卖出！<br />"
            resp['operation'] += 'SiCha,'
            resp['symbol'] += symbol + ','
            resp['code'] = 200
            transaction_history.status = '死叉'
        # 止损位
        elif (buy_price - cur_price) / buy_price * 100 >= prevent_lose:
            resp['data'] += f"{symbol}跌破止损位，现在止损卖出！<br />"
            resp['operation'] += 'ZhiSun,'
            resp['symbol'] += symbol + ','
            resp['code'] = 200
            transaction_history.status = '止损'
        else:
            # 如果没有任何操作:
            flag = False
        if flag:
            # 判断是否存在：
            obj = TransactionHistory.query.filter(TransactionHistory.symbol == symbol,
                                                  TransactionHistory.date == buy_date).all()
            if not obj and hold_time > -1:
                # 写入选股历史数据库:
                try:
                    db.session.add(transaction_history)
                    db.session.commit()
                except Exception as e:
                    app.logger.info(e)
        # 16日清仓:
        # elif hold_time > 0 and time % 16 == 0:
        #     resp['msg'] = "到达清仓时间，提示清仓！"
    return jsonify(resp)


@route_index.route('/jobs')
@restful
def jobs():
    update = Update()
    update.main()
    return "jobs"


@route_index.route('/message', methods=['GET', 'POST'])
@restful
def message():
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    req = request.values
    symbol = req['symbol']
    date = datetime.datetime.now().strftime('%Y%m%d')
    phone = req['phone']
    operation = req['operation']
    res = Notify.query.filter_by(symbol=symbol, date=date, user_id=g.current_user.uid).first()
    if not res:
        send = Message()
        send.notify(symbol, operation, phone)
        notification = Notify()
        notification.symbol = symbol
        notification.date = date
        notification.user_id = g.current_user.uid
        db.session.add(notification)
        db.session.commit()
    return resp



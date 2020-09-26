# -*- coding: utf-8 -*-
from flask import g
from application import app
from common.models.UserInfo import UserInfo
from web.controllers.compute.common.ComputeIndex import ComputeIndex

class ViewUtils(object):
    @staticmethod
    def refresh_stocklist():
        # 只刷新持股列表div，所以将持股列表信息发送  来自/index:
        html = ''
        hold_list = UserInfo.query.filter_by(user_id=g.current_user.uid).order_by(UserInfo.buy_date).all()
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
        for item in hold_list:
            html += "<li><span><i class='fa fa-trash trash-list' id='trash'></i>股票:" + item.hold_stock + "&nbsp;&nbsp;&nbsp;名称:" + item.name + " &nbsp;&nbsp;&nbsp;选期:" + \
                    item.buy_date + " &nbsp;&nbsp;&nbsp;买价:" + str(item.buy_price) + " &nbsp;&nbsp;&nbsp;持有:" + str(
                item.hold_time) + "天</span></li>"
        return html
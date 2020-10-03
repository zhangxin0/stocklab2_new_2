# coding:utf-8
from flask import g
from common.models.TransactionHistory import TransactionHistory

class GetHistoryByPage(object):
    @classmethod
    def get_history_by_page(cls,page=1,limit=10):
        """
        Get history transaction data by page & limit
        :param page:
        :param limit:
        :return:
        """
        history_list = TransactionHistory.query.filter_by(uid=g.current_user.uid).order_by(
            TransactionHistory.date.desc()).offset((page - 1) * limit).limit(limit).all()

        html_history_list = ''
        for item in history_list:
            html_history_list += f'<tr height="40px"><td>{item.date}</td> <td>{item.name}</td> <td>{item.symbol}</td> <td>{item.hold_time}</td> <td>{item.status}</td></tr>'

        return html_history_list
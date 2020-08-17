# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    __table_args__ = (
        db.Index('USER_STOCK_DATE', 'user_id', 'hold_stock', 'buy_date'),
    )

    id = db.Column(db.BigInteger, primary_key=True, info='id')
    hold_stock = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='持有股票代码')
    name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='股票名称')
    user_id = db.Column(db.ForeignKey('user.uid'), nullable=False, server_default=db.FetchedValue(), info='用户id fk')
    buy_price = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='卖出价格')
    sold_price = db.Column(db.Float, info='卖出价格')
    strategy = db.Column(db.String(2000), info='当前交易策略')
    buy_date = db.Column(db.String(20), info='买入日期')
    hold_time = db.Column(db.Float, info='卖出日期')

    user = db.relationship('User', primaryjoin='UserInfo.user_id == User.uid', backref='user_infos')
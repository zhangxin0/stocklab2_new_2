# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Index, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db




class TransactionHistory(db.Model):
    __tablename__ = 'transaction_history'

    id = db.Column(db.BigInteger, primary_key=True, info='history id')
    uid = db.Column(db.BigInteger, nullable=False, info='用户id')
    date = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='选出日期')
    name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='股票名称')
    symbol = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='股票代码')
    hold_time = db.Column(db.String(2), nullable=False, server_default=db.FetchedValue(), info='持有时间')
    status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='状态')

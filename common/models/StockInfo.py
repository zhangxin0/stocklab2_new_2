# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Index, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db




class StockInfo(db.Model):
    __tablename__ = 'stock_info'
    __table_args__ = (
        db.Index('SYMBOL_TRADE_DATE', 'symbol', 'trade_date'),
    )

    id = db.Column(db.BigInteger, primary_key=True, info='stock id')
    symbol = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='????')
    trade_date = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='????')
    name = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='????')
    open = db.Column(db.Float, info='???')
    close = db.Column(db.Float, info='???')
    high = db.Column(db.Float, info='???')
    low = db.Column(db.Float, info='???')
    vol = db.Column(db.Float, info='???')

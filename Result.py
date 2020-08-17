# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Index, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Result(db.Model):
    __tablename__ = 'result'
    __table_args__ = (
        db.Index('SYMBOL_DATE', 'symbol', 'date'),
    )

    id = db.Column(db.BigInteger, primary_key=True, info='result id')
    symbol = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='选股结果')
    date = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='选股日期')
    price = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='买入价格')

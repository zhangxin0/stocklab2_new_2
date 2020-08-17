# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, Index, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class StockList(db.Model):
    __tablename__ = 'stock_list'

    id = db.Column(db.BigInteger, primary_key=True, info='id')
    symbol = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='symbol')
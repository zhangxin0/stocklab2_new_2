# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db


class UserPage(db.Model):
    __tablename__ = 'user_page'
    uid = db.Column(db.Integer, primary_key=True, info='uid')
    page = db.Column(db.Integer, nullable=False, default=1, info='页码')


# coding: utf-8
from application import db




class CursorDate(db.Model):
    __tablename__ = 'cursor_date'

    id = db.Column(db.BigInteger, primary_key=True, info='stock id')
    cursor_date = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='cursor date')

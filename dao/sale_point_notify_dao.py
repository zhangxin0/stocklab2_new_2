from common.models.SalePointNotify import SalePointNotify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, func, TypeDecorator, Text


db = SQLAlchemy(session_options=dict(autoflush=False))

class SalePointNotifyDao():
    @staticmethod
    def select_all():
        return SalePointNotify.query.filter(SalePointNotify.status == 1).all()

    @staticmethod
    def select_notify_by_id(id):
        return SalePointNotify.query.filter(SalePointNotify.id == id).first()

    @staticmethod
    def select_notify_by_symbol(symbol):
        return SalePointNotify.query.filter(SalePointNotify.symbol == symbol).first()


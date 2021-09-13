from application import db


class Notify(db.Model):
    __tablename__ = 'notify'

    id = db.Column(db.BigInteger, primary_key=True, info='id')
    symbol = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='持有股票代码')
    user_id = db.Column(db.ForeignKey('user.uid'), nullable=False, index=True, server_default=db.FetchedValue(), info='用户id fk')
    date = db.Column(db.Date, nullable=False, server_default=db.FetchedValue(), info='日期')
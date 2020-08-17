from application import db


class Notify(db.Model):
    __tablename__ = 'notify'
    __table_args__ = (
        db.Index('SYMBOL_DATE_UID', 'symbol', 'date', 'user_id'),
    )

    id = db.Column(db.BigInteger, primary_key=True, info='id')
    symbol = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='持有股票代码')
    date = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='交易日期')
    user_id = db.Column(db.ForeignKey('user.uid'), nullable=False, index=True, server_default=db.FetchedValue(), info='用户id fk')

    user = db.relationship('User', primaryjoin='Notify.user_id == User.uid', backref='notifies')
from application import db


class SalePointNotify(db.Model):
    __tablename__ = 'sale_point_notify'

    id = db.Column(db.BigInteger, primary_key=True, info='id')
    symbol = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='持有股票代码')
    user_id = db.Column(db.ForeignKey('user.uid'), nullable=False, index=True, server_default=db.FetchedValue(), info='用户id fk')
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建日期')
    modify_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='修改日期')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='状态，0=无效，1=有效')
    buy_price = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='买入价')
    profit_point = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='止盈位')
    cut_point = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='止损点')
    version = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='版本号')
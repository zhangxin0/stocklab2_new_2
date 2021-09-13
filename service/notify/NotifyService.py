from dao.sale_point_notify_dao import SalePointNotifyDao
from common.models.SalePointNotify import SalePointNotify
from application import db

class NotifyService():
    def save_sale_point(self, dto):
        sale_point_notify = SalePointNotifyDao.select_notify_by_symbol(dto.symbol)
        if not sale_point_notify:
            sale_point_notify = SalePointNotify()
            sale_point_notify.create_time = dto.time
        sale_point_notify.modify_time = dto.time
        sale_point_notify.symbol = dto.symbol
        sale_point_notify.cut_point = dto.cut_point
        sale_point_notify.profit_point = dto.profit_point
        sale_point_notify.buy_price = dto.buy_price
        sale_point_notify.user_id = dto.user_id
        sale_point_notify.status = 1
        db.session.add(sale_point_notify)
        db.session.flush([sale_point_notify])
        db.session.commit()
        return sale_point_notify

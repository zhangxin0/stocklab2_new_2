"""
暂时采用web接口的调用进行止损通知
"""
# from apscheduler.schedulers.blocking import BlockingScheduler
# from web.controllers.compute.common.ReadCursor import ReadCursor
# from web.controllers.compute.common.WriteDb import WriteDb
# from web.controllers.compute.common.ReadDb import ReadDb
# from datetime import datetime
# from web.controllers.notification.notify import Message
# from common.models.Notify import Notify
#
# class SendMessage(object):
#
#     def send_message(self):
#         resp = {'code': 200, 'msg': 'success', 'data': {}}
#
#         symbol = req['symbol']
#         date = datetime.now().strftime('%Y%m%d')
#         phone = req['phone']
#         operation = req['operation']
#         res = Notify.query.filter_by(symbol=symbol, date=date, user_id=g.current_user.uid).first()
#         if not res:
#             send = Message()
#             send.notify(symbol, operation, phone)
#             notification = Notify()
#             notification.symbol = symbol
#             notification.date = date
#             notification.user_id = g.current_user.uid
#             db.session.add(notification)
#             db.session.commit()
#         return resp
#
#
#     def main(self):
#         print('开始定时更新任务，每天18点更新数据库和19点更新选股结果.')
#         scheduler = BlockingScheduler()
#         scheduler.add_job(self.send_message, 'interval', seconds=15)
#         try:
#             scheduler.start()
#         except Exception as e:
#             print(e)
#
#
# if __name__ == '__main__':
#     update = SendMessage()
#     update.main()
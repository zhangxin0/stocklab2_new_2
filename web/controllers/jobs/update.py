"""
update dababase on 3600 seconds
intervals.
"""
from apscheduler.schedulers.background import BackgroundScheduler
import web.controllers.compute.GetData as getData
import requests


class Update:
    def predict(self):
        # 请求predict
        URL = "http://0.0.0.0:5000/predict"
        r = requests.get(url=URL)
        print("选股结果已更新！")
        return r

    def update(self):
        global disable
        print('开始更新')
        if not disable:
            disable = True
            getData.main()
            disable = False


    def main(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.update, 'interval', seconds=10)
        scheduler.add_job(self.predict, 'interval', seconds=10)
        scheduler.start()
        print('开始定时更新任务，每0.5小时更新数据库和算法.')


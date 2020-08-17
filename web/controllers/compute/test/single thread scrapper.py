import time
import requests
total = 100

def request():
    url = 'http://0.0.0.0:8999'
    r = requests.get(url, timeout = 10)

if __name__ == '__main__':
    start = time.perf_counter()
    for i in range(0,total):
        request()
    end = time.perf_counter()
    print(f"单线程爬取{total}个网页，时间:{end-start}")

# 单线程爬取100个网页，时间:10.650077946
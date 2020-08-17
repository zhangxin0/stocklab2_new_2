import time
import requests
from multiprocessing.dummy import Pool
total = 4000
thread = 600

def request():
    url = 'http://0.0.0.0:8999'
    try:
        r = requests.get(url, timeout = 10)
    except requests.exceptions.Timeout:
        print ("Timeout occurred")

def divide(i):
    for j in range(0, total//thread):
        request()

if __name__ == '__main__':
    start = time.perf_counter()
    i = [j for j in range(0,thread)]
    with Pool(thread) as p:
        p.map(divide, i)
    end = time.perf_counter()
    print(f"{thread}个线程爬取{total}个网页，时间:{end-start}")
# 1s
# 500个线程爬取4000个网页，时间:10.881199435000001

# 2s
# 600个线程爬取4000个网页，时间:20.130478475
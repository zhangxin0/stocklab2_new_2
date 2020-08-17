import time
import requests
from multiprocessing.dummy import Pool
import asyncio
import aiohttp
total = 4000
thread = 10
coroutine_num = 300

async def request():
    url = 'http://0.0.0.0:8999'
    # await 是同步的
    for i in range(total//coroutine_num):
        async with aiohttp.ClientSession() as session:
             async with session.get(url) as resp:
                 print(await resp.text())

async def divide(j):
    # tasks 之间是并发的
    tasks = [asyncio.create_task(request()) for i in range(0, coroutine_num//thread)]
    await asyncio.gather(*tasks)

def coro_run(i):
    asyncio.run(divide(i))

if __name__ == '__main__':
    start = time.perf_counter()
    i = [j for j in range(0,thread)]
    with Pool(thread) as p:
        p.map(coro_run, i)
    end = time.perf_counter()
    print(f"{thread}个线程with协程{coroutine_num}爬取{total}个网页，时间:{end-start}")

# 单个协程，并发300,爬取4000个网页，时间:14.220001987
# 5个线程with协程并发300爬取4000个网页，时间:14.162760989999999

# 多线程+协程爬取速度与单线程+协程一致，而且容易崩溃
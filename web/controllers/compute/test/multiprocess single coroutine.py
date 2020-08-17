from multiprocessing import Pool
import os
import asyncio
import aiohttp
import time

total = 4000
coroutine_num = 2400
process_num = 4

async def request():
    url = 'http://0.0.0.0:8999'
    for i in range(total//coroutine_num):
        async with aiohttp.ClientSession() as session:
             async with session.get(url) as resp:
                 print(await resp.text())


async def download_all():
    tasks = [asyncio.create_task( request()) for i in range(coroutine_num//process_num)]
    await asyncio.gather(*tasks)


def coro_run():
    asyncio.run(download_all())

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    start = time.perf_counter()
    p = Pool(process_num)
    for i in range(process_num):
        p.apply_async(coro_run())
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    end = time.perf_counter()
    print(f"{process_num}个进程with协程{coroutine_num}爬取{total}个网页，时间:{end-start}")
# 1s
# 8个进程with协程300爬取4000个网页，时间:105.477750033
# 8个进程with协程500爬取4000个网页，时间:65.545005431
# 8个进程with协程1000爬取4000个网页，时间:34.415408522999996
# 8个进程with协程4000爬取4000个网页，时间:17.55350985
# 8个进程with协程8000爬取4000个网页，时间:0.21980524899999998
# 8个进程with协程10000爬取4000个网页，时间:0.225729773
# 4个进程with协程2000爬取4000个网页，时间:14.137769218999999
# 4个进程with协程2400爬取4000个网页，时间:9.389187028
# 4个进程with协程3200爬取4000个网页，时间:9.709930719

# 3s
# 4个进程with协程2800爬取4000个网页，时间:17.484880104 -不稳定
# 4个进程with协程2400爬取4000个网页，时间:17.310358721
# 8个进程with协程2400爬取4000个网页，时间:26.415039412
# 6个进程with协程2400爬取4000个网页，时间:25.166989291
# 多个进程开到700比较稳定
import time
import asyncio
import aiohttp

total = 4000
coroutine_num = 500
num = 0


async def request():
    url = 'http://0.0.0.0:8999'
    # try:
    global num
    #for i in range(total // coroutine_num):
    for i in range(1):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                num += 1
                print(await resp.text(), num)

    # except Exception as e:
    #     print(e)


async def download_all(start1):
    tasks = [asyncio.create_task(request()) for i in range(coroutine_num)]
    await asyncio.gather(*tasks)
    start1 += coroutine_num
    print(start1)
    return start1


def coro_run():
    start1 = 0
    while start1 < 4000:
        start1 = asyncio.run(download_all(start1))


if __name__ == '__main__':
    start = time.perf_counter()
    coro_run()
    end = time.perf_counter()
    print(f"单个协程，并发{coroutine_num},爬取{total}个网页，时间:{end - start}")

# response 1s
# 单个协程，并发800,爬取4000个网页，时间:8.166242761
# 单个协程，并发500,爬取4000个网页，时间:9.674017177
# 单个协程，并发200,爬取4000个网页，时间:20.759105348000002
# 单个协程，并发300,爬取4000个网页，时间:14.220001987

# response 3s:
# 单个协程，并发500,爬取4000个网页，时间:25.521460569
# 并发600,爬取4000个网页，时间:19.934549988
# 协程并发超过500容易崩，达到最大请求并发 最大并发500 or 800 不稳定


import asyncio
import functools

async def w(c, t):
    await asyncio.sleep(t)

async def createWorker(queue, name, func):
    count = 0
    while not queue.empty():
        count = count + 1
        item = queue.get_nowait()
        await func(name, item)

    #print("worker[{}] existed after {} tasks".format(name, count))

# 协程入口
async def multi_worker(tasks, func, worker_count = 3):
    queue = asyncio.Queue(len(tasks), loop=asyncio.get_running_loop())

    # 100 个任务, 分配
    for i in tasks:
        queue.put_nowait(i)

    return await asyncio.gather(
        *[
            createWorker(queue, "{}".format(x+1), func)
            for x in range(worker_count)
        ]
    )

def Main():
    tasks  = [{"id":x, "count": x%3 +1 } for x in range(20)]

    # 主线程, 简单阻塞等待任务结束
    loop = asyncio.get_event_loop()
    # 转移给协程
    async def func(name, item):
        t = item["count"]
        i = item["id"]
        print("worker[{}] start item {}, sleep {}".format(name, i, t))
        await w(i, t)

    loop.run_until_complete(multi_worker(tasks, func, 20))
    loop.close()


if __name__ == "__main__":
    Main()

import asyncio
import functools
import requests
import sys
import json
import yaml
from urllib.parse import quote
import async_tasks
from os.path import expanduser

config = {}

with open(expanduser("~/.openclashconfig"), 'r') as file:
    content = file.read()
    config = yaml.safe_load(content)

baseUrl = config["base_url"]
authHeaders = config["headers"]
DELAY_TEST_URL= config["test_url"]
SHOW_ERROR = config.get("show_error", False)
TIMEOUT = config.get("show_error", 3000)
WORKER_COUNT = config.get("worker_count", 20)

def Main(args):
    proxies = getAllProxies({})

    pCount = len(proxies) 
    if pCount > 0 :
        loop = asyncio.get_event_loop()
        print("processing {} proxies".format(pCount))
        loop.run_until_complete(startRefreshingJob(proxies))
        loop.close()

def getAllProxies(config):
    proxies = []
    r = requests.get("{}/proxies".format(baseUrl), headers = authHeaders)
    if r.status_code != 200:
        # do errr
        pass

    return json.loads(r.text, encoding="utf-8")["proxies"]

async def startRefreshingJob(proxiesMap):
    proxies = [
        {"name": x, "info": proxiesMap[x]}
        for x in proxiesMap
    ]

    async def handler(worker_name, item):
        proxy = item["info"]
        name = item["name"]

        if proxy["type"] not in ["Vmess", "Shadowsocks"]:
            return

        await refreshProxyDelay(worker_name, name, proxy, DELAY_TEST_URL ,TIMEOUT)

    await async_tasks.multi_worker(proxies, handler, worker_count = 20)


async def refreshProxyDelay(job, name, proxy, url,timeout=500):
    delay_url = "{}/proxies/{}/delay?timeout={timeout}&url={testUrl}".format(
        baseUrl,
        quote(proxy["name"]),
        timeout = timeout,
        testUrl = quote(url)
    )

    func = functools.partial(requests.get, delay_url, headers = authHeaders, timeout = timeout)

    r = await asyncio.get_running_loop().run_in_executor(None, func , None)

    if r.status_code == 200:
        delay = json.loads(r.text)
        print("Task{}::proxy [{}] delay {}".format(job, proxy["name"], delay["delay"]))
    elif SHOW_ERROR:
        print("Task{}::proxy [{}] get delay error".format(job, name))



if __name__ == "__main__":
   Main(None) 

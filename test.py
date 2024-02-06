import asyncio

import time

async def a():
    time.sleep(1)
    print("a")

async def b():
    time.sleep(1)
    print("b")

asyncio.ensure_future(a())
asyncio.ensure_future(b())
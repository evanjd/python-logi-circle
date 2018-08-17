import aiohttp
import asyncio
import sys
import logging
from logi_circle import Logi

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

logi = Logi('user@email.com', 'password')


async def run_test():
    await logi.login()
    await logi.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(run_test())
loop.close()

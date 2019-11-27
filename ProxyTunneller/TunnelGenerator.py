import asyncio
import random
from asyncio import Queue
from typing import List

from ProxyTunneller import Proxy, Tunnel


class TunnelGenerator:
    __inner_proxy_pool: List[Proxy]
    __outer_proxy_pool: List[Proxy]
    queue: Queue
    allow_only_invisible_tunnels: bool = True
    tunnels_lifetime: int = 10*60

    def __init__(self, queue: Queue, inner_proxy_pool: List[Proxy], outer_proxy_pool: List[Proxy]):
        self.__inner_proxy_pool = inner_proxy_pool
        self.__outer_proxy_pool = outer_proxy_pool
        self.queue = queue

    def run(self):
        asyncio.create_task(self._start())

    async def _start(self):
        for outer_proxy in self.__outer_proxy_pool:
            inner_proxy = random.choice(self.__inner_proxy_pool)
            tunnel = Tunnel(inner_proxy, outer_proxy)
            await tunnel.build(self.tunnels_lifetime)
            if self.allow_only_invisible_tunnels:
                tunnel_is_correct: bool = await tunnel.is_invisible()
            else:
                tunnel_is_correct: bool = await tunnel.is_available_to_resource('http://ifconfig.me/ip')
            if tunnel_is_correct:
                await self.queue.put(tunnel)
            else:
                asyncio.create_task(tunnel.destroy())

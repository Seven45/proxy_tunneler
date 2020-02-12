import asyncio
import random
from asyncio import Queue, Task
from typing import List, Callable

import pproxy

from ProxyTunneller import Proxy, Tunnel


class TunnelGenerator:
    __inner_proxy_pool: List[Proxy]
    __outer_proxy_pool: List[Proxy]
    queue: Queue
    check_tunnels_for_invisibility: bool = False
    check_tunnels_for_availability: bool = False
    tunnels_lifetime: int = 5 * 60
    __generation_task: Task
    lock: asyncio.Lock

    def __init__(self,
                 queue: Queue,
                 inner_proxy_pool: List[Proxy],
                 outer_proxy_pool: List[Proxy],
                 lock: asyncio.Lock = asyncio.Lock()):
        self.__inner_proxy_pool = inner_proxy_pool
        self.__outer_proxy_pool = outer_proxy_pool
        self.queue = queue
        self.lock = lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__generation_task.cancel()
        while not self.queue.empty():
            tunnel = self.queue.get_nowait()
            self.queue.task_done()
            tunnel.destroy()

    def run(self, traffic_writer: Callable = pproxy.server.DUMMY):
        self.__generation_task = asyncio.create_task(self._start(traffic_writer))

    async def _start(self, verbose_func: Callable):
        for outer_proxy in self.__outer_proxy_pool:
            async with self.lock:
                while self.queue.full():
                    await asyncio.sleep(1)

                inner_proxy = random.choice(self.__inner_proxy_pool)
                tunnel = Tunnel(inner_proxy, outer_proxy, verbose_func=verbose_func)
                await tunnel.build(self.tunnels_lifetime)

                tunnel_is_correct = True
                if self.check_tunnels_for_invisibility:
                    tunnel_is_correct = await tunnel.is_invisible()
                if self.check_tunnels_for_availability:
                    tunnel_is_correct = await tunnel.is_available_to_resource('http://ifconfig.me/ip')

                if tunnel_is_correct:
                    await self.queue.put(tunnel)
                else:
                    await tunnel.destroy()

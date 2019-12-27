import asyncio
from datetime import datetime, timedelta
from typing import Callable, Optional

import pproxy
from aiohttp import ClientSession, ClientError, ServerConnectionError
from aiosocksy.connector import ProxyClientRequest, ProxyConnector

from ProxyTunneller import Proxy, utils


class Tunnel:
    build_time: datetime
    destroy_time: datetime
    __destroy_task: asyncio.Task
    port: int
    inner_proxy: Proxy
    outer_proxy: Proxy
    server: asyncio.AbstractServer

    def __init__(self,
                 inner_proxy: Proxy,
                 outer_proxy: Proxy,
                 port: Optional[int] = None,
                 verbose_func: Optional[Callable] = pproxy.server.DUMMY):
        if port is None:
            port = utils.get_ephemeral_port()
        self.port = port
        self.inner_proxy = inner_proxy
        self.outer_proxy = outer_proxy
        self.verbose_func = verbose_func

    def __str__(self) -> str:
        return self.route_info

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.destroy())

    @property
    def url(self) -> str:
        return f'http://localhost:{self.port}'

    @property
    def route_info(self) -> str:
        return f'{self.url} -> {self.inner_proxy} -> {self.outer_proxy}'

    @property
    async def ping(self) -> int:
        return await utils.get_proxy_ping(self.url)

    async def is_invisible(self, ip_judge: str = 'http://ifconfig.me/ip') -> bool:
        try:
            inner_ip, outer_ip = await asyncio.gather(*[
                utils.get_visible_ip(self.inner_proxy.url, ip_judge),
                utils.get_visible_ip(self.url, ip_judge)
            ])
            if inner_ip == outer_ip:
                return False
        except ServerConnectionError:
            return False
        return True

    async def is_available_to_resource(self, resource: str) -> bool:
        try:
            async with ClientSession(connector=ProxyConnector(), request_class=ProxyClientRequest) as client:
                async with client.get(resource, proxy=self.url, timeout=5) as response:
                    if response.status != 200:
                        return False
        except (ClientError, asyncio.TimeoutError):
            return False
        return True

    async def build(self, lifetime: int = 0) -> None:
        self.build_time = datetime.now()
        if lifetime > 0:
            self.destroy_time = self.build_time + timedelta(seconds=lifetime)
            self.__destroy_task = asyncio.create_task(self.run_destruction_timer())
        server = pproxy.Server(f'http+socks4+socks5://0.0.0.0:{self.port}')
        connection = pproxy.Connection(f'{self.inner_proxy.url}__{self.outer_proxy.url}')
        try:
            self.server = await server.start_server({'rserver': [connection],
                                                     'verbose': self.verbose_func})
        except OSError:
            self.port = utils.get_ephemeral_port()
            await self.build(lifetime)

    async def destroy(self) -> None:
        if hasattr(self, 'server'):
            self.server.close()
            await self.server.wait_closed()

    async def run_destruction_timer(self):
        sleep_time = self.destroy_time - self.build_time
        await asyncio.sleep(sleep_time.seconds)
        await self.destroy()

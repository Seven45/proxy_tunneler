import itertools
import socket
import time
from asyncio import TimeoutError
from operator import attrgetter
from typing import List, TypeVar

from aiohttp import ClientSession, ClientError, ServerConnectionError
from aiosocksy.connector import ProxyConnector, ProxyClientRequest

T = TypeVar('T')


def get_ephemeral_port() -> int:
    port = 0
    while port < 49152:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.bind(('', 0))
        port = temp_socket.getsockname()[1]
        temp_socket.close()
    return port


def group_objects_by_attr(objects: List[T], attr_name: str) -> List[List[T]]:
    result = list()
    objects = sorted(objects, key=attrgetter(attr_name))
    grouped_objects = itertools.groupby(objects, key=lambda obj: obj.__getattribute__(attr_name))
    for _, _object in grouped_objects:
        result.append(list(_object))
    return result


async def get_proxy_ping(proxy_url: str, ping_target: str = 'https://google.com') -> int:
    conn = ProxyConnector()

    start_time = time.process_time()
    try:
        async with ClientSession(connector=conn, request_class=ProxyClientRequest) as client:
            async with client.get(ping_target, proxy=proxy_url, timeout=5) as response:
                end_time = time.process_time()
                if response.status != 200:
                    ping = None
                else:
                    ping = int((end_time - start_time) * 1000)
    except (ClientError, TimeoutError, ValueError):
        ping = None
    return ping


async def get_visible_ip(proxy_url: str, ip_judge: str = 'http://ifconfig.me/ip') -> str:
    try:
        async with ClientSession(connector=ProxyConnector(), request_class=ProxyClientRequest) as client:
            async with client.get(ip_judge, proxy=proxy_url, timeout=5) as response:
                return await response.text()
    except (ClientError, TimeoutError):
        raise ServerConnectionError

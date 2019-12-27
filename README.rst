ProxyTuneller
=============

|made-with-python| |PyPI-version| |Hit-Count| |Downloads|

.. |made-with-python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
   :target: https://www.python.org/
.. |PyPI-version| image:: https://badge.fury.io/py/ProxyTunneller.svg
   :target: https://pypi.python.org/pypi/ProxyTunneller/
.. |Hit-Count| image:: http://hits.dwyl.io/Seven45/ProxyTunneller.svg
   :target: https://pypi.python.org/pypi/ProxyTunneller/
.. |Downloads| image:: https://pepy.tech/badge/ProxyTunneller
   :target: https://pepy.tech/project/ProxyTunneller

Library for create/generation proxy tunnels.

Installation
------------

.. code-block:: rst

  $ pip3 install ProxyTuneller

Examples
--------

Create proxy tunnel

.. code-block:: python

    import asyncio

    from ProxyTunneller import Proxy, Tunnel


    async def main():
        inner_proxy = Proxy('http', '104.28.10.155', 80)
        outer_proxy = Proxy('socks5', '5.9.143.59', 3128)
        tunnel = Tunnel(inner_proxy, outer_proxy, verbose_func=print)
        await tunnel.build()
        print(tunnel.url)

    if __name__ == '__main__':
        asyncio.run(main())

Generate tunnels from proxy-pool

.. code-block:: python

    import asyncio

    from ProxyTunneller import Proxy, TunnelGenerator


    async def main():
        inner_proxies = [
            Proxy('http', '104.28.10.145', port)
            for port in range(13010, 13030)
        ]
        outer_proxies = [
            Proxy('socks5', '138.197.157.44', port)
            for port in range(40055, 40200)
        ]

        queue = asyncio.Queue()
        generator = TunnelGenerator(queue, inner_proxies, outer_proxies)
        # support transparent tunnels
        generator.allow_only_invisible_tunnels = False
        # close each tunnel in 20 minutes after opening (0 - not close)
        generator.tunnels_lifetime = 20*60
        generator.run(traffic_writer=print) #  or any func for writing traffic
        while True:
            try:
                tunnel = await asyncio.wait_for(queue.get(), 60)
            except asyncio.TimeoutError:
                break
            print(tunnel.url)


    if __name__ == '__main__':
        asyncio.run(main())

Parallel running of generators for each proxy-provider

.. code-block:: python

    import asyncio
    from typing import List

    import databases
    from ProxyTunneller import Proxy, TunnelGenerator, utils


    db_url = '<URL_FOR_CONNECT_TO_YOUR_DATABASE>'
    dataBase = databases.Database(db_url)


    async def get_proxies() -> List[Proxy]:
        if not dataBase.is_connected:
            await dataBase.connect()
        query = f'''SELECT * FROM proxies WHERE proxy_type IN ('http', 'socks4', 'socks5')'''
        proxies = await dataBase.fetch_all(query)
        proxies = list(map(lambda proxy: Proxy(proxy['proxy_type'],
                                               proxy['host'],
                                               proxy['port'],
                                               proxy['provider_name']),
                           proxies))
        return proxies


    async def fill_queue(queue: asyncio.Queue):
        inner_proxies = [
            Proxy('http', '1.0.0.101', port)
            for port in range(13010, 13030)
        ]
        outer_proxies = await get_proxies()
        grouped_proxy_lists = utils.group_objects_by_attr(outer_proxies, 'provider')

        for proxy_list in grouped_proxy_lists:
            generator = TunnelGenerator(queue, inner_proxies, proxy_list)
            generator.run()


    async def main():
        queue = asyncio.Queue(maxsize=200)
        await fill_queue(queue)
        while True:
            try:
                tunnel = await asyncio.wait_for(queue.get(), 60)
            except asyncio.TimeoutError:
                await fill_queue(queue)
                continue
            print(str(tunnel))


    if __name__ == '__main__':
        asyncio.run(main())


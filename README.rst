ProxyTuneller
=============

|made-with-python| |PyPI-version| |Hit-Count| |Downloads|

.. |made-with-python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
   :target: https://www.python.org/
.. |PyPI-version| image:: https://badge.fury.io/py/pproxy.svg
   :target: https://pypi.python.org/pypi/pproxy/
.. |Hit-Count| image:: http://hits.dwyl.io/qwj/python-proxy.svg
   :target: https://pypi.python.org/pypi/pproxy/
.. |Downloads| image:: https://pepy.tech/badge/pproxy
   :target: https://pepy.tech/project/pproxy

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


    await def main():
        inner_proxy = Proxy('http', '104.28.10.155', 80)
        outer_proxy = Proxy('socks5', '5.9.143.59', 3128)
        tunnel = Tunnel(inner_proxy, outer_proxy)
        await tunnel.build
        print(tunnel.url)

    if __name__ == '__main__':
        asyncio.run(main())

Generate tunnels from proxy-pools

.. code-block:: python

    import asyncio
    from ProxyTunneller import Proxy, TunnelGenerator


    await def main():
        inner_proxies = [
            Proxy('http', '104.28.10.145', port)
            for port in range(12040, 12054)
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
        generator.run()
        while True:
            try:
                tunnel = await asyncio.wait_for(queue.get(), 60)
            except asyncio.TimeoutError:
                break
            print(tunnel.url)


    if __name__ == '__main__':
        asyncio.run(main())


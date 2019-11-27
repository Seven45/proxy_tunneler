from ProxyTunneller import utils


class Proxy:
    scheme: str
    host: str
    port: int
    provider: str

    def __init__(self, scheme: str, host: str, port: int, provider: str = None):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.provider = provider

    def __str__(self) -> str:
        return self.url

    @property
    def address(self) -> str:
        return f'{self.host}:{self.port}'

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.address}'

    @property
    async def ping(self) -> int:
        return await utils.get_proxy_ping(self.url)

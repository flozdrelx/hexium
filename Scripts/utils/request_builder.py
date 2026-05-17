from urllib.parse import urlparse
from helpers.converter import Validate

class RequestBuilder:
    def __init__(self, url: str):
        validation = Validate(url)
        url = validation.reform()

        self.url = urlparse(url)
        self.host = self.url.hostname
        self.secure = self.url.scheme == 'https'
        self.port = self.url.port or (443 if self.secure else 80)
        self.path = self.url.path or '/'

        if self.url.query:
            self.path = f'{self.path}?{self.url.query}'

        if self.url.scheme not in ('http', 'https'):
            raise ValueError('Networking get supports http:// and https:// URLs.')

        if not self.host:
            raise ValueError('Please provide a valid URL.')

    def build_get_request(self) -> str:
        host_header = self.host

        if self.url.port:
            host_header = f'{self.host}:{self.url.port}'

        request = (
            f'GET {self.path} HTTP/1.1\r\n'
            f'Host: {host_header}\r\n'
            'User-Agent: Hexium/0.03\r\n'
            'Connection: close\r\n\r\n'
        )

        return request
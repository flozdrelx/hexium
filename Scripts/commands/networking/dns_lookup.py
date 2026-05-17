import socket
from helpers.converter import Validate

class DNSLookup:
    def __init__(self, url):
        self.url = url

    def execute(self):
        host = Validate(self.url).hostname()

        if not host:
            return 'Please provide a valid host for dns_lookup.'

        try:
            ip_addr = socket.gethostbyname(host)
        except socket.gaierror as e:
            return f'DNS lookup failed for {host}: {e}'

        return f'IP address for {host}: {ip_addr}'
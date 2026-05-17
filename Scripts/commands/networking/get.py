from utils.response_parser import Parser
import socket
import ssl

class GetRequest:
    def __init__(self, host: str, port: int = 80, secure: bool = False):
        self.host = host
        self.port = port
        self.secure = secure

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.client.settimeout(20)

    def connect(self):
        self.client.connect((self.host, self.port))

        if self.secure:
            context = ssl.create_default_context()
            self.client = context.wrap_socket(self.client, server_hostname=self.host)
            self.client.settimeout(20)

    def send_request(self, request: str):
        self.client.sendall(request.encode())

    def receive_response(self) -> bytes:
        response = b''

        while True:
            chunk = self.client.recv(4096)

            if not chunk:
                break

            response += chunk

        parser = Parser(response)

        return parser.response_parse()

    def close(self):
        self.client.close()

    def send_and_recieve(self, request: str):
        try:
            self.connect()
            self.send_request(request)

            return self.receive_response()

        except OSError as e:
            return {
                'headers': '',
                'body': f'Error sending GET request: {e}'
            }

        finally:
            self.close()

    def send_and_receive(self, request: str):
        return self.send_and_recieve(request)
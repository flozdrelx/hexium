class Parser:
    def __init__(self, response: bytes):
        self.response = response

    def decode_chunked_body(self, body: bytes) -> bytes:
        decoded = []
        remaining = body

        while remaining:
            size_line, separator, remaining = remaining.partition(b'\r\n')

            if not separator:
                return body

            try:
                size = int(size_line.split(b';', 1)[0], 16)
            except ValueError:
                return body

            if size == 0:
                break

            decoded.append(remaining[:size])
            remaining = remaining[size:]

            if remaining.startswith(b'\r\n'):
                remaining = remaining[2:]

        return b''.join(decoded)

    def response_parse(self):
        headers, separator, body = self.response.partition(b'\r\n\r\n')

        if not separator:
            return {
                'headers': '',
                'body': self.response.decode(errors='ignore')
            }

        header_text = headers.decode(errors='ignore')

        if 'transfer-encoding: chunked' in header_text.lower():
            body = self.decode_chunked_body(body)

        return {
            'headers': header_text,
            'body': body.decode(errors='ignore')
        }
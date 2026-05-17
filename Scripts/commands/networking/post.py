import requests
from helpers.converter import Validate
from utils.http_formatter import format_requests_response

class PostRequest:
    def __init__(self, url, args):
        self.url = url
        self.args = args 

    def parse_data(self):
        data = {}

        for pair in self.args:
            if '=' not in pair:
                return None, f'Invalid POST data "{pair}". Use key=value.'

            key, value = pair.split('=', 1)

            if not key:
                return None, 'POST data keys cannot be empty.'

            data[key] = value

        return data, None

    def post_request(self):
        validation = Validate(self.url)
        self.url = validation.reform()

        data, error = self.parse_data()

        if error:
            return error

        try:
            response = requests.post(self.url, data=data, timeout=15)

            return format_requests_response(response)

        except requests.exceptions.RequestException as e:
            return f'Error sending POST request: {e}'
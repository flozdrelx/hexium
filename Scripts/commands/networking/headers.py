from helpers.converter import Validate
import requests

class CheckHeaders:
    def __init__(self, url):
        self.url = url

    def execute(self):
        validation = Validate(self.url)
        self.url = validation.reform()

        try:
            response = requests.get(self.url, timeout=15)
            lines = [
                'Status',
                f'  HTTP {response.status_code}',
                '',
                'Headers'
            ]

            lines.extend(f'  {key}: {value}' for key, value in response.headers.items())

            return '\n'.join(lines)

        except requests.exceptions.RequestException as e:
            return f'Error fetching the website: {e}'
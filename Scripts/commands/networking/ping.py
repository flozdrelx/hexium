import subprocess
import platform
from helpers.converter import Validate

class CheckPing:
    def __init__(self, url):
        self.url = url

    def execute(self):
        host = Validate(self.url).hostname()

        if not host:
            return 'Please provide a valid host for ping.'

        system = platform.system().lower()

        if system == 'windows':
            command = ['ping', '-n', '4', host]
        else:
            command = ['ping', '-c', '4', host]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=20
            )

            if result.returncode != 0:
                return result.stderr or result.stdout or 'Ping failed.'

            return result.stdout

        except Exception as e:
            return f'Ping failed: {e}'
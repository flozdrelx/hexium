import re
from urllib.parse import urlparse

class Validate:
    def __init__(self, string):
        self.string = string

    def reform(self):
        self.string = self.string.strip()

        lower_string = self.string.lower()

        if not lower_string.startswith('http://') and not lower_string.startswith('https://'):
            self.string = 'http://' + self.string

        return self.string

    def is_blank(self):
        return not bool(self.string.strip())
    
    def which_url(self):
        url = self.string[4:].strip()

        return url if url else None

    def hostname(self):
        url = self.reform()
        parsed = urlparse(url)

        return parsed.hostname
    
    def sanitize_url(self):
        self.string = re.sub(r"[<>:'/\\|?*\s]+", '_', self.string.strip())
        self.string = re.sub(r'[^\w.\-=]+', '_', self.string)
        self.string = re.sub(r'\s+', '_', self.string)
        self.string = re.sub(r'_+', '_', self.string)
        self.string = self.string.strip('_.')

        if not self.string:
            self.string = 'website'

        return self.string
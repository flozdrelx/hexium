import re

class Validate:
    def __init__(self, string):
        self.string = string

    def reform(self):
        if not self.string.startswith('http://') and not self.string.startswith('https://'):
            self.string = 'http://' + self.string

        return self.string

    def is_blank(self):
        return not bool(self.string.strip())
    
    def which_url(self):
        url = self.string[4:].strip()

        return url if url else None
    
    def sanitize_url(self):
        self.string = re.sub(r'[<>:"/\\|?*\s]+', '_', self.string.strip())
        self.string = re.sub(r'[^\w.\-=]+', '_', self.string)
        self.string = re.sub(r'\s+', '_', self.string)
        self.string = re.sub(r'_+', '_', self.string)
        self.string = self.string.strip('_.')

        if not self.string:
            self.string = 'website'

        return self.string
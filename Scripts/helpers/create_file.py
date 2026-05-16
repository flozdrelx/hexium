from pathlib import Path
from helpers.converter import Validate

def sanitize_filename(filename):
    return Validate(filename).sanitize_url()

class CreateFile:
    def __init__(self, directory, filename, content):
        self.directory = directory
        self.filename = filename
        self.content = content

    def create(self):
        dir_path = Path(self.directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / sanitize_filename(self.filename)
        file_path.write_text(self.content, encoding='utf-8')

        return file_path
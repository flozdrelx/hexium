from helpers.create_file import CreateFile
import helpers.converter as converter
from pathlib import Path
import html2text
import requests
import bs4

SAVE_OPTIONS = {'md', 'html', 'both'}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEBSITES_DIR = PROJECT_ROOT / 'websites'

class GetWebsite:
    def __init__(self, url, save_option='both'):
        self.url = url
        self.save_option = save_option

    def convert(self):
        url_converter = converter.Validate(self.url)

        if url_converter.is_blank():
            return 'URL cannot be empty.'

        self.url = url_converter.reform()
        
    def markdown_from_html(self, html):
        converter = html2text.HTML2Text()
        converter.ignore_images = True

        return converter.handle(html)

    def title_from_html(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')

        if soup.head and soup.head.title and soup.head.title.string:
            return soup.head.title.string.strip()

        return 'website'

    def save_files(self, title, html, markdown):
        saved_files = []

        if self.save_option in ('html', 'both'):
            html_file = CreateFile(WEBSITES_DIR, f'{title}.html', html)
            saved_files.append(html_file.create())

        if self.save_option in ('md', 'both'):
            markdown_file = CreateFile(WEBSITES_DIR, f'{title}.md', markdown)
            saved_files.append(markdown_file.create())

        return saved_files

    def get(self):
        conversion_error = self.convert()

        if conversion_error:
            return conversion_error

        if self.save_option not in SAVE_OPTIONS:
            return 'Save option must be md, html, or both.'

        try:
            response = requests.get(self.url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return f'Error fetching the website: {e}'

        html = response.text
        markdown = self.markdown_from_html(html)
        title = self.title_from_html(html)
        saved_files = self.save_files(title, html, markdown)
        saved_names = ', '.join(path.name for path in saved_files)

        return f'Website has been saved in the websites folder: {saved_names}'
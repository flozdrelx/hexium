from helpers.create_file import CreateFile
import helpers.converter as converter
from pathlib import Path
from urllib.parse import urljoin, urlparse
import html2text
import requests
import bs4

SAVE_OPTIONS = {'md', 'html', 'both'}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEBSITES_DIR = PROJECT_ROOT / 'websites'
ASSET_ATTRIBUTES = {
    'img': ('src',),
    'script': ('src',),
    'source': ('src', 'srcset'),
    'video': ('src', 'poster'),
    'audio': ('src',),
    'link': ('href',),
}

class GetWebsite:
    def __init__(self, url, save_option='both', download_assets=False):
        self.url = url
        self.save_option = save_option
        self.download_assets = download_assets
        self.session = requests.Session()

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

    def folder_name_from_title(self, title):
        return converter.Validate(title).sanitize_url()

    def unique_directory(self, directory):
        if not directory.exists():
            return directory

        counter = 2

        while True:
            candidate = directory.with_name(f'{directory.name}_{counter}')

            if not candidate.exists():
                return candidate

            counter += 1

    def should_download_asset(self, tag, attribute):
        if tag.name != 'link':
            return True

        rel_values = [value.lower() for value in tag.get('rel', [])]

        return (
            attribute == 'href'
            and any(rel in rel_values for rel in ('stylesheet', 'icon', 'shortcut icon', 'preload'))
        )

    def local_asset_path(self, asset_url, used_names):
        parsed = urlparse(asset_url)
        asset_name = Path(parsed.path).name or 'asset'
        asset_name = converter.Validate(asset_name).sanitize_url()

        if '.' not in asset_name:
            asset_name = f'{asset_name}.bin'

        original_name = asset_name
        counter = 2

        while asset_name in used_names:
            suffix = Path(original_name).suffix
            stem = Path(original_name).stem
            asset_name = f'{stem}_{counter}{suffix}'
            counter += 1

        used_names.add(asset_name)

        return Path('assets') / asset_name

    def download_asset(self, asset_url, website_dir, local_path):
        try:
            response = self.session.get(asset_url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return False

        file_path = website_dir / local_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(response.content)

        return True

    def localize_srcset(self, srcset, website_dir, used_names, stats):
        localized_items = []

        for item in srcset.split(','):
            parts = item.strip().split()

            if not parts:
                continue

            asset_url = parts[0]
            local_url = self.localize_asset(asset_url, website_dir, used_names, stats)
            parts[0] = local_url or asset_url
            localized_items.append(' '.join(parts))

        return ', '.join(localized_items)

    def localize_asset(self, asset_url, website_dir, used_names, stats):
        if not asset_url or asset_url.startswith(('data:', 'mailto:', 'tel:', '#')):
            return None

        absolute_url = urljoin(self.url, asset_url)
        parsed = urlparse(absolute_url)

        if parsed.scheme not in ('http', 'https'):
            return None

        local_path = self.local_asset_path(absolute_url, used_names)

        if self.download_asset(absolute_url, website_dir, local_path):
            stats['downloaded'] += 1
            return local_path.as_posix()

        stats['failed'] += 1
        return None

    def localize_assets(self, html, website_dir):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        used_names = set()
        stats = {'downloaded': 0, 'failed': 0}

        for tag_name, attributes in ASSET_ATTRIBUTES.items():
            for tag in soup.find_all(tag_name):
                for attribute in attributes:
                    if not tag.has_attr(attribute) or not self.should_download_asset(tag, attribute):
                        continue

                    if attribute == 'srcset':
                        tag[attribute] = self.localize_srcset(tag[attribute], website_dir, used_names, stats)
                        continue

                    local_url = self.localize_asset(tag[attribute], website_dir, used_names, stats)

                    if local_url:
                        tag[attribute] = local_url

        return str(soup), stats

    def save_files(self, title, html, markdown, website_dir):
        saved_files = []

        if self.save_option in ('html', 'both'):
            html_file = CreateFile(website_dir, 'index.html', html)
            saved_files.append(html_file.create())

        if self.save_option in ('md', 'both'):
            markdown_file = CreateFile(website_dir, 'index.md', markdown)
            saved_files.append(markdown_file.create())

        return saved_files

    def get(self):
        conversion_error = self.convert()

        if conversion_error:
            return conversion_error

        if self.save_option not in SAVE_OPTIONS:
            return 'Save option must be md, html, or both.'

        try:
            response = self.session.get(self.url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return f'Error fetching the website: {e}'

        html = response.text
        markdown = self.markdown_from_html(html)
        title = self.title_from_html(html)
        folder_name = self.folder_name_from_title(title)
        website_dir = self.unique_directory(WEBSITES_DIR / folder_name)
        asset_stats = None

        if self.download_assets and self.save_option in ('html', 'both'):
            html, asset_stats = self.localize_assets(html, website_dir)

        saved_files = self.save_files(title, html, markdown, website_dir)
        saved_names = ', '.join(path.name for path in saved_files)
        message = f'Website has been saved in {website_dir}: {saved_names}'

        if asset_stats:
            message += f'\nAssets downloaded: {asset_stats["downloaded"]}'

            if asset_stats['failed']:
                message += f' ({asset_stats["failed"]} failed)'

        return message

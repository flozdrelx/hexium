import mimetypes
import re
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

MIME_MAP = {
    'text/css': '.css',
    'text/javascript': '.js',
    'application/javascript': '.js',
    'application/x-javascript': '.js',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/svg+xml': '.svg',
    'image/webp': '.webp',
    'image/x-icon': '.ico',
    'image/vnd.microsoft.icon': '.ico',
    'font/woff': '.woff',
    'font/woff2': '.woff2',
    'font/ttf': '.ttf',
    'font/otf': '.otf',
    'application/font-woff': '.woff',
    'application/font-woff2': '.woff2',
}

class GetWebsite:
    def __init__(self, url, save_option='both', download_assets=False):
        self.url = url
        self.save_option = save_option
        self.download_assets = download_assets

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.downloaded_absolute_urls = {}

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

        rel = tag.get('rel', [])

        if isinstance(rel, str):
            rel_values = [rel.lower()]
        else:
            rel_values = [value.lower() for value in rel if isinstance(value, str)]

        return (
            attribute == 'href'
            and any(rel in rel_values for rel in ('stylesheet', 'icon', 'shortcut icon', 'preload'))
        )

    def download_sub_asset(self, asset_url, website_dir, used_names, stats):
        parsed = urlparse(asset_url)
        path_suffix = Path(parsed.path).suffix.lower()
        
        if path_suffix in ('.html', '.htm', '.php', '.asp', '.aspx'):
            return None

        local_path_str = self.download_asset(asset_url, website_dir, used_names, stats)
        
        if local_path_str:
            filename = Path(local_path_str).name
            self.downloaded_absolute_urls[asset_url] = filename
            
            return filename

        self.downloaded_absolute_urls[asset_url] = None
        
        return None

    def localize_css_assets(self, css_text, css_url, website_dir, used_names, stats, is_external_css=True):
        url_pattern = re.compile(r'url\(\s*([\'"]?)(.*?)\1\s*\)', re.IGNORECASE)

        def replace_url(match):
            quote = match.group(1) or '"'
            original_path = match.group(2).strip()

            if not original_path or original_path.startswith(('data:', 'mailto:', 'tel:', '#')):
                return match.group(0)

            absolute_asset_url = urljoin(css_url, original_path)

            if absolute_asset_url in self.downloaded_absolute_urls:
                local_asset_name = self.downloaded_absolute_urls[absolute_asset_url]
            else:
                local_asset_name = self.download_sub_asset(absolute_asset_url, website_dir, used_names, stats)

            if local_asset_name:
                resolved_path = local_asset_name if is_external_css else f'assets/{local_asset_name}'
                
                return f'url({quote}{resolved_path}{quote})'

            return match.group(0)

        import_pattern = re.compile(r'@import\s+([\'"])(.*?)\1', re.IGNORECASE)

        def replace_import(match):
            quote = match.group(1)
            original_path = match.group(2).strip()

            if not original_path or original_path.startswith(('data:', 'mailto:', 'tel:', '#')):
                return match.group(0)

            absolute_asset_url = urljoin(css_url, original_path)

            if absolute_asset_url in self.downloaded_absolute_urls:
                local_asset_name = self.downloaded_absolute_urls[absolute_asset_url]
            else:
                local_asset_name = self.download_sub_asset(absolute_asset_url, website_dir, used_names, stats)

            if local_asset_name:
                resolved_path = local_asset_name if is_external_css else f'assets/{local_asset_name}'
                return f'@import {quote}{resolved_path}{quote}'

            return match.group(0)

        css_text = url_pattern.sub(replace_url, css_text)
        css_text = import_pattern.sub(replace_import, css_text)
        return css_text

    def download_asset(self, asset_url, website_dir, used_names, stats):
        try:
            response = self.session.get(asset_url, timeout=15)
            response.raise_for_status()

        except requests.exceptions.RequestException:
            stats['failed'] += 1
            return None

        content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
        ext = None

        if content_type in MIME_MAP:
            ext = MIME_MAP[content_type]
        else:
            ext = mimetypes.guess_extension(content_type)

        parsed = urlparse(asset_url)
        path_suffix = Path(parsed.path).suffix.lower()

        if path_suffix in ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.otf'):
            ext = path_suffix

        if not ext:
            ext = '.bin'

        base_name = Path(parsed.path).stem or 'asset'
        base_name = converter.Validate(base_name).sanitize_url()

        asset_name = f'{base_name}{ext}'
        original_name = asset_name
        counter = 2
        while asset_name in used_names:
            asset_name = f'{base_name}_{counter}{ext}'
            counter += 1

        used_names.add(asset_name)

        local_path = Path('assets') / asset_name
        full_path = website_dir / local_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if ext == '.css':
            try:
                css_text = response.text
                css_text = self.localize_css_assets(css_text, asset_url, website_dir, used_names, stats, is_external_css=True)
                full_path.write_text(css_text, encoding='utf-8', errors='ignore')

            except Exception:
                full_path.write_bytes(response.content)
        else:
            full_path.write_bytes(response.content)

        stats['downloaded'] += 1
        
        return local_path.as_posix()

    def localize_asset(self, asset_url, website_dir, used_names, stats):
        if not asset_url or asset_url.startswith(('data:', 'mailto:', 'tel:', '#')):
            return None

        absolute_url = urljoin(self.url, asset_url)
        parsed = urlparse(absolute_url)

        if parsed.scheme not in ('http', 'https'):
            return None

        if absolute_url in self.downloaded_absolute_urls:
            local_name = self.downloaded_absolute_urls[absolute_url]

            if local_name:
                return f'assets/{local_name}'

            return None

        local_path_str = self.download_asset(absolute_url, website_dir, used_names, stats)

        if local_path_str:
            filename = Path(local_path_str).name
            self.downloaded_absolute_urls[absolute_url] = filename
            
            return local_path_str

        self.downloaded_absolute_urls[absolute_url] = None
        
        return None

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

        for tag in soup.find_all('style'):
            if tag.string:
                tag.string = self.localize_css_assets(tag.string, self.url, website_dir, used_names, stats, is_external_css=False)

        for tag in soup.find_all(True):
            if tag.has_attr('style'):
                style_content = tag['style']
                tag['style'] = self.localize_css_assets(style_content, self.url, website_dir, used_names, stats, is_external_css=False)

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

        self.url = response.url
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
from commands.main.get import GetWebsite
from commands.clear import Clear
from commands.exit import Exit
from commands.networking.get import GetRequest
from commands.networking.post import PostRequest
from commands.networking.dns_lookup import DNSLookup
from commands.networking.headers import CheckHeaders
from commands.networking.ping import CheckPing
from utils.parser import CommandParser
from utils.http_formatter import format_parsed_response
from utils.request_builder import RequestBuilder
from urllib.parse import urljoin

class ExecuteMainCommands:
    def __init__(self, command, help_msg):
        self.command = command
        self.help_msg = help_msg

    def parse_get_command(self):
        parser = CommandParser(self.command)
        parsed, error = parser.parse()

        if error:
            return None, None, None, error

        command_name, args = parsed

        if len(args) < 1:
            return None, None, None, 'Please provide a URL after the \'get\' command.'

        url = args[0]
        option_args = args[1:]
        save_option = 'both'
        download_assets = False

        while option_args:
            option = option_args.pop(0).lower()

            if option in ('--assets', '-a'):
                download_assets = True
            elif option in ('--save', '-s'):
                if not option_args:
                    return None, None, None, 'Use get <URL> [md|html|both] [--assets] or get <URL> --save [md|html|both] [--assets].'

                save_option = option_args.pop(0).lower()
            elif option.removeprefix('--') in ('md', 'html', 'both'):
                save_option = option.removeprefix('--')
            else:
                return None, None, None, 'Use get <URL> [md|html|both] [--assets] or get <URL> --save [md|html|both] [--assets].'

        if save_option not in ('md', 'html', 'both'):
            return None, None, None, 'Save option must be md, html, or both.'

        if download_assets and save_option == 'md':
            return None, None, None, 'Asset downloading requires html or both.'

        return url, save_option, download_assets, None

    def execute(self):
        command_name = self.command.split(maxsplit=1)[0].lower() if self.command else ''

        if command_name == 'get':
            url, save_option, download_assets, error = self.parse_get_command()

            if error:
                return error
            
            get_website = GetWebsite(url, save_option, download_assets)
            return get_website.get()

        elif command_name == 'clear':
            clear = Clear(self.help_msg)
            clear.execute()
        
        elif command_name == 'exit':
            exit = Exit()
            exit.execute()

        elif command_name == 'return':
            return 'return'

        elif self.command:
            return 'Unknown command. Use get <URL> [md|html|both] [--assets], clear, return, or exit.'
        
class ExecuteHTTPCommands:
    REDIRECT_STATUSES = {301, 302, 303, 307, 308}
    MAX_REDIRECTS = 5

    def __init__(self, command, help_msg):
        self.command = command
        self.help_msg = help_msg

    def parse_command(self):
        parser = CommandParser(self.command)
        parsed, error = parser.parse()

        if error:
            return None, None, error

        command_name, args = parsed
        return command_name, args, None

    def get_status_code(self, response):
        status_line = response.get('headers', '').splitlines()[0:1]

        if not status_line:
            return None

        parts = status_line[0].split()

        if len(parts) < 2:
            return None

        try:
            return int(parts[1])
        except ValueError:
            return None

    def get_header(self, response, header_name):
        target = header_name.lower()

        for header in response.get('headers', '').splitlines()[1:]:
            name, separator, value = header.partition(':')

            if separator and name.strip().lower() == target:
                return value.strip()

        return None

    def get_response(self, url):
        current_url = url
        visited_urls = set()
        redirects = []

        while True:
            try:
                builder = RequestBuilder(current_url)
            except ValueError as e:
                return None, str(e)

            base_url = builder.url.geturl()

            if base_url in visited_urls:
                return None, f'Redirect loop detected at {base_url}.'

            visited_urls.add(base_url)
            request = builder.build_get_request()
            client = GetRequest(builder.host, builder.port, builder.secure)
            response = client.send_and_receive(request)

            status_code = self.get_status_code(response)

            if status_code not in self.REDIRECT_STATUSES:
                response['redirects'] = redirects
                response['final_url'] = base_url
                return response, None

            location = self.get_header(response, 'Location')

            if not location:
                response['redirects'] = redirects
                response['final_url'] = base_url
                return response, None

            current_url = urljoin(base_url, location)

            if len(redirects) >= self.MAX_REDIRECTS:
                blocked_redirect = (status_code, base_url, current_url)
                return None, self.format_redirect_limit_error(redirects, blocked_redirect)

            redirects.append((status_code, base_url, current_url))

    def format_redirect_limit_error(self, redirects, blocked_redirect):
        lines = [f'Too many redirects. Stopped after {self.MAX_REDIRECTS} redirects.']

        for status_code, source_url, target_url in redirects:
            lines.append(f'  HTTP {status_code}: {source_url} -> {target_url}')

        status_code, source_url, target_url = blocked_redirect
        lines.append(f'  Blocked HTTP {status_code}: {source_url} -> {target_url}')

        return '\n'.join(lines)

    def execute(self):
        command_name, args, error = self.parse_command()

        if error:
            return error

        if command_name == 'get':
            if len(args) != 1:
                return 'Please provide exactly one url for get.'
            
            url = args[0]
            response, error = self.get_response(url)

            if error:
                return error

            return f'\n{format_parsed_response(response)}\n'
        
        elif command_name == 'post':
            if len(args) < 2:
                return 'Use post <URL> key=value [key=value ...].'

            url = args[0]
            post_args = args[1:]
            post = PostRequest(url, post_args)
            response = post.post_request()

            return f'\n{response}\n'

        elif command_name == 'dns_lookup':
            if len(args) != 1:
                return 'Please provide exactly one url for dns_lookup.'

            url = args[0]
            dns_lookup = DNSLookup(url)
            return dns_lookup.execute()
        
        elif command_name == 'headers':
            if len(args) != 1:
                return 'Please provide exactly one url for headers.'
            
            url = args[0]
            headers = CheckHeaders(url)
            return headers.execute()
        
        
        elif command_name == 'ping':
            if len(args) != 1:
                return 'Please provide exactly one url for ping.'
            
            url = args[0]
            ping = CheckPing(url)
            return ping.execute()
        
        elif command_name == 'clear':
            clear = Clear(self.help_msg)
            clear.execute()

        elif command_name == 'exit':
            exit = Exit()
            exit.execute()

        elif command_name == 'return':
            return 'return'

        elif self.command:
            return 'Unknown command. Use get <URL>, post <URL> key=value [key=value ...], dns_lookup <URL>, headers <URL>, ping <URL>, clear, return, or exit.'
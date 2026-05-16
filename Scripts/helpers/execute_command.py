from commands.get import GetWebsite
from commands.clear import Clear
from commands.exit import Exit
import shlex

class ExecuteCommand:
    def __init__(self, command, help_msg):
        self.command = command
        self.help_msg = help_msg

    def parse_get_command(self):
        try:
            parts = shlex.split(self.command)
        except ValueError as e:
            return None, None, f'Could not parse command: {e}'

        if len(parts) < 2:
            return None, None, 'Please provide a URL after the \'get\' command.'

        url = parts[1]
        option_parts = parts[2:]
        save_option = 'both'

        if len(option_parts) == 1:
            save_option = option_parts[0].lower().removeprefix('--')
        elif len(option_parts) == 2 and option_parts[0].lower() in ('--save', '-s'):
            save_option = option_parts[1].lower()
        elif len(option_parts) > 0:
            return None, None, 'Use get <URL> [md|html|both] or get <URL> --save [md|html|both].'

        if save_option not in ('md', 'html', 'both'):
            return None, None, 'Save option must be md, html, or both.'

        return url, save_option, None

    def execute(self):
        command_name = self.command.split(maxsplit=1)[0].lower() if self.command else ''

        if command_name == 'get':
            url, save_option, error = self.parse_get_command()

            if error:
                return error
            
            get_website = GetWebsite(url, save_option)
            return get_website.get()

        elif command_name == 'clear':
            clear = Clear(self.help_msg)
            clear.execute()
        
        elif command_name == 'exit':
            exit = Exit()
            exit.execute()

        elif self.command:
            return 'Unknown command. Use get <URL> [md|html|both], clear, or exit.'
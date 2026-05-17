import shlex

class CommandParser:
    def __init__(self, command):
        self.command = command

    def parse(self):
        try:
            parts = shlex.split(self.command)
        except ValueError as e:
            return None, f'Could not parse command: {e}'

        if not parts:
            return None, 'No command entered.'

        command_name = parts[0].lower()
        args = parts[1:]

        return (command_name, args), None
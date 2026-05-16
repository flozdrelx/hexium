import os

class Clear:
    def __init__(self, help_msg):
        self.help_msg = help_msg

    def execute(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
        print(self.help_msg)
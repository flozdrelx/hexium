from helpers.execute_command import ExecuteHTTPCommands, ExecuteMainCommands
from commands.exit import Exit
import os

os.system('cls' if os.name == 'nt' else 'clear')

START_MSG = '''Welcome to Hexium Browser Prototype V0.03!

To get started, select a browsing mode:
    1. Download Website
    2. Send HTTP Request [BETA]

Or use 'exit' to exit the browser.
    '''

DOWNLOAD_MODE_MSG = '''You are now in Download Website mode:

    * Use get <URL> [md|html|both] [--assets] to download a website.
    * Use \'clear\' to clear the console.
    * Use \'return\' to return to the mode selection menu.
    * Use \'exit\' to exit the browser.
            '''

HTTP_MODE_MSG = '''You are now in HTTP Request mode:

    * Use \'get <URL>\' to send a get request to the specified URL.
    * Use \'post <URL> key=value [key=value ...]\' to send form data to the specified URL.
    * Use \'ping <URL>\' to check the website\'s ping.
    * Use \'dns_lookup <URL>\' to perform a DNS lookup for the specified URL.
    * Use \'headers <URL>\' to view the headers of the specified URL.
    * Use \'clear\' to clear the console.
    * Use \'return\' to return to the mode selection menu.
    * Use \'exit\' to exit the browser.
            '''

def run_mode(executor_class, mode_msg):
    print()
    print(mode_msg)

    while True:
        command = input('>>> ').strip()

        if not command:
            continue

        executor = executor_class(command, mode_msg)
        result = executor.execute()

        if result == 'return':
            print(f'\n{START_MSG}')
            break

        if result:
            print(result)

def main():
    print(START_MSG)

    while True:
        option = input('>>> ').strip().lower()
        
        if option == '1':
            run_mode(ExecuteMainCommands, DOWNLOAD_MODE_MSG)

        elif option == '2':
            run_mode(ExecuteHTTPCommands, HTTP_MODE_MSG)

        elif option == 'exit':
            exit = Exit()
            exit.execute()

        else:
            print('Please select 1, 2, or exit.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nExiting Hexium Browser. Goodbye!')
    except Exception as e:
        print(f'An error occurred: {e}')
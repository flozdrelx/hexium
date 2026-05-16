from helpers.execute_command import ExecuteCommand
import os

os.system('cls' if os.name == 'nt' else 'clear')

def main():
    start_msg = '''Welcome to Hexium Browser Prototype V0.02!

    * Use \'get <URL> [md|html|both]\' to fetch and save a website.
    * Use \'clear\' to clear the console.
    * Use \'exit\' to quit the application.
    '''

    print(start_msg)

    while True:
        command = input('>>> ').strip()
        execute_command = ExecuteCommand(command, start_msg)
        result = execute_command.execute()

        if result:
            print(result)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nExiting Hexium Browser. Goodbye!')
    except Exception as e:
        print(f'An error occurred: {e}')
from models import *
import inquirer
from helpers import *
from pyfiglet import Figlet
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme


## Begin workflow
if __name__ == '__main__':
    f = Figlet(font='slant')
    console = Console()
    console.print(f.renderText('TermiJob'), highlight=False, )   
    user_list = User.show_all()
    if len(user_list) == 0:
        register_user()
    else:
        start_path = [
                inquirer.List('start',
                        message="Welcome to TermiJob!  Are you a returning user?",
                        choices=['Yes', 'No']
                    )
        ]
        answers = inquirer.prompt(start_path)

        if answers['start'] == "No":
            register_user()
        elif answers['start'] == "Yes":
            user = returning_user()
            main_menu(user)


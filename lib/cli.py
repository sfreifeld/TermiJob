from models import *
import inquirer
from helpers import *
from pyfiglet import Figlet



if __name__ == '__main__':
    f = Figlet(font='slant')
    print(f.renderText('TermiJob'))   
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


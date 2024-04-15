from models import *
import inquirer
import requests
import sqlite3
import json
import animation
import time
import sys
import csv
from datetime import datetime
from jobspy import scrape_jobs
from rich import print
from rich.console import Console
from rich.table import Table
import pandas as pd
from pyfiglet import Figlet



def register_user():
    while True:
        print("Let's get you registered!\n")
        name = input("What is your name?\n")
        print(f"\nNice to meet you [bright_magenta]{name}[/bright_magenta]!")
        while True:
            email = input("What is your email?\n")
            if "@" in email:
                break
            else:
                print("\nPlease enter a valid email address.")
        

        confirmation = [
            inquirer.List('confirm',
                          message=f"\n\nIs this information correct?\n Name: {name} \n Email: {email}\n",
                          choices = ['Yes', 'No']
                        )
        ]
        confirm_answers = inquirer.prompt(confirmation)

        if confirm_answers['confirm'] == "Yes":
            new_user = User(name, email)
            new_user.create()
            print(f"Thanks [bright_magenta]{name}[/bright_magenta], you've now been registered!")
            set_user_preferences(new_user,False)
            main_menu(new_user)
        else:
            print("That's ok! Let's try this again.\n")


def returning_user():
    user_list = User.show_all()
    choices = [(user.name, user) for user in user_list]
    user_selection = [
            inquirer.List('select',
                          message=f"Welcome back!  Which user are you?",
                          choices = choices
                        )
        ]
    selected_user = inquirer.prompt(user_selection)['select']
    print(f"Hi there [bright_magenta]{selected_user.name}[/bright_magenta]!")
    return(selected_user)


def main_menu(user):
    main_menu = [
            inquirer.List('menu_option',
                          message=f"What would you like to do today?",
                          choices = [('Read Instructions',1),('Update User Preferences',2), ('View/Edit Keywords',3), ('Job Search!',4),('View Saved Jobs',5),('Delete Account',6),('Exit',7)]
                        )
        ]
    menu_selection = inquirer.prompt(main_menu)['menu_option']
    if menu_selection == 1:
        read_instructions(user)
    elif menu_selection == 2:
        set_user_preferences(user, True)
    elif menu_selection == 3:
        view_user_keywords(user)
    elif menu_selection == 4:
        keyword_choice = job_search(user)
        job_scraper(user, keyword_choice)
    elif menu_selection == 5:
        view_saved_jobs(user)
    elif menu_selection == 6:
        delete_account(user)
    elif menu_selection == 7:
        sys.exit()
        

def read_instructions(user):
    f = Figlet(font='slant')
    console = Console()
    console.print(f.renderText('TermiJob'), highlight=False, ) 
    print("TermiJob is your cli solution to the stress of jobhunting.  You will be able to aggregate a list of perfect jobs for you, without having to dredge through dozens of job boards!\n")
    print("[bold bright_magenta]INSTRUCTIONS[bold bright_magenta]")
    print("1. Register a user account and set your user preferences")
    print("2. Create a keyword that you want to use for job search")
    print("[italic]Ex: python, software engineer, adtech[/italic]")
    print("3. Select the Job Search! option and pick which keyword you would like to use")
    print("4 Select the View Saved Jobs button to see a list of your saved jobs or export them.")
    print("\nThat's it - you're done!\n")

    input("Press Enter to return to the main menu")
    main_menu(user)




def set_user_preferences(user, is_update):
    print("Let's get your job preferences set up.\n")
    remote_question = [
        inquirer.List('remote',
                      message="What is your preferred job location mode?",
                      choices=['Remote', 'In Person', 'Hybrid'])
    ]
    remote_answer = inquirer.prompt(remote_question)

    if remote_answer['remote'] != 'Remote':
        location_question = [
            inquirer.Text('location',
                          message="Where would you like to work? Please input as 'City, State Abbreviation'")
        ]
        location_answer = inquirer.prompt(location_question)
    else:
        location_answer = {'location': 'USA'}

    experience_level_question = [
        inquirer.List('experience_level',
                      message="What is your experience level?",
                      choices=["Entry", "Senior", "Executive"])
    ]
    experience_level_answer = inquirer.prompt(experience_level_question)

    preferences_answer = {**remote_answer, **location_answer, **experience_level_answer}

    new_user_preference = UserPreferences(preferences_answer['remote'], preferences_answer.get('location', ''), preferences_answer['experience_level'], user.id)
    if not is_update:
        new_user_preference.save_preferences()
        print("Your preferences have been set!")
        main_menu(user)
    else:
        new_user_preference.update_preferences()
        print("Your preferences have been updated!")
        main_menu(user)


def view_user_keywords(user):
    print("A keyword is a word that you would like your job search to use.")
    print("This could be a skill, job title, industry, ect")
    print("[italic]Examples: Python, software engineer, adtech[/italic]")
    print("\nHere is a list of your keywords:")
    keyword_list = Keyword.show_all_by_user(user.id)
    if len(keyword_list) == 0:
        print("[red]No keywords created yet.[/red]\n")
    for key in keyword_list:
        print(f'[bright_magenta]{key.keyword}[/bright_magenta]')
    keyword = input("\nPlease enter a new keyword, or press enter to go back to the main menu\n")
    if keyword == "":
        main_menu(user)
    else:
        new_keyword = Keyword(keyword, user.id)
        new_keyword.create()
        print(f"\n '[bright_magenta]{new_keyword.keyword}[/bright_magenta]' has been added to your keyword list!")
        main_menu(user)


def job_search(user):
    keyword_items = Keyword.show_all_by_user(user.id)
    choices  = [keyword.keyword for keyword in keyword_items]
    keyword_selection = [
    inquirer.List('keyword',
                    message="Which keywords would you like to use for your search?",
                    choices= choices,
                    ),
]
    answers = inquirer.prompt(keyword_selection)
    return answers["keyword"]


def job_scraper(user, keyword):

    connection = sqlite3.connect("./db/mydatabase.db")
    user1 = user.get_preferences()
    print(user1.id)
    print(f"remote: {user1.remote}")
    print(f"location:{user1.location}")

    jobs = scrape_jobs(
        site_name=["indeed", "glassdoor"],
        search_term=keyword,
        location=user1.location,
        results_wanted=20,
        hours_old=96,
        country_indeed='USA'
    )

    print(jobs.head())
    
    dropped_columns=['job_url_direct','currency','emails','company_addresses','company_revenue','company_description','logo_photo_url','banner_photo_url','ceo_name','ceo_photo_url']
    jobs = jobs.drop_duplicates(subset=['title','company'], keep='first')
    print(jobs.head())
    filtered_jobs = job_filter(user, jobs)
    print(f"Congrats! Found {len(filtered_jobs)} jobs")
    filtered_jobs =filtered_jobs.drop(dropped_columns, axis=1)
    filtered_jobs['user_id']= user.id
    filtered_jobs.to_sql('jobrecords', connection, if_exists='append', index=False)
    main_menu(user)


def job_filter(user, dataframe) :
    user1 = user.get_preferences()
    regex_pattern = ""

    print(f'exp level: {user1.experience_level}')

    if user1.experience_level == "Entry":
        words_to_exclude = ["Senior", "Manager", "Director","Sr.", "Staff", "Lead", "Principal", "III", "IV"]
        regex_pattern = '|'.join(words_to_exclude)
    elif user1.experience_level == "Senior":
        words_to_exclude = ["Jr.", "Junior","Director"]
        regex_pattern = '|'.join(words_to_exclude)
    elif user1.experience_level == "Executive":
        words_to_exclude = ["Jr.", "Junior","Senior","Sr.","III", "II", "IV"]
        regex_pattern = '|'.join(words_to_exclude)

    filtered_dataframe = dataframe[~dataframe['title'].str.contains(regex_pattern, case=False, na=False)]

    if user1.remote == "Remote":
        filtered_dataframe = filtered_dataframe[filtered_dataframe['is_remote'] == True]
    elif user1.remote == "In Person":
        filtered_dataframe = filtered_dataframe[filtered_dataframe['is_remote'] == False]
    return filtered_dataframe




def delete_account(user):
    delete_account_confirmation = [
    inquirer.List('confirmation',
                    message="Are you sure you want to delete your account?  This action cannot be reversed.",
                    choices= [("Yes I'm Sure",1), ("No, I changed my mind",2)]
                    ),
]
    delete_account_response = inquirer.prompt(delete_account_confirmation)
    if delete_account_response["confirmation"] == 2:
        main_menu(user)
    elif delete_account_response["confirmation"] == 1:
        user.delete()
        print(f"[bright_magenta]{user.name}[/bright_magenta] has been deleted.")
        sys.exit()


def view_saved_jobs(user):
    jobs = user.show_jobs_by_user()
    print(f"You have {len(jobs)} saved jobs\n")
    console = Console()
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Job Title")
    table.add_column("Company")
    for job in jobs:
        table.add_row(
            job.title,
            job.company
        )
    console.print(table)
    export_option = [
    inquirer.List('export',
                    message="Would you like to export this list?",
                    choices= [("Yes",1), ("No",2)]
                    ),
]
    export_option_response = inquirer.prompt(export_option)
    if export_option_response["export"] == 1:
        jobs_df = pd.DataFrame([job.__dict__ for job in jobs])
        currentDateTime = datetime.now().strftime("%m-%d-%Y")
        jobs_df.to_csv(f'./outputs/output{currentDateTime}.csv', header=True, index=False)
        main_menu(user)
    elif export_option_response["export"] == 2:
        main_menu(user)

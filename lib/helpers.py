from models import *
import inquirer
import requests
import sqlite3
import json
import animation
import time
import sys
import csv
from jobspy import scrape_jobs
from rich import print
from rich.console import Console
from rich.table import Table


def register_user():
    while True:
        print("Let's get you registered!\n")
        name = input("What is your name?\n")
        print(f"\nNice to meet you [bright_magenta]{name}[/bright_magenta]!")
        email = input("What is your email?\n")
        print("\nGreat! Almost there.")
        apikey = input("Please give us your linkedin api key.\n")

        confirmation = [
            inquirer.List('confirm',
                          message=f"\n\nIs this information correct?\n Name: {name} \n Email: {email} \n Api Key: {apikey}\n",
                          choices = ['Yes', 'No']
                        )
        ]
        confirm_answers = inquirer.prompt(confirmation)

        if confirm_answers['confirm'] == "Yes":
            new_user = User(name, email, apikey)
            new_user.create()
            print(f"Thanks [bright_magenta]{name}[/bright_magenta], you've now been registered!")
            set_user_preferences(new_user)
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
                          choices = [('Update user preferences',1), ('View/Edit Keywords',2), ('Make a job search!',3),('View Saved Jobs',4),('Delete Account',5),('Exit',6)]
                        )
        ]
    menu_selection = inquirer.prompt(main_menu)['menu_option']
    if menu_selection == 1:
        update_user_preferences(user)
    elif menu_selection == 2:
        view_user_keywords(user)
    elif menu_selection == 3:
        keyword_choice = job_search(user)
        scrape_jobs(user, keyword_choice)
    elif menu_selection == 4:
        view_saved_jobs(user)
    elif menu_selection == 5:
        delete_account(user)
    elif menu_selection == 6:
        sys.exit()
        



def set_user_preferences(user):
    print("Let's get your job preferences set up.\n")
    user_preferences = [
            inquirer.List('remote',
                          message=f"Would you like jobs that are remote or in person/hybrid?",
                          choices = [('Remote'), ('In Person'), ('Hybrid')]
                        )
        ]
    preferences_answer = inquirer.prompt(user_preferences)
    new_user_preference = UserPreferences(user.id, preferences_answer['remote'])
    new_user_preference.save_preferences()
    print("Your preferences have been set!")

def update_user_preferences(user):
    user_preferences = [
            inquirer.List('remote',
                          message=f"Would you like jobs that are remote or in person/hybrid?",
                          choices = [('Remote'), ('In Person'), ('Hybrid')]
                        )
        ]
    preferences_answer = inquirer.prompt(user_preferences)
    updated_user_preference = UserPreferences(preferences_answer['remote'],user.id)
    updated_user_preference.update_preferences()
    print("Your preferences have been updated!")
    main_menu(user)


def view_user_keywords(user):
    print("A keyword is a word that you would like your job search to use.")
    print("This could be a skill, job title, industry, ect")
    print("[italic]Examples: Python, software engineer, adtech[/italic]")
    print("\nHere is a list of your keywords:")
    keyword_list = Keyword.show_all_by_user(user.id)
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

    jobs = scrape_jobs(
        site_name="indeed", #change to add glassdoor when working
        search_term=keyword,
        location="Denver, CO",
        results_wanted=20,
        hours_old=96,
        country_indeed='USA'
    )
    
    dropped_columns=['job_url_direct','currency','emails','company_addresses','company_revenue','company_description','logo_photo_url','banner_photo_url','ceo_name','ceo_photo_url']
    jobs = jobs.drop_duplicates(subset=['title','company'], keep='first')
    print(f"Congrats! Found {len(jobs)} jobs")
    jobs =jobs.drop(dropped_columns, axis=1)
    jobs['user_id']= user.id
    jobs.to_sql('jobrecords', connection, if_exists='append', index=False)
    main_menu(user)



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
    print("Would you like to export this list?")
    sys.exit()

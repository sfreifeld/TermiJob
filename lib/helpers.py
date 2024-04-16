from models import *
import inquirer
import sqlite3
import sys
from datetime import datetime
from jobspy import scrape_jobs
from rich import print
from rich.console import Console
from rich.table import Table
import pandas as pd
from pyfiglet import Figlet
from alive_progress import alive_bar
import time 



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
                          message=f"\n\nIs this information correct?\n Name: {name} \n Email: {email}",
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
    return(selected_user)


def main_menu(user):
    print(f"Hi there [bright_magenta]{user.name}[/bright_magenta]!\n")
    print(f"Currently, there are [bright_green]{user.count_jobrecords('Not Applied')}[/bright_green] job opportunities available for application. In total, you have applied to [bright_green]{user.count_jobrecords('Applied')}[/bright_green] jobs.\n")
    main_menu = [
            inquirer.List('menu_option',
                          message=f"What would you like to do today?",
                          choices = [('Read Instructions',1),('Update User Preferences',2), ('View/Add Keywords',3), ('Job Search!',4),('View Saved Jobs',5),('Mark Jobs As Applied',6),('Delete Account',7),('Exit',8)]
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
        if keyword_choice:
            job_scraper(user, keyword_choice)
    elif menu_selection == 5:
        view_saved_jobs(user)
    elif menu_selection == 6:
        mark_as_applied(user)
    elif menu_selection == 7:
        delete_account(user)
    elif menu_selection == 8:
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
    print("5 Make sure to click the Mark Jobs As Applied option to keep track of which jobs you've applied for .")
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
    if len(keyword_items) == 0:
        print("\nYou don't have any keywords to use.  Please select the [bold bright_magenta] View/Create Keywords [/bold bright_magenta] option from the main menu to make a job search.\n")
        input("Press enter to go back to the main menu.")
        main_menu(user)
    choices  = [keyword.keyword for keyword in keyword_items]
    keyword_selection = [
        inquirer.List('keyword',
                      message="Which keywords would you like to use for your search?",
                      choices=choices,
                      ),
    ]
    answers = inquirer.prompt(keyword_selection)
    return answers["keyword"]


def job_scraper(user, keyword):

    connection = sqlite3.connect("./db/mydatabase.db")
    user1 = user.get_preferences()


    with alive_bar( title="Fetching jobs...", spinner=None, unknown="waves", monitor=False, elapsed=False, stats=False) as bar:
        jobs = scrape_jobs(
            site_name=["indeed", "glassdoor"],
            search_term=keyword,
            location=user1.location,
            results_wanted=20,
            hours_old=96,
            country_indeed='USA',
            verbose=0
        )


        dropped_columns=['job_url_direct','currency','emails','company_addresses','company_revenue','company_description','logo_photo_url','banner_photo_url','ceo_name','ceo_photo_url']
        jobs = jobs.drop_duplicates(subset=['title','company'], keep='first')
        filtered_jobs = job_filter(user, jobs)
        filtered_jobs =filtered_jobs.drop(dropped_columns, axis=1)
        filtered_jobs['user_id']= user.id
        filtered_jobs['applied'] = "Not Applied"

        bar()

    connection = sqlite3.connect("./db/mydatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT title, company FROM jobrecords")
    existing_jobs = cursor.fetchall()
    existing_jobs_df = pd.DataFrame(existing_jobs, columns=['title', 'company'])
    new_jobs = pd.merge(filtered_jobs, existing_jobs_df, on=['title', 'company'], how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
    if not new_jobs.empty:
        new_jobs.to_sql('jobrecords', connection, if_exists='append', index=False)
        print(f"\nCongrats!  You have saved {len(new_jobs)} new jobs.\n")
        job_titles = [f"{row['title']} at {row['company']}" for index, row in new_jobs.iterrows()]
        deselect_question = [
            inquirer.Checkbox('deselect_jobs',
                          message="Select any jobs you do not wish to apply for (use Space to select, Enter to confirm):",
                          choices=job_titles,
                          ),
    ]
        deselected_jobs_answers = inquirer.prompt(deselect_question)['deselect_jobs']
        deselected_jobs = new_jobs[new_jobs.apply(lambda row: f"{row['title']} at {row['company']}" in deselected_jobs_answers, axis=1)]

        # Remove deselected jobs from the database
        for index, row in deselected_jobs.iterrows():
            cursor.execute("UPDATE jobrecords SET applied = 'trashed' WHERE title = ? AND company = ?", (row['title'], row['company']))
        connection.commit()
    else:
        print("\n[red]Sorry, no new jobs to insert.[/red]\n")
    
    main_menu(user)


def job_filter(user, dataframe) :
    user1 = user.get_preferences()
    regex_pattern = ""

    if user1.experience_level == "Entry":
        words_to_exclude = ["Senior", "Manager", "Director","Sr.", "Staff", "Lead", "Principal", "III", "IV","Chief"]
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
    job_options = [
    inquirer.List('options',
                    message="Which jobs would you like to view? Applied, not applied, or all?",
                    choices= [("Applied",1), ("Not Applied",2), ("All",3)]
                    ),
    ]
    job_options_response = inquirer.prompt(job_options)
    if job_options_response["options"] == 1:
        jobs = user.show_jobs_by_user('applied')
    elif job_options_response["options"] == 2:
        jobs = user.show_jobs_by_user('not applied')
    elif job_options_response["options"] == 3:
        jobs = user.show_jobs_by_user('both')
        


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
        currentDateTime = datetime.now().strftime("%m-%d-%Y-%m")
        jobs_df.to_csv(f'./outputs/output{currentDateTime}.csv', header=True, index=False)
        main_menu(user)
    elif export_option_response["export"] == 2:
        main_menu(user)


def mark_as_applied(user):
    jobs = user.show_jobs_by_user("both")
    if not jobs:
        print("You have no saved jobs to mark as applied.")
        return

    print(f"You have {len(jobs)} saved jobs\n")
    job_titles = [f"{job.title} at {job.company}" for job in jobs]

    # Ask if the user wants to select all jobs
    select_all_question = [
        inquirer.Confirm('select_all',
                         message="Do you want to mark all jobs as applied?",
                         default=False),
    ]
    select_all_answer = inquirer.prompt(select_all_question)
    
    if select_all_answer['select_all']:
        for job in jobs:
            job.applied = "Applied"  # Set the applied attribute to "Applied"
            job.update()  # Call the update method to save the change in the database
        print(f"Marked {len(jobs)} job(s) as applied.")
    else:
        # If not selecting all, let the user choose jobs individually
        apply_question = [
            inquirer.Checkbox('applied_jobs',
                              message="Select the jobs you've applied to (Space to select, Enter to confirm):",
                              choices=job_titles,
                              ),
        ]
        applied_jobs_answers = inquirer.prompt(apply_question)['applied_jobs']
        applied_jobs = [job for job in jobs if f"{job.title} at {job.company}" in applied_jobs_answers]
        
        for job in applied_jobs:
            job.applied = "Applied"  # Set the applied attribute to "Applied"
            job.update()
        # Here, update the selected jobs as applied in your data structure or database
        print(f"Marked {len(applied_jobs)} job(s) as applied.")

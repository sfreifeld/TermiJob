import csv
from jobspy import scrape_jobs
import sqlite3
import pandas as pd

connection = sqlite3.connect("./db/mydatabase.db")

df = pd.read_csv('jobs.csv')
dropped_columns=['job_url_direct','currency','emails','company_addresses','company_revenue','company_description','logo_photo_url','banner_photo_url','ceo_name','ceo_photo_url']
df=df.drop(dropped_columns, axis=1)
df['user_id']=16
df = df.drop_duplicates(subset=['title','company'], keep='first')
df.to_sql('jobrecords', connection, if_exists='append', index=False)
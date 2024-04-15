import sqlite3
connection = sqlite3.connect("./db/mydatabase.db")
cursor = connection.cursor()
from alive_progress.styles import showtime


class User:
    def __init__(self, name, email, apikey, id = None):
        self.id = id
        self.name = name
        self.email = email
        self.apikey = apikey

    def create(self):
        cursor.execute('''
        INSERT INTO users(name, email, apikey)
        VALUES (?,?,?)
        ''',
        (self.name, self.email, self.apikey))
        self.id = cursor.lastrowid  # Get the last inserted id
        connection.commit()
        

    @classmethod
    def show_all(self):
        selections = cursor.execute('''
        SELECT * FROM users;
        ''').fetchall()
        user_list = []
        for item in selections:
            user = User(item[1],item[2],item[3],item[0])
            user_list.append(user)
        return user_list
    
    def delete(self):
        cursor.execute(f'''
        DELETE FROM users
        WHERE id = {self.id};
        ''')
        connection.commit()
        cursor.execute(f'''
        DELETE FROM userpreferences
        WHERE user_id = {self.id};
        ''')
        connection.commit()
        cursor.execute(f'''
        DELETE FROM keywords
        WHERE user_id = {self.id};
        ''')
        connection.commit()

    def show_jobs_by_user(self):
        job_records = cursor.execute('''
        SELECT * FROM jobrecords
        WHERE user_id = ?
        ''', (self.id,)).fetchall()
        jobs_list = []
        for item in job_records:
            job = Jobrecord(item[1],item[2], item[3], item[4],item[5], item[6], item[7],item[8], item[9], item[10],item[11], item[12],item[13], item[14], item[15],item[16], item[17],item[0])
            jobs_list.append(job)
        return jobs_list

        
class UserPreferences:
    def __init__(self, remote, user_id, id = None):
        self.id = id
        self.remote = remote
        self.user_id = user_id

    def save_preferences(self):
        user_preferences = cursor.execute('''
        INSERT INTO userpreferences(remote, user_id)
        VALUES (?,?)''', (self.remote, self.user_id))
        connection.commit()

    def update_preferences(self):
        user_preferences = cursor.execute('''
        UPDATE userpreferences
        SET remote = ?
        WHERE user_id = ?
        ''', (self.remote, self.user_id))
        connection.commit()


class Keyword:
    def __init__(self, keyword, user_id, id = None):
        self.id = id
        self.keyword = keyword
        self.user_id = user_id



    def create(self):
        cursor.execute('''
        INSERT INTO keywords(keyword, user_id)
        VALUES (?,?)
        ''',
        (self.keyword, self.user_id)).fetchone()
        connection.commit()


    @classmethod
    def show_all_by_user(cls, user_id):
        keywords = cursor.execute('''
        SELECT * FROM keywords
        WHERE user_id = ?
        ''', (user_id,)).fetchall()
        keywords_list = []
        for item in keywords:
            keyword = Keyword(item[1],item[2], item[0])
            keywords_list.append(keyword)
        return keywords_list


class Jobrecord: #18 params
    def __init__(self, site, job_url, title, company, location, job_type, date_posted, interval, min_amount, max_amount, is_remote, description, company_url, company_url_direct, company_industry, company_num_employees, user_id, id = None):
        self.id = id
        self.site = site
        self.job_url = job_url
        self.title = title
        self.company = company
        self.location = location
        self.job_type = job_type
        self.date_posted = date_posted
        self.interval = interval
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.is_remote = is_remote
        self.description = description
        self.company_url = company_url
        self.company_url_direct = company_url_direct
        self.company_industry = company_industry
        self.company_num_employees = company_num_employees
        self.user_id = user_id

    
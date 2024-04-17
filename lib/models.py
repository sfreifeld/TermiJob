import sqlite3
connection = sqlite3.connect("./db/mydatabase.db")
cursor = connection.cursor()

# full CRUD
class User:
    def __init__(self, name, email, id = None):
        self.id = id
        self.name = name
        self.email = email

    def create(self):
        cursor.execute('''
        INSERT INTO users(name, email)
        VALUES (?,?)
        ''',
        (self.name, self.email))
        self.id = cursor.lastrowid
        connection.commit()

    def update(self):
        pass

    def get_preferences(self):
        preferences_data = cursor.execute('''
        SELECT  id, remote, location, experience_level, user_id
        FROM userpreferences
        WHERE user_id = ?
        ''', (self.id,)).fetchone()
        
        return UserPreferences(preferences_data[1], preferences_data[2], preferences_data[3], preferences_data[4], preferences_data[0])


    @classmethod
    def show_all(cls):
        selections = cursor.execute('''
        SELECT * FROM users;
        ''').fetchall()
        user_list = []
        for item in selections:
            user = User(item[1],item[2],item[0])
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

    def show_jobs_by_user(self, type):
        if type == "applied":
            job_records = cursor.execute('''
            SELECT * FROM jobrecords
            WHERE user_id = ? AND applied = 'Applied'
            ''', (self.id,)).fetchall()
        elif type == "not applied":
            job_records = cursor.execute('''
            SELECT * FROM jobrecords
            WHERE user_id = ? AND applied ='Not Applied'
            ''', (self.id,)).fetchall()
        elif type == "both":
            job_records = cursor.execute('''
            SELECT * FROM jobrecords
            WHERE user_id = ? AND applied in ('Not Applied', 'Applied')
            ''', (self.id,)).fetchall()
        
        jobs_list = []
        for item in job_records:
            job = Jobrecord(item[1],item[2], item[3], item[4],item[5], item[6], item[7],item[8], item[9], item[10],item[11], item[12],item[13], item[14], item[15],item[16], item[17], item[18], item[0])
            jobs_list.append(job)
        return jobs_list
    
    def count_jobrecords(self, type):
        count = cursor.execute('''
        SELECT COUNT(*)
        FROM jobrecords
        WHERE user_id = ?
        AND applied = ?
        ''', (self.id, type,)).fetchone()[0]
        return count

        
class UserPreferences:
    def __init__(self, remote, location, experience_level, user_id, id = None):
        self.id = id
        self.remote = remote
        self.location = location
        self.experience_level = experience_level
        self.user_id = user_id
        

    def save_preferences(self):
        user_preferences = cursor.execute('''
        INSERT INTO userpreferences(remote, location, experience_level, user_id)
        VALUES (?,?,?,?)''', (self.remote, self.location, self.experience_level, self.user_id))
        connection.commit()

    def update_preferences(self):
        user_preferences = cursor.execute('''
        UPDATE userpreferences
        SET remote = ?, location = ?, experience_level = ?
        WHERE user_id = ?
        ''', (self.remote, self.location, self.experience_level, self.user_id))
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
    def __init__(self, site, job_url, title, company, location, job_type, date_posted, interval, min_amount, max_amount, is_remote, description, company_url, company_url_direct, company_industry, company_num_employees, applied, user_id, id = None):
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
        self.applied = applied
        self.user_id = user_id

    def update(self):
        job_applied = cursor.execute('''
        UPDATE jobrecords
        SET applied = ?
        WHERE id = ?
        ''', (self.applied, self.id))
        connection.commit()

    
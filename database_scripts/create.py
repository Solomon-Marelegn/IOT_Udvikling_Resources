import pymysql


def connect(database):
    try:
        connection = pymysql.connect(
            user='user1',
            password = 'test',
            host = '192.168.2.21',
            port=3306,
            database = database)
        print("connected to database")
        return connection
        
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None
    
def create_ratings():
    conn = connect('customer_satisfaction')
    cur = conn.cursor()

    queries = [
        """DROP TABLE IF EXISTS ratings;""",
        """CREATE TABLE ratings (
            id int NOT NULL AUTO_INCREMENT,
            feedback VARCHAR(255) NOT NULL,
            time VARCHAR(255) NOT NULL,
            date VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        );""" 
    ]

    confirmation = input('Reset Database. continue [Y/n]? ')
    if confirmation.lower() in ('y', 'yes'):
        for query in queries:
            cur.execute(query)
        print('successfully created table(s)')

    conn.commit()
    conn.close()

def create_admins():
    conn = connect('users')
    cur = conn.cursor()
    queries = [
        """DROP TABLE IF EXISTS admins;""",
        """CREATE TABLE admins (
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL);""",

        """INSERT INTO admins (username, password) 
        VALUES ('admin', 'test');"""
    ]
    confirmation = input('Reset Database. continue [Y/n]? ')
    if confirmation.lower() in ('y', 'yes'):
        for query in queries:
            cur.execute(query)
        print('successfully created table(s)')

    conn.commit()
    conn.close()
            
create_ratings()
create_admins()        



import pymysql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_to_db(feedback, _time, _date, location):
    conn = pymysql.connect(
    user='user1',
    password = 'test',
    host = '192.168.2.21',
    port=3306,
    database = 'customer_satisfaction')
    cur = conn.cursor()
    query = f"""INSERT INTO ratings (feedback, time, date, location)  
                VALUES('{feedback}', '{_time}', '{_date}', '{location}');"""
    cur.execute(query)
    logger.info(f'Inserted message: {feedback}, {_date}, {_time} {location} to db')
    conn.commit()
    conn.close()






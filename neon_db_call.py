import psycopg2
import credentials
from datetime import datetime

def neon_db_call(line_to_write_csv, now):
    # opens connection to Neon database 
    db_conn = psycopg2.connect(credentials.DATABASE_URL)

    # strftime() method used to create a string
    # representing the current time.
    currentTime = now.strftime("%m/%d/%Y, %H:%M:%S")

    """Insert weather reading into database"""
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO weather_data (id, date_time, temp_f, humidity_percent, pressure_mb, light_lumens) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (
                        line_to_write_csv['id'],
                        currentTime,
                        line_to_write_csv['temperature'],
                        line_to_write_csv['humidity'], 
                        line_to_write_csv['pressure'],
                        line_to_write_csv['light']
                        ))
        
        db_conn.commit()

    #close neon database connection
    db_conn.close()


#testing the function
"""now = datetime.now()

# strftime() method used to create a string
# representing the current time.
currentTime = now.strftime("%m/%d/%Y, %H:%M:%S")

line_to_write_csv = {
    'id' : 9000,
    'currentTime': currentTime,
    'temperature': 89.99, 
    'humidity': 99,
    'pressure': 1000.00,
    'light': 100.00
    }

neon_db_call(line_to_write_csv)"""
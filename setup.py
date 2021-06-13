from dotenv import dotenv_values
import sqlite3

config = dotenv_values('.env')

conn = sqlite3.connect(config['SQLITE_DB_FILE'])
cur = conn.cursor()

cur.execute('''CREATE TABLE Triggers
               (name text, content text, embed text)''')

conn.commit()
conn.close()

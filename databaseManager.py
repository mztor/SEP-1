import sqlite3 as sql

def getRandomVerse():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM verses ORDER BY RANDOM() LIMIT 1")
    verse = cur.fetchone()
    con.close()
    print(verse)
    return verse
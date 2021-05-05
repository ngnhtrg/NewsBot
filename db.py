import sqlite3
import parse


conn = sqlite3.connect('data.db')


def create_tables(cur, conn):
    # Delete old tables, if there are.
    cur.execute('DROP TABLE IF EXISTS topic')
    cur.execute('DROP TABLE IF EXISTS doc')

    # SQL query to create tables
    cur.execute('''
        CREATE TABLE topic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url VARCHAR(255),
            description VARCHAR(255),
            articles TEXT,
            LastUpdateTime DATE
        )''')
    cur.execute('''
        CREATE TABLE doc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(255),
            Heading VARCHAR(255),
            LastUpdateTime DATE,
            text TEXT,
            tags VARCHAR(255)
        )''')

    # Send the current transaction.
    conn.commit()


def add_topics(cur):
    for item in parse.topics:
        cur.execute('''
            INSERT INTO topic
            (name, url, description, articles, LastUpdateTime)
            VALUES (?, ?, ?, ?, ?);''', (
                item[0], item[1], item[2], item[3], item[4]))


def add_docs(cur):
    for item in parse.articles:
        cur.execute('''
            INSERT INTO doc
            (url, Heading, LastUpdateTime, text, tags)
            VALUES (?, ?, ?, ?, ?);''', (
                item[0], item[1], item[2], item[3], item[4]))


with sqlite3.connect('data.db') as conn:
    query_for_doc = '''SELECT Heading
               FROM doc
               ORDER BY LastUpdateTime DESC
               '''
    query_for_topic = '''SELECT name
               FROM topic
               ORDER BY LastUpdateTime DESC
               '''
    cur = conn.cursor()

    create_tables(cur, conn)

    add_topics(cur)
    add_docs(cur)

    cur.execute(query_for_doc)
    cur.execute(query_for_topic)

    conn.commit()

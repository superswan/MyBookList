import requests
import json
import sqlite3
from sqlite3 import Error
from tabulate import tabulate
from imgcat import imgcat

database = r'data/library.db'

sql_create_library_table = """CREATE TABLE IF NOT EXISTS library (
                                        id integer PRIMARY KEY,
                                        isbn text NOT NULL,
                                        title text NOT NULL,
                                        authors text,
                                        date text,
                                        publisher text,
                                        pages integer,
                                        cover text                        
                                    );"""

"""
 FUNCTIONS 
-----------------
"""
def get_book_isbn(isbn):
    isbn = '0-13-110362-8'.strip("-")
    url = 'https://openlibrary.org/api/books?bibkeys=ISBN:'+isbn+'&jscmd=data&format=json'
    r = requests.get(url+isbn)
    response = r.text.replace('var _OLBookInfo = ','')[:-1]
    book_data = json.loads(response)

    book_s = book_data["ISBN:"+isbn]
    title = book_s['title']
    publisher = book_s['publishers'][0]['name']
    authors = book_s['by_statement']
    published_date = book_s['publish_date']
    page_count = book_s['number_of_pages']
    img_url = book_s['cover']['medium']
    img = requests.get(img_url).content
    #imgcat(img, height=7)


def connect_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
        print(f"sqlite version: {sqlite3.version}")
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn 

def create_table(conn, create_table_sql):
    try:
        c =  conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_book(conn, book_details):
    sql = ''' INSERT INTO library(isbn, title, authors, date, publisher, pages, cover)
              VALUES(?,?,?,?,?,?,?) ''' 
    cur = conn.cursor()
    cur.execute(sql, book_details)
    return cur.lastrowid

"""
    CLASSES
-----------------
""" 
class book:
   def __init__(self, isbn, title, authors, published_date, publisher, page_count, cover_url):
        self.isbn = isbn 
        self.title = title 
        self.authors = authors 
        self.published_date = published_date
        self.publisher = publisher 
        self.page_count = page_count 
        self.cover_url = cover_url

 
#format_book_data = print(f"{title}\n{authors}\n{publisher}\nPages: {page_count}\nISBN: {isbn}")

table = [[title],[authors],[f"Pages: {page_count}"],[f"ISBN: {isbn}"],[img_url]]
#print(tabulate(table)) 
bookObj = book(isbn, title, authors, published_date, publisher, page_count, img_url)
conn = connect_db(r'data/libray.db')
book_1 = (bookObj.isbn, bookObj.title, bookObj.authors, bookObj.published_date, bookObj.publisher, bookObj.page_count, bookObj.cover_url)
if conn is not None:
# create library table
    create_table(conn, sql_create_library_table)
else:
    print("Error! cannot create the database connection.")

with conn:
    create_book(conn, book_1)

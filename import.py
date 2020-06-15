import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine('postgres://zxbpcdixgtqlbe:03a463ba3f8cb3377e6ef55b597755b018de74becf7f10d7058603af5fca1528@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dfkcvkmjtpduih')
db = scoped_session(sessionmaker(bind=engine))


def main():
    booklist = open("books.csv")
    reader = csv.reader(booklist)
    for isbn, title,author, year in reader:
        db.execute("INSERT INTO books (isbn, title,author,year) VALUES (:isbn, :title, :author,:year)",
                    {"isbn": isbn, "title": title, "author": author,"year":year})
    db.commit()
    print("Done")

if __name__ == "__main__":
    main()

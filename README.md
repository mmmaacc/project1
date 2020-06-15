# Project 1

Web Programming with Python and JavaScript

Per the requirements, I made a database in Heroku.
I called it Paper Tomatoes.

These are the details of the database.

Host
ec2-3-91-112-166.compute-1.amazonaws.com

Database
dfkcvkmjtpduih

User
zxbpcdixgtqlbe

Port
5432

Password
03a463ba3f8cb3377e6ef55b597755b018de74becf7f10d7058603af5fca1528

URI
postgres://zxbpcdixgtqlbe:03a463ba3f8cb3377e6ef55b597755b018de74becf7f10d7058603af5fca1528@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dfkcvkmjtpduih

Heroku CLI
heroku pg:psql postgresql-objective-46336 --app papertomatoes

I used adminer to build 3 tables with the following columns:
books
  book_id (primary), title, author,year, isbn
users
  user_id (primary), username, password
reviews
  review_id(primary),review_text,rating,user_id(foreign key tied to user table),
  book_id(foreign key tied to books table)

I also got a developer account at goodreads.com with secret key:SjsqZLc7J7XumRI6bYoSlQ.

The website has 4 pages:
   login    
   register
   search - search for book based on title, author or isbn
   books - display book by request and allow user to enter a review
   errors - display errors that occurred when trying to read or add to Database

The application.py is of course the module that routes and processes the
webpages.  It also includes a json response for json requests to the database.

Imports.py will update the heroku database from books.csv.

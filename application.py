# Project 1 - book review website  Paper Tomatoes
# application module

import os,requests,json

from flask import Flask, session,render_template,request,url_for,redirect,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# key used in session
app.secret_key = '47hAHNBDJDjjd890G2'


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


Session(app)

# Set up database
engine = create_engine('postgres://zxbpcdixgtqlbe:03a463ba3f8cb3377e6ef55b597755b018de74becf7f10d7058603af5fca1528@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dfkcvkmjtpduih')
db = scoped_session(sessionmaker(bind=engine))




# first screen will be the login screen
@app.route('/',methods=['GET','POST'])
def login():
    session.pop('user_id',None)
    if request.method == 'POST':
        user_to_get =  request.form['username']
        password_entered =  request.form['password']
        user = db.execute("SELECT * FROM users WHERE username = :user", {"user":user_to_get}).fetchone()
        if user.password == password_entered:
            session['user_id'] = user.user_id
            return render_template('search.html')
        else:
            return render_template('/')
    else:
        return render_template('login.html')

# register new users
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # get form input
        user_to_enter = request.form.get("username")
        password_to_enter = request.form.get("password")

        # attempt to enter data - usernames have unique constraint
        try:
            db.execute("INSERT INTO users (username, password)                 \
                        VALUES (:username, :password)",                        \
                       {"username":user_to_enter,"password": password_to_enter})

        except:
            return render_template('register.html',feedback="Error occurred, try different username")

        # go back to login screen if successful
        else:
            db.commit()
            return redirect('/')
    # just display form
    else:
        return render_template('register.html')

# take user out of the session if they logout
@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect('/')

# first screen after login page
# display search fields
# if item found then display list of matches
# if not logged in then display index/login page
@app.route('/search', methods=['GET','POST'])
def search():
    # check that user is logged in
    if 'user_id' not in session:
        return redirect('/')

    # find a match on either title, author, or isbn
    if request.method == 'POST':
        title_to_find = request.form.get("title")
        author_to_find = request.form.get("author")
        isbn_to_find = request.form.get("isbn")

        # search on title if entered
        if title_to_find:
            title_to_find = '%' + title_to_find + '%'
            books = db.execute("SELECT title FROM books WHERE title LIKE :title", {"title": title_to_find}).fetchall()

        elif author_to_find:
            author_to_find = '%' + author_to_find + '%'
            books = db.execute("SELECT title FROM books WHERE author LIKE :author", {"author":author_to_find}).fetchall()

        elif isbn_to_find:
            isbn_to_find = '%' + isbn_to_find + '%'
            books = db.execute("SELECT title FROM books WHERE isbn LIKE :isbn", {"isbn": isbn_to_find}).fetchall()
        else:
            return render_template('search.html')

        # if something found then list all the titles Found
        if books:
            return render_template('search.html',books=books)
        else:
            return render_template('search.html',feedback="Book not found")

    # just display form
    else:
        return render_template('search.html')


@app.route('/book/<title>')
def book_found(title):

    # search for book to get book_id to look for review
    book_item = db.execute("SELECT * FROM books WHERE title = :title", {"title": title}).fetchone()
    book_list = []

    # book should be found since we found it - but you know jic
    if book_item:
        book_review= db.execute("SELECT review_text FROM reviews WHERE book_id = :book_id", {"book_id": book_item.book_id}).fetchall()

         # get rating data from good reads
        res = requests.get("https://www.goodreads.com/book/review_counts.json",   \
                            params={"isbns": book_item.isbn, "key": "SjsqZLc7J7XumRI6bYoSlQ"})

        # if book found in goodreads website then add their data
        if res.status_code == 200:
            book_data = res.json()
            book_gr = book_data["books"]
            book_list.append({"title":book_item.title,"author":book_item.author,"year":book_item.year,"isbn":book_item.isbn,   \
                                      "average_rating":book_gr[0]['average_rating'],\
                                      "number_of_reviews":book_gr[0]['work_ratings_count'],"book_reviews":book_review})
        else:
            book_list.append({"title":book.title,"author":book.author,"year":book.year,"isbn":book.isbn,"averate_rating":'None',\
                               "number_of_reviews":'None',"book_reviews":book_review})

        return render_template('books.html',book=book_list[0])
    else:
        return render_template('errors.html',message='ERROR-BOOK NOT FOUND')



@app.route('/api/<isbn_to_get>', methods=['GET'])
def book_api(isbn_to_get):
    book_data = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn_to_get}).fetchone()
    if book_data == None:
        return jsonify({"error": 404})
    else:
        rating_data = db.execute("SELECT ROUND(AVG(rating),1) AS average_rating, COUNT(rating) AS rating_count FROM reviews WHERE book_id = :book_id",{"book_id":book_data.book_id}).fetchall();
        rating_item = rating_data[0]
        average = rating_item[0]
        if average == None:
            average = 0.0
        count = rating_item[1]
        return jsonify({"title":book_data.title, "author":book_data.author,"year":book_data.year, "isbn":book_data.isbn,"review_count":count,"average_score":float(average)})


@app.route('/review/<title>', methods=['POST'])
def review(title):
    rating_to_enter = request.form.get("rating")

    if rating_to_enter.isdigit() == False:
        return render_template('errors.html',message="ERROR-ENTER NUMBER BETWEEN 1-5")

    if int(rating_to_enter) not in range(1,6):
        return render_template('errors.html',message="ERROR-ENTER NUMBER BETWEEN 1-5")

    # find book
    book_title= db.execute("SELECT book_id FROM books WHERE title = :title", {"title": title}).fetchone()

    # if book not found then return with error page
    if not book_title:
        return render_template('errors.html',message='ERROR-BOOK NOT FOUND')

    # get user id from session
    user_id_to_enter = session['user_id']

    # did user already enter a review for this book ?
    book_review= db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id=:user_id",  \
                             {"book_id": book_title.book_id,"user_id":user_id_to_enter}).fetchone()

    # yes - user can only enter one review per book - return with error
    if book_review:
            return render_template('error.html',message='YOU HAVE ALREADY REVIEWED THIS BOOK')

    # get review from template
    review_to_enter = request.form.get("review")

    # attempt to enter data
    try:
        db.execute("INSERT INTO reviews (review_text, rating,user_id,    \
                   book_id)                                              \
                   VALUES (:review_text, :rating,:user_id,               \
                   :book_id)",                                           \
                   {"review_text":review_to_enter, "rating":rating_to_enter, \
                   "user_id":user_id_to_enter,"book_id":book_title.book_id})
    except:
        return render_template('error.html',message='ERROR-UNABLE TO ADD REVIEW')


    db.commit()

    # return to search screen
    return render_template('search.html')

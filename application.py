import os
import json as JSON
import types
from flask import Flask, session , request ,render_template , flash , redirect , url_for , session , logging
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from Data import Books
from flask_mysqldb import MySQL 
from wtforms import Form ,StringField,TextAreaField,PasswordField,validators , SelectField , IntegerField
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#Configure mySQLDatabase
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USERS'] = 'zahid'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'bookreviewapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.run(debug=True)

#Initialize mySQL Database
mysql = MySQL(app)
app.secret_key = 'afrahdawood12'


Books = Books()

@app.route("/")
def index():
    return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/books')
def books():
	return render_template('books.html' , books = Books)



class SearchForm(Form):

    choices = [('isbn', 'ISBN'),

               ('title', 'Title'),

               ('author', 'Author'),

               ('year' , 'Year')]

    select = SelectField('Search for Books:', choices=choices)

    search = StringField('')


class RegisterForm(Form):
    name = StringField('Name' , [validators.Length(min=4,max=50)])
    username = StringField('Username' , [validators.Length(min=4,max=25)])
    email = StringField('Email' , [validators.Length(min=5,max=50)])
    password = PasswordField('Password',[
    		validators.DataRequired(),
    		validators.EqualTo('confirm' , message = "Passwords do not match")
    	])
    confirm = PasswordField('Confirm Password')



@app.route('/login', methods =['GET','POST'])
def login():

	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']

		cur = mysql.connection.cursor()

		result = cur.execute("SELECT * FROM users WHERE username = %s",[username])

		if result > 0:
			#get password hash
			data = cur.fetchone()
			password = data['password']

			if sha256_crypt.verify(password_candidate , password):
				app.logger.info('PASSWORD MATCHED')
				session['logged_in'] = True
				session['username'] = username

				flash('You are now logged in ' ,'success')
				return redirect(url_for('dashboard'))

			else:
				error = 'Invalid Login'
				return render_template('login.html' , error = error)
			cur.close()
		else:
			error = 'Username not found'
			return render_template('login.html' , error = error)


	return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	flash('You are now logged out' , 'success')
	return redirect(url_for('login'))

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

	
class BookForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])
	rating = IntegerField('Rate 1 - 5' ,[validators.NumberRange(min=1 , max=5)])


@app.route('/results/<string:id>/')
def result(id):
	client = goodreads.Client(client_id="uIcQQiAbnQPgbupzd4YpNQ", client_secret="qGtVwOrD8Dqm5aCPpS8um1SwBlAIMe4D2sizAvaiV8") # Secret is optional
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM books WHERE id = %s",[id]) 
	book = cur.fetchone()   
	reviews = cur.execute("SELECT * FROM bookreview WHERE book_id = %s" , [id])
	reviewsall = cur.fetchall()
	cur.close()
	return render_template('book_page.html' ,  book = book , reviewsall = reviewsall)   

    
@app.route('/results/<string:id>/addreview/', methods =['GET','POST'])
def add_review(id):
	form = BookForm(request.form)
	if request.method == 'POST' and form.validate():
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM bookreview WHERE reviewCount = 1 AND book_id = %s;" , [id])
		if result > 0:
			flash('Review Already Exists', 'danger')
			return redirect(url_for('dashboard'))
		else:
			title = form.title.data   
			body = form.body.data 
			rating = form.rating.data
			title = str(title)
			body = body.replace('<p>'," ")      
			body = body.replace('</p>'," ")
			body = body.replace('<br>'," ")
			body = str(body)
			books_id = id
			reviewCount = 1
			cur.execute("INSERT INTO bookreview(title ,body , book_id , rating ,reviewCount ) VALUES (%s, %s, %s , %s , %s)", (title, body, books_id, rating , reviewCount))
			mysql.connection.commit()      
			flash('Review Created', 'success')
			flash(results)
			return redirect(url_for('dashboard'))
	return render_template('add_review.html' ,id=id , form=form)




@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    select_string = search.data['select']
    cur = mysql.connection.cursor()
    sqlSyntax = 'SELECT * FROM books WHERE {} = %s'.format(select_string)
    cur.execute(sqlSyntax, (search_string,))
    results = cur.fetchall()

    if not results:

        flash('No results found!')
        return redirect('/')
    else:
        return render_template('results.html', results=results)



@app.route('/dashboard' , methods = ['GET','POST'])
@is_logged_in
def dashboard():
	search = SearchForm(request.form)
	if request.method == 'POST':
		return search_results(search)
	return render_template('dashboard.html', form=search)
    

    
        

@app.route('/register', methods =['GET','POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		name = form.name.data 
		email = form.email.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#Create Cursor
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s, %s,%s,%s)", (name , email , username , password))

		#commit to the database
		mysql.connection.commit()

		cur.close()

		flash("Congratulations on being registered")
		return redirect(url_for('index'))
	return render_template('register.html' , form = form)

if __name__ == '__main__':
	app.secret_key = 'afrahdawood12'
	app.run(debug=True)




	#INSERT INTO bookreview(book_id , title , body)  VALUES(5024 , 'Yes this is the first review', 'nothing obvious just casual things about the frist review what do you want to say');
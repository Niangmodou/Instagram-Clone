'''
Finstagram
Intro. to Database Systems Spring 2020
MADE WITH LOVE BY MODOU NIANG
'''
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import time

#Initialize the app from Flask
app = Flask(__name__)

#Defining SALT for password hashing function
SALT = 'CS3083'

#Set up connection to MySQL Database
connection = pymysql.connect(host='localhost',
                             port= 8889,
                             user= 'root',
                             password='root',
                             db='Finstagram',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


#Define route for the root
@app.route('/')
def index():
    return render_template('index.html')

#Define route to logout
@app.route('/logout')
def logout():
    session['username'].pop()
    return redirect('/')

#Define route for login page
@app.route('/login')
def login():
    return render_template('login.html')


#Define route for register page
@app.route('/register')
def register():
    return render_template('register.html')


#Define route for login authentification
@app.route('/loginAuth', methods=['GET','POST'])
def login_auth():
    cursor = connection.cursor()
    if(request.form):
        username = request.form['username']
        password = reqeust.form['password'] + SALT
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        #Query to get current user from database
        query = 'SELECT * FROM Person WHERE username = %s AND password = %s'
        cursor.execute(query,(username,password))
        data = cursor.fetchone()
        cursor.close()

        if(data):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid Login Credentials. Please Try Again'
            return render_template('login.html',error= error)

    error = 'Unknown error has occured'
    return render_template('login.html',error= error)


#Define route for register authentification
@app.route('/registerAuth')
def register_auth():
    cursor = connection.cursor()
    if(request.form):
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['username']
        password = request.form['password'] + SALT
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        email = request.form['email']

        #Checks if a user with the matching username already exists
        try:
            #Query to insert new user in our database
            query = 'INSERT INTO (firstName,lastName,username,password,email) \
                     VALUES ({},{},{},{},{})'.format(first_name,last_name,username,password,email)
            cursor.execute(query)

        except pymysql.err.IntegrityError:
            error = '{} is already taken. Try Again '.format(username)
            return render_template('register.html',error= error)

    else:
        error = 'Unknown error has occured'
        return render_template('register.html',error= error)


#Define route to view visible photos (Required Feature 1)
@app.route('/home')
def home():
    username = session['username']
    cursor = connection.cursor()

    #Query to get photos from the people the user is following
    following = 'SELECT pId, postingDate, filePath, caption, poster \
                 FROM Photo JOIN Follow ON(poster=followee) \
                 WHERE follower={} AND followStatus=TRUE'.format(username)

    #Query to get photos that are shared with the user
    shared_with = 'SELECT pID FROM SharedWith \
                   WHERE ({},groupName) IN (SELECT * FROM BelongTo)'.format(username)

    #Query to get photos that the user has posted
    posted = 'SELECT pId, postingDate, filePath, caption, poster FROM Photo \
              WHERE poster = {}'.format(username)

    #Query that gets all the distinct photos a user can view
    query = 'SELECT DISTINCT * FROM %s UNION %s UNION %s ORDER BY postingDate DESC'

    cursor.exceute(query, (following,shared_with,posted))
    data = cursor.fetchall()
    cursor.close()

    #Query to retrieve all users that are tagged in the photos
    cursor = connection.cursor()
    tagged_query = 'SELECT _______ FROM _____ WHERE tagStatus= TRUE'
    cursor.execute()
    tagged = cursor.fetchall()

    #Query to retrieve all users that have reacted to the photos
    cursor = connection.cursor()
    reacted_query = 'SELECT username, emoji, comment FROM ReactTo'
    cursor.execute()
    reacted = cursor.fetchall()

    return render_template('home.html',username= session['username'], photos= data)

#Define route to view further photo info (Required Feature 2)

#Define route to post a photo (Required Feature 3)
@app.route('/postPhoto', methods=['POST'])
def post_photo():
    if(request.files):
        cursor = connection.cursor()




        #Query that inserts the new photo into the Database
        query = 'INSERT INTO Photo ()'
    else:
        error = 'Unable to upload Image'
        return render_template('home.html',error=error)
#Define route to follow a person (Required Feature 4)

#Define route to create a friend group (Required Feature 5)
print(time.timestamp)


app.secret_key = 'some random key here. usually in env.'
'''
if __name__ == "__main__":
    app.run('127.0.0.1', 5000)
'''

'''
Finstagram
Intro. to Database Systems Spring 2020
MADE WITH LOVE BY MODOU NIANG
'''
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import time
import datetime as dt

#Initialize the app from Flask
app = Flask(__name__)

app.debug = True

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
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


#Define route for register page
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


#Define route for login authentification
@app.route('/loginAuth', methods=['POST'])
def login_auth():
    cursor = connection.cursor()
    if(request.form):
        username = request.form['username']
        password = request.form['password'] + SALT
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        #Query to get current user from database
        query = 'SELECT * FROM Person WHERE username = %s AND password = %s'
        cursor.execute(query,(username,password_hash))
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
@app.route('/registerAuth', methods=['POST'])
def register_auth():
    cursor = connection.cursor()
    if(request.form):
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['username']
        password = request.form['password'] + SALT
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        email = request.form['email']
        '''
        cursor = connection.cursor()
        query = 'SELECT * FROM PERSON WHERE username = %s'
        cursor.execute(query,(username))
        data = cursor.fetchone()

        if(data):
            error = "This user already exists"
            return render_template('register.html', error = error)
        '''
        #Checks if a user with the matching username already exists
        try:
            #Query to insert new user in our database
            query = 'INSERT INTO Person VALUES (%s,%s,%s,%s,%s)'
            cursor.execute(query, (username,password_hash,first_name,last_name,email))
            connection.commit()
            cursor.close()
            return redirect(url_for('login'))

        except pymysql.err.IntegrityError:
            error = '{} is already taken. Try Again '.format(username)
            return render_template('register.html',error= error)

    else:
        error = 'Unknown error has occured'
        return render_template('register.html',error= error)


#Define route to view visible photos and photo information (Required Feature 1 and 2)
@app.route('/home')
def home():
    username = session['username']
    cursor = connection.cursor()
    current_time = time.time()
    timestamp = dt.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')

    #Query to get photos from the people the user is following
    following = 'CREATE VIEW followingPhotos AS \
                (SELECT DISTINCT pId, postingDate, filePath, caption, poster \
                FROM Photo JOIN Follow ON(poster=followee) \
                WHERE follower= %s AND followStatus=TRUE)'
    cursor.execute(following, (username))

    #Query to get photos that are shared with the user
    shared_with = 'CREATE VIEW sharedPhotos AS \
                  (SELECT DISTINCT pID, postingDate, filePath, caption, poster \
                  FROM SharedWith NATURAL JOIN Photo WHERE (%s,groupName) \
                  IN (SELECT username,groupName FROM BelongTo))'
    cursor.execute(shared_with, (username))

    #Query to get photos that the user has posted
    posted = 'CREATE VIEW userPhotos AS \
             (SELECT DISTINCT pId, postingDate, filePath, caption, poster \
             FROM Photo WHERE poster = %s)'
    cursor.execute(posted, (username))

    #Query that gets all the distinct photos a user can view
    query = 'SELECT * FROM followingPhotos UNION (SELECT * FROM sharedPhotos)\
             UNION (SELECT * FROM userPhotos) ORDER BY postingDate DESC'
    cursor.execute(query)

    data = cursor.fetchall()

    #Dropping Views
    query = 'DROP VIEW followingPhotos, userPhotos, sharedPhotos'
    cursor.execute(query)

    #Query to retrieve all users that are tagged in the photos
    cursor = connection.cursor()
    tagged_query = 'SELECT * FROM Tag NATURAL JOIN Person NATURAL JOIN \
                    Photo WHERE tagStatus = TRUE'
    cursor.execute(tagged_query)
    tagged = cursor.fetchall()

    #Query to retrieve all users that have reacted to the photos
    cursor = connection.cursor()
    reacted_query = 'SELECT username, emoji, comment FROM ReactTo'
    cursor.execute(reacted_query)
    reacted = cursor.fetchall()
    cursor.close()

    return render_template('home.html',
                           username= session['username'],
                           images= data,
                           tagged= tagged,
                           reacted_to = reacted_query)


'''
#Define route to post a photo (Required Feature 3)
@app.route('/postPhoto', methods=['POST'])
def post_photo():
    if(request.form): #maybe request.files
        cursor = connection.cursor()
        current_time = time.time()
        timestamp = dt.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')


        #Query that inserts the new photo into the Database
        query = 'INSERT INTO Photo (postingDate,filePath,allFollowers,caption,poster) \
                 VALUES ({},{},{},{},{})'.format(,)
        cursor.execute(query)
        data
        message
    else:
        error = 'Unable to upload Image'
        return render_template('home.html',error=error)

#Define route to follow a person (Required Feature 4)
@app.route('/followUser', methods=['POST'])
def follow():
    if(request.form): #maybe request.files
        pass
    else:
        error = 'Unable to follow user'
        return render_template('home.html',error=error)
'''

#Define route to create a friend group (Required Feature 5)

#Define route to unfollow a user (Extra Feature 1)

#Define route to react to a photo (Extra Feature 2)


app.secret_key = 'some random key here. usually in env.'

if __name__ == "__main__":
    app.run('127.0.0.1', 5000)
#'''

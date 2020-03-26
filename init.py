'''
Finstagram
Intro. to Database Systems Spring 2020
MADE WITH LOVE BY MODOU NIANG
'''
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

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
def home():
    return render_template('index.html')

#Define route for login page
@app.route('/login')
def register():
    return render_template('login.html')

#Define route for register page
@app.route('/register')
def register():
    return render_template('register.html')

#Define route for login authentification
@app.route('/loginAuth')
def login_auth():
    pass #to be supplied by prof Frankl

#Define route for register authentification
@app.route('/registerAuth')
def register_auth():
    pass #to be supplied by prof Frankl

#Define route to view visible photos (Required Feature 1)
@app.route('/home')
def homepage():
    username = session["username"]
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

#Define route to follow a person (Required Feature 4)

#Define route to create a friend group (Required Feature 5)


if __name__ == "__main__":
    app.run('127.0.0.1', 5000)

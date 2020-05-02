'''
Finstagram
Intro. to Database Systems Spring 2020
MADE WITH LOVE BY MODOU NIANG
'''
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import time
import os
import datetime as dt

#Initialize the app from Flask
app = Flask(__name__)

app.debug = True

#PART 3 -> Required Feature 1 and 2

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


#Define route for the root COMPLETED
@app.route('/')
def index():
    return render_template('index.html')

#Define route to logout COMPLETED
@app.route('/signOut')
def logout():
    session.pop('username')
    #session['username'].pop()
    return redirect('/')

#Define route for login page COMPLETED
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


#Define route for register page COMPLETED
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


#Define route for login authentification COMPLETED
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


#Define route for register authentification COMPLETED
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

        #Checks if user with the same credentials exists
        if(user_exists(username,email)):
            error = "This user already exists"
            return render_template('register.html', error = error)
        else:
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

def user_exists(username,email):
    cursor = connection.cursor()
    query = 'SELECT * FROM PERSON WHERE username = %s and email=%s'
    cursor.execute(query,(username,email))
    data = cursor.fetchone()
    cursor.close()
    if(data):
        return True
    else:
        return False;

def get_time():
    current_time = time.time()
    return dt.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')

#Define route to view visible photos and photo information (Required Feature 1 and 2) COMPLETED
@app.route('/home')
def home():
    username = session['username']
    cursor = connection.cursor()
    timestamp = get_time()

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
    query = 'CREATE VIEW query AS SELECT * FROM followingPhotos UNION (SELECT * FROM sharedPhotos)\
             UNION (SELECT * FROM userPhotos) ORDER BY postingDate DESC'
    cursor.execute(query)

    #Query to get the Person information
    query = 'SELECT * FROM Person INNER JOIN ex ON ex.poster = Person.username'
    cursor.execute(query)

    data = cursor.fetchall()

    #Dropping Views
    query = 'DROP VIEW followingPhotos, userPhotos, sharedPhotos,query'
    cursor.execute(query)

    #Query to retrieve all users that are tagged in the photos
    tagged_query = 'SELECT * FROM Tag NATURAL JOIN Person NATURAL JOIN \
                    Photo WHERE tagStatus = TRUE'
    cursor.execute(tagged_query)
    tagged = cursor.fetchall()

    #Query to retrieve all users that have reacted to the photos
    reacted_query = 'SELECT username, emoji, comment FROM ReactTo'
    cursor.execute(reacted_query)
    reacted = cursor.fetchall()
    cursor.close()
    return render_template('home.html',
                           username= session['username'],
                           images= data,
                           tagged= tagged,
                           reacted_to = reacted)

#------------------------------------------------------------------------------------------------------------------------------------------

#Define route to post a photo (Required Feature 3)
@app.route('/postPhoto', methods=['POST'])
def post_photo():
    cursor = connection.cursor()
    if(request.files):
        poster = session['username']
        #Retrieving photo information

        #Retrieving the path of the folder
        FOLDER = os.path.join(os.getcwd(), 'Photos')
        file = request.files.get('photo','')
        name = file.filename
        print("Checkpoint 1")
        filepath = os.path.join(FOLDER,name)
        file.save(filepath)
        print("Checkpoint 2")
        all_followers = request.form['allFollowers']
        caption = request.form['caption']
        #Retrieving Timestamp
        timestamp = get_time()
        if(all_followers == 'true'):
            all_followers = True
        else:
            all_followers = False
        #Query that inserts the new photo into the database
        query = 'INSERT INTO Photo (postingDate,filePath,allFollowers,caption,poster) \
                 VALUES (%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(timestamp,filePath,allFollowers,caption,poster))
        print("Checkpoint 3")
        cursor.close()
        return redirect(url_for('home'))
    else:
        print("error")
        error = 'Unable to upload Image'
        return render_template('home.html',error=error)


#Define route to follow a person (Required Feature 4)
@app.route('/followUser', methods=['POST'])
def follow():
    cursor = connection.cursor()
    if(request.form):
        follower = session['username']
        followee = request.form['followee']

        if(follow_user(follower,followee)):
            error = 'You have already requested to follow this user'
            return render_template('home.html',error = error)
        else:
            query = 'INSERT INTO Follow(follower,followee,followStatus)VALUES(%s,%s,%s)'
            cursor.execute(query,(follower,followee,0))
            cursor.close()
            return redirect('/home')
    else:
        error = 'Unable to follow user'
        return render_template('home.html',error = error)

#Define route to view all follow requests
@app.route('/followRequests', methods=['GET'])
def follow_requests():
    cursor = connection.cursor()
    if(request.form):
        follower = session['username']

        #Query retrieves all the follow requests that have not been accepted
        query = 'SELECT * FROM Follow WHERE follower=%s AND followStatus=0'
        cursor.execute(query,(follower))
        data = cursor.fetchall()
        cursor.close()
        print(data)
        return render_template('home.html',requests = data)
    else:
        error = 'Unable to retrieve follow requests'
        return render_template('home.html',error = error)

#Define route to manage requests
@app.route('/manageRequests',methods=['POST'])
def manage_requests():
    cursor = connection.cursor()
    if(request.form):
        follower = session['username']
        followee = request.form['followee']
        status = request.form['followRequest']

        if(status == 'true'):
            query = 'UPDATE Follow SET followStatus=True WHERE follower=%s AND followee=%s'
            cursor.execute(query,(follower,followee))
            cursor.close()
        else:
            query = 'DELETE FROM Follow WHERE follower=%s AND followee=%s'
            cursor.execute(query,(follower,followee))
            cursor.close()
        return render_template('home.html')
    else:
        error = 'Unable to manage requests'
        return render_template('home.html',error = error)

def follow_user(follower,followee):
    cursor = connection.cursor()
    query = 'SELECT * FROM Follow WHERE follower=%s and followee=%s'
    cursor.execute(query,(follower,followee))
    data = cursor.fetchone()
    cursor.close()
    if(data):
        return True
    else:
        return False

#Define route to create a friend group (Required Feature 5) COMPLETED
@app.route('/createGroup', methods=['POST'])
def create_group():
    if(request.form):
        cursor = connection.cursor()
        #Retrieving Group information
        group_creator = session['username']
        group_name = request.form['groupName']
        description = request.form['groupDescription']

        #Checks if the user already has a group with the same name
        if(group_exists(group_name,group_creator)):
            error = 'User already has a group with an existing name'
            return render_template('home.html',error = error)
        else:
            #Query that inserts the new group into the database
            query = 'INSERT INTO FriendGroup(groupName,groupCreator,description)\
                     VALUES(%s,%s,%s)'
            cursor.execute(query,(group_name,group_creator,description))

            #Query that inserts the group in the users BelongTo TABLE
            query = 'INSERT INTO BelongTo(username,groupName,groupCreator) VALUES (%s,%s,%s)'
            cursor.execute(query,(group_creator,group_name,group_creator))
            cursor.close()

            return redirect('/home')
    else:
        error = 'Unable to create a group'
        return render_template('home.html',error=error)

def group_exists(group_name,group_creator):
    cursor = connection.cursor()
    query = 'SELECT * FROM FriendGroup WHERE groupName=%s and groupCreator=%s'
    cursor.execute(query,(group_name,group_creator))
    data = cursor.fetchone()
    cursor.close()
    if(data):
        return True
    else:
        return False

#Define route to react to a photo (Extra Feature 1)
@app.route('/reactTo',methods=['POST'])
def react_to():
    cursor = connection.cursor()
    if(request.form):
        username = session['username']
        photo_id = request.form['pId']
        comment = request.form['comment']
        emoji = request.form['emoji']
        timestamp = get_time()
        #Check if user already reacted to this photo
        query = 'SELECT * FROM ReactTo WHERE username=%s AND pId=%s'
        cursor.execute(query,(username,photo_id))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            error = 'You have already reacted to this photo'
        else:
            #Query inserts a tuple into the reactTo table
            query = 'INSERT INTO ReactTo(username,pId,reactionTime,comment,emoji)'
            cursor.execute(query,(username,photo_id,timestamp,comment,emoji))
            cursor.close()
            return render_template('home.html')
    else:
        error = 'Unable to react to photo'
        return render_template('home.html',error = error)

#Define route to unfollow a user (Extra Feature 2)
@app.route('/unfollow', methods=['POST'])
def unfollow():
    cursor = connection.cursor()
    if(request.form):
        follower = session['username']
        followee = request.form['followee']

        #Query is used to delete the tuple that establishes the relationship
        query = 'DELETE FROM Follow WHERE follower=%s AND followee=%s'

        cursor.execute(query,(follower,followee))
        cursor.close()
        return redirect('/home')
    else:
        error = 'Unable to unfollow user'
        return render_template('home.html',error = error)


app.secret_key = 'some random key here. usually in env.'

'''
TO DO!!!!!!!!!!!!!!!
- Fix Redirect Errors(Maybe use a javascript window alert)
- Display Follow requests
- Complete reactTo
- Fix Image display
- Fix Image reactions query
- Fix Posting photos
'''

if __name__ == "__main__":
    app.run('127.0.0.1', 5000)

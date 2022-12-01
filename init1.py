# Import Flask Library
import hashlib
from flask import Flask, render_template, request, session, url_for, redirect, flash, jsonify, make_response
import pymysql.cursors

# for uploading photo:
from app import app
#from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# Initialize the app from Flask
##app = Flask(__name__)
##app.secret_key = "secret key"

# hash password and salt
salt = "6083database"

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='holly',
                       password='hzs1212',
                       db='Cookzilla',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# check user's group and return GroupName and GroupCreator
def getUserGroup(user):
    cursor = conn.cursor()
    query = 'SELECT gName, gCreator FROM groupmembership WHERE memberName = %s'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close
    return data

# if logged in, return username; if not return Null


def checkUserLogin():
    user = None
    # check if the user logged in or not
    if session.get('username'):
        user = session['username']
    return user

# Define a route to hello function


@app.route('/')
def hello():
    user = checkUserLogin()
    status = 'No User Logged In!'
    if user:
        status = 'User Logged In!'
    return render_template('index.html', status=status, info=user)

# Define route for login


@app.route('/login')
def login():
    if session.get('username'):
        session.pop('username')
    return render_template('login.html')

# Define route for register


@app.route('/register')
def register():
    if session.get('username'):
        session.pop('username')
    return render_template('register.html')

# Authenticates the login


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    # check password in sha256
    password = request.form['password']
    password = password + salt
    password = password.encode('utf-8')
    password = hashlib.sha256(password).hexdigest()

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        # returns an error message to the html page
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

# Authenticates the register


@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    # store password in sha256
    password = request.form['password']
    password = password + salt
    password = password.encode('utf-8')
    password = hashlib.sha256(password).hexdigest()
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    if not fname:
        fname = None
    if not lname:
        lname = None
    if not email:
        email = None

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO person (username, password, lname, fname, email) VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, lname, fname, email))
        conn.commit()
        cursor.close()
        return redirect(url_for('hello'))


@app.route('/home')
def home():
    user = None
    # check if the user logged in or not
    if session.get('username'):
        user = session['username']
    print(user)
    # if user did not log in, go back to the login page
    if not user:
        return redirect(url_for('login'))
    return render_template('home.html', username=user)

# Define a route to post an event page


@app.route('/postEvent')
def postEventPage():
    user = None
    # check if the user logged in or not
    if session.get('username'):
        user = session['username']
    # if user did not log in, go back to the login page
    if not user:
        return redirect(url_for('login'))

    data = getUserGroup(user)
    return render_template('post_event.html', username=user, groups=data)

# post event


@app.route('/postEvent', methods=['GET', 'POST'])
def postEvent():
    user = session['username']
    finalPath = []
    # check if pictures
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            finalPath = None
        else:
            files = request.files.getlist('files[]')
            for file in files:
                if file.filename == '':
                    continue
                elif file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    finalPath.append(os.path.join(
                        app.config['UPLOAD_EVENT_FOLDER'], filename))
                    #flash('File successfully uploaded')
                    # return redirect('/')
                else:
                    data = getUserGroup(user)
                    error = 'Allowed file types are png, jpg, jpeg, gif'
                    return render_template('post_event.html', username=user, groups=data, error=error)
                    #flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                    # return redirect(request.url)

    # get information
    eName = request.form['eName']
    eDesc = request.form['eDesc']
    if not eDesc:
        eDesc = None
    eDate = request.form['eDate']
    gName = request.form['gName']
    gCreator = request.form['gCreator']

    # check if the user is in the group
    cursor = conn.cursor()
    query = 'SELECT * FROM groupmembership WHERE memberName = %s AND gName = %s AND gCreator = %s'
    cursor.execute(query, (user, gName, gCreator))
    data = cursor.fetchall()
    # if not, give an error message
    if not data:
        error = 'You are not permitted to add event for a group that you are not a member of!'
        conn.commit()
        cursor.close()
        data = getUserGroup(user)
        return render_template('post_event.html', username=user, groups=data, error=error)
    # else add the data to the database
    query = 'INSERT INTO event (eName, eDesc, eDate, gName, gCreator) VALUES(%s, %s, %s, %s, %s)'
    cursor.execute(query, (eName, eDesc, eDate, gName, gCreator))

    eID = cursor.lastrowid
    # deal with pictures, if no pictures, skip
    if finalPath:
        i = 0
        for finalP in finalPath:
            firstpart = finalP.rsplit(
                '.', 1)[0].lower() + '-' + str(eID) + '-' + str(i)
            secondpart = finalP.rsplit('.', 1)[1].lower()
            finalP = firstpart + "." + secondpart
            query = 'INSERT INTO eventpicture (eID, pictureURL) VALUES(%s, %s)'
            cursor.execute(query, (eID, finalP))
            file.save(os.path.join(finalP))
    conn.commit()
    cursor.close()
    data = getUserGroup(user)
    message = 'You have added an event with eventID: ' + str(eID)
    return render_template('post_event.html', username=user, groups=data, message=message)


@app.route('/logout')
def logout():
    if session.get('username'):
        session.pop('username')
    return redirect('/')


@app.route('/postRecipe', methods=['GET', 'POST'])
def post_recipe():
    ingredient = {}
    unit = {}
    cursor = conn.cursor()
    query = 'SELECT iName FROM Ingredient ORDER BY iName'
    cursor.execute(query)
    ingredient = cursor.fetchall()
    query = 'SELECT unitName FROM Unit ORDER BY unitName'
    cursor.execute(query)
    unit = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        # username = session['username']
        username = '123'
        cursor = conn.cursor()
        # insert into Recipe table
        query = 'INSERT INTO Recipe(title,numServings,postedBy) VALUES (%s, %s, %s)'
        cursor.execute(
            query, (request.form['title'], request.form['numServings'], username))
        # get auto_increment recipeID
        recipeID = cursor.lastrowid
        conn.commit()

        ingredients = request.form.getlist('ingredient')
        amounts = request.form.getlist('amount')
        units = request.form.getlist('unit')
        tags = request.form.getlist('tag')
        steps = request.form.getlist('step')
        pictures = request.files.getlist('pictures')
        # insert into RecipeTag table
        for tagText in tags:
            query = 'INSERT INTO RecipeTag(recipeID,tagText) VALUES (%s, %s)'
            cursor.execute(query, (recipeID, tagText))
            conn.commit()

        # insert into RecipeIngredient table
        for i in zip(ingredients, units, amounts):
            query = 'INSERT INTO RecipeIngredient(recipeID, iName, unitName, amount) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (recipeID, i[0], i[1], i[2]))
            conn.commit()

        # insert into step table
        for index, step in enumerate(steps):
            query = 'INSERT INTO Step (stepNo, recipeID, sDesc) VALUES (%s, %s, %s)'
            cursor.execute(query, (str(index), recipeID, step))
            conn.commit()

        # insert into recipepicture table
        for file in pictures:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_dir = os.path.join(
                    app.config['UPLOAD_RECIPE_FOLDER'], str(recipeID))
                file_url = os.path.join(
                    app.config['UPLOAD_RECIPE_FOLDER'], str(recipeID), filename)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                file.save(file_url)
                # flash('File successfully uploaded')
                query = 'INSERT INTO RecipePicture (recipeID,pictureURL) VALUES (%s, %s)'
                cursor.execute(query, (recipeID, str(file_url)))
                conn.commit()
            else:
                flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
        cursor.close()

    return render_template('post_recipe.html', ingredient=ingredient, unit=unit)


@app.route('/searchRecipes')
def SearchRecipes():
    return render_template('search_recipes.html')


@app.route('/searchRecipesResult', methods=['GET', 'POST'])
def SearchRecipesResult():
    if request.method == 'GET':
        query_tag = request.args.get("tag")
        query_stars = int(request.args.get("stars"))
        query_operator = request.args.get("operator")

        cursor = conn.cursor()
        data = {
            'query_tag': query_tag,
            'query_stars': query_stars,
            'query_operator': query_operator
        }
        result = []

        print(data)

        if query_tag == "":
            # search only avgstars
            statement = (
                "select recipeID, title, numServings, postedBy, avgstars "
                "from recipe_avgstars "
                "where avgstars > %(query_stars)s"
            )
            try:
                cursor.execute(statement, data)
                for (recipeID, title, numServings, postedBy, avgstars) in cursor:
                    result.append(
                        (recipeID, title, numServings, postedBy, avgstars))
                cursor.close()
            except pymysql.InternalError as err:
                print("Something went wrong: {}".format(err))
                return "failed"
        return str(result)


class SelfException(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


@app.errorhandler(SelfException)
def self_exception(error):
    response = make_response(error.message)
    response.status_code = error.status_code
    return response


@app.route('/exception')
def exception():
    raise SelfException('No privilege to access the resource', status_code=403)


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

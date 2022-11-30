# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
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

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='root',
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
                    app.config['UPLOAD_FOLDER'], str(recipeID))
                file_url = os.path.join(
                    app.config['UPLOAD_FOLDER'], str(recipeID), filename)
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

# # Define a route to hello function
# @app.route('/')
# def hello():
#     return render_template('index.html')

# # Define route for login
# @app.route('/login')
# def login():
#     return render_template('login.html')

# # Define route for register
# @app.route('/register')
# def register():
#     return render_template('register.html')

# # Authenticates the login
# @app.route('/loginAuth', methods=['GET', 'POST'])
# def loginAuth():
#     # grabs information from the forms
#     username = request.form['username']
#     password = request.form['password']
#     # cursor used to send queries
#     cursor = conn.cursor()
#     # executes query
#     query = 'SELECT * FROM user WHERE username = %s and password = %s'
#     cursor.execute(query, (username, password))
#     # stores the results in a variable
#     data = cursor.fetchone()
#     # use fetchall() if you are expecting more than 1 data row
#     cursor.close()
#     error = None
#     if(data):
#         # creates a session for the the user
#         # session is a built in
#         session['username'] = username
#         return redirect(url_for('home'))
#     else:
#         # returns an error message to the html page
#         error = 'Invalid login or username'
#         return render_template('login.html', error=error)

# # Authenticates the register
# @app.route('/registerAuth', methods=['GET', 'POST'])
# def registerAuth():
#     # grabs information from the forms
#     username = request.form['username']
#     password = request.form['password']
#     # cursor used to send queries
#     cursor = conn.cursor()
#     # executes query
#     query = 'SELECT * FROM user WHERE username = %s'
#     cursor.execute(query, (username))
#     # stores the results in a variable
#     data = cursor.fetchone()
#     # use fetchall() if you are expecting more than 1 data row
#     error = None
#     if(data):
#         # If the previous query returns data, then user exists
#         error = "This user already exists"
#         return render_template('register.html', error=error)
#     else:
#         ins = 'INSERT INTO user VALUES(%s, %s)'
#         cursor.execute(ins, (username, password))
#         conn.commit()
#         cursor.close()
#         return render_template('index.html')

# @app.route('/home')
# def home():
#     user = session['username']
#     cursor = conn.cursor()
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, (user))
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('home.html', username=user, posts=data)

# @app.route('/post', methods=['GET', 'POST'])
# def post():
#     username = session['username']
#     cursor = conn.cursor()
#     blog = request.form['blog']
#     query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
#     cursor.execute(query, (blog, username))
#     conn.commit()
#     cursor.close()
#     return redirect(url_for('home'))

# @app.route('/select_blogger')
# def select_blogger():
#     # check that user is logged in
#     #username = session['username']
#     # should throw exception if username not found

#     cursor = conn.cursor()
#     query = 'SELECT DISTINCT username FROM user'
#     cursor.execute(query)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('select_blogger.html', user_list=data)

# @app.route('/show_posts', methods=["GET", "POST"])
# def show_posts():
#     poster = request.args['poster']
#     cursor = conn.cursor()
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, poster)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('show_posts.html', poster_name=poster, posts=data)

# @app.route('/')
# def upload_form():
#     return render_template('upload.html')

# @app.route('/', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No file selected for uploading')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             flash('File successfully uploaded')
#             return redirect('/')
#         else:
#             flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
#             return redirect(request.url)

# @app.route('/logout')
# def logout():
#     session.pop('username')
#     return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 8800, debug=True)

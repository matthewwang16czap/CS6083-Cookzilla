# Import Flask Library
import decimal
import hashlib
from flask import Flask, render_template, request, session, url_for, redirect, flash, jsonify, make_response, send_from_directory
import pymysql.cursors

# for uploading photo:
from app import app
from werkzeug.utils import secure_filename
import os
import html

# seletable units
mass_selection = ['g', 'kg', 'mg', 'oz', 'lb', 'none']
volume_selection = ['fl oz', 'l', 'ml', 'pt', 'none']

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

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

# conn = pymysql.connect(host='localhost',
#                         port=3306,
#                         user='Sihan',
#                         password='Wsh010217',
#                         db='cs6083_project',
#                         charset='utf8mb4',
#                         cursorclass=pymysql.cursors.DictCursor)


def allowed_image(filename):
    if "." not in filename:
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
    cursor.execute(query, user)
    data = cursor.fetchall()
    cursor.close
    return data
  
#check user's events and return eid, ename, edate, edesc 
#check if the event date and time is greater than now; check if the event is RSVP before
def getUserEvent(user):
    cursor = conn.cursor()
    query = 'SELECT eID, eName, eDesc, eDate FROM Person Join GroupMembership ON Person.userName = GroupMembership.memberName NATURAL JOIN `Event` WHERE username = %s AND eDate > NOW() AND (userName, eID) NOT IN(SELECT userName, eID FROM rsvp WHERE rsvp.userName = %s AND rsvp.eID = eID) ORDER BY eID ASC'
    cursor.execute(query, (user, user))
    data = cursor.fetchall()
    cursor.close
    return data

def getEventPicture(eID):
    cursor = conn.cursor()
    query = 'SELECT pictureURL FROM eventPicture WHERE eID = %s'
    cursor.execute(query, (eID))
    data = cursor.fetchall()
    list = []
    for d in data:
        list.append(d['pictureURL'])
    cursor.close
    return list

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
    if data:
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
    cursor.execute(query, username)
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
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

@app.route('/postReview')
def postReviewPage():
  return render_template('post_review.html');

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
#post event
@app.route('/postEvent', methods=['GET', 'POST'])
def postEvent():
    user = session['username']
    finalPath = []
    #check if pictures
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
                    #file.save(os.path.join(app.config['UPLOAD_EVENT_FOLDER'], filename))
                    finalPath.append(os.path.join(app.config['UPLOAD_EVENT_FOLDER'], filename))
                    #flash('File successfully uploaded')
                    #return redirect('/')
                else:
                    data = getUserGroup(user)
                    error = 'Allowed file types are png, jpg, jpeg, gif'
                    return render_template('post_event.html', username = user, groups = data, error=error)
                    #flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                    #return redirect(request.url)

    #get information
    eName = request.form['eName']
    eDesc = request.form['eDesc']
    if not eDesc:
        eDesc = None
    eDate = request.form['eDate']
    gName = request.form['gName']
    gCreator = request.form['gCreator']

    #check if the user is in the group
    cursor = conn.cursor()
    query = 'SELECT * FROM groupmembership WHERE memberName = %s AND gName = %s AND gCreator = %s'
    cursor.execute(query, (user, gName, gCreator))
    data = cursor.fetchall()
    #if not, give an error message
    if not data:
        error = 'You are not permitted to add event for a group that you are not a member of!'
        conn.commit()
        cursor.close()
        data = getUserGroup(user)
        return render_template('post_event.html', username = user, groups = data, error=error)
    #else add the data to the database
    query = 'INSERT INTO event (eName, eDesc, eDate, gName, gCreator) VALUES(%s, %s, %s, %s, %s)'
    cursor.execute(query, (eName, eDesc, eDate, gName, gCreator))

    eID = cursor.lastrowid
    #deal with pictures, if no pictures, skip
    if finalPath:
        i = 0
        files = request.files.getlist('files[]')
        for finalP, file in zip(finalPath, files):
            firstpart = finalP.rsplit('.', 1)[0].lower() + '-' + str(eID) + '-' + str(i)
            secondpart = finalP.rsplit('.', 1)[1].lower()
            finalP = firstpart + "." + secondpart
            query = 'INSERT INTO eventpicture (eID, pictureURL) VALUES(%s, %s)'
            cursor.execute(query, (eID, finalP))
            file.save(finalP)
            i = i + 1
    conn.commit()
    cursor.close()
    data = getUserGroup(user)
    message = 'You have added an event with eventID: ' + str(eID)
    return render_template('post_event.html', username = user, groups = data, message = message)

#Define a route to rsvp page
@app.route('/rsvp')
def rsvpPage():
    user = checkUserLogin()
    if not user:
        return redirect(url_for('login'))
    data = getUserEvent(user)
    if not data:
        error = "You cannot RSVP any event"
        return render_template('rsvp.html', username=user, error=error)
    for d in data:
        #print (d['eID'])
        #data2.append(d['eID'])
        d['pictureURL'] = (getEventPicture(d['eID']))
        #print (d['pictureURL'])
    # print (data)
    return render_template('rsvp.html', username=user, events=data)

#RSVP
@app.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    user = session['username']
    #get information
    if "eID" not in request.form:
        error = "You cannot RSVP any event"
        return render_template('rsvp.html', username=user, error=error)
    eID = request.form['eID']
    response = request.form['response']

    if not response:
        error = 'You must select your response!'
        data = getUserEvent(user)
        return render_template('rsvp.html', username = user, events = data, error=error)
    #check if the user is in the group
    cursor = conn.cursor()
    query = 'SELECT * FROM Person Join GroupMembership ON Person.userName = GroupMembership.memberName NATURAL JOIN `Event` WHERE eID = %s'
    cursor.execute(query, (eID))
    data = cursor.fetchall()
    
    #if not, give an error message
    if not data:
        error = 'You are not permitted to RSVP for a group that you are not a member of!'
        conn.commit()
        cursor.close()
        data = getUserEvent(user)
        for d in data:
            d['pictureURL'] = (getEventPicture(d['eID']))
        return render_template('rsvp.html', username = user, events = data, error=error)
    
    #check if rsvp before
    query = 'SELECT * FROM rsvp WHERE userName = %s AND eID = %s'
    cursor.execute(query, (user, eID))
    data = cursor.fetchall()

    #if there is data, give an error message
    if data:
        error = 'You have RSVP before'
        conn.commit()
        cursor.close()
        data = getUserEvent(user)
        for d in data:
            d['pictureURL'] = (getEventPicture(d['eID']))
        return render_template('rsvp.html', username = user, events = data, error=error)
    
    #else add the data to the database
    query = 'INSERT INTO rsvp (username, eID, response) VALUES(%s, %s, %s)'
    cursor.execute(query, (user, eID, response))
    conn.commit()
    cursor.close()
    data = getUserEvent(user)
    for d in data:
        d['pictureURL'] = (getEventPicture(d['eID']))
    message = 'You have RSVP'
    return render_template('rsvp.html', username = user, events = data, message = message)


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
            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)
                file_dir = os.path.join(
                    'static', app.config['UPLOAD_RECIPE_FOLDER'], str(recipeID))
                file_url = os.path.join(
                    'static', app.config['UPLOAD_RECIPE_FOLDER'], str(recipeID), filename)
                save_url = os.path.join(
                    app.config['UPLOAD_RECIPE_FOLDER'], str(recipeID), filename)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                file.save(file_url)
                # flash('File successfully uploaded')
                query = 'INSERT INTO RecipePicture (recipeID,pictureURL) VALUES (%s, %s)'
                cursor.execute(query, (recipeID, str(save_url)))
                conn.commit()
            else:
                flash('Allowed image types are png, jpg, jpeg, gif')
        cursor.close()

    return render_template('post_recipe.html', ingredient=ingredient, unit=unit)


@app.route('/searchRecipes')
def search_recipes():
    return render_template('search_recipes.html')


@app.route('/searchRecipesResult', methods=['GET', 'POST'])
def search_recipes_result():
    if request.method == 'GET':
        # get parameters
        query_tag = request.args.get("tag")
        query_stars = int(request.args.get("stars"))
        query_operator = request.args.get("operator")
        # prepare query
        cursor = conn.cursor()
        data = {
            'query_tag': query_tag,
            'query_stars': query_stars,
            'query_operator': query_operator
        }
        results = []
        # case: only query_stars condition
        if query_tag == "":
            statement = (
                "select recipeID, title, numServings, postedBy, avgstars "
                "from recipe_avgstars "
                "where avgstars > %(query_stars)s"
            )
        # case: only query_tag condition
        elif query_stars == 0:
            statement = (
                "select r.recipeID, r.title, r.numServings, r.postedBy, ra.avgstars "
                "from recipe r "
                "left join recipetag rt on r.recipeID = rt.recipeID "
                "left join recipe_avgstars ra on r.recipeID = ra.recipeID "
                "where rt.tagText = %(query_tag)s"
            )
        # case: query_tag condition and query_stars condition
        elif query_operator == "and":
            statement = (
                "select r.recipeID, r.title, r.numServings, r.postedBy, ra.avgstars "
                "from recipe r "
                "left join recipetag rt on r.recipeID = rt.recipeID "
                "left join recipe_avgstars ra on r.recipeID = ra.recipeID "
                "where rt.tagText = %(query_tag)s and ra.avgstars > %(query_stars)s"
            )
        # case: query_tag condition or query_stars condition
        elif query_operator == "or":
            statement = (
                "select r.recipeID, r.title, r.numServings, r.postedBy, ra.avgstars "
                "from recipe r "
                "left join recipetag rt on r.recipeID = rt.recipeID "
                "left join recipe_avgstars ra on r.recipeID = ra.recipeID "
                "where rt.tagText = %(query_tag)s or ra.avgstars > %(query_stars)s"
            )

        # run the query
        try:
            cursor.execute(statement, data)
            results = cursor.fetchall()
        except pymysql.InternalError as err:
            print("Error from MySQL: {}".format(err))
            raise SelfException(err, status_code=502)
        return render_template('search_recipes_result.html', results=results)


@app.route('/SearchRecipeDetail/<recipeID>')
def search_recipe_detail(recipeID):

    # sample: {'recipeID': '2', 'title': 'Test1', 'numServings': 1, 'postedBy': 'Sihan', 'ingredients': {'beef': {'unitName': 'lb', 'amount': Decimal('2')}}, 'avgStars': Decimal('3.3333'), 'pictureURLs': ['/test/TestURL'], 'tags': ['fry'], 'relatedRecipes': {}, 'reviews': {'Sihan': {'revTitle': None, 'revDesc': None, 'stars': 5, 'pictureURLs': ['/test/TestURL']}, 'Sihan2': {'revTitle': None, 'revDesc': None, 'stars': 4, 'pictureURLs': []}, 'Sihan3': {'revTitle': None, 'revDesc': None, 'stars': 1, 'pictureURLs': []}}, 'Steps': {1: {'sDesc': 'do first thing'}, 2: {'sDesc': 'do second thing'}}}

    recipe_detail = {
        'recipeID': recipeID,
        'title': "",
        'numServings': "",
        'postedBy': "",
        'ingredients': {},  # dict of ingredients dict
        'avgStars': "",
        'pictureURLs': [],  # list of pictureURLs to trace the pictures
        'tags': [],  # list of tags
        'relatedRecipes': {},  # dict of related Recipes dicts of ids and names
        'reviews': {},  # dict of reviews dicts of username, title, description, stars, and photoURLs
        'Steps': {},  # dict of steps dicts of stepNo and description
        'unitConversions': {},
        'preferunits':{}
    }
    # prepare queries to get all recipe_detail
    cursor = conn.cursor()

    # find unit preference
    username = checkUserLogin()
    if username is not None:
        # run the query
        statement = (
            "select userName, unitName, unitType "
            "from preferunits "
            "where userName = %s "
        )
        try:
            cursor.execute(statement, username)
            results = cursor.fetchall()
            for result in results:
                recipe_detail['preferunits'][result['unitType']] = result['unitName']
        except pymysql.InternalError as err:
            print("Error from MySQL: {}".format(err))
            raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select title, numServings, postedBy, avgstars "
        "from recipe_avgstars "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        result = cursor.fetchone()
        recipe_detail['title'] = result['title']
        recipe_detail['numServings'] = result['numServings']
        recipe_detail['postedBy'] = result['postedBy']
        recipe_detail['avgStars'] = result['avgstars']
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select pictureURL "
        "from recipepicture "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        results = cursor.fetchall()
        for result in results:
            recipe_detail['pictureURLs'].append(
                result['pictureURL'].replace('\\', '/'))
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select tagText "
        "from recipetag "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        results = cursor.fetchall()
        for result in results:
            recipe_detail['tags'].append(result['tagText'])
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select recipe1, recipe2 "
        "from relatedrecipe "
        "where recipe1 = %s or recipe2 = %s"
    )
    try:
        cursor.execute(statement, (recipeID, recipeID))
        results = cursor.fetchall()
        related_recipes_ids = []
        for result in results:
            # get related recipes ids
            if result['recipe1'] == recipeID:
                related_recipes_ids.append(str(result['recipe2']))
            else:
                related_recipes_ids.append(str(result['recipe1']))
        # remove duplicates and itself
        related_recipes_ids = set(related_recipes_ids)
        related_recipes_ids.discard(recipeID)
        # get recipe title of each id, put the info
        for related_recipe_id in related_recipes_ids:
            statement = (
                "select title "
                "from recipe "
                "where recipeID = %s"
            )
            cursor.execute(statement, related_recipes_ids)
            result = cursor.fetchone()
            related_recipe_info = {
                'title': result['title']
            }
            recipe_detail['relatedRecipes'][related_recipe_id] = related_recipe_info
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select userName, revTitle, revDesc, stars "
        "from review "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        results = cursor.fetchall()
        for result in results:
            review = {
                'revTitle': result['revTitle'],
                'revDesc': result['revDesc'],
                'stars': result['stars'],
                'pictureURLs': []
            }
            recipe_detail['reviews'][result['userName']] = review
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select userName, pictureURL "
        "from reviewpicture "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        results = cursor.fetchall()
        for result in results:
            recipe_detail['reviews'][result['userName']]['pictureURLs'].append(
                result['pictureURL'].replace('\\', '/'))
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select stepNo, sDesc "
        "from step "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        results = cursor.fetchall()
        for result in results:
            step_info = {
                'sDesc': result['sDesc']
            }
            recipe_detail['Steps'][result['stepNo']] = step_info
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # get unit conversion ratio
    statement = ("select * from unitconversion;")
    try:
        cursor.execute(statement)
        results = cursor.fetchall()
        for result in results:
            unit_for_source = {
                'name': result['destinationUnit'], 'ratio': float(result['ratio'])}
            unit_for_dest = {
                'name': result['sourceUnit'], 'ratio': 1/(float(result['ratio']))}
            if result['sourceUnit'] not in recipe_detail['unitConversions']:
                recipe_detail['unitConversions'][result['sourceUnit']] = [
                    unit_for_source]
            elif unit_for_source not in recipe_detail['unitConversions'][result['sourceUnit']]:
                recipe_detail['unitConversions'][result['sourceUnit']].append(
                    unit_for_source)

            if result['destinationUnit'] not in recipe_detail['unitConversions']:
                recipe_detail['unitConversions'][result['destinationUnit']] = [
                    unit_for_dest]
            elif unit_for_dest not in recipe_detail['unitConversions'][result['destinationUnit']]:
                recipe_detail['unitConversions'][result['destinationUnit']].append(
                    unit_for_dest)
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query
    statement = (
        "select iName, unitName, amount "
        "from recipeingredient "
        "where recipeID = %s"
    )
    try:
        cursor.execute(statement, recipeID)
        results = cursor.fetchall()
        for result in results:
            ingredient = {
                'unitName': result['unitName'],
                'amount': result['amount']
            }
            # if unit preference exist, change to preference
            if username is not None:
                if ingredient['unitName'] in mass_selection and recipe_detail['preferunits']['mass'] is not None:
                    targetunits = recipe_detail['unitConversions'][ingredient['unitName']]
                    ratio = 0
                    for targetunit in targetunits:
                        if targetunit['name'] == recipe_detail['preferunits']['mass']:
                            ratio = targetunit['ratio']
                            ingredient['unitName'] = recipe_detail['preferunits']['mass']
                            ingredient['amount'] = decimal.Decimal(ingredient['amount']) * decimal.Decimal(ratio)
                if ingredient['unitName'] in volume_selection and recipe_detail['preferunits']['volume'] is not None:
                    targetunits = recipe_detail['unitConversions'][ingredient['unitName']]
                    ratio = 0
                    for targetunit in targetunits:
                        if targetunit['name'] == recipe_detail['preferunits']['volume']:
                            ratio = targetunit['ratio']
                            ingredient['unitName'] = recipe_detail['preferunits']['volume']
                            ingredient['amount'] = decimal.Decimal(ingredient['amount']) * decimal.Decimal(ratio)
            recipe_detail['ingredients'][result['iName']] = ingredient
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # log user's access
    if username is not None:
        statement = (
            "insert into viewhistory (userName, recipeID) "
            "values (%s, %s)"
        )
        try:
            cursor.execute(statement, (username, recipeID))
            conn.commit()
        except pymysql.InternalError as err:
            print("Error from MySQL: {}".format(err))
            raise SelfException(err, status_code=502)

    print(recipe_detail)
    return render_template('recipe_detail.html', data=recipe_detail, recipeID=recipeID)


@app.route('/postReview/<recipeID>', methods=['GET', 'POST'])
def post_review(recipeID):
    # recipeID = request.args['recipeID']
    if request.method == "GET":
        return render_template('post_review.html', recipeID=recipeID)
    if request.method == "POST":
        username = checkUserLogin()
        if not username:
            return redirect(url_for('login'))
        else:
            cursor = conn.cursor()
            pictures = request.files.getlist('pictures')
            # check pictures
            for file in pictures:
                if file and not(allowed_image(file.filename)):
                    flash('Allowed image types are png, jpg, jpeg, gif')
                    return render_template('post_review.html', recipeID=recipeID)
            # check if the user have already posted review of this recipe
            query = 'SELECT * FROM Review WHERE userName = %s AND recipeID = %s;'
            cursor.execute(query, (username, recipeID))
            data = cursor.fetchone()
            if data:
                # update
                query = 'UPDATE Review SET revTitle = %s, revDesc = %s, stars = %s WHERE userName = %s AND recipeID = %s;'
                cursor.execute(
                    query, (request.form['revTitle'], request.form['revDesc'], request.form['stars'], username, recipeID))
                conn.commit()
                query = 'DELETE FROM ReviewPicture WHERE userName = %s AND recipeID = %s;'
                cursor.execute(
                    query, (username, recipeID))
                conn.commit()

            else:
                # insert
                query = 'INSERT INTO Review(userName, recipeID, revTitle, revDesc, stars) VALUES (%s, %s, %s, %s, %s);'
                cursor.execute(
                    query, (username, recipeID, request.form['revTitle'], request.form['revDesc'], request.form['stars']))
                conn.commit()
            # upload review pictures
            for file in pictures:
                if file:
                    filename = secure_filename(file.filename)
                    file_dir = os.path.join(
                        'static', app.config['UPLOAD_REVIEW_FOLDER'], str(recipeID), str(username))
                    file_url = os.path.join(
                        'static', app.config['UPLOAD_REVIEW_FOLDER'], str(recipeID), str(username), filename)
                    save_url = os.path.join(
                        app.config['UPLOAD_REVIEW_FOLDER'], str(recipeID), str(username), filename)
                    if not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                    file.save(file_url)
                    # flash('File successfully uploaded')
                    query = 'INSERT INTO ReviewPicture (username,recipeID,pictureURL) VALUES (%s, %s, %s)'
                    cursor.execute(query, (username, recipeID, str(save_url)))
                    conn.commit()
            cursor.close()
            return redirect(url_for('home'))


# present the preference and allow user to change preferred unit on submit
@app.route('/Preference/<username>')
def show_preference(username):
    # the following should be in mysql server
    viewing_history = {} # contains at most 10 recently viewed recipe ids and title
    unit_preference = {} # choose unit to be shown

    # prepare queries to get viewing_history and unit_preference
    cursor = conn.cursor()

    # run the query to get history
    statement = (
        "select v.recipeID, r.title, v.timestamp "
        "from viewhistory v natural join recipe r "
        "where v.username = %s "
        "order by v.timestamp desc "
        "limit 10"
    )
    try:
        cursor.execute(statement, username)
        results = cursor.fetchall()
        for result in results:
            viewed_recipe = {
                'title': result['title'],
                'timestamp': result['timestamp']
            }
            viewing_history[result['recipeID']] = viewed_recipe
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # run the query to get preferunits
    statement = (
        "select username, unitName, unitType "
        "from preferunits "
        "where username = %s "
    )
    try:
        cursor.execute(statement, username)
        results = cursor.fetchall()
        for result in results:
            unit_preference[result['unitType']] = result['unitName']
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    # if no unit preference, set None
    if 'mass' not in unit_preference:
        unit_preference['mass'] = 'none'
    if 'volume' not in unit_preference:
        unit_preference['volume'] = 'none'

    return render_template('preference.html', username=username, viewing_history=viewing_history, unit_preference=unit_preference, mass_selection=mass_selection, volume_selection=volume_selection)


# excecuting change preferred unit on submit
@app.route('/ChangePeference/<username>/<unit_type>', methods=['GET'])
def change_preference(username, unit_type):
    data = {
        'unit_name': request.args.get("unitname"),
        'username': username,
        'unit_type': unit_type
    }
    # prepare queries
    cursor = conn.cursor()

    # run the query to check existence
    statement = (
        "select userName, unitName, unitType "
        "from preferunits "
        "where userName = %(username)s and unitType = %(unit_type)s "
    )
    try:
        cursor.execute(statement, data)
        result = cursor.fetchone()
    except pymysql.InternalError as err:
        print("Error from MySQL: {}".format(err))
        raise SelfException(err, status_code=502)

    if result is None:
        statement = (
            "insert into preferunits (userName, unitName, unitType) "
            "values (%(username)s, %(unit_name)s, %(unit_type)s)"
        )
        try:
            cursor.execute(statement, data)
            conn.commit()
        except pymysql.InternalError as err:
            print("Error from MySQL: {}".format(err))
            raise SelfException(err, status_code=502)
    else:
        statement = (
            "update preferunits "
            "set unitName = %(unit_name)s "
            "where userName = %(username)s and unitType = %(unit_type)s "
        )
        try:
            cursor.execute(statement, data)
            conn.commit()
        except pymysql.InternalError as err:
            print("Error from MySQL: {}".format(err))
            raise SelfException(err, status_code=502)
    return redirect(url_for('show_preference', username=username))

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

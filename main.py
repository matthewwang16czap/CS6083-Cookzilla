# coding:utf-8
import mysql.connector
from mysql.connector import errorcode
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_cors import CORS

# global variable
route_addr = 'localhost'
route_port = 5600
success_token = 'WadsfoeiWUdwaoiWUhdwdh'

app = Flask(__name__)  # create flask app
app.config['JSON_AS_ASCII'] = False  # prohibit chinese decode

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# app.secret_key = 'abc'  # setup secrete key for transferring data in form

# 数据库变量
cnx = None
cnx = mysql.connector.connect(user='Sihan', password='Wsh010217', host='127.0.0.1', database='cs6083_project')

@app.route('/')
def HomePage():
    return redirect(url_for('SearchRecipes'))

@app.route('/SearchRecipes')
def SearchRecipes():
    return render_template('SearchRecipes.html')

@app.route('/SearchRecipesResult', methods=['GET', 'POST'])
def SearchRecipesResult():
    if request.method == 'GET':
        query_tag = request.args.get("tag")
        query_stars = int(request.args.get("stars"))
        query_operator = request.args.get("operator")

        cursor = cnx.cursor()
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
                    result.append((recipeID, title, numServings, postedBy, avgstars))
                cursor.close()
            except mysql.connector.Error as err:
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

if __name__ == '__main__':
    app.run(host=route_addr, port=route_port, debug=True)
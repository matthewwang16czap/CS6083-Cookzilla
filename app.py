from flask import Flask

#UPLOAD_FOLDER = '/Users/phyllisfrankl/Documents/Magic\ Briefcase/CS3083\ Spring\ 2020/FlaskDemoSpr2020/FlaskDemoPhotos'
UPLOAD_RECIPE_FOLDER = 'RecipePhotos'
UPLOAD_EVENT_FOLDER = 'EventPhotos'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_EVENT_FOLDER'] = UPLOAD_EVENT_FOLDER
app.config['UPLOAD_RECIPE_FOLDER'] = UPLOAD_RECIPE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

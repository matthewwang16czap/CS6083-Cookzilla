from flask import Flask
import os

#UPLOAD_FOLDER = '/Users/phyllisfrankl/Documents/Magic\ Briefcase/CS3083\ Spring\ 2020/FlaskDemoSpr2020/FlaskDemoPhotos'
UPLOAD_RECIPE_FOLDER = 'static\RecipePhotos'
UPLOAD_EVENT_FOLDER = 'static\EventPhotos'
UPLOAD_REVIEW_FOLDER = 'static\ReviewPictures'
ALLOWED_IMAGE_EXTENSIONS = set(['PNG', 'JPG', 'JPEG', 'GIF'])

app = Flask(__name__, static_folder="static")
app.secret_key = "secret key"
app.config['UPLOAD_EVENT_FOLDER'] = UPLOAD_EVENT_FOLDER
app.config['UPLOAD_RECIPE_FOLDER'] = UPLOAD_RECIPE_FOLDER
app.config['UPLOAD_REVIEW_FOLDER'] = UPLOAD_REVIEW_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['ALLOWED_IMAGE_EXTENSIONS'] = ALLOWED_IMAGE_EXTENSIONS

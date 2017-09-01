from flask import Flask

from flask import send_from_directory

app = Flask(__name__)
from app import views

app.config['FIGURE_FOLDER'] = "figures"

@app.route('/uploads/<filename>')
def figure_file(filename):
    return send_from_directory(app.config['FIGURE_FOLDER'],
                               filename)

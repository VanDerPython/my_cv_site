from flask import Flask,render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
SECRET_KEY = os.urandom(32)



class FeedBackForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    message = StringField("message",validators=[DataRequired()], )
    submit = SubmitField("Submit")
app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/index")
def home_page():
    return redirect("index")


@app.route("/about")
def about():
    return render_template("about.html")
if __name__ == "__main__":
    app.run(debug=True)
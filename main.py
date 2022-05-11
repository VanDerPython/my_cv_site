from flask import Flask,render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired
import os
import re
SECRET_KEY = os.urandom(32)


# Forms
class JobForm(FlaskForm):
    place = StringField("Место работы", validators=[DataRequired()])
    date = StringField("Срок работы", validators=[DataRequired()])
    position = StringField("Должность",validators=[DataRequired()], )
    achievements = CKEditorField("Осуществленные компетенции", validators=[DataRequired()])
    submit = SubmitField("Submit")
app = Flask(__name__)
Bootstrap(app)

#Connect to DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ckeditor =CKEditor(app)
app.config["SECRET_KEY"] = SECRET_KEY

#DB TABLE
class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    job_title = db.Column(db.String(250),unique=False,nullable=False)
    working_time = db.Column(db.String(250), unique = False, nullable = False)
    achievements = db.Column(db.String(250),unique = False,nullable = False)
    position = db.Column(db.String(250), unique = False, nullable = False)

# db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/index")
def home_page():
    return redirect("index")


@app.route("/all_jobs", methods = ["GET","POST"])
def all_jobs():
    posts =JobPost.query.all()
    return render_template("all_jobs.html",posts = posts)

@app.route("/add_job", methods = ["GET","POST"])
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        new_job = JobPost(
            job_title = form.place.data,
            working_time = form.date.data,
            achievements = form.achievements.data,
            position = form.position.data
        )
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for("all_jobs"))
    return render_template("add_post.html", form=form)

@app.route("/about")
def about():
    return render_template("about.html")
if __name__ == "__main__":
    app.run(debug=True)
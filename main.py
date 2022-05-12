from flask import Flask,render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired
import sqlite3
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
#Коррекция базы данных (УДАЛИТЬ)
# db_correction = sqlite3.connect("jobs.db")
# cursor = db_correction.cursor()
# cursor.execute(f"ALTER TABLE job_post ADD COLUMN font_awesome 'string'")
ckeditor =CKEditor(app)
app.config["SECRET_KEY"] = SECRET_KEY

#DB TABLE
class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    job_title = db.Column(db.String(250),unique=False,nullable=False)
    working_time = db.Column(db.String(250), unique = False, nullable = False)
    achievements = db.Column(db.String(250),unique = False,nullable = False)
    position = db.Column(db.String(250), unique = False, nullable = False)

#db.create_all()



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/index")
def home_page():
    return redirect("index")


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
        return redirect(url_for("about"))
    return render_template("add_post.html", form=form)

@app.route("/about")
def about():
    posts = JobPost.query.all()
    return render_template("about.html", posts = posts)

@app.route("/job<int:job_post>")
def job(job_post):
    current_post = JobPost.query.get(job_post)
    return render_template("job_info.html",post = current_post)

@app.route("/edit_job/job<int:job_post>",methods=["GET","POST"])
def edit_job(job_post):
    post = JobPost.query.get(job_post)
    edit_job = JobForm(
            place = post.job_title,
            date = post.working_time,
            achievements = post.achievements,
            position = post.position)
    if request.method == "POST":
        post.job_title = edit_job.place.data
        post.working_time = edit_job.date.data
        post.achievements = edit_job.achievements.data
        post.position = edit_job.position.data
        db.session.commit()
        return redirect(url_for("job", job_post = job_post))
    return render_template("add_post.html", form =edit_job, is_edit = True)


if __name__ == "__main__":
    app.run(debug=True)
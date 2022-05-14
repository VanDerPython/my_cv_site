from flask import Flask,render_template, redirect, request, url_for,abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired
import sqlite3
from flask_login import UserMixin,login_user,LoginManager,login_required,current_user,logout_user
from functools import wraps
from werkzeug.security import  generate_password_hash, check_password_hash
import datetime as dt
import os
import re
SECRET_KEY = os.urandom(32)
def admin_only(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if current_user.id !=1:
            return abort(403)
        return f(*args,**kwargs)
    return decorated_function
# Forms
class JobForm(FlaskForm):
    place = StringField("Место работы", validators=[DataRequired()])
    date = StringField("Срок работы", validators=[DataRequired()])
    position = StringField("Должность",validators=[DataRequired()], )
    achievements = CKEditorField("Осуществленные компетенции", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")

class BlogForm(FlaskForm):
    post_title = StringField("Заголовок", validators=[DataRequired()])
    post_subtitle = StringField("Подзаголовок", validators=[DataRequired()])
    author = StringField("Автор", validators=[DataRequired()])
    topic = StringField("Тема публикации", validators=[DataRequired()])
    body = CKEditorField("Пост", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")

class RegisterForm(FlaskForm):
    name = StringField("Никнейм",validators=[DataRequired()])
    email = StringField("Адрес эл.почты", validators=[DataRequired()])
    password = StringField("Пароль",validators=[DataRequired()])
    submit = SubmitField("Подтвердить")

class LoginForm(FlaskForm):
    email = StringField("Адрес эл.почты", validators=[DataRequired()])
    password = PasswordField("Пароль",validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


app = Flask(__name__)
Bootstrap(app)

#Connect to DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
#Коррекция базы данных (УДАЛИТЬ)
# db_correction = sqlite3.connect("jobs.db")
# cursor = db_correction.cursor()
# cursor.execute(f"ALTER TABLE job_post ADD COLUMN font_awesome 'string'")
ckeditor =CKEditor(app)
app.config["SECRET_KEY"] = SECRET_KEY

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
#DB TABLE
class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    job_title = db.Column(db.String(250),unique=False,nullable=False)
    working_time = db.Column(db.String(250), unique = False, nullable = False)
    achievements = db.Column(db.String(250),unique = False,nullable = False)
    position = db.Column(db.String(6000), unique = False, nullable = False)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_title = db.Column(db.String(250), unique = True, nullable = False)
    post_subtitle = db.Column(db.String(250), unique = True, nullable = False)
    author = db.Column(db.String(250), unique = False,nullable = False)
    date = db.Column(db.String(250), unique = False, nullable = False)
    topic = db.Column(db.String(250), unique = False, nullable = False)
    body = db.Column(db.String(250), unique = True, nullable = False)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(250), unique = False, nullable = False)
    email = db.Column(db.String(250), unique = False, nullable = False)
    password = db.Column(db.String(250), unique = False, nullable = False)

# db.create_all()



@app.route("/")
def start():
    return render_template("starting_page.html")


@app.route("/index")
def index():
    return render_template("index.html",is_loggedin = current_user.is_authenticated)

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        hash_and_salted_password = generate_password_hash(
            request.form.get("password"),
            method = "pbkdf2:sha256",
            salt_length=8
        )
        new_user = Users(
            name = form.name.data,
            email = form.email.data,
            password = hash_and_salted_password

        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('blog'))
    return render_template("register.html", form=form,is_loggedin = current_user.is_authenticated)

@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Users.query.filter_by(email = email).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html", form = form,is_loggedin = current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/add_job", methods = ["GET","POST"])
@admin_only
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
    return render_template("add_job.html", form=form, current_user=current_user,is_loggedin = current_user.is_authenticated)

@app.route("/about")
def about():
    posts = JobPost.query.all()
    return render_template("about.html", posts = posts,is_loggedin = current_user.is_authenticated)

@app.route("/job<int:job_post>")
def job(job_post):
    current_post = JobPost.query.get(job_post)
    return render_template("job_info.html",post = current_post,is_loggedin = current_user.is_authenticated)

@app.route("/edit_job/job<int:job_post>",methods=["GET","POST"])
@admin_only
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
    return render_template("add_job.html", form =edit_job, is_edit = True, current_user=current_user,is_loggedin = current_user.is_authenticated)


@app.route("/blog")
def blog():
    all_posts = BlogPost.query.all()
    if current_user.is_authenticated:
        return render_template("programmer_blog.html",posts = all_posts, is_loggedin = True)
    return render_template("programmer_blog.html", is_loggedin = False )


@app.route("/add_post", methods = ["GET", "POST"])
@admin_only
def add_post():
    form = BlogForm()
    if request.method == "POST":
        new_post = BlogPost(
        post_title=form.post_title.data,
        post_subtitle = form.post_subtitle.data,
        author = form.author.data,
        date = dt.datetime.now().strftime("%d.%m.%Y"),
        topic = form.topic.data,
        body = form.body.data,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog'))
    return render_template("add_post.html", form = form, current_user = current_user,is_loggedin = current_user.is_authenticated)

@app.route("/post<post_number>")
def read_post(post_number):
    selected_post = BlogPost.query.get(post_number)
    return render_template("post.html", post = selected_post,is_loggedin = current_user.is_authenticated)

@app.route("/contacts")
def contacts():
    return render_template("contacts.html", is_loggedin = current_user.is_authenticated)

@app.route("/edit_post/post<int:post_number>", methods=["GET","POST"])
@admin_only
def edit_post(post_number):
    post = BlogPost.query.get(post_number)
    edit_post = BlogForm(
    post_title=post.post_title,
    post_subtitle = post.post_subtitle,
    author = post.author,
    topic = post.topic,
    body = post.body)
    if request.method == "POST":
        post.post_title = edit_post.post_title.data
        post.post_subtitle = edit_post.post_subtitle.data
        post.author = edit_post.author.data
        post.topic = edit_post.topic.data
        post.body = edit_post.body.data
        db.session.commit()
        return redirect(url_for('blog', blog_post=post_number))
    return render_template("add_post.html", form = edit_post, current_user = current_user)
if __name__ == "__main__":
    app.run(debug=True)

#TODO 1. Сделать раздел блога
#TODO 1.1 Сделать верстку блога
#Todo 1.1.1 Сделать CSS блога
#Todo 1.4 Добавить изображения

# TODO 2 сделать верстку понятной, что ты залогинился или нет

#Todo 3 Сделать рефактор кода
#TOdo 3.1. Сделать рефактор КСС
#Todo 3.2. Сделать рефактор темплейтов, проверить существующие классы на их наличие в КСС

#Todo 4. Исправить баги
#Todo 4.2 Баг с черным текстом на синей кнопке - исправлено
# Todo 4.3 Сделать ссылку на лого VanDerPython - сделано
#Todo 4.4. Поймать ошибку базы при попытке сделать пост с одинаковым названием
#Todo 4.5 Почему то необходим повторный логин - исправлено
#Todo 4.6 Зазвездить пароль - исправлено

#Todo 5. Защитить правами админа разделы с кнопками для админа (блог и опыт работы)

# Todo 6. Сделать портфолио
# Todo 6.1 Сделать раздел портфолио
# Todo 6.2 Сделать верстку портфолио (вероятный дизайн - две колонки, внизу отдельный див с информацией об обучающих мини-проектах)
# Todo 6.3 сделать ссылки на ГитХаб или Репл.ит с примерами кода соответтсвующих проектов
#Todo 6.4 Прикрипить примеры работы на карусель на основной странице

# Todo 7. Поставить на сервер

#Todo 8 . Решить вопрос с дизайном, подумать что можно исправить и добавить
#Todo 8.1 Цвета
# Todo 8.2 Верстка
# Todo 8.3 Оформление картинками на бэкграунд
# Todo 8.4 Осмотреть шрифты на предмет их кореляции, отсутствии прыжков
# Todo 8.5 Подумать над использованием другого шрифта, привести шрифт к единообразию

#Todo 9. Решить вопрос защиты данных, подумать над защитой от атак

#Todo 10. Страница, посвященная стеку технологий
# Todo 10.1. Краткое описание технологии, мой уровень владения ей, чем полезна
# Todo 10.2 Для основых и второстепенных технооогий

#Todo 11. Поработать над основным заполенинем сайта
#Todo 11.1 Убрать все заглушки и поставить нормальную, действующую информацию


#Todo 13 Создать див на странице о себе, посвященный пройденным курсам и прочитанным книгам


#Todo 15.1 Офомление титульной страница
#Todo 15.4 Кнопка - мои работы??

#Todo 16 Сделать реляционное взаимодействие баз
#Todo 16.1 Сделать сортировку по теме технологий

#Todo 17 сделать файловую систему

#Todo 18 Уменьшить размер значков футера

#Todo 19 Сделать высвечивание флешек при действиях логина и пр.

#Todo 20 Доработать CSS страниц с формами
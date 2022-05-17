from flask import Flask, render_template, redirect, request, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, SelectField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired
import sqlite3
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime as dt
import os
import git
import re
SECRET_KEY = os.urandom(32)
UPLOAD_FOLDER = '/files'
ALLOWED_EXTENSTION = {"txt",'pdf','png','jpg','jpeg','gif'}

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
# Forms


class JobForm(FlaskForm):
    place = StringField("Место работы", validators=[DataRequired()])
    date = StringField("Срок работы", validators=[DataRequired()])
    position = StringField("Должность", validators=[DataRequired()], )
    achievements = CKEditorField("Осуществленные компетенции", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class BlogForm(FlaskForm):
    post_title = StringField("Заголовок", validators=[DataRequired()])
    post_subtitle = StringField("Подзаголовок", validators=[DataRequired()])
    author = StringField("Автор", validators=[DataRequired()])
    topic = StringField("Тема публикации", validators=[DataRequired()])
    img = FileField("Картинки")
    body = CKEditorField("Пост", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class RegisterForm(FlaskForm):
    name = StringField("Никнейм", validators=[DataRequired()])
    email = StringField("Адрес эл.почты", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class LoginForm(FlaskForm):
    email = StringField("Адрес эл.почты", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class PortfolioForm(FlaskForm):
    project_name = StringField("Название проекта", validators=[DataRequired()])
    tech_name = StringField("Стек примененных технологий", validators=[DataRequired()])
    project_aim = SelectField("Цель проекта (коммерческий или тренировочный)",choices=[("commerce","Коммерческий"),("training", "Обучающий")], validators=[DataRequired()])
    project_body = CKEditorField("Суть проекта", validators=[DataRequired()])
    repositary_link = StringField("Ссылка на репозиторий", validators=[DataRequired()])
    img = FileField("Изображения")
    submit = SubmitField("Подтвердить")
app = Flask(__name__)
Bootstrap(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
def allowed_file(filename):
    return "." in filename and \
filename.rsplit(',',1)[1].lower() in ALLOWED_EXTENSTION
#Connect to DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

#Коррекция базы данных (УДАЛИТЬ)
# db_correction = sqlite3.connect("jobs.db")
# cursor = db_correction.cursor()
# cursor.execute(f"ALTER TABLE portfolio ADD COLUMN img 'string'")
ckeditor = CKEditor(app)
app.config["SECRET_KEY"] = SECRET_KEY


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
#DB TABLE


class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(250), unique=False, nullable=False)
    working_time = db.Column(db.String(250), unique=False, nullable=False)
    achievements = db.Column(db.String(250), unique=False, nullable=False)
    position = db.Column(db.String(6000), unique=False, nullable=False)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(250), unique=True, nullable=False)
    post_subtitle = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), unique=False, nullable=False)
    date = db.Column(db.String(250), unique=False, nullable=False)
    topic = db.Column(db.String(250), unique=False, nullable=False)
    body = db.Column(db.String(250), unique=True, nullable=False)
    img = db.Column(db.String(250), unique = False, nullable = False)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    email = db.Column(db.String(250), unique=False, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)

class Portfolio(db.Model):
    __tablename__= "portfolio"
    id = db.Column(db.Integer,primary_key=True)
    project_name = db.Column(db.String(250), unique=True, nullable=False)
    technology_id = db.Column(db.Integer, ForeignKey("technology.id"))
    project_aim = db.Column(db.String(250), unique=False, nullable=False)
    project_body = db.Column(db.String(6000), unique=False, nullable=False)
    img = db.Column(db.String(250))
    repositary_link = db.Column(db.String(250), unique=False, nullable=False)
    children = relationship("Technology", back_populates="parent")
class Technology(db.Model):
    __tablename__ = "technology"
    id = db.Column(db.Integer, primary_key = True)
    technology_name = db.Column(db.String(250), unique = True, nullable = False)
    parent = relationship("Portfolio", back_populates = "children")
db.create_all()

@app.route("/update_server", methods = ['POST'])
def webhook():
    if request.method == "POST":
        repo = git.Repo("/home/VanDerPython/.git")
        origin = repo.remotes.origin
        origin.pull()
        return "Updated PythonAnywhere successfully",200
    else:
        return "Wrong eveny type",400

@app.route("/")
def start():
    return render_template("starting_page.html")


@app.route("/index")
def index():
    return render_template("index.html", is_loggedin=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if Users.query.filter_by(email=form.email.data).first():
            flash("Пользователь с таким адресом электронной почты уже зарегистрирован")
            return redirect(url_for("login"))
        hash_and_salted_password = generate_password_hash(
            request.form.get("password"),
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = Users(
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password

        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('blog'))
    return render_template("register.html", form=form, is_loggedin=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Users.query.filter_by(email=email).first()
        if not user:
            flash("Пользователя с таким адресом электронной почты не существует")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Неправильный пароль")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html", form=form, is_loggedin=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/add_job", methods=["GET", "POST"])
@admin_only
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        new_job = JobPost(
            job_title=form.place.data,
            working_time=form.date.data,
            achievements=form.achievements.data,
            position=form.position.data
        )
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for("about"))
    return render_template("add_job.html",
                           form=form, current_user=current_user,
                           is_loggedin=current_user.is_authenticated)


@app.route("/about")
def about():
    posts = JobPost.query.all()
    dt1 = dt.datetime(2022, 2, 22)
    dt2 = dt.datetime.now()
    days_passed = dt2 - dt1

    return render_template("about.html", posts=posts, is_loggedin=current_user.is_authenticated, days = days_passed.days)


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
        file_dir = os.path.join(os.path.dirname(app.instance_path), "static/images/uploaded")
        file = form.img.data
        new_post = BlogPost(
        post_title=form.post_title.data,
        post_subtitle = form.post_subtitle.data,
        author = form.author.data,
        date = dt.datetime.now().strftime("%d.%m.%Y"),
        topic = form.topic.data,
        body = form.body.data,
        img = f"images/uploaded/blog{form.post_title.data}.png"
        )
        db.session.add(new_post)
        db.session.commit()
        if file:
            file.filename = f"blog{form.post_title.data}.png"
            safe_filename = secure_filename(file.filename)
            file.save(os.path.join(file_dir,safe_filename))
        return redirect(url_for('blog'))

    return render_template("add_post.html", form = form, current_user = current_user,is_loggedin = current_user.is_authenticated)

@app.route("/post<post_number>")
def read_post(post_number):
    selected_post = BlogPost.query.get(post_number)
    selected_file = selected_post.img
    return render_template("post.html",file = selected_file, post = selected_post,is_loggedin = current_user.is_authenticated)

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
@app.route("/blog/delete_post<int:post_number>")
@admin_only
def post_delete(post_number):
    case_to_delete = BlogPost.query.get(post_number)
    db.session.delete(case_to_delete)
    db.session.commit()
    return redirect(url_for('blog'))
@app.route("/portfolio")
def portfolio():
    all_portfolio_cases = Portfolio.query.all()
    all_techs = Technology.query.all()
    return render_template("portfolio.html", posts = all_portfolio_cases, tech = all_techs)

@app.route("/add_portfolio_case", methods = ["GET","POST"])
@admin_only
def add_portfolio_case():
    form = PortfolioForm()
    technology = Technology.query.all()
    technology_list=[item.technology_name for item in technology]
    if request.method == "POST":
        file_dir = os.path.join(os.path.dirname(app.instance_path), "static/images/uploaded")
        file = form.img.data
        new_technology_name = form.tech_name.data
        existing_technology = Technology.query.filter_by(technology_name = new_technology_name).first()
        new_case = Portfolio(
        project_name = form.project_name.data,
        project_aim = form.project_aim.data,
        technology_id = existing_technology.id,
        project_body = form.project_body.data,
        repositary_link = form.repositary_link.data,
        img = f"images/uploaded/port{form.project_name.data}.png"
        )
        db.session.add(new_case)
        db.session.commit()
        if not new_technology_name in technology_list:
            new_technology = Technology(
                technology_name=new_technology_name
            )
            db.session.add(new_technology)
            db.session.commit()
            new_case.technology_id = new_technology.id
        if file:
            file.filename = f"blog{form.project_name.data}.png"
            safe_filename = secure_filename(file.filename)
            file.save(os.path.join(file_dir, safe_filename))
        return redirect(url_for("portfolio"))
    return render_template("add_portfolio.html", form=form,  is_loggedin = current_user.is_authenticated)

@app.route("/portfolio/case<int:case>")
def portfolio_case(case):
    selected_case = Portfolio.query.get(case)
    return render_template("portfolio_case.html", post = selected_case)

@app.route("/portfolio/edit_case<int:case>", methods = ["GET","POST"])
@admin_only
def portfolio_edit(case):
    case = Portfolio.query.get(case)
    edit_case = PortfolioForm(
        project_name=case.project_name,
        tech_name=case.tech_name,
        project_aim=case.project_aim,
        project_body=case.project_body,
        repositary_link=case.repositary_link)
    if request.method == "POST":
        case.project_name = edit_case.project_name.data
        case.tech_name = edit_case.tech_name.data
        case.project_aim = edit_case.project_aim.data
        case.project_body = edit_case.project_body.data
        case.repositary_link = edit_case.repositary_link.data
        db.session.commit()
        return redirect(url_for('portfolio'))
    return render_template("add_portfolio.html", form=edit_case, current_user=current_user)
@app.route("/portfolio/delete_case<int:case>")
@admin_only
def portfolio_delete(case):
    case_to_delete = Portfolio.query.get(case)
    db.session.delete(case_to_delete)
    db.session.commit()
    return redirect(url_for('portfolio'))
if __name__ == "__main__":
    app.run(debug=True)

#TODO 1. Сделать раздел блога

#Todo 3 Сделать рефактор кода
#TOdo 3.1. Сделать рефактор КСС
#Todo 3.2. Сделать рефактор темплейтов, проверить существующие классы на их наличие в КСС

#Todo 4. Исправить баги
#Todo 4.4. Поймать ошибку базы при попытке сделать пост с одинаковым названием


# Todo 6. Сделать портфолио
# Todo 6.2 Сделать верстку портфолио (вероятный дизайн - две колонки, внизу отдельный див с информацией об обучающих мини-проектах)
#Todo 6.4 Прикрепить примеры работы на карусель на основной странице

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
# Todo 10.2 Для основых и второстепенных технологий

#Todo 11. Поработать над основным заполенинем сайта
#Todo 11.1 Убрать все заглушки и поставить нормальную, действующую информацию

#Todo 12.  Сделать отправку сообщения по почте формы

#Todo 13. Поставить паролизатор на регистрацию - done
#Todo 14. Исправить хотелки
#todo 14.1 Исправить шрифт стека технологий
#Todo 14.2

#Todo 16 Сделать реляционное взаимодействие баз
#Todo 16.1 Сделать сортировку по теме технологий
#Todo 16.2 Сдвиг титульного листа - сделано
#Todo 16.3 Добавить больше паддинга на странице контактов между способами связи - сделано
# Todo 16.4 Добавить языки в портфолио
#Todo 16.5 Добавить гугл в портфолио
#Todo 16.6 Проверить орфографию
# Todo 16.7 Активировать ссылку на гитхаб и телеграмм - сделано
# Todo 16.8 Зафиксировать размер страниц при отсутствии наполнения - сделано
#Todo 16.9 Проверить отображение залогиненых - сделано
#Todo 16.10 Отображать Имя при логине в шапке - сделано
#Todo 16.11 Заполнить нормальной информацией
#Todo 16.12 Решить с кнопкой посмотреть проекты, если они отображатся внизу - сделано
#Todo 16.13 Посмотреть вопрос с доступами на сайт в раздел блога и прочего - сделано
#Todo 16.14 Сделать замену кнопки логина на вход
#Todo 16.15 Увеличить шрифт форм - сделать

#Todo 17 сделать файловую систему


# Todo 18 Сделать hr немного потемнее
#Todo 20 Доработать CSS страниц с формами - сделано
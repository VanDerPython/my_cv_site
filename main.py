from flask import Flask,render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired
import sqlite3
import datetime as dt
import os
import re
SECRET_KEY = os.urandom(32)


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
    position = db.Column(db.String(6000), unique = False, nullable = False)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_title = db.Column(db.String(250), unique = True, nullable = False)
    post_subtitle = db.Column(db.String(250), unique = True, nullable = False)
    author = db.Column(db.String(250), unique = False,nullable = False)
    date = db.Column(db.String(250), unique = False, nullable = False)
    topic = db.Column(db.String(250), unique = False, nullable = False)
    body = db.Column(db.String(250), unique = True, nullable = False)


db.create_all()



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
    return render_template("add_job.html", form=form)

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
    return render_template("add_job.html", form =edit_job, is_edit = True)


@app.route("/blog")
def blog():
    all_posts = BlogPost.query.all()
    return render_template("programmer_blog.html",posts = all_posts)

@app.route("/add_post", methods = ["GET", "POST"])
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
    return render_template("add_post.html", form = form)

@app.route("/post<post_number>")
def read_post(post_number):
    selected_post = BlogPost.query.get(post_number)
    return render_template("post.html", post = selected_post)

if __name__ == "__main__":
    app.run(debug=True)

#TODO 1. Сделать раздел блога
#TODO 1.1 Сделать верстку блога
#Todo 1.1.1 Сделать CSS блога
#TODO 1.2. Добавить подзаголовок в таблицу
#TODO 1.3 Создать путь для блога, логику для блога
#Todo 1.3.1 Блог должен принимать информацию от админа, форматировать ее и ставить на страницу как пост
#Todo 1.3.3. Доступ - только зарегистрированным и авторизованным пользователям, иначе - уведомление о необходимости регистрации
#Todo 1.4 Добавить изображения
#Todo 1.5 Сделать страницу поста
#Todo 1.5.1 Сделать верстку страницы поста
#Todo 1.5.2 Сделать возможность редактирования поста

#Todo 2 Сделать регистрацию
#Todo 2.1 Сделать интерфейс регистрации
#Todo 2.2. Сделать таблицу пользователей
#Todo 2.3 Сделать функционал для зарегистрированных пользователей
#Todo 2.3.1 Основной функционал - просмотр блога

#Todo 3 Сделать рефактор кода
#TOdo 3.1. Сделать рефактор КСС
#Todo 3.2. Сделать рефактор темплейтов, проверить существующие классы на их наличие в КСС

#Todo 4. Исправить баги
#Todo 4.1 Баг с отображением таймлайна(есть прерывистые линии)
#Todo 4.2 Баг с черным текстом на синей кнопке
# Todo 4.3 Сделать ссылку на лого VanDerPython
#Todo 4.4. Поймать ошибку базы при попытке сделать пост с одинаковым названием

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

# Todo 12 Убрать информацию об образовании в серую часть на странице о себе

#Todo 13 Создать див на странице о себе, посвященный пройденным курсам и прочитанным книгам

#Todo 14 Сделать раздел "Контакты"
#Todo 14.1 продублировать форму для обратной связи
#Todo 14.2. Основные данные о своих контактах
#Todo 14.3 Подумать, нужен ли он вообще

#Todo 15 Сделать титулную страницу
#Todo 15.1 Офомление титульной страница
#Todo 15.2 Кнопка контактов
#Todo 15.3 Кнопка  исследовать сайт
#Todo 15.4 Кнопка - мои работы??

#Todo 16 Сделать реляционное взаимодействие баз
#Todo 16.1 Сделать сортировку по теме технологий

#Todo 17 сделать файловую систему

#Todo 18 Уменьшить размер значков футера
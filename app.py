from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)
from datetime import datetime
from flask_session import Session
from models import db, Question
import sqlite3
import re
import random

'''Fatemeh code:'''
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
Session(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

with app.app_context():
    db.create_all()
#Questions show
@app.route('/question',methods=['GET', 'POST'])
@login_required
def category_index():
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    if request.method == 'POST':
        category=request.form['category']
        return redirect(f'/question/{category}')
    return render_template('category_index.html')

@app.route('/question/<category>')
def index(category):
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    questions = Question.query.filter(Question.category==category)
    if category!='math' and category!='historical' and category!='game' and category!='soccer' and category!='movie' and category!='general_information':
        return render_template('404.html')
    else:
        category=list(category)
        category[0]=category[0].upper()
        return render_template('index.html', questions=questions,category=(''.join(category)))

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        answer = request.form['answer']
        print(f'User  answer: {answer}') 
        return redirect('/')
    return render_template('question.html', question=question)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    if request.method == 'POST':
        text = (request.form['text']).strip()
        option1 = (request.form['option1']).strip()
        option2 = (request.form['option2']).strip()
        option3 = (request.form['option3']).strip()
        option4 = (request.form['option4']).strip()
        correct_answer = request.form['correct_answer']
        category=request.form['category']

        new_question = Question(text=text, option1=option1, option2=option2,
                                option3=option3, option4=option4,
                                correct_answer=correct_answer,category=category)
        db.session.add(new_question)
        db.session.commit()
        flash("Question added!")
        return redirect('/add_question')
    return render_template('add_question.html')

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    question = Question.query.get_or_404(question_id)
    questiondir=question.category
    db.session.delete(question)
    db.session.commit()
    return redirect(f'/question/{questiondir}')

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("instance/questions.db")
    cursor = conn.execute('SELECT * FROM question WHERE id = ?',(question_id,))
    
    for row in cursor:
        edit_question=row[1]
        edit_awnser1=row[2]
        edit_awnser2=row[3]
        edit_awnser3=row[4]
        edit_awnser4=row[5]
        edit_correct_awnser=row[6]
        edit_category=row[7]
    try:
        if request.form ['submit_button']=='Save changes':
            text = (request.form['text']).strip()
            option1 = (request.form['option1']).strip()
            option2 = (request.form['option2']).strip()
            option3 = (request.form['option3']).strip()
            option4 = (request.form['option4']).strip()
            correct_answer = request.form['correct_answer']
            category = request.form['category']
            conn.execute('''UPDATE question SET text = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, correct_answer = ?,  category = ? WHERE id = ?''',(text, option1,option2,option3,option4,correct_answer,category,question_id))
            conn.commit()
            conn.close()
            return redirect('/question')
    except:
        return render_template('edit_question.html', edit_question=edit_question,
                           edit_awnser1=edit_awnser1,
                           edit_awnser2=edit_awnser2,
                           edit_awnser3=edit_awnser3,
                           edit_awnser4=edit_awnser4,
                           edit_correct_awnser=edit_correct_awnser,
                           category=edit_category)
    

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return User(
            id=user_data[0],
            username=user_data[1],
            password=user_data[2],
            is_admin=user_data[3],
        )
    return None


# Database building
def init_sqlite_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        is_admin BOOLEAN NOT NULL DEFAULT 0)"""
    )
    conn.commit()
    conn.close()

init_sqlite_db()

def createuser_sqlite_db(userfor):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS "+userfor+" (id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT NOT NULL,correct TEXT NOT NULL,questions TEXT NOT NULL,date TEXT NOT NULL)")
    conn.commit()
    conn.close()


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        username_pattern = re.compile(r"^(?=\S+$).{3,}$")
        password_pattern = re.compile(r"^(?=\S+$)(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")

        if not username_pattern.match(username):
            flash("Username must be at least 3 characters and contain no spaces.")
            return render_template("register.html")

        if not password_pattern.match(password):
            flash(
                "Password must be at least 8 characters, contain at least one number, one capital letter, and one special symbol without spaces."
            )
            return render_template("register.html")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This username is already registered!")
            return render_template("register.html")

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            flash("Registration was successful. Now you can login.")
        except Exception as e:
            flash(f"Error occurred: {str(e)}")
        finally:
            conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form["username"]
        new_password = request.form["password"]

        username_pattern = re.compile(r"^(?=\S+$).{3,}$")
        password_pattern = re.compile(r"^(?=\S+$)(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")

        if not username_pattern.match(new_username):
            flash("Username must be at least 3 characters and contain no spaces.")
            return redirect(url_for("edit_profile"))

        if not password_pattern.match(new_password):
            flash(
                "Password must be at least 8 characters, contain at least one number, one capital letter, and one special symbol without spaces."
            )
            return redirect(url_for("edit_profile"))

        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_username, new_password, current_user.id))
        conn.commit()
        conn.close()

        flash("Your profile has been updated successfully.")
        return redirect(url_for("dashboard"))

    return render_template("profile.html", username=current_user.username)

# user login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        )
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user = User(
                id=user_data[0],
                username=user_data[1],
                password=user_data[2],
                is_admin=user_data[3],
            )
            login_user(user)
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Username or password is incorrect!")

    return render_template("login.html")

@app.route("/")
@app.route("/home")
def home():
    if not current_user.is_authenticated:
        return render_template("home.html")
    else:
        if session.get("is_admin"):
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("dashboard"))

        

@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("is_admin"):
        flash("Access Denied! Only members can access this page.")
        logout_user()
    createuser_sqlite_db(current_user.username)
    flash("You have successfully logged in.")
    return render_template("dashboard.html", username=current_user.username)


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_username = request.form["admin_username"]
        admin_password = request.form["admin_password"]

        if admin_username == "admin" and admin_password == "adminadmin":
            admin = User(
                id=1, username=admin_username, password=admin_password, is_admin=True
            )
            login_user(admin)
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin username or password.")

    return render_template("admin_login.html")


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if not session.get("is_admin"):
        flash("Access Denied! Only admin can access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    flash("You have successfully logged in as admin.")
    return render_template("admin_dashboard.html", username=current_user.username)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("is_admin", None)
    flash("You have successfully logged out.")
    return redirect(url_for("login"))


@app.route("/admin_logout")
@login_required
def admin_logout():
    logout_user()
    session.pop("is_admin", None)
    flash("You have successfully logged out.")
    return redirect(url_for("admin_login"))


@app.route('/user_question')
@login_required
def index_question():
       if  session.get("is_admin"):
        flash("Access Denied! Admins cannot access this page.")
        logout_user()
        return redirect(url_for("login"))
       return render_template('index_question.html')

@app.route('/quiz', methods=['POST'])
@login_required
def quiz():
        if  session.get("is_admin"):
            flash("Access Denied! Admins cannot access this page.")
            logout_user()
            return redirect(url_for("login"))
        global category_id
        category_id = request.form['category']
        num_questions = int(request.form['num_questions'])
        questions = Question.query.filter_by(category=category_id).all()
        question_random=list()
        for question in questions:
            question_random.append(question.id)
        random_choice=random.sample(question_random,k=num_questions)
        global questions_choose
        questions_choose = Question.query.filter(Question.id.in_(random_choice)).all()
        return render_template('quiz.html', questions=questions_choose)

@app.route('/result', methods=['POST'])
@login_required
def result():
       if  session.get("is_admin"):
        flash("Access Denied! Admins cannot access this page.")
        logout_user()
        return redirect(url_for("login"))
       score = 0
       total_questions = len(request.form)
       stat_selected_option=dict()
       for key in request.form:
           if key.startswith('question_'):
               question_id = key.split('_')[1]
               selected_option = request.form[key]
               question = Question.query.get(question_id)
               stat_selected_option[question.id]=(selected_option)
               if selected_option == question.correct_answer:
                   score += 1
       datetime_=datetime.now()
       date=datetime_.strftime("%d/%m/%Y")
       time=datetime_.strftime("%H:%M:%S")
       datequiz=f'{date} {time}'
       conn = sqlite3.connect("users.db")
       cursor = conn.cursor()
       score=str(score)
       total_questions=str(total_questions)
       cursor.execute("INSERT INTO "+current_user.username+" (category, correct, questions, date) VALUES (?, ?, ?, ?)",(category_id, score, total_questions, datequiz),)
       conn.commit()
       conn.close()
       score=int(score)
       total_questions=int(total_questions)
       return render_template('result.html', score=score, total_questions=total_questions, questions=questions_choose,stat_selected_option=stat_selected_option)

@app.route('/stats/<category>')
def stats(category):
        if session.get("is_admin"):
            flash("Access Denied! Admins cannot access this page.")
            logout_user()
            return redirect(url_for("login"))
        conn = sqlite3.connect("users.db")
        cursor = conn.execute("SELECT * FROM "+current_user.username+"")
        stat=cursor.fetchall()
        conn.close()
        if category!='math' and category!='historical' and category!='game' and category!='soccer' and category!='movie' and category!='general_information':
            return render_template('404.html')
        else:
            category=list(category)
            category[0]=category[0].upper()
            for i,b in enumerate(stat):
                stat[i]=[]
                for l in b:
                    stat[i].append(l)
            return render_template('stats.html', questions=stat,category=(''.join(category)))


@app.route('/selectstats',methods=['GET', 'POST'])
@login_required
def select_stats():
    if session.get("is_admin"):
        flash("Access Denied! Admins cannot access this page.")
        logout_user()
        return redirect(url_for("admin_login"))
    if request.method == 'POST':
        category=request.form['category']
        return redirect(f'/stats/{category}')
    return render_template('selectstats.html')

if __name__ == '__main__':
        app.run(debug=True)
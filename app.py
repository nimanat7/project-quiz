from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Question
import sqlite3
import re


'''Fatemeh code:'''
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
#hello
with app.app_context():
    db.create_all()
#Questions show
@app.route('/question',methods=['GET', 'POST'])
def category_index():
    if request.method == 'POST':
        category=request.form['category']
        return redirect(f'/question/{category}')
    return render_template('category_index.html')

@app.route('/question/<category>')
def index(category):
    category=category
    questions = Question.query.filter(Question.category==category)
    if category!='math' and category!='historical' and category!='game' and category!='soccer' and category!='movie' and category!='english' and category!='general_information':
        return render_template('404.html')
    else:
        return render_template('index.html', questions=questions)

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        answer = request.form['answer']
        print(f'User  answer: {answer}') 
        return redirect('/')
    return render_template('question.html', question=question)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        text = request.form['text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']
        category=request.form['category']

        new_question = Question(text=text, option1=option1, option2=option2,
                                option3=option3, option4=option4,
                                correct_answer=correct_answer,category=category)
        db.session.add(new_question)
        db.session.commit()
        return redirect('/question')
    return render_template('add_question.html')

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect('/question')

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
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
        if request.form ['submit_button']=='اعمال تغییرات سوال':
            text = request.form['text']
            option1 = request.form['option1']
            option2 = request.form['option2']
            option3 = request.form['option3']
            option4 = request.form['option4']
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
    

'''Nima code:'''
# Database building
def init_sqlite_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT)"""
    )
    conn.commit()
    conn.close()


init_sqlite_db()


# have problems
# Registration


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")

        if not password_pattern.match(password):
            flash(
                "Password must be at least 8 characters, contain at least one number, one capital letter and one special symbol!"
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
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, 'None'),
            )
            conn.commit()
            flash("Registration was successful.Now You can login.")
        except Exception as e:
            flash(f"Error occurred: {str(e)}")
        finally:
            conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# have problems
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
        user = cursor.fetchone()

        conn.close()

        if user:
            flash("Login successfully!")
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Username or password is incorrect!")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return f"welcome , {session['username']}!"
    else:
        return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)


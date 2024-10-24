from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Question

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/question')
def index():
    questions = Question.query.all()
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

        new_question = Question(text=text, option1=option1, option2=option2,
                                option3=option3, option4=option4,
                                correct_answer=correct_answer)
        db.session.add(new_question)
        db.session.commit()
        return redirect('/')
    return render_template('add_question.html')

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect('/')

# Database building
def init_sqlite_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL)"""
    )
    conn.commit()
    conn.close()


init_sqlite_db()


# have problems
# Registration


#@app.route("/")
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
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
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


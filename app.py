from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "your_secret_key"


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
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")

        if not password_pattern.match(password):
            flash(
                "Password must be at least 8 characters, contain at least one number, one capital letter and one special symbol."
            )
            return render_template("register.html")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This username is already registered.")
            return render_template("register.html")

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()
        conn.close()

        flash("Registration was successful. You can login.")
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
            flash("Username or password is incorrect.")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return f"welcome , {session['username']}!"
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

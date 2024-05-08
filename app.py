from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)

def retrieveKey():
    with open("secret_key.txt") as key:
        return key.read()

app.secret_key = retrieveKey()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

@app.route("/weight", methods=["GET", "POST"])
@login_required
def weight():
    if request.method == "POST":
        #Get goal weight information from the form and store in db.
        current_weight = request.form.get("current weight")
        goal_weight = request.form.get("goal weight")
        goal_step = request.form.get("goal step")
        goal_direction = 0
        if current_weight > goal_weight:
            goal_direction = -1
        elif current_weight < goal_weight:
            goal_direction = 1
        else:
            goal_direction = 0
        # TO-DO: Calculate BMI
        bmi = 0
        return redirect("/weight")
    else:
        #TO-DO: Query database on GET request and if no goals set, force user to set goal.
        return render_template("weight.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #Retrieve username, password, and confirmation and handle non-input errors
        form_username = request.form.get("username").lower()
        form_password = request.form.get("password")
        form_confirmation = request.form.get("confirmation")
        if not form_username:
            errormsg = "Please enter a username to register."
            return render_template("register.html", errormsg=errormsg)
        if not form_password:
            errormsg = "Please enter a password to register."
            return render_template("register.html", errormsg=errormsg)
        if form_password != form_confirmation:
            errormsg = "Password does not match confirmation."
            return render_template("register.html", errormsg=errormsg)
        #Query database to see if username already exists
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        res = cur.execute("SELECT * FROM users WHERE username = ?", (form_username,))
        username_res = res.fetchall()
        cur.close()
        if username_res:
            errormsg = "Username already exists. Please enter a different username."
            return render_template("register.html", errormsg=errormsg)
        #If username does not exist, hash password and store it in database.
        cur_writeuser = con.cursor()
        hashed_password = bcrypt.generate_password_hash(form_password).decode('utf-8')
        cur_writeuser.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (form_username, hashed_password,))
        con.commit()
        con.close()
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    if request.method == "POST":
        #Get username from form and check against database
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        username = request.form.get("username").lower()
        res = cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        username_res = res.fetchone()
        con.close()
        #If username is not in database, send error telling user to register.
        if not username_res:
            errormsg = "Username could not be found. Please register if you do not have an account."
            return render_template("login.html", errormsg=errormsg)
        #user_hash is assigned to the row selected, 2nd index is hash.
        user_hash = username_res[2]
        user_id = username_res[0]
        password_plaintext = request.form.get("password")
        is_password_valid = bcrypt.check_password_hash(user_hash, password_plaintext)
        if is_password_valid:
            session["user"] = username
            session["user_id"] = user_id
            return redirect("/")
        else:
            errormsg = "Password is incorrect. Please try again."
            return render_template("login.html", errormsg=errormsg)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_id")
    return redirect("/login")
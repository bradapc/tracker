from flask import Flask, render_template, request, redirect
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

def getUsername():
    pass

@app.route("/")
def index():
    return render_template("index.html")

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
    if request.method == "POST":
        #Get username from form and check against database
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        username = request.form.get("username").lower()
        res = cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        username_res = res.fetchall()
        con.close()
        #If username is not in database, send error telling user to register.
        if not username_res:
            errormsg = "Username could not be found. Please register if you do not have an account."
            return render_template("login.html", errormsg=errormsg)
        #user_hash is assigned to the row selected, 2nd index is hash.
        user_hash = username_res[0][2]
        password_plaintext = request.form.get("password")
        is_password_valid = bcrypt.check_password_hash(user_hash, password_plaintext)
        if is_password_valid:
            return redirect("/")
        else:
            errormsg = "Password is incorrect. Please try again."
            return render_template("login.html", errormsg=errormsg)
    else:
        return render_template("login.html")
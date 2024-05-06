from flask import Flask, render_template, request, redirect
import sqlite3
import bcrypt

app = Flask(__name__)

@app.route("/")
def index():
    return "You're in!"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #Get username from form and check against database
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        username = request.form.get("username")
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
        if password_plaintext == user_hash:
            return redirect("/")
        else:
            errormsg = "Password is incorrect. Please try again."
            return render_template("login.html", errormsg=errormsg)
        #password = str.encode(password_plaintext)
        #salt = bcrypt.gensalt()
        #hashed = bcrypt.hashpw(password, salt)
    else:
        return render_template("login.html")
from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime

#TODO: Use JS for visual feedback on form validation, not flask.
#Use flask for validation but only to redirect because app.py becomes bloated otherwise with
#errormsgs.

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

def convertImperialWeightToMetric(weight):
    return 0.45359237 * weight

def convertMetricWeightToImperial(weight):
    return 2.204623 * weight

def convertImperialHeightToMetric(height):
    return 2.54 * height

def convertMetricHeightToImperial(height):
    return height / 2.54

def getUnits(weight_goals):
    units = {}
    if weight_goals['units'] == "metric":
        units['weight_unit'] = "kg"
        units['height_unit'] = "cm"
    elif weight_goals['units'] == "imperial":
        units['weight_unit'] = "lb"
        units['height_unit'] = "inches"
    return units

def weightGoalExists():
    con = sqlite3.connect("tracker.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute("SELECT * FROM weight_goals WHERE user_id = ?", (session['user_id'],))
    res = res.fetchone()
    cur.close()
    con.close()
    return res

def getWeightLog():
    con = sqlite3.connect("tracker.db")
    cur = con.cursor()
    con.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM weight_log WHERE user_id = ?", (session['user_id'],))
    weight_log = []
    weight_log = cur.fetchall()
    cur.close()
    con.close()
    return weight_log

def getFormattedDateTime():
    current_time = datetime.now()
    dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string

def splitDateTime(weight_log):
    new_weight_log = []
    for entry in weight_log:
        new_entry = []
        dt_list = entry[2].split()
        dt_list[1] = dt_list[1][0:5]
        new_entry.append(entry[0])
        new_entry.append(entry[1])
        new_entry.append(dt_list[0])
        new_entry.append(dt_list[1])
        new_weight_log.append(new_entry)
    return new_weight_log


@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

@app.route("/weight", methods=["GET", "POST"])
@login_required
def weight():
    if weightGoalExists():
        return redirect("/weight/log")
    if request.method == "POST":
        #Get goal weight information from the form.
        current_weight = request.form.get("current weight")
        goal_weight = request.form.get("goal weight")
        goal_step = request.form.get("goal step")
        goal_direction = 0
        #Error handle incorrectly filled out fields.
        if not current_weight or not goal_weight:
            errormsg = "Please fill out all form fields to set a goal."
            return render_template("weight.html", errormsg=errormsg)
        else:
            try:
                current_weight = float(current_weight)
                goal_weight = float(goal_weight)
            except:
                errormsg = "Please enter a number in the weight fields to set a goal."
                return render_template("weight.html", errormsg=errormsg)
        #Specify goal direction based on weight difference (lose vs gain vs maintain).
        if current_weight > goal_weight:
            goal_direction = -1
        elif current_weight < goal_weight:
            goal_direction = 1
        else:
            goal_direction = 0

        # Calculate BMI
        selected_unit = request.form['units']
        bmi = 0

        if selected_unit == "imperial":
            height_in_feet = request.form.get("feet")
            height_in_inches = request.form.get("inches")
            height = 0
            #Error handle incorrect entries into height fields.
            if not height_in_feet or not height_in_inches:
                errormsg = "Please fill out all form fields to set a goal."
                return render_template("weight.html", errormsg=errormsg)
            else:
                try:
                    height = (float(height_in_feet) * 12) + float(height_in_inches)
                except:
                    errormsg = "Please enter a number in the height fields to set a goal."
                    return render_template("weight.html", errormsg=errormsg)
            bmi = 703 * (current_weight / height**2)

        elif selected_unit == "metric":
            height = request.form.get("cm")
            if not height:
                errormsg = "Please fill out all form fields to set a goal."
                return render_template("weight.html", errormsg=errormsg)
            try:
                height = float(height)
            except:
                errormsg = "Please enter a number in the height field to set a goal."
                return render_template("weight.html", errormsg=errormsg)
            bmi = current_weight / (height / 100)**2
        
        #Get current date and time for insertion into database
        dt_string = getFormattedDateTime()

        #Enter data in database weight_goals table if no weight goal exists
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        if weightGoalExists():
            cur.execute("UPDATE weight_goals SET goal_weight = ?, goal_step = ?, height = ?, goal_direction = ?, units = ?, time = ? WHERE user_id = ?", (goal_weight, goal_step, height, goal_direction, selected_unit, dt_string, session['user_id']),)
            #TODO: add log into weight_log for goal updates (goal updates not added yet)
            con.commit()
        else:
            cur.execute("INSERT INTO weight_goals (user_id, goal_weight, goal_step, height, goal_direction, units, time) VALUES(?, ?, ?, ?, ?, ?, ?)", (session['user_id'], goal_weight, goal_step, height, goal_direction, selected_unit, dt_string,))
            cur.execute("INSERT INTO weight_log (user_id, weight, time) VALUES(?, ?, ?)", (session['user_id'], current_weight, dt_string,))
            con.commit()
        cur.close()
        con.close()
        return redirect("/weight/log")
    else:
        return render_template("weight.html")

@app.route("/weight/log", methods=["GET", "POST"])
@login_required
def weight_log():
    weight_goals = weightGoalExists()
    if not weight_goals:
        return redirect("/weight")
    weight_log = getWeightLog()
    units = getUnits(weight_goals)
    new_weight_log = splitDateTime(weight_log)
    #TODO: Allow addition of weights
    #TODO: Graphs / data
    #TODO: Lowest weight, bmi, etc.
    if request.method == "POST":
        new_weight_entry = request.form.get("weight-entry")
        if not new_weight_entry:
            errormsg = "Please enter a weight."
            return render_template("weight_log.html", errormsg=errormsg, user=session['user'], weight_goals=weight_goals, units=units, new_weight_log=new_weight_log)
        try:
            new_weight_entry = float(new_weight_entry)
        except:
            errormsg = "Please enter only numbers into the weight form."
            return render_template("weight_log.html", errormsg=errormsg, user=session['user'], weight_goals=weight_goals, units=units, new_weight_log=new_weight_log)
        dt_string = getFormattedDateTime()
        #Insert entry into database
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        cur.execute("INSERT INTO weight_log (user_id, weight, time) VALUES(?, ?, ?)", (session['user_id'], new_weight_entry, dt_string,))
        con.commit()
        return redirect("/weight/log")
    else:
        return render_template("weight_log.html", user=session['user'], weight_goals=weight_goals, units=units, new_weight_log=new_weight_log)

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
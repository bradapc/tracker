from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime
import re

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
    cur.execute("SELECT * FROM weight_log WHERE user_id = ? ORDER BY time DESC", (session['user_id'],))
    weight_log = []
    weight_log = cur.fetchall()
    cur.close()
    con.close()
    return weight_log

def getFormattedDateTime():
    current_time = datetime.now()
    dt_string = current_time.strftime("%d-%m-%Y")
    return dt_string

def computeBMI(height, weight, units):
    bmi = 0
    if units == 'imperial':
        bmi = 703 * (weight / height**2)
    elif units == 'metric':
        bmi = weight / (height / 100)**2
    return bmi

def addBMI(log, height, units):
    weight_log = []
    for row in log:
        bmi = computeBMI(height, row['weight'], units)
        bmi_str = "%0.1f" % bmi
        row['bmi'] = bmi_str
        weight_log.append(row)
    return weight_log

def getUserGoals():
    con = sqlite3.connect("tracker.db")
    cur = con.cursor()
    cur.execute("SELECT goal_id, goal_title, goal_desc FROM user_goals WHERE user_id = ?", (session['user_id'],))
    user_goals = []
    user_goals = cur.fetchall()
    return user_goals

def isProperDateString(date_input):
    date = date_input.split("-")
    if (not (re.search("[0-9][0-9][0-9][0-9]", date[0]) and
        re.search("0|1[0-9]", date[1]) and
        re.search("[0-31]", date[2]))):
            return False
    return True

def convertWLTupleToList(log):
    new_log = []
    for row in log:
        new_row = {}
        new_row['log_id'] = row[0]
        new_row['user_id'] = row[1]
        new_row['weight'] = row[2]
        new_row['time'] = row[3]
        new_log.append(new_row)
    return new_log


@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    user_goals = getUserGoals()
    if request.method == "POST":
        goal_title = request.form.get("goal title")
        goal_description = request.form.get("goal description")
        if len(goal_title) > 80 or len(goal_description) > 500:
            return redirect("/goals")
        if not goal_title or not goal_description:
            return redirect("/goals")
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        cur.execute("INSERT INTO user_goals (user_id, goal_title, goal_desc) VALUES(?, ?, ?)", (session['user_id'], goal_title, goal_description,))
        con.commit()
        con.close()
        return redirect("/goals")
    else:
        return render_template("goals.html", user=session['user'], user_goals=user_goals)
    
@app.route("/goals/remove", methods=["GET", "POST"])
@login_required
def goals_remove():
    if request.method == "POST":
        goal_id = request.form['remove_goal']
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        cur.execute("DELETE FROM user_goals WHERE goal_id = ?", (goal_id,))
        con.commit()
        return redirect("/goals")
    else:
        return redirect("/goals")

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
        
        #Get current date for insertion into database
        dt_string = getFormattedDateTime()

        #Enter data in database weight_goals table if no weight goal exists
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        if weightGoalExists():
            cur.execute("UPDATE weight_goals SET goal_weight = ?, goal_step = ?, height = ?, goal_direction = ?, units = ?, time = ? WHERE user_id = ?", (goal_weight, goal_step, height, goal_direction, selected_unit, dt_string, session['user_id']),)
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
    weight_log_tuple = getWeightLog()
    weight_log = convertWLTupleToList(weight_log_tuple)
    units = getUnits(weight_goals)
    weight_log = addBMI(weight_log, weight_goals['height'], weight_goals['units'])
    min_entry = min(weight_log, key=lambda x:x['weight'])
    max_entry = max(weight_log, key=lambda x:x['weight'])

    #Stats for progress over log
    date_format = "%Y-%m-%d"
    first_entry = weight_log[len(weight_log) - 1]
    last_entry = weight_log[0]
    a = datetime.strptime(first_entry['time'], date_format)
    b = datetime.strptime(last_entry['time'], date_format)
    delta = b - a
    weight_diff = last_entry['weight'] - first_entry['weight']

    stats = {
        'min_weight': min_entry,
        'max_weight': max_entry,
        'weight_diff': weight_diff,
        'days_diff': delta.days
    }
    if request.method == "POST":
        new_weight_entry = request.form.get("weight-entry")
        weight_entry_date = request.form.get("date set")
        if not isProperDateString(weight_entry_date):
            errormsg = "Invalid date."
            return render_template("weight_log.html", errormsg=errormsg, user=session['user'], weight_goals=weight_goals, units=units, weight_log=weight_log, stats=stats)
        if not new_weight_entry:
            errormsg = "Please enter a weight."
            return render_template("weight_log.html", errormsg=errormsg, user=session['user'], weight_goals=weight_goals, units=units, weight_log=weight_log, stats=stats)
        try:
            new_weight_entry = float(new_weight_entry)
        except:
            errormsg = "Please enter only numbers into the weight form."
            return render_template("weight_log.html", errormsg=errormsg, user=session['user'], weight_goals=weight_goals, units=units, weight_log=weight_log, stats=stats)
        dt_string = weight_entry_date
        #Insert entry into database
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        cur.execute("INSERT INTO weight_log (user_id, weight, time) VALUES(?, ?, ?)", (session['user_id'], new_weight_entry, dt_string,))
        con.commit()
        return redirect("/weight/log")
    else:
        return render_template("weight_log.html", user=session['user'], weight_goals=weight_goals, units=units, weight_log=weight_log, stats=stats)

@app.route("/weight/log/delete", methods=["POST"])
@login_required
def weight_log_delete():
    log_id = request.form['delete log']
    con = sqlite3.connect("tracker.db")
    cur = con.cursor()
    cur.execute("DELETE FROM weight_log WHERE log_id = ?", (log_id,))
    con.commit()
    return redirect("/weight/log")

@app.route("/weight/log/edit", methods=["POST"])
@login_required
def weight_log_edit():
    weight_input = request.form.get("weight edit")
    date_input = request.form.get("date edit")
    if not weight_input or not date_input:
        return redirect("/weight/log")
    date = date_input.split("-")
    if not isProperDateString(date_input):
        return redirect("/weight/log")
    dt_string = date[2] + "/" + date[1] + "/" + date[0]
    id = request.form['button edit log']
    con = sqlite3.connect("tracker.db")
    cur = con.cursor()
    cur.execute("UPDATE weight_log SET weight = ?, time = ? WHERE log_id = ?", (weight_input, dt_string, id,))
    con.commit()
    return redirect("/weight/log")

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
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return "You're in!"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("login.html")
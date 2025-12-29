from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "leadtracker_secret"

def get_db():
    return sqlite3.connect("database.db")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT id FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cur.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (email, password) VALUES (?,?)",
            (email, password)
        )
        db.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, name, phone, service, status FROM leads WHERE user_id=?",
        (session["user_id"],)
    )
    leads = cur.fetchall()
    return render_template("dashboard.html", leads=leads)

@app.route("/add", methods=["GET", "POST"])
def add_lead():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        service = request.form["service"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO leads (user_id, name, phone, service, status) VALUES (?,?,?,?,?)",
            (session["user_id"], name, phone, service, "New")
        )
        db.commit()
        return redirect("/dashboard")

    return render_template("add_lead.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/update/<int:lead_id>", methods=["POST"])
def update_status(lead_id):
    if "user_id" not in session:
        return redirect("/")

    new_status = request.form["status"]

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE leads SET status=? WHERE id=? AND user_id=?",
        (new_status, lead_id, session["user_id"])
    )
    db.commit()
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)
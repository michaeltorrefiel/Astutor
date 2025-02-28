from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost", user="root", password="root", database="flask_login_db"
)
cursor = db.cursor()


@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pass = hashlib.sha256(
            password.encode()
        ).hexdigest()  # password encryption

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:  # check if user exists
            flash(
                "User already exists. Please choose a different username.", "error"
            )  # if user exist, return error message where user already exists
            return redirect(url_for("register"))

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_pass),
        )  # if user does not exist, save to db
        db.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))  # redirect to login page

    return render_template("register.html")


@app.route("/login")  # temp login
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)

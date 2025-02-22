from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from datetime import datetime
import random

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'temp_astutor'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

def query_exec(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return(rows)

def one_time_password():
    otp = ""
    for _ in range(6):
        otp += str(random.randint(0, 9))
    return otp

def otp_verification(email, otp):
    rows = query_exec(f"select otp from otps where email = '{email}'")
    if not rows:
        return False
    
    if otp == rows[0]["otp"]:
        return True
    return False

@app.route("/")
def home_page():
    home = """
    <h1>Astutor</h1>
    """
    return home

@app.route("/student", methods=["GET"])
def get_records():

    rows = query_exec("select * from students")
    
    return make_response(jsonify(rows), 200)

@app.route("/otp", methods=["POST"])
def get_otp():
    conn = mysql.connection
    cur = conn.cursor()

    info = request.get_json()
    email = info["email"]
    generated_otp = one_time_password()

    try:
        cur.execute(
        f"""
            insert into otps(email, otp) value('{email}', '{generated_otp}')
        """
        )

        conn.commit()

        db_otp = query_exec(f"select otp from otps where email = '{email}'")
        otp = db_otp[0]["otp"] if db_otp else None

        return make_response(jsonify({"message": "otp sent successfully", "otp": otp}), 201)
    
    except Exception as e:
        conn.rollback()
        return make_response(jsonify({"error": str(e)}), 500)

    finally:
        cur.close()

@app.route("/student", methods=["POST"])
def sign_up():
    conn = mysql.connection
    cur = conn.cursor()

    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    email = info["email"]
    otp = info["otp"]
    age = info["age"]
    gender = info["gender"]

    if otp_verification(email, otp) == False:
        return make_response(jsonify({"message": "otp is wrong"}), 401)

    try:
        cur.execute(
            f"""
            insert into students(first_name, last_name, email, age, gender) value('{first_name}', '{last_name}', '{email}', '{age}', '{gender}')
            """
        )

        conn.commit()
        rows_affected = cur.rowcount

        return make_response(jsonify({"message": "record added successfully", "rows_affected": rows_affected}), 201)
    
    except Exception as e:
        conn.rollback()
        return make_response(jsonify({"error": str(e)}), 500)

    finally:
        cur.close()

if __name__ == "__main__":
    app.run(debug=True)
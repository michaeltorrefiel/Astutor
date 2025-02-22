from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'astutor'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

def query_exec(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return(rows)

@app.route("/")
def home_page():
    home = """
    <h1>Hello, world</h1>
    """
    return home

@app.route("/student", methods=["GET"])
def get_records():

    rows = query_exec("select * from student")
    
    return make_response(jsonify(rows), 200)

@app.route("/student", methods=["POST"])
def sign_up():
    cur = mysql.connection.cursor()

    info = request.get_json()
    id = info["id"]
    firstName = info["firstName"]
    lastName = info["lastName"]
    email = info["email"]
    Gender = info["Gender"]

    cur.execute(
    f"""
        insert into student(id, firstName, lastName, email, Gender) value('{id}', '{firstName}', '{lastName}', '{email}', '{Gender}')
    """
    )

    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()

    return make_response(jsonify({"message": "record added successfully", "rows_affected": rows_affected}), 201)

if __name__ == "__main__":
    app.run(debug=True)
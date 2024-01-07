
from flask import Flask, render_template, url_for, request, g, redirect, session
from database import connect_to_database, getDatabase
from werkzeug.security import generate_password_hash, check_password_hash
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'eco_db'):
        g.eco_db.close()

def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = getDatabase()
        user_cursor = db.execute("select * from users where username = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route('/')
def index():
    user = get_current_user()
    return render_template('landing.html',user=user)


def get_total_points_for_user(username):
    db = getDatabase()
    cursor = db.execute("SELECT points FROM users WHERE username = ?", [username])
    users = cursor.fetchone()
    return users['points'] if users else 0

@app.route('/login', methods = ["POST","GET"])
def login():
    user  = get_current_user()
    error = None
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        db = getDatabase()
        fetchedperson_cursor=db.execute("select * from users where username = ?",[name])
        personfromdatabase = fetchedperson_cursor.fetchone()
        if personfromdatabase:
            if password == personfromdatabase['password']:
                session['user'] = personfromdatabase['username']
                return redirect(url_for('home'))
            else:
                error = "username or password did not match. Try again"
                return render_template('login.html', error = error)
        else:
            error = "username or password did not match, try again"
            return redirect(url_for('login'))
        
    return render_template("login.html", user=user)

@app.route('/register', methods = ["POST", "GET"])
def register():
    user  = get_current_user()
    error = None
    if request.method == "POST":
        db = getDatabase()
        name = request.form['username']
        password = request.form['password']

        user_fetching_cursor = db.execute("select * from users where username = ?",[name])
        existing_user = user_fetching_cursor.fetchone()
        if existing_user:
            error = "username already taken, please try again"
            return render_template("register.html", error = error)
        
        db.execute("insert into users (username, password, points) values (?,?,?)",[name, password, 0])
        db.commit()
        session['user'] = name
        return redirect(url_for('index'))
    return render_template("register.html", user=user)

@app.route('/selectATask')
def selectATask():
    return render_template("selectATask.html")

def update_points(username, points):
    db = getDatabase()
    db.execute("UPDATE users SET points = ? WHERE username = ?", [points, username])
    db.commit()

@app.route('/claim_task/<int:task_points>', methods=['POST'])
def claim_task(task_points):
    user = get_current_user()

    if user:
        current_points = get_total_points_for_user(user['username'])
        new_points = current_points + task_points

        update_points(user['username'], new_points)

    return redirect(url_for('selectATask'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/homepage')
def home():
    user = get_current_user()
    total_points = get_total_points_for_user(user['username']) if user else 0
    return render_template("home.html", user=user, total_points=total_points)

if __name__ == "__main__":
    app.run(debug = True)
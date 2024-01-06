from flask import Flask, render_template, url_for, request, g, redirect
from database import connect_to_database, getDatabase

app = Flask(__name__)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'eco_db'):
        g.eco_db.close()

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register', methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        db = getDatabase()
        name = request.form['name']
        password = request.form['password']
        db.execute("insert into table users (username, password, points) values (?,?,?)",[name, password, 0])
        db.commit()
        return redirect(url_for('index'))
    return render_template("register.html")

@app.route('/selectATask')
def selectATask():
    return render_template("selectATask.html")


@app.route('/logout')
def logout():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug = True)
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from database import getDatabase
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import DBAPIError
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'os.urandom(24)'  # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1947@localhost/ecoConn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    points = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Define the Task model
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    is_claimed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref='tasks_claimed')


# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "error")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists", "error")
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except DBAPIError as e:
            db.session.rollback()
            flash("A database error occurred.", "error")
            app.logger.error('Database error: %s', str(e))
            return redirect(url_for('register'))
    return render_template("register.html")


@app.route('/select_task')
def select_task():
    tasks = Task.query.filter_by(is_claimed=False).all()
    return render_template('selectAtask.html', tasks=tasks)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/claim_task/<int:task_id>', methods=['POST'])
def claim_task(task_id):
    if 'user_id' not in session:
        flash("You must be logged in to claim tasks", "error")
        return redirect(url_for('login'))

    try:
        task = Task.query.get_or_404(task_id)
        user = User.query.get(session['user_id'])

        if task and not task.is_claimed:
            task.is_claimed = True
            task.user_id = user.id  # Associate the task with the user
            user.points += task.points  # Add points to the user
            db.session.commit()
            flash(f"You have claimed the task: {task.content}", "success")
        else:
            flash("This task has already been claimed or does not exist.", "error")
    except DBAPIError as e:
        db.session.rollback()
        flash("A database error occurred while claiming the task.", "error")

    return redirect(url_for('select_task'))




if __name__ == '__main__':
    app.run(debug=True)

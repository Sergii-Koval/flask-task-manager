from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
from models import Task, User
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@app.route('/create-task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_task.html')


@app.route('/edit-task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get(id)
    if request.method == 'POST':
        task.title = request.form['title']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)


@app.route('/delete-task/<int:id>', methods=['POST'])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))



@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        if password != password2:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first() is not None:
            flash('Username already exists')
            return redirect(url_for('register'))
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Successfully registered')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.verify_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('login.html')



if __name__ == "__main__":
    app.run(debug=True)

import time
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
from models import Task, User
from flask_migrate import Migrate
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not check_admin_role():
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('role')

        user = User.query.get(user_id)
        if user:
            user.role = new_role
            db.session.commit()

    users = User.query.all()
    return render_template('admin.html', users=users)


def check_admin_role():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.role == 'admin':
            return True
    return False


def check_dev_role():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.role in ('admin', 'dev'):
            return True
    return False


@app.route('/')
def index():
    pending_tasks = Task.query.filter_by(status='pending').order_by(Task.create_time).all()
    in_progress_tasks = Task.query.filter_by(status='in_progress').order_by(Task.create_time).all()
    done_tasks = Task.query.filter_by(status='done').order_by(Task.done_time).all()

    return render_template('index.html',
                           pending_tasks=pending_tasks,
                           in_progress_tasks=in_progress_tasks,
                           done_tasks=done_tasks
                           )


@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_task = Task(title=title, description=description, status='pending')
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_task.html')


@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)



@app.route('/delete-task/<int:id>', methods=['POST'])
def delete_task(id):
    if not check_admin_role():
        return redirect(url_for('index'))

    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


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
        if User.query.filter_by(username=username).first() is not None:
            flash('Username already exists')
        elif password != password2:
            flash('Passwords do not match')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Successfully registered')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return {'current_user': user}
    return {'current_user': None}


@app.route('/accept_task/<int:id>', methods=['POST'])
def accept_task(id):
    task = Task.query.get(id)
    if 'user_id' in session and session['user_role'] in ['admin', 'dev'] and task.status == 'pending':
        task.status = 'in_progress'
        task.user_id = session['user_id']
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return "You do not have the required permissions to accept this task", 403


@app.route('/complete_task/<int:id>', methods=['POST'])
def complete_task(id):
    task = Task.query.get(id)
    if task and 'user_id' in session and (
            session['user_id'] == task.user_id or session['user_role'] == 'admin') and task.status == 'in_progress':
        task.status = 'done'
        task.done_time = int(time.time())
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return "You do not have the required permissions to complete this task", 403


@app.template_filter('unixtime')
def unixtime_filter(s):
    return datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S') if s else 'N/A'


if __name__ == "__main__":
    app.run(debug=True)

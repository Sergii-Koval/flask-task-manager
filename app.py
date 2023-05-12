from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db
from models import Task, User
from flask_migrate import Migrate
from config import Config

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


@app.route('/create-task', methods=['GET', 'POST'])
def create_task():
    if not check_admin_role():
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_task.html')


@app.route('/edit-task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    if not check_admin_role():
        return redirect(url_for('index'))

    task = Task.query.get(id)
    if request.method == 'POST':
        task.title = request.form['title']
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


if __name__ == "__main__":
    app.run(debug=True)

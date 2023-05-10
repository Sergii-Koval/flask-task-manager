from flask import Flask, render_template, request, redirect, url_for
from database import db
from models import Task
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


if __name__ == "__main__":
    app.run(debug=True)

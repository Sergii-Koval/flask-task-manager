# Task Management System

This is a simple Task Management System developed with Flask, Flask-SQLAlchemy and Flask-Migrate. The application allows users to create, edit, and delete tasks. It also provides user authentication and user role management features.

## Installation
```
pip install flask
pip install flask_sqlalchemy
pip install flask_migrate
pip install werkzeug
```
## Usage
To run the application, navigate to the root directory of the project and execute the following command:
```
python app.py
```
This will start the server and the application will be accessible at http://localhost:5000.
## Project Structure
models.py: Contains the database models for the application. The Task and User classes represent tasks and users in the system respectively.

database.py: Initializes SQLAlchemy, an ORM for interacting with the database.

config.py: Contains the configuration for the application, including the database URI and secret key.

app.py: The main entry point of the application. This file contains the route definitions and application logic.
## Features

-User registration and authentication.

-Ability for users to create, edit, and delete tasks.

-Role-based access control (admin, developer, user).

-Task status management (pending, in progress, done).

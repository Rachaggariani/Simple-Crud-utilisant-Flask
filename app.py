from flask import Flask, render_template, redirect, url_for, request, flash
from flask_migrate import Migrate
from flask_restful import Api
from config.Config import Config 
from extensions import db
from resources.user import UserListResource 
import pymysql
import os

pymysql.install_as_MySQLdb()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config
    app.secret_key = os.urandom(24)
    print(app.config)  # Print configuration for debugging
    register_extensions(app)
    register_resources(app)
    return app

# Register extensions like SQLAlchemy and Flask-Migrate
def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)

# Register API resources
def register_resources(app):
    api = Api(app)
    api.add_resource(UserListResource, '/users', '/users/<int:user_id>')  # Allow user_id in URL

app = create_app()

@app.route('/', methods=['GET'])
def list_users():
    response, status_code = UserListResource().get()
    return render_template('users.html', users=response), status_code

@app.route('/addUser', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        response, status_code = UserListResource().post()
        if status_code == 201:
            username = response['data']['username']  # Récupérer le nom d'utilisateur du response
            flash(f"User {username} added successfully!", 'success')  # Message personnalisé
        else:
            flash(response['message'], 'danger')
        return redirect(url_for('list_users'))
    return render_template('addUser.html')

@app.route('/deleteUser/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    response, status_code = UserListResource().delete(user_id)
    flash(response['message'], 'danger' if status_code == 200 else 'warning')
    return redirect(url_for('list_users'))

@app.route('/editUser/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        response, status_code = UserListResource().put(user_id)
        flash(response['message'], 'info' if status_code == 200 else 'danger')
        return redirect(url_for('list_users'))
    
    # Handling GET request to retrieve user details for editing
    response, status_code = UserListResource().get(user_id)
    return render_template('editUser.html', user=response), status_code

if __name__ == '__main__':
    app.run(debug=True, port=5006)

from flask import request
from flask_restful import Resource
from http import HTTPStatus
from utils import hash_password
from models.user import User
from extensions import db 

class UserListResource(Resource):
    def get(self, user_id=None):
        if user_id is None:
            return self.get_all_users()  # Récupération de tous les utilisateurs
        else:
            return self.get_user_by_id(user_id)  # Récupération d'un utilisateur par ID

    def get_all_users(self):
        # Récupération de tous les utilisateurs
        users = User.query.all()
        data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password':user.password
            }
            for user in users
        ]
        return data, HTTPStatus.OK

    def get_user_by_id(self, user_id):
        # Récupération de l'utilisateur par ID
        user = User.query.get(user_id)
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        else:
          data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password':user.password
                 }
        return data, HTTPStatus.OK
    # Define the "post" method to handle POST requests
    def post(self):
       # if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        non_hash_password = request.form.get('password')

        # Vérifiez que tous les champs requis sont fournis
        if not username or not email or not non_hash_password:
            return {'message': 'Username, email, and password are required'}, HTTPStatus.BAD_REQUEST

        # Check if a user with the same username already exists
        if User.get_by_username(username):
            return {'message': 'Username already used'}, HTTPStatus.BAD_REQUEST

        # Hash the un-hashed password
        password = hash_password(non_hash_password)

        # Create an instance of the "User" class
        user = User(
            username=username,
            email=email,
            password=password
        )

        # Save the user to the database
        user.save()

        # Create a data dictionary
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }

        # Return data with a "201 Created" status code
        return {
            'message': 'User added successfully',
            'data': data
        }, HTTPStatus.CREATED
    
    def put(self, user_id):
        # Retrieve the user by ID
        user = User.query.get(user_id)
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND


        # Update user fields if provided
        username = request.form.get('username')
        email = request.form.get('email')
        non_hash_password = request.form.get('password')
        update_messages = []
        
        if username and username != user.username:
           user.username = username
           update_messages.append(f"{username}")
           
        if email and email!=user.email:
           user.email=email
           update_messages.append(f"{email}")
        
        if non_hash_password:
           user.password = hash_password(non_hash_password)
           update_messages.append(f"{hash_password}")

        # Commit the changes if using SQLAlchemy
        db.session.commit()

        if update_messages:
        # Construire le message de manière appropriée
            if len(update_messages) == 1:
                 update_message = f"{update_messages[0]} updated successfully!"  # Un seul champ mis à jour
            else:
            # Plusieurs champs mis à jour
                 update_message = f"{', '.join(update_messages)} updated successfully!"
        else:
            update_message = "No fields were updated."  # Aucun champ modifié

        return {
         'message': update_message,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }, HTTPStatus.OK
    
    def delete(self, user_id):
        # Retrieve the user by ID
        user = User.query.get(user_id)
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        # Delete the user
        user.delete()  # Make sure this method actually removes the user from the database

        # Commit the changes if using SQLAlchemy
        db.session.commit()  # Ensure you have imported 'db' from your extensions

        # Return a confirmation message
        return {'message': 'User deleted successfully'}, HTTPStatus.OK
    
    def patch(self, user_id):
        # Récupération de l'utilisateur par ID
        user = User.query.get(user_id)
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        json_data = request.get_json()
        if json_data is None:
            return {'message': 'No input data provided'}, HTTPStatus.BAD_REQUEST

        # Mise à jour des champs d'utilisateur si fournis
        if 'username' in json_data:
            user.username = json_data['username']

        if 'email' in json_data:
            user.email = json_data['email']

        if 'password' in json_data:
            user.password = hash_password(json_data['password'])

        try:
            # Sauvegarde des modifications
            db.session.commit()
        except Exception as e:
            # Gérer les erreurs de commit
            db.session.rollback()
            return {'message': 'An error occurred while updating the user: {}'.format(str(e))}, HTTPStatus.INTERNAL_SERVER_ERROR

        # Création d'une réponse avec les données mises à jour
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }

        return {
        'message': 'User updated successfully',
        'data': data
    }, HTTPStatus.OK
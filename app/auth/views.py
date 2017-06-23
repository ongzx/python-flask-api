# /app/auth/views.py

from . import auth_blueprint

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User

class RegistrationView(MethodView):
    """This class registers a new user."""

    def post(self):
        """Handle POST request for this view. Url --> /auth/register"""

        # query user see if its exists
        user = User.query.filter_by(email=request.data['email']).first()
        
        if not user:
            try:
                post_data = request.data
                # register the user
                email = post_data['email']
                password = post_data['password']
                firstName = post_data['firstName']
                lastName = post_data['lastName']
                profileThumbnailUrl = post_data['profileThumbnailUrl']

                user = User(email=email, password=password, firstName=firstName, lastName=lastName, profileThumbnailUrl=profileThumbnailUrl)
                user.save()

                response = {
                    'message': 'You registered successfully. Please log in.'
                }

                return make_response(jsonify(response)), 201

            except Exception as e:
                response = {
                    'message': str(e)
                }
                return make_response(jsonify(response)), 401
        else:
            # there is an existing user. Prevent register twice
            response = {
                'message': 'User already exists. Please login.'
            }

            return make_response(jsonify(response)), 202

class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""

    def post(self):
        """Handle POST request for this view. Url ---> /auth/login"""
        try:
            user = User.query.filter_by(email=request.data['email']).first()

            if user and user.password_is_valid(request.data['password']):
                # generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.id)
                
                if access_token:
                    response = {
                        'id': user.id,
                        'email': user.email,
                        'firstName': user.firstName,
                        'lastName': user.lastName,
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user does not exist
                response = {
                    'message': 'Invalid email or password, Please try again'
                }
                return make_response(jsonify(response)), 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500

registration_view = RegistrationView.as_view('register_view')
login_view = LoginView.as_view('login_view')
# define the rule for registration url ---> /auth/register
# then add the rule to blueprint
auth_blueprint.add_url_rule('/auth/register', view_func=registration_view, methods=['POST'])
auth_blueprint.add_url_rule('/auth/login', view_func=login_view, methods=['POST'])

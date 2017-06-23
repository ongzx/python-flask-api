# app/models.py

from app import db
from flask import current_app
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

class User(db.Model):
    """This class defines the users table"""

    __tablename__ = 'users'

    #Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    firstName = db.Column(db.String(500))
    lastName = db.Column(db.String(500))
    profileThumbnailUrl = db.Column(db.String(500))
    products = db.relationship('Product', order_by='Product.id', cascade="all, delete-orphan")

    def __init__(self, email, password, firstName, lastName, profileThumbnailUrl):
        """Initialize the user with an email and a password together with required info"""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()
        self.firstName = firstName
        self.lastName = lastName
        self.profileThumbnailUrl = profileThumbnailUrl

    def password_is_valid(self, password):
        """Checks the password against its hash to validate the user password"""
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database. This includes creating a user and editing one."""
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """Generates the access token"""
        try:
            #set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            #create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string
        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token."
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login."


class Product(db.Model):
    """This class represents the products table. """

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.String)
    brand = db.Column(db.String)
    description = db.Column(db.String)
    measurement = db.Column(db.String(1000))
    image = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, price, brand, description, measurement, image, created_by):
        """initialize with name, price, brand, description, measurement, image """
        self.name = name
        self.price = price
        self.brand = brand
        self.description = description
        self.measurement = measurement
        self.image = image
        self.created_by = created_by

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        return Product.query.filter_by(created_by=user_id)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        """Return a representation of a product instance."""
        return "<Product: {}>".format(self.name)
# app/__init__.py

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    from app.models import Product, User

    app = FlaskAPI(__name__, instance_relative_config = True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/products/', methods=['POST', 'GET'])
    def products():
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # attempt to decode the token and get user id
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    price = str(request.data.get('price', ''))
                    brand = str(request.data.get('brand', ''))
                    description = str(request.data.get('description', ''))
                    measurement = str(request.data.get('measurement', ''))
                    image = str(request.data.get('image', ''))

                    if name and price and brand and description and measurement and image:
                        product = Product(
                            name=name,
                            price=price,
                            brand=brand,
                            description=description,
                            measurement=measurement,
                            image=image,
                            created_by=user_id)
                        product.save()
                        response = jsonify({
                            'id': product.id,
                            'name': product.name,
                            'price': product.price,
                            'brand': product.brand,
                            'description': product.description,
                            'measurement': product.measurement,
                            'image': product.image,
                            'date_created': product.date_created,
                            'date_modified': product.date_modified,
                            'created_by': user_id
                        })
                        return make_response(response), 201

                    else:
                        response = jsonify({
                            "message": "Missing params"
                        })
                        return make_response(response), 400

                else:
                    products = Product.query.filter_by(created_by=user_id)
                    results = []

                    for product in products:
                        obj = {
                            'id': product.id,
                            'name': product.name,
                            'price': product.price,
                            'brand': product.brand,
                            'description': product.description,
                            'measurement': product.measurement,
                            'image': product.image,
                            'date_created': product.date_created,
                            'date_modified': product.date_modified,
                            'created_by': product.created_by
                        }
                        results.append(obj)

                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, payload is the error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def product_manipulation(id, **kwargs):

        # get the access token form authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # if the id is not a string(error), we have a user id
                product = Product.query.filter_by(id=id).first()
                if not product:
                    about(404)

                if request.method == 'DELETE':
                    product.delete()
                    return {
                        "message": "product {} deleted successfully".format(product.id)
                    }, 200

                elif request.method == 'PUT':
                    name = str(request.data.get('name', ''))
                    product.name = name
                    product.save()
                    response = jsonify({
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'brand': product.brand,
                        'description': product.description,
                        'measurement': product.measurement,
                        'image': product.image,
                        'date_created': product.date_created,
                        'date_modified': product.date_modified,
                        'created_by': product.created_by
                    })
                    return make_response(response), 200
            else:
                # GET
                response = jsonify({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'brand': product.brand,
                    'description': product.description,
                    'measurement': product.measurement,
                    'image': product.image,
                    'date_created': product.date_created,
                    'date_modified': product.date_modified,
                    'created_by': product.created_by
                })
                return make_response(response), 200
        else:
            # user is not legit, payload is gonna be an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
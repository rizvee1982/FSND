import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    try: 
        drinks = Drink.query.all()
        drink_list = []
        for drink in drinks:
            drink_list.append(drink.short())
        return jsonify({'success': True, "drinks": drink_list}), 200
    except:
        abort(422)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try: 
        drinks = Drink.query.all()
        drink_list = []
        for drink in drinks:
            drink_list.append(drink.long())
        return jsonify({'success': True, "drinks": drink_list}), 200
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    try:
        request_json = request.get_json()
        title = request_json.get('title')
        recipe = json.dumps(request_json.get('recipe'))
        drink = Drink(title=title, recipe = recipe)
        drinkArr = []
        drinkArr.append(drink.long())
        drink.insert() 
        return jsonify({'success': True, 'drinks': drinkArr}), 200
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    if drink_id is None: 
        abort(404)
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    request_json = request.get_json()
    drink.title = request.json.get('title')
    drink.recipe = json.dumps(request_json.get('recipe'))
    drink.update()
    drinks = []
    drinks.append(drink.long())
    return jsonify({'success': True, 'drinks': drinks}), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        if drink_id is None: 
            abort(404)
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({'success': True, "delete":drink_id}), 200
    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Resource not found."
                    }), 404


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

from __future__ import print_function  # In python 2.7

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import sys

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    print('GET-------------', file=sys.stderr)
    selection = Drink.query.all()

    # if len(selection) < 1:
    #     abort(404)

    drinks = [d.short() for d in selection]

    return jsonify({
        'success': True,
        'drinks': drinks,
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def get_drinks_details(payload):
    selection = Drink.query.all()

    # if len(selection) < 1:
    #     abort(404)

    drinks = [d.long() for d in selection]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


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
@requires_auth(permission='post:drinks')
def post_drinks(jwt):
    body = request.json

    if 'title' not in body or 'recipe' not in body:
        abort(422)

    new_drink = Drink(title=body['title'], recipe=json.dumps(body['recipe']))
    new_drink.insert()

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    }), 200


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
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drinks(jwt, id):
    body = request.json
    if not id:
        abort(422)

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    if 'title' in body:
        drink.title = body['title']

    if 'recipe' in body:
        drink['recipe'] = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


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


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(jwt, id):
    body = request.json
    if not id:
        abort(422)

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': [drink.id]
    }), 200


# Error Handling
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
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": AuthError,
        "message": "unauthorized access"
    }), 401


"""

$env:FLASK_APP="src/api.py"
$env:FLASK_ENV="development"
flask run

https://afifym.us.auth0.com/authorize?audience=coffee&response_type=token&client_id=0OcpMMQUIUrdoXT3yD92B4jz1PsAR074&redirect_uri=http://localhost:8100/tabs/user-page
b
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjV4bGRqZUpQNEd1dVRvaEs1MUMtdiJ9.eyJpc3MiOiJodHRwczovL2FmaWZ5bS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAzZmRjMWY0YjQ5NzkwMDY5MjY5M2IxIiwiYXVkIjoiY29mZmVlIiwiaWF0IjoxNjE0ODcwNTAyLCJleHAiOjE2MTQ4Nzc3MDIsImF6cCI6IjBPY3BNTVFVSVVyZG9YVDN5RDkyQjRqejFQc0FSMDc0Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.AHz6hof3OBNMizGrQggaN2GDm88HEdiTCfnUpF21LGy7HGEPIGUl1MA2yuF7QPJq8fTVibrbgeYmQA3dExp2APVd6-3RZMb-GpFfg18P-ffS45nAvINFDOCXgO7fNP_aQ1e4GHgRSpFaJIPncbVhHoCaBTRFU-XXZjvU6vEbiy5OUwDxS130xDI9xIA2MVJ1DXbyFgS83ixtCzh6jZhPovoa0XWiXLg7sI4MTo-gyq9BLxwei0oNkQT-fSX2u1vrWODXL5-J4DsHmhb8H2Acj_Kd_sTjyhcsE6LOYJ_Brg27Ia07TTScYaO-IJUzFu6FQ7jwnZ0auhlvptbOthVkKg
"""

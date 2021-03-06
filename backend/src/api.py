import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
Done uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
Done implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
                    "success": True,
                    "drinks": drinks
                    })


'''
Done implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def drink_detail(payload):
    print(payload)
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
                    "success": True,
                    "drinks": drinks
                    })


'''
Done implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):
    body = request.get_json()
    title = body["title"]
    recipe = body["recipe"]

    if title == '':
        abort(422)

    new_drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
        new_drink.insert()
    except:
        abort(422)

    drink = [new_drink.long()]
    return jsonify({
                    "success": True,
                    "drinks": drink
                    })


'''
Done implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    body = request.get_json()

    if body is None:
        abort(404)

    try:
        title = body['title']
        recipe = body.get('recipe', None)
        drink.title = title
        drink.recipe = drink.recipe if recipe is None else json.dumps(recipe)
        drink.update()
    except:
        abort(422)

    return jsonify({
                    "success": True,
                    "drinks": [drink.long()]
                    })


'''
Done implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
    except:
        abort(422)

    return jsonify({
            "success": True,
            "delete": f"{drink_id}"
            })


# Error Handling

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    'success': False,
                    'error': 401,
                    "message": "Unauthorized"
                    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "Forbidden"
                    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Not Found"
                    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "Unprocessable"
                    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "Server Error"
                    }), 500


'''
Done implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
Done implement error handler for 404
    error handler should conform to general task above
'''


'''
Done implement error handler for AuthError
    error handler should conform to general task above
'''

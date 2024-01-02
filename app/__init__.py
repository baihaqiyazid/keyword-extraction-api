from flask import Flask, request
import logging
from app.response import ResponseFormat
from .extension import api
from .resources import ns
from werkzeug.exceptions import BadRequest, InternalServerError, MethodNotAllowed


app = Flask(__name__)

api.init_app(app)
api.add_namespace(ns)

logging.basicConfig(format="[%(asctime)s] - [%(levelname)s] - [%(name)s] - %(message)s", filename="logging.log")

@api.errorhandler(BadRequest)
def badRequest(error):
    response = ResponseFormat(
        code=error.code,
        data=None, 
        message=error.description, 
        config=None,
        status=error.name
    ).to_dict()

    return response, error.code

@api.errorhandler(InternalServerError)
def internalServerError(error):
    response = ResponseFormat(
        code=error.code,
        data=None, 
        config=None,
        message=error.description, 
        status="NOK"
    ).to_dict()

    return response, error.code

@api.errorhandler(MethodNotAllowed)
def methodNotFound(error):
    response = ResponseFormat(
        code=error.code,
        data=None, 
        config=None,
        message="Method Not Found!", 
        status="NOK"
    ).to_dict()
    
    
    return response, error.code

@app.errorhandler(400)
def badRequestSentence(error):
    response = ResponseFormat(
        code=error.code,
        data=None, 
        config=None,
        message=error.description, 
        status=error.name
    ).to_dict()

    return response, error.code

@app.errorhandler(404)
def notFound(error):

    response = ResponseFormat(
        code=error.code,
        data=None, 
        config=None,
        message=error.description, 
        status=error.name
    ).to_dict()

    route_name = request.path # Get the route name
    logger = logging.getLogger(route_name)  # Create a logger with the route name
    logger.error(f"Error: 404")

    return response, error.code

if __name__ == '__main__':
    app.run(debug=True)


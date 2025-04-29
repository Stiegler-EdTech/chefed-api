"""A decorator that logs information about the current app, route, and function arguments.

Args:
    route_func (function): The function to be decorated.

Returns:
    function: The decorated function.

"""
from functools import wraps
from flask import Flask, request, current_app

def inspecto(f):
    @wraps(f)
    def wrapper_(*args, **kwargs):
        app_name = current_app.name
        current_app.logger.info(f"Running app: {current_app.name}")
        current_app.logger.info(f"Route: {request.path}")
        current_app.logger.info(f"*args: {args}")
        current_app.logger.info(f"**kwargs: {kwargs}")
        return f(*args, **kwargs)
    return wrapper_
    




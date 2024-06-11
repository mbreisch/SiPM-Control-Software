from flask import Blueprint

control_bp = Blueprint('control', __name__, static_folder='static', template_folder='templates')

from . import routes

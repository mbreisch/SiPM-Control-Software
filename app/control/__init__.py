from flask import Blueprint, send_from_directory

control_bp = Blueprint('control', __name__, static_folder='static', template_folder='templates', url_prefix="./app/control/")

from . import routes
from flask import Blueprint, send_from_directory

ambient_bp = Blueprint('ambient', __name__, static_folder='static', template_folder='templates', url_prefix="./app/ambient/")

from . import routes
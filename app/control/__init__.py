from flask import Blueprint, send_from_directory

control_bp = Blueprint('control', __name__, static_folder='/home/pi/SSoft_exp/app/control/static', template_folder='/home/pi/SSoft_exp/app/control/templates')

from . import routes
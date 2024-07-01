from flask import Blueprint, send_from_directory

daq_bp = Blueprint('daq', __name__, static_folder='static', template_folder='templates', url_prefix="./app/daq/")

from . import routes
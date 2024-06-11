from flask import Blueprint, send_from_directory
import os
print(f"!!!!!!!!!!!!!!!!!!!!!!!!!{os.getcwd()}!!!!!!!!!!!!!!!!!!!!!!")
control_bp = Blueprint('control', __name__, static_folder='static', template_folder='templates', url_prefix="")

from . import routes
from flask import Blueprint, send_from_directory

control_static_bp = Blueprint('control_static', __name__, static_folder='static', template_folder='templates')

@control_static_bp.route('/static/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(control_static_bp.static_folder + '/js', filename)

# Register the blueprint with your Flask application
app.register_blueprint(control_static_bp, url_prefix='/control')

from . import routes
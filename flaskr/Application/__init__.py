from flask import Flask
import secrets
def create_app(config=None):
    """Generates the Application and initialises the blueprints.

    Args:
        config (flask app config, optional): Not used. Defaults to None.

    Returns:
        flask app: Application with all functions
    """
    app=Flask(__name__)

    # register all the blueprints
    from Application import views
    with app.app_context():
        views.init_blueprints()
        app.config["SECRET_KEY"]=secrets.token_hex(16)

    return app


# To run this app, use:
# copied from: https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/

# For Linux and Mac:

# $ export FLASK_APP=Application
# $ export FLASK_ENV=development
# $ flask run

# For Windows cmd, use set instead of export:

# > set FLASK_APP=Application
# > set FLASK_ENV=development
# > flask run

# For Windows PowerShell, use $env: instead of export:

# > $env:FLASK_APP = "Application"
# > $env:FLASK_APP = "Application"
# > flask run

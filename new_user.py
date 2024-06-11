from app import create_app, db
from app.models import User
import getpass

def main():
    app = create_app()
    app.app_context().push()

    # Prompt the user for the username
    username = input("Enter username: ")

    # Prompt the user for the password
    password = getpass.getpass("Enter password: ")

    # Instantiate a new User object
    new_user = User(username=username)

    # Set the password for the user
    new_user.set_password(password)

    # Add the user object to the SQLAlchemy session
    db.session.add(new_user)

    # Commit the changes to the database
    db.session.commit()

    print("User successfully created.")

if __name__ == "__main__":
    main()
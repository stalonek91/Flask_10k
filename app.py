# Virtual env is called -> flask_10k/bin/activate /// deactivate after finished work

# Use TODO and FIXME
# TODO: generic -> add error handling to databases or basically in forms, try except
# TODO: add functionality which connects tracker with user ID
# TODO: add dissapearring effect in CSS for flash messages
# TODO: add 2 flash messages when deleting 2 entries fast
# TODO: add search of lessons by keywords
# FIXME: nie dziala pepe!!!!

from flask import Flask

from flask_login import LoginManager


from flask_migrate import Migrate
from extensions import db, bcrypt
from functions import create_tables,  init_login_manager

from blueprints.auth import auth_bp
from blueprints.content import content_bp

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db.init_app(app)
bcrypt.init_app(app)

migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Log in first to access the tracker!'

init_login_manager(login_manager)

app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)


if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)


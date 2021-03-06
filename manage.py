from main import app
from main import db
from main import models

from flask_script import Manager
from flask_script import Shell

from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from main.models.users import User


def _make_context():
    return dict(app=app, db=db, models=models)

migrate = Migrate(app, db)

manager = Manager(app)

manager.add_command('db', MigrateCommand)

manager.add_command('shell', Shell(make_context=_make_context))


@manager.command
def init_db():
    db.create_all()
    print "DB initialized!"


@manager.command
def add_user(username, password):
    user = User(username=username)
    user.set_password_hash(password)
    db.session.add(user)
    db.session.commit()
    print "Added {0}!".format(user.username)


if __name__ == "__main__":
    manager.run()

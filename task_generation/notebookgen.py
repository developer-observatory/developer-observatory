#! Copyright (C) 2017 Lukas Löhle
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

from database import db
from flask import Flask
import os.path
from flaskext.markdown import Markdown
from views import nb_gen


def create_app():
    app = Flask(__name__)
    db_path = os.path.join(os.path.dirname(__file__), 'tmp', 'db.sqlite')
    db_uri = 'sqlite:///{}'.format(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'L1AW8zWU79Msw8RPDptM'
    Markdown(app)
    app.jinja_env.line_statement_prefix = '% '
    app.jinja_env.line_comment_prefix = '##'
    app.jinja_env.add_extension('jinja2.ext.do')
    app.register_blueprint(nb_gen, url_prefix='')
    db.init_app(app)
    return app, db_path


def setup_db():
    with application.app_context():
        db.create_all()

if __name__ == '__main__':
    application, db_path = create_app()
    if not os.path.isfile(db_path):
        setup_db()
    application.run(debug=False)

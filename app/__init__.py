import os

from flask import Flask

from app.config import Config
from app.errors import register_error_handlers
from app.extensions import api as smorest_api
from app.extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if config:
        app.config.from_mapping(config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    smorest_api.init_app(app)

    from app.api.categories import blueprint as categories_blueprint
    from app.api.health import blueprint as health_blueprint
    from app.api.products import blueprint as products_blueprint

    smorest_api.register_blueprint(health_blueprint)
    smorest_api.register_blueprint(categories_blueprint)
    smorest_api.register_blueprint(products_blueprint)
    register_error_handlers(app)

    return app

from flask import Flask, request, current_app
from config import Config
from flask_bootstrap import Bootstrap4
import logging, os
from logging.handlers import RotatingFileHandler

bootstrap = Bootstrap4()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bootstrap.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp)

    from app.reports.routes import get_stat_value_forever, get_stat_by_faction_value_forever, combine_stat_by_faction
    app.jinja_env.filters['get_stat_value_forever'] = get_stat_value_forever
    app.jinja_env.filters['get_stat_by_faction_value_forever'] = get_stat_by_faction_value_forever
    app.jinja_env.filters['combine_stat_by_faction'] = combine_stat_by_faction

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/statfuse.log', maxBytes=100000, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('StatFuse startup')

    return app
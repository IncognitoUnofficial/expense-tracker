from dotenv import load_dotenv
from flask import Flask

from app.config import Config
from app.extensions import csrf, db, login_manager

load_dotenv()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth.routes import auth_bp
    from app.categories.routes import categories_bp
    from app.expenses.routes import expenses_bp
    from app.dashboard.routes import dashboard_bp
    from app.account.routes import account_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(account_bp)

    @app.template_filter("money")
    def money_filter(value):
        return f"${value:,.2f}"

    return app

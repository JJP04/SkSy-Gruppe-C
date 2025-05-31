import os
from flask import Flask
from .extensions import db
from .models import User
from flask_login import LoginManager

def create_app():
    # Absoluter Pfad zum aktuellen Verzeichnis (app/)
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )

    app.config.from_object('config.Config')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .recipe import recipe_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(recipe_bp)

    with app.app_context():
        db.create_all()

    return app

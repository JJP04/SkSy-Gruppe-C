import os
from flask import Flask

def create_app():
    # Absoluter Pfad zum aktuellen Verzeichnis (app/)
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )

    app.config.from_object('config.Config')

    from .auth import auth_bp
    from .dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app

import os
from flask import Flask
from .extensions import db
from .models import User
from flask_login import LoginManager
from transformers import pipeline
from .models import User, Recipe


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

    # erstes Mal starten dauert, da Model lokal heruntergeladen wird (Achtung, ~ 1 GB)
    app.ner_pipeline = pipeline(
        "ner",
        model="edwardjross/xlm-roberta-base-finetuned-recipe-all",
        tokenizer="edwardjross/xlm-roberta-base-finetuned-recipe-all",
        aggregation_strategy="simple"

    )

    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .recipe import recipe_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipe_bp)

    with app.app_context():
      #  Recipe.__table__.drop(db.engine, checkfirst=True)  #Tabelle löschen
        db.create_all()
    return app

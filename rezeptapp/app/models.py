from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)



    # Neue Felder für Sicherheitsfragen + gehashte Antworten
    question1 = db.Column(db.String(128))
    answer1_hash = db.Column(db.String(128))

    question2 = db.Column(db.String(128))
    answer2_hash = db.Column(db.String(128))

    question3 = db.Column(db.String(128))
    answer3_hash = db.Column(db.String(128))

    # Methode zum Passwort setzen (Hashing)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Sicherheitsantworten setzen + prüfen
    def set_answer(self, index, answer):
        hashed = generate_password_hash(answer.lower(), method='pbkdf2:sha256', salt_length=8)
        setattr(self, f'answer{index}_hash', hashed)

    def check_answer(self, index, answer):
        hashed = getattr(self, f'answer{index}_hash')
        return check_password_hash(hashed, answer.lower())

# Neue Tabelle: speichert rohe, eingereichte Zutaten unabhängig von "offiziellen" Ingredients
class RawIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    recipe = db.relationship("Recipe", backref="raw_ingredients")

# Zutaten-Tabelle: speichert eindeutige Zutaten
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)


    recipe_ingredients = db.relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")

# Verbindungstabelle: verknüpft Rezepte mit Zutaten
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe-ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)

    # Referenzen zurück
    recipe = db.relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipe_ingredients")

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='recipes') #ermöglicht bidirektionalen Zugriff von User auf alle seine Rezepte und v.v.
    recipe_ingredients = db.relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")


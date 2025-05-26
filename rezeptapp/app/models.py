from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=False, nullable=False)
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
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Sicherheitsantworten setzen + prüfen
    def set_answer(self, index, answer):
        hashed = generate_password_hash(answer.lower())
        setattr(self, f'answer{index}_hash', hashed)

    def check_answer(self, index, answer):
        hashed = getattr(self, f'answer{index}_hash')
        return check_password_hash(hashed, answer.lower())
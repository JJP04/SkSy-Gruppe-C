from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from .extensions import db
import random

DEFAULT_QUESTIONS = [
    "Wie heißt dein erstes Haustier?",
    "Was ist dein Lieblingsessen?",
    "In welcher Stadt bist du geboren?",
    "Was war dein erstes Auto?",
    "Wie heißt dein Lieblingslehrer?",
    "Was ist dein Lieblingsfilm?",
    "Wie heißt deine Mutter mit Mädchennamen?",
    "Was ist deine Lieblingsfarbe?",
    "In welcher Straße bist du aufgewachsen?",
    "Was ist dein Traumreiseziel?"
]

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    tab = request.args.get('tab', 'login')

    # 3 zufällige Sicherheitsfragen
    if request.method == 'GET' and tab == 'register':
        selected_questions = random.sample(DEFAULT_QUESTIONS, 3)
        return render_template('login.html', active_tab='register', questions=selected_questions)

    if request.method == 'POST':
        # Logindaten auslesen
        if 'login' in request.form:
            email = request.form.get('email')
            password = request.form.get('password')

            # Check ob User existiert
            user = User.query.filter(User.email == email).first()

            if user and user.check_password(password):
                # Login erfolgreich
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Falsche Email oder Passwort.', 'error')

            return render_template('login.html', active_tab='login')

        # Registrierungsdaten auslesen
        if 'register' in request.form:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if len(username) > 16:
                flash('Username darf maximal 16 Zeichen haben.', 'error')
                return render_template('login.html', active_tab='register')

            if len(email) > 64:
                flash('Email darf maximal 64 Zeichen haben.', 'error')
                return render_template('login.html', active_tab='register')

            if len(password) > 32:
                flash('Passwort darf maximal 32 Zeichen haben.', 'error')
                return render_template('login.html', active_tab='register')

            # Check Passwortbestätigung
            if password != confirm_password:
                flash('Passwörter stimmen nicht überein.', 'error')
                return render_template('login.html', active_tab='register')

            # Check ob Email oder Username schon existiert
            if User.query.filter((User.email == email) | (User.username == username)).first():
                flash('Benutzername oder E-Mail existiert bereits.', 'error')
                return render_template('login.html', active_tab='register')

            # Sicherheitsfragen und Antworten auslesen
            question1 = request.form.get('question1')
            answer1 = request.form.get('answer1')
            question2 = request.form.get('question2')
            answer2 = request.form.get('answer2')
            question3 = request.form.get('question3')
            answer3 = request.form.get('answer3')


            if not all([answer1, answer2, answer3]):
                flash('Bitte alle Antworten zu den Sicherheitsfragen eingeben!', 'error')
                return render_template('login.html', active_tab='register', questions=[question1, question2, question3])

            # User anlegen (Passwort verschlüsseln + Antworten zu Sicherheitsfragen speichern)
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            new_user.question1 = question1
            new_user.set_answer(1, answer1)
            new_user.question2 = question2
            new_user.set_answer(2, answer2)
            new_user.question3 = question3
            new_user.set_answer(3, answer3)
            db.session.add(new_user)
            db.session.commit()

            # Erfolgreich: Weiterleiten zum Login
            flash('Benutzerkonto erstellt, bitte einloggen.', 'success')
            return render_template('login.html', active_tab='login')



    return render_template('login.html', active_tab=tab)


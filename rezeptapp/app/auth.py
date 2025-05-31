from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from sqlalchemy import func
from flask_login import login_user
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
        session['questions'] = selected_questions
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
                login_user(user)
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

            # Sicherheitsfragen & Antworten auslesen
            questions = session.get('questions')
            answer1 = request.form.get('answer1')
            answer2 = request.form.get('answer2')
            answer3 = request.form.get('answer3')

            if len(username) > 16:
                flash('Username darf maximal 16 Zeichen haben.', 'error')
                return render_template('login.html', active_tab='register', questions=questions)

            if len(email) > 64:
                flash('Email darf maximal 64 Zeichen haben.', 'error')
                return render_template('login.html', active_tab='register', questions=questions)

            if len(password) > 32:
                flash('Passwort darf maximal 32 Zeichen haben.', 'error')
                return render_template('login.html', active_tab='register', questions=questions)

            # Check Passwortbestätigung
            if password != confirm_password:
                flash('Passwörter stimmen nicht überein.', 'error')
                return render_template('login.html', active_tab='register', questions=questions)

            # Check ob Email oder Username schon existiert
            if User.query.filter((User.email == email) | (User.username == username)).first():
                flash('Benutzername oder E-Mail existiert bereits.', 'error')
                return render_template('login.html', active_tab='register', questions=questions)


            if not all([answer1, answer2, answer3]):
                flash('Bitte alle Antworten zu den Sicherheitsfragen eingeben!', 'error')
                return render_template('login.html', active_tab='register', questions=questions)

            # User anlegen (Passwort verschlüsseln + Antworten zu Sicherheitsfragen speichern)
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            new_user.question1 = questions[0]
            new_user.set_answer(1, answer1)
            new_user.question2 = questions[1]
            new_user.set_answer(2, answer2)
            new_user.question3 = questions[2]
            new_user.set_answer(3, answer3)

            db.session.add(new_user)
            db.session.commit()

            # Erfolgreich: Weiterleiten zum Login
            flash('Benutzerkonto erstellt, bitte einloggen.', 'success')
            return render_template('login.html', active_tab='login')


    return render_template('login.html', active_tab=tab)


# Passwort-Reset Start: E-Mail abfragen und Frage anzeigen
@auth_bp.route('/pw_reset_start', methods=['GET', 'POST'])
def pw_reset_start():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()


        #  DEBUG-Ausgabe ins Terminal
        print("DEBUG: Eingegebene E-Mail:", email)
        users = User.query.all()
        print("DEBUG: E-Mails in DB:")
        for u in users:
            print("-", u.email)

        user = User.query.filter(db.func.lower(User.email) == email).first()

        if user:
            index = random.randint(1,3)
            session['reset_email'] = email
            session['questions_index'] = index
            question = getattr(user, f'question{index}')
            return redirect(url_for('auth.pw_reset_verify'))
        else:
            flash('E-Mail nicht gefunden.', 'error')


    return render_template('reset_start.html')

# Passwort-Reset Abschluss: Antwort prüfen + neues Passwort setzen
@auth_bp.route('/pw_reset_verify', methods=['GET', 'POST'])
def pw_reset_verify():
    email = session.get('reset_email')
    index = session.get('questions_index')

    if not email or not index:
        flash("Sitzung abgelaufen oder ungültig. Bitte erneut starten.", "error")
        return redirect(url_for('auth.pw_reset_start'))

    user = User.query.filter(func.lower(User.email) == email.lower()).first()

    if request.method == 'GET':
        question = getattr(user, f'question{index}')
        return render_template('reset_verify.html', question=question)

    # POST-Fall
    answer = request.form.get('answer')
    new_password = request.form.get('new_password')

    user = User.query.filter(func.lower(User.email) == email.lower()).first()

    if user and user.check_answer(index, answer):
        user.set_password(new_password)
        db.session.commit()
        flash('Passwort erfolgreich geändert. Bitte einloggen.', 'success')
        return redirect(url_for('auth.login', tab='login'))
    else:
        flash('Antwort war falsch', 'error')
        question = getattr(user, f'question{index}')
        return render_template('reset_verify.html', question=question)

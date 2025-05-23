from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from .extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    tab = request.args.get('tab', 'login')

    if request.method == 'POST':
        # Logindaten auslesen
        if 'login' in request.form:
            email = request.form.get('email')
            password = request.form.get('password')

            # Check ob User existiert
            user = User.query.filter(User.email == email).first()

            if user and user.password == password:
                # Login erfolgreich
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Falsche Email oder Passwort.', 'error')

            return render_template('login.html')

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

            # User anlegen
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            # Erfolgreich: Weiterleiten zum Login
            flash('Benutzerkonto erstellt, bitte einloggen.', 'success')
            return render_template('login.html', active_tab='login')

        if 'pw_reset' in request.form:
            email = request.form.get('email')
            new_password = request.form.get('password')
            user = User.query.filter(User.email == email).first()
            if user:
                user.password = new_password
                db.session.commit()
                flash('Passwort erfolgreich geändert.', 'success')
                return render_template('login.html', active_tab='login')
            else:
                flash('Benutzer mit dieser E-Mail nicht gefunden.', 'error')
                return render_template('login.html', active_tab='passwortVergessen')

    return render_template('login.html', active_tab=tab)

from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login')
def login():
    return render_template('login.html')

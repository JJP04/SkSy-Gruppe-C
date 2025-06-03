from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from .models import User
from .extensions import db

#für die profilansicht


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@dashboard_bp.route('/profil')
@login_required
def profil():
    return render_template('profile.html', user=current_user)

@dashboard_bp.route("/profil/loeschen", methods=["POST"])
@login_required
def profil_loeschen():
    user_id = current_user.id
    logout_user()

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("Dein Profil wurde erfolgreich gelöscht.", "info")

    return redirect(url_for("auth.login"))
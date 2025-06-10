from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, logout_user

from .models import User, Recipe, Ingredient, RecipeIngredient, RawIngredient
from .extensions import db

# für die profilansicht


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def rezepte():
    r = Recipe.query.all()
    return render_template("dashboard.html", rezepte=r)


@dashboard_bp.route('/profile')
@login_required
def profile():
    r = Recipe.query.filter_by(user_id=current_user.id).all()
    anzahl_rezepte = len(r)
    print("Rezepte:", r)
    print("Anzahl:", anzahl_rezepte)
    return render_template('profile.html', user=current_user, rezepte=r, anzahl_rezepte=anzahl_rezepte)



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


@dashboard_bp.route('/profil/bearbeiten', methods=['GET', 'POST'])
@login_required
def profil_bearbeiten():
    if request.method == 'POST':
        neuer_name = request.form.get('username')
        neue_email = request.form.get('email')

        current_user.username = neuer_name
        current_user.email = neue_email

        db.session.commit()
        flash('Profil aktualisiert.', 'success')
        return redirect(url_for('dashboard.profile'))

    return render_template('profil_bearbeiten.html', user=current_user)

@dashboard_bp.route('/recipe/<int:id>')
def recipe_details(id):
    rezepte= Recipe.query.all()
    rezept = next((r for r in rezepte if r.id == id), None)
    user = User.query.get(rezept.user_id)
    zutaten = RawIngredient.query.filter_by(recipe_id=id).all()

    print(zutaten)
    return render_template('recipe_details.html', rezept=rezept, creator=user, zutaten=zutaten)

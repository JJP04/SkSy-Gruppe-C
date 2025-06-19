from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, logout_user
from sqlalchemy import or_

from .models import User, Recipe, Ingredient, RecipeIngredient, RawIngredient
from .extensions import db

# für die profilansicht


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def rezepte():
    #r = Recipe.query.all()

    r = Recipe.query.filter(
        or_(
            Recipe.visibility == "public",
            (Recipe.visibility == "private") & (Recipe.user_id == current_user.id)
        )
    ).all()

    return render_template("dashboard.html", rezepte=r)


@dashboard_bp.route('/profile')
@login_required
def profile():
    r = Recipe.query.filter_by(user_id=current_user.id).all()
    anzahl_rezepte = len(r)
    print("Rezepte:", r)
    print("Anzahl:", anzahl_rezepte)
    return render_template('profile.html', user=current_user, rezepte=r, anzahl_rezepte=anzahl_rezepte)


@dashboard_bp.route("/profil/loeschen", methods=['GET', 'POST'])
@login_required
def profil_loeschen():
    user_id = current_user.id

    if request.method == 'GET':
        rezeptanzahl = Recipe.query.filter_by(user_id=user_id).count()
        print(">> Rezeptanzahl:", rezeptanzahl)

        if rezeptanzahl == 0:
            # Keine Rezepte → direkt löschen

            logout_user()
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            flash("Dein Profil wurde erfolgreich gelöscht.", "info")
            return redirect(url_for("auth.login"))
        else:
            # Rezepte vorhanden → Bestätigung anzeigen






            return render_template(
                'profil_loeschen_bestaetigung.html',
                rezeptanzahl=rezeptanzahl  # Wichtig: Anzahl übergeben!
            )

    if request.method == 'POST':
        delete_recipes = request.form.get('delete_recipes') == 'true'

        if delete_recipes:
            recipes = Recipe.query.filter(Recipe.user_id == user_id).all()
            # Zuerst alle zugehörigen RawIngredients & RecipeIngredients löschen
            for recipe in recipes:
                RawIngredient.query.filter_by(recipe_id=recipe.id).delete()
                RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

            Recipe.query.filter_by(user_id=user_id).delete()
        else:
            #private löschen, da diese sonst in der DB nutzlos rumliegen
            recipes = Recipe.query.filter(
                Recipe.user_id == user_id,
                Recipe.visibility == "private"
            ).all()

            # Zuerst alle zugehörigen RawIngredients löschen
            for recipe in recipes:
                RawIngredient.query.filter_by(recipe_id=recipe.id).delete()
                RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

            # Dann die Rezepte löschen
            Recipe.query.filter(
                Recipe.user_id == user_id,
                Recipe.visibility == "private"
            ).delete()

            #öffentliche bleiben bestehen
            Recipe.query.filter_by(user_id=user_id).update({
                'user_id': 9999,
                'author_deleted': True
            })

        logout_user()
        user = User.query.get(user_id)
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


@dashboard_bp.route('/dashboard/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        flash('Bitte gib einen Suchbegriff ein.', 'warning')
        return redirect(url_for('dashboard.rezepte'))

    rezepte = Recipe.query.filter(Recipe.title.ilike(f'%{query}%')).all()
    if not rezepte:
        flash('Keine Rezepte gefunden.', 'info')

    return render_template('dashboard.html', rezepte=rezepte, query=query)


@dashboard_bp.route('/recipe/<int:id>')
def recipe_details(id):
    rezepte = Recipe.query.all()
    rezept = next((r for r in rezepte if r.id == id), None)
    user = User.query.get(rezept.user_id)
    raw_zutaten = RawIngredient.query.filter_by(recipe_id=id).all()
    verified_zutaten = [ri.ingredient for ri in rezept.recipe_ingredients]
    # Case-insensitive deduplication
    zutaten = list({z.name.lower(): z for z in raw_zutaten + verified_zutaten}.values())
    print(zutaten)
    return render_template('recipe_details.html', rezept=rezept, creator=user, zutaten=zutaten)

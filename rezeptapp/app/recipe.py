from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, abort
from sqlalchemy import func
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os

from .models import User, Recipe, Ingredient, RecipeIngredient, RawIngredient
from .extensions import db
from difflib import get_close_matches

# pip install transformers torch flask (braucht etwas länger ~3min)
# used model: https://huggingface.co/edwardjross/xlm-roberta-base-finetuned-recipe-all


recipe_bp = Blueprint('recipe', __name__)


@recipe_bp.route('/recipe/create', methods=['GET'])
def create():
    return render_template('recipe.html', title="", ingredients=[], active_tab="create")  # initiales laden von create


@recipe_bp.route('/recipe/analyze', methods=['GET', 'POST'])
def analyze():
    title = request.form.get('title')
    description = request.form.get('description')
    visibility = request.form.get('visibility')

    # Validierung
    if not title or not description or not visibility:
        flash("Alle Felder sind erforderlich.", "error")
        return redirect(url_for('recipe.create'))

    image = request.files.get('imageUpload')
    image_path = ''

    if image and image.filename.endswith('.jpg'):
        filename = secure_filename(image.filename)
        tmp_folder = os.path.join(current_app.root_path, 'static', 'Images')
        full_path = os.path.join(tmp_folder, filename)
        image.save(full_path)
        image_path = f"images/{filename}"

    # NER-Modell aus dem Flask App-Context holen
    ner = current_app.ner_pipeline

    # Text analysieren
    ner_results = ner(description)

    # print("→ KI-Rohantwort:", ner_results)

    # Extrahiere Zutaten, Mengen etc. je nach Modell-Output
    # Beispiel: alle Wörter aus Entities mit Label 'NAME' sammeln
    ingredients = []
    for entity in ner_results:
        # Prüfe, ob das Modell Labels wie 'NAME' liefert (je nach Modell unterschiedlich!)
        if entity.get('entity_group') == 'NAME':
            ingredients.append(entity.get('word'))

    cleaned_ingredients = list(set([word.lower() for word in ingredients if len(word) > 2]))  # duplikate entfernen

    # Übergabe an neue Seite
    return render_template(
        'recipe.html', active_tab='ingredients', ingredients=cleaned_ingredients, title=title, description=description,
        visibility=visibility, image_path=image_path
    )


# Ähnlichkeitsprüfung für neue Zutaten
def finde_aehnliche_zutat(name, bekannte_zutaten, schwelle=0.8):
    matches = get_close_matches(name.lower(), bekannte_zutaten, n=1, cutoff=schwelle)
    return matches[0] if matches else None


@recipe_bp.route('/recipe/save', methods=['GET', 'POST'])
def save():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    visibility = request.form.get('visibility', 'private')
    author = current_user
    image_path = request.form.get('image_path', '')

    if not author.is_authenticated:
        flash("Nicht eingeloggt.", "error")
        return redirect(url_for('auth.login'))

    raw_input_ingredients = request.form.getlist('ingredients[]')
    raw_input_ingredients = [i.strip().lower() for i in raw_input_ingredients if i.strip()]

    if not title or not raw_input_ingredients:
        flash("Titel und Zutaten dürfen nicht leer sein.", "error")
        return redirect(url_for('dashboard.dashboard'))

    neues_rezept = Recipe(
        title=title,
        description=description,
        visibility=visibility,
        user_id=author.id,  # wichtig: das User-FK-Feld
        image_path=image_path
    )
    db.session.add(neues_rezept)

    db.session.flush()

    bekannte_zutaten = [z.name for z in Ingredient.query.all()]
    verwendungsschwelle = 3

    for name in raw_input_ingredients:
        match = finde_aehnliche_zutat(name, bekannte_zutaten)
        existing = None

        if match:
            existing = Ingredient.query.filter_by(name=match).first()
        else:
            raw = RawIngredient(name=name, recipe=neues_rezept)
            db.session.add(raw)

            count = db.session.query(RawIngredient).filter_by(name=name).count()
            if count >= verwendungsschwelle:
                existing = Ingredient(name=name)
                db.session.add(existing)
                bekannte_zutaten.append(name)

        if existing:
            db.session.add(RecipeIngredient(recipe=neues_rezept, ingredient=existing))

    db.session.commit()

    return redirect(url_for('dashboard.rezepte'))

@recipe_bp.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Nur der Ersteller darf löschen
    if recipe.user_id != current_user.id:
        abort(403)

    RawIngredient.query.filter_by(recipe_id=recipe.id).delete()
    RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()
    db.session.delete(recipe)
    db.session.commit()
    flash('Rezept gelöscht.', 'success')
    return redirect(url_for('dashboard.profile'))    # oder dein Dashboard

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from sqlalchemy import func
from flask_login import current_user
from .models import User, Recipe, Ingredient, RecipeIngredient, RawIngredient
from .extensions import db
from difflib import get_close_matches

#pip install transformers torch flask (braucht etwas länger ~3min)
#used model: https://huggingface.co/edwardjross/xlm-roberta-base-finetuned-recipe-all


recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipe/create', methods=['GET'])
def create():
    return render_template('recipe.html', title="", ingredients=[], active_tab="create") #initiales laden von create

@recipe_bp.route('/recipe/analyze', methods=['GET', 'POST'])
def analyze():
    title = request.form.get('title')
    description = request.form.get('description')
    visibility = request.form.get('visibility')

    # Validierung
    if not title or not description or not visibility:
        flash("Alle Felder sind erforderlich.", "error")
        return redirect(url_for('recipe.create'))

    # NER-Modell aus dem Flask App-Context holen
    ner = current_app.ner_pipeline

    # Text analysieren
    ner_results = ner(description)

    #print("→ KI-Rohantwort:", ner_results)

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
        'recipe.html', active_tab='ingredients', ingredients=cleaned_ingredients, title=title, description=description, visibility=visibility
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
        user_id=author.id  # wichtig: das User-FK-Feld
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

    flash("Rezept erfolgreich gespeichert!", "success")
    return redirect(url_for('dashboard.rezepte'))

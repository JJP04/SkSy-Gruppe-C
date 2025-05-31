from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from sqlalchemy import func
from flask_login import current_user
from .models import User, Recipe
from .extensions import db

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

@recipe_bp.route('/recipe/save', methods=['GET', 'POST'])
def save():
    title = request.form['title']
    description = request.form['description']
    visibility = request.form['visibility']
    author = current_user

    if not author.is_authenticated:
        flash("Nicht eingeloggt.", "error")
        return redirect(url_for('auth.login'))

    neues_rezept = Recipe(
        title=title,
        description=description,
        visibility=visibility,
        user_id=author.id  # wichtig: das User-FK-Feld
    )
    db.session.add(neues_rezept)
    db.session.commit()

    return redirect(url_for('dashboard.dashboard'))
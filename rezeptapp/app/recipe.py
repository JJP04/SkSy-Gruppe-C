from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from sqlalchemy import func
from flask_login import current_user
from .models import User, Recipe
from .extensions import db


recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipe/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        visibility = request.form['visibility']
        author = current_user  # oder current_user.id

        neues_rezept = Recipe(
            title=title,
            description=description,
            visibility=visibility,
            user_id=author.id  # wichtig: das User-FK-Feld
        )
        db.session.add(neues_rezept)
        db.session.commit()
        return redirect(url_for('dashboard.dashboard'))



    return render_template('recipe.html')
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, logout_user
from sqlalchemy import or_

from .models import User, Recipe, Ingredient, RecipeIngredient, RawIngredient
from .extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_dashboard():
    users = User.query.all()
    return render_template('admin.html', users=users)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user_id == 9999:
        flash("Dieser Account kann nicht gelöscht werden", "success")
        return redirect(url_for('admin.admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash("Benutzer gelöscht", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    RawIngredient.query.filter_by(recipe_id=recipe.id).delete()
    RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()
    db.session.delete(recipe)
    db.session.commit()
    flash("Rezept gelöscht", "success")
    return redirect(url_for('admin.admin_dashboard'))
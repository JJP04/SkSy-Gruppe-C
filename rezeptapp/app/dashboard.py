from flask import Blueprint, render_template
from flask_login import login_required, current_user #für die profilansicht


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@dashboard_bp.route('/profil')
@login_required
def profil():
    return render_template('profil.html', user=current_user)
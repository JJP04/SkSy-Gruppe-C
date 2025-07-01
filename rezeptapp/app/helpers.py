import os
from uuid import uuid4
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def save_image(file_storage, subfolder="uploads", old_filename=None):
    """
    Speichert ein hochgeladenes Bild und gibt den relativen Pfad zurück.
    subfolder: 'uploads' (Profil) oder 'images' (Rezepte) etc.
    """
    if not allowed(file_storage.filename):
        raise ValueError("Ungültiges Dateiformat")

    # Zielordner erstellen (app/static/<subfolder>)
    base = os.path.join(current_app.root_path, "static", subfolder)
    os.makedirs(base, exist_ok=True)

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{ext}"
    full_path = os.path.join(base, filename)
    file_storage.save(full_path)

    # alte Datei löschen
    if old_filename:
        try:
            os.remove(os.path.join(base, old_filename))
        except OSError:
            pass

    # Rückgabe: Pfad ab /static – damit url_for('static', filename=path) funktioniert
    return f"{subfolder}/{filename}"

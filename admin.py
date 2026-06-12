from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import os
import secrets
from functools import wraps
from supabase import create_client, Client

app = Flask(__name__, template_folder='.')
CORS(app, origins=["https://interactiv-media.netlify.app"])

# ==================== CONNEXION SUPABASE ====================
# Les secrets sont lus depuis les variables d'environnement Render
# (jamais écrits en dur dans le code)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "tuteur")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "motdepasse123")

# Stocke les tokens de session actifs en mémoire
sessions_actives = {}

# ==================== DÉCORATEUR AUTH ====================

def connexion_requise(f):
    """Vérifie que le token JWT est valide avant d'autoriser l'accès."""
    @wraps(f)
    def verification(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token not in sessions_actives or sessions_actives[token] < datetime.now().timestamp():
            return jsonify({'erreur': 'Non autorisé'}), 401
        return f(*args, **kwargs)
    return verification

# ==================== ROUTES ADMIN ====================

@app.route('/api/admin/login', methods=['POST'])
def connexion_admin():
    """Connexion admin : renvoie un token si les identifiants sont corrects."""
    donnees = request.get_json()
    username = donnees.get('username')
    password = donnees.get('password')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = secrets.token_urlsafe(32)
        # Token valide pendant 1 heure
        sessions_actives[token] = datetime.now().timestamp() + 3600
        return jsonify({'token': token, 'expires_in': 3600})
    return jsonify({'erreur': 'Identifiants invalides'}), 401

@app.route('/api/admin/deconnexion', methods=['POST'])
@connexion_requise
def admin_deconnexion():
    """Supprime le token de session (déconnexion)."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token in sessions_actives:
        del sessions_actives[token]
    return jsonify({'message': 'Déconnecté'}), 200

# ==================== ROUTES ÉVÉNEMENTS ====================

@app.route('/api/evenements', methods=['GET'])
def obtenir_evenements():
    """Renvoie tous les événements (accessible publiquement)."""
    resultat = supabase.table("agenda").select("*").order("date", desc=False).execute()
    return jsonify(resultat.data)

@app.route('/api/admin/evenements', methods=['GET'])
@connexion_requise
def admin_obtenir_evenements():
    """Renvoie tous les événements (réservé admin)."""
    resultat = supabase.table("agenda").select("*").order("date", desc=False).execute()
    return jsonify(resultat.data)

@app.route('/api/admin/evenements', methods=['POST'])
@connexion_requise
def admin_ajouter_evenement():
    """Ajoute un nouvel événement dans Supabase."""
    donnees = request.get_json()
    nouvel_event = {
        "titre": donnees.get("titre"),
        "date": donnees.get("date"),
        "description": donnees.get("description")
    }
    resultat = supabase.table("agenda").insert(nouvel_event).execute()
    return jsonify(resultat.data[0]), 201

@app.route('/api/admin/evenements/<int:id>', methods=['PUT'])
@connexion_requise
def admin_modifier_evenement(id):
    """Modifie un événement existant."""
    donnees = request.get_json()
    modifications = {}
    if "titre" in donnees:
        modifications["titre"] = donnees["titre"]
    if "date" in donnees:
        modifications["date"] = donnees["date"]
    if "description" in donnees:
        modifications["description"] = donnees["description"]
    resultat = supabase.table("agenda").update(modifications).eq("id", id).execute()
    if resultat.data:
        return jsonify(resultat.data[0])
    return jsonify({'erreur': 'Événement non trouvé'}), 404

@app.route('/api/admin/evenements/<int:id>', methods=['DELETE'])
@connexion_requise
def admin_supprimer_evenement(id):
    """Supprime un événement."""
    supabase.table("agenda").delete().eq("id", id).execute()
    return jsonify({'message': 'Événement supprimé'}), 200

# ==================== PAGE ADMIN ====================

@app.route('/admin-evenements')
def page_admin_evenements():
    return render_template('admin_evenements.html')

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Permet de vérifier que le service tourne (utilisé par le front pour réveiller Render)."""
    return jsonify({'status': 'OK'}), 200

# ==================== LANCEMENT ====================

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

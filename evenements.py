from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import os
import secrets
from functools import wraps
from supabase import create_client, Client

app = Flask(__name__, template_folder='.')

CORS(app, origins=["https://interactiv-media.netlify.app"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not all([SUPABASE_URL, SUPABASE_KEY, ADMIN_USERNAME, ADMIN_PASSWORD]):
    print("   SUPABASE_URL, SUPABASE_KEY, ADMIN_USERNAME, ADMIN_PASSWORD")
    exit(1)

print("Connexion à Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

sessions_actives = {}

def connexion_requise(f):
    @wraps(f)
    def verification(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token not in sessions_actives or sessions_actives[token] < datetime.now().timestamp():
            return jsonify({'erreur': 'Non autorisé'}), 401
        return f(*args, **kwargs)
    return verification

@app.route('/api/admin/login', methods=['POST'])
def connexion_admin():
    donnees = request.get_json()
    if donnees.get('username') == ADMIN_USERNAME and donnees.get('password') == ADMIN_PASSWORD:
        token = secrets.token_urlsafe(32)
        sessions_actives[token] = datetime.now().timestamp() + 3600
        return jsonify({'token': token})
    return jsonify({'erreur': 'Identifiants invalides'}), 401

@app.route('/api/evenements', methods=['GET'])
def obtenir_evenements():
    try:
        aujourd_hui = datetime.now().date().isoformat()
        futurs = supabase.table("agenda").select("*").gte("date", aujourd_hui).order("date").execute()
        nb_passes = max(0, 10 - len(futurs.data))
        passes = supabase.table("agenda").select("*").lt("date", aujourd_hui).order("date", desc=True).limit(nb_passes).execute()
        resultat = passes.data[::-1] + futurs.data
        return jsonify(resultat)
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/admin/evenements', methods=['GET'])
@connexion_requise
def admin_obtenir_evenements():
    resultat = supabase.table("agenda").select("*").order("date").execute()
    return jsonify(resultat.data)

@app.route('/api/admin/evenements', methods=['POST'])
@connexion_requise
def admin_ajouter_evenement():
    donnees = request.get_json()
    resultat = supabase.table("agenda").insert({
        "type": donnees.get("type"),
        "titre": donnees.get("titre"),
        "date": donnees.get("date"),
        "description": donnees.get("description"),
        "lieu": donnees.get("lieu")
    }).execute()
    return jsonify(resultat.data[0]), 201

@app.route('/api/admin/evenements/<int:id>', methods=['PUT'])
@connexion_requise
def admin_modifier_evenement(id):
    donnees = request.get_json()
    modifications = {}
    for champ in ["type", "titre", "date", "description", "lieu"]:
        if champ in donnees:
            modifications[champ] = donnees[champ]
    resultat = supabase.table("agenda").update(modifications).eq("id", id).execute()
    return jsonify(resultat.data[0] if resultat.data else {})

@app.route('/api/admin/evenements/<int:id>', methods=['DELETE'])
@connexion_requise
def admin_supprimer_evenement(id):
    supabase.table("agenda").delete().eq("id", id).execute()
    return jsonify({'message': 'Supprimé'})

@app.route('/admin-evenements')
def page_admin_evenements():
    return render_template('admin_evenements.html')

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

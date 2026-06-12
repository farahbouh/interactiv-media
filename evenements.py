from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import secrets
from functools import wraps
from supabase import create_client, Client

app = Flask(__name__, template_folder='.')
CORS(app)

# ==================== VOS IDENTIFIANTS SUPABASE ====================
SUPABASE_URL = "https://dzkrdctxfzyshcpcqmmf.supabase.co"
SUPABASE_KEY = "REMOVED"
# ===================================================================

print("Connexion à Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connecté !")

ADMIN_USERNAME = "tuteur"
ADMIN_PASSWORD = "motdepasse123"
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
        resultat = supabase.table("agenda").select("*").execute()
        return jsonify(resultat.data)
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/admin/evenements', methods=['GET'])
@connexion_requise
def admin_obtenir_evenements():
    resultat = supabase.table("agenda").select("*").execute()
    return jsonify(resultat.data)

@app.route('/api/admin/evenements', methods=['POST'])
@connexion_requise
def admin_ajouter_evenement():
    donnees = request.get_json()
    resultat = supabase.table("agenda").insert({
        "titre": donnees.get("titre"),
        "date": donnees.get("date"),
        "description": donnees.get("description")
    }).execute()
    return jsonify(resultat.data[0]), 201

@app.route('/api/admin/evenements/<int:id>', methods=['PUT'])
@connexion_requise
def admin_modifier_evenement(id):
    donnees = request.get_json()
    modifications = {}
    if "titre" in donnees:
        modifications["titre"] = donnees["titre"]
    if "date" in donnees:
        modifications["date"] = donnees["date"]
    if "description" in donnees:
        modifications["description"] = donnees["description"]
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

@app.route('/evenements.html')
def page_evenements():
    return render_template('evenements.html')

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
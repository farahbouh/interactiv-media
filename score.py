from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict
from time import time
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# ---------- Configuration Supabase ----------
import traceback

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {'OK' if SUPABASE_KEY else 'MANQUANTE'}")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase connecté OK")
except Exception as e:
    print(f"ERREUR Supabase: {e}")
    traceback.print_exc()
    raise

# ---------- Pour limiter les envois par IP ----------
dernier_envoi_par_ip = defaultdict(float)
DELAI_SECONDES = 10

# ---------- Nettoyer la base pour ne garder que les N meilleurs scores ----------
def nettoyer_top_n(n=50):
    """Garde seulement les N meilleurs scores dans Supabase"""
    try:
        # Récupérer tous les scores triés
        response = supabase.table("scores")\
            .select("*")\
            .order("score", desc=True)\
            .execute()
        
        # Supprimer ceux qui dépassent la limite
        if len(response.data) > n:
            ids_a_supprimer = [item['id'] for item in response.data[n:]]
            for id_item in ids_a_supprimer:
                supabase.table("scores").delete().eq("id", id_item).execute()
    except Exception as e:
        print(f"Erreur nettoyage: {e}")

# ---------- Route pour ajouter un score ----------
@app.route('/api/score', methods=['POST'])
def ajouter_score():
    # Limitation par IP
    ip = request.remote_addr
    maintenant = time()
    if maintenant - dernier_envoi_par_ip[ip] < DELAI_SECONDES:
        return jsonify({'erreur': 'Attendez quelques secondes avant de renvoyer un score.'}), 429
    dernier_envoi_par_ip[ip] = maintenant

    # Récupération des données
    donnees = request.get_json()
    pseudo = donnees.get("pseudo")
    score = donnees.get("score")

    if not pseudo or score is None:
        return jsonify({'erreur': 'Pseudo et score requis.'}), 400

    try:
        # Insertion dans Supabase
        data = {
            "pseudo": pseudo,
            "score": score,
            "date": datetime.now().isoformat()
        }
        supabase.table("scores").insert(data).execute()
        
        # Nettoyage : on garde seulement les 50 meilleurs scores
        nettoyer_top_n(50)
        
        return jsonify({'statut': 'score enregistré'}), 201
    except Exception as e:
        return jsonify({'erreur': f'Erreur base de données: {str(e)}'}), 500

# ---------- Route pour récupérer le top 10 ----------
@app.route('/api/scores', methods=['GET'])
def obtenir_top_scores():
    try:
        response = supabase.table("scores")\
            .select("pseudo, score, date")\
            .order("score", desc=True)\
            .limit(10)\
            .execute()
        
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

# ---------- Health check pour Render ----------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'API is running'}), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
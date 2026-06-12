from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict
from time import time
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis d'autres origines (ex: Netlify)

# ==================== CONNEXION SUPABASE ====================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Vérification au démarrage
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {'OK' if SUPABASE_KEY else 'MANQUANTE'}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase connecté")

# ==================== ANTI-SPAM ====================

# Mémorise le dernier envoi par adresse IP
dernier_envoi_par_ip = defaultdict(float)
DELAI_SECONDES = 10  # Délai minimum entre deux envois

# ==================== FONCTIONS UTILITAIRES ====================

def garder_top_n(n=50):
    """Supprime les scores au-delà du top N pour ne pas surcharger la base."""
    tous_les_scores = supabase.table("scores").select("*").order("score", desc=True).execute()
    if len(tous_les_scores.data) > n:
        ids_a_supprimer = [s['id'] for s in tous_les_scores.data[n:]]
        for id_score in ids_a_supprimer:
            supabase.table("scores").delete().eq("id", id_score).execute()

# ==================== ROUTES ====================

@app.route('/api/score', methods=['POST'])
def ajouter_score():
    """Reçoit un score envoyé par le quiz et l'enregistre dans Supabase."""

    # Vérification anti-spam par IP
    ip = request.remote_addr
    maintenant = time()
    if maintenant - dernier_envoi_par_ip[ip] < DELAI_SECONDES:
        return jsonify({'erreur': 'Attendez quelques secondes avant de renvoyer un score.'}), 429
    dernier_envoi_par_ip[ip] = maintenant

    # Lecture des données envoyées par le quiz
    donnees = request.get_json()
    pseudo = donnees.get("pseudo")
    score = donnees.get("score")

    # Vérification que les champs sont bien présents
    if not pseudo or score is None:
        return jsonify({'erreur': 'Pseudo et score requis.'}), 400

    # Enregistrement dans Supabase
    nouveau_score = {
        "pseudo": pseudo,
        "score": score,
        "date": datetime.now().isoformat()
    }
    supabase.table("scores").insert(nouveau_score).execute()

    # Nettoyage : on garde seulement les 50 meilleurs
    garder_top_n(50)

    return jsonify({'statut': 'score enregistré'}), 201


@app.route('/api/scores', methods=['GET'])
def obtenir_top_scores():
    """Renvoie les 10 meilleurs scores, triés du plus grand au plus petit."""
    resultats = supabase.table("scores") \
        .select("pseudo, score, date") \
        .order("score", desc=True) \
        .limit(10) \
        .execute()
    return jsonify(resultats.data)


@app.route('/health', methods=['GET'])
def health_check():
    """Route de vérification : permet de savoir si l'API tourne."""
    return jsonify({'status': 'API is running'}), 200


# ==================== LANCEMENT ====================

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

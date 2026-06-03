from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
from collections import defaultdict
from time import time

app = Flask(__name__)
CORS(app)

# ---------- Pour limiter les envois par IP ----------
dernier_envoi_par_ip = defaultdict(float)
DELAI_SECONDES = 10   # 10 secondes entre deux soumissions

# ---------- Initialisation de la base ----------
def initialiser_base():
    connexion = sqlite3.connect("data/scores.db")
    curseur = connexion.cursor()
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT NOT NULL,
            score INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    connexion.commit()
    connexion.close()

initialiser_base()

# ---------- Nettoyer la base pour ne garder que les N meilleurs scores ----------
def nettoyer_top_n(n=50):
    connexion = sqlite3.connect("data/scores.db")
    curseur = connexion.cursor()
    curseur.execute('''
        DELETE FROM scores
        WHERE id NOT IN (
            SELECT id FROM scores
            ORDER BY score DESC
            LIMIT ?
        )
    ''', (n,))
    connexion.commit()
    connexion.close()

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

    # Insertion en base
    connexion = sqlite3.connect("data/scores.db")
    curseur = connexion.cursor()
    curseur.execute('INSERT INTO scores (pseudo, score, date) VALUES (?, ?, ?)',
                    (pseudo, score, datetime.now().isoformat()))
    connexion.commit()
    connexion.close()

    # Nettoyage : on garde seulement les 50 meilleurs scores
    nettoyer_top_n(50)

    return jsonify({'statut': 'score enregistré'}), 201

# ---------- Route pour récupérer le top 10 ----------
@app.route('/api/scores', methods=['GET'])
def obtenir_top_scores():
    connexion = sqlite3.connect("data/scores.db")
    curseur = connexion.cursor()
    curseur.execute("SELECT pseudo, score, date FROM scores ORDER BY score DESC LIMIT 10")
    lignes = curseur.fetchall()
    connexion.close()
    scores = [{'pseudo': ligne[0], 'score': ligne[1], 'date': ligne[2]} for ligne in lignes]
    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
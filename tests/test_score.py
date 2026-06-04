import pytest
import sys
import os

# Ajoute le dossier parent pour pouvoir importer ton app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importe ton application (remplace 'score' par le nom de ton fichier sans .py)
from score import app

@pytest.fixture
def client():
    """Crée un client de test pour Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test que l'endpoint /health fonctionne"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'API is running'

def test_get_scores(client):
    """Test que l'endpoint /api/scores retourne une liste"""
    response = client.get('/api/scores')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_post_score_success(client):
    """Test que l'envoi d'un score fonctionne"""
    response = client.post('/api/score', 
                          json={'pseudo': 'testeur', 'score': 42})
    assert response.status_code == 201
    assert response.json['statut'] == 'score enregistré'

def test_post_score_missing_pseudo(client):
    """Test que l'API refuse les scores sans pseudo"""
    response = client.post('/api/score', 
                          json={'score': 10})
    assert response.status_code == 400
    assert 'erreur' in response.json

def test_post_score_missing_score(client):
    """Test que l'API refuse les scores sans valeur"""
    response = client.post('/api/score', 
                          json={'pseudo': 'testeur'})
    assert response.status_code == 400
    assert 'erreur' in response.json
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from score import app, dernier_envoi_par_ip

@pytest.fixture(autouse=True)
def reset_rate_limit():
    dernier_envoi_par_ip.clear()
    yield

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'API is running'

def test_get_scores(client):
    response = client.get('/api/scores')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_post_score_success(client):
    response = client.post('/api/score',
                          json={'pseudo': 'testeur', 'score': 42})
    assert response.status_code == 201
    assert response.json['statut'] == 'score enregistré'

def test_post_score_missing_pseudo(client):
    response = client.post('/api/score',
                          json={'score': 10})
    assert response.status_code == 400
    assert 'erreur' in response.json

def test_post_score_missing_score(client):
    response = client.post('/api/score',
                          json={'pseudo': 'testeur'})
    assert response.status_code == 400
    assert 'erreur' in response.json
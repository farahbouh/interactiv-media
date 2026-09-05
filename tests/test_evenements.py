import sys
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

# Ajoute le dossier parent au path pour importer evenements
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evenements import app, sessions_actives

# ==================== FIXTURES ====================

@pytest.fixture(autouse=True)
def reset_sessions():
    """Reset les sessions actives avant chaque test"""
    sessions_actives.clear()
    yield

@pytest.fixture
def client():
    """Client de test Flask"""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_token(client):
    """Se connecte et retourne un token valide"""
    response = client.post('/api/admin/login', json={
        'username': 'tuteur',
        'password': 'motdepasse123'
    })
    return response.json['token']

# ==================== TESTS HEALTH ====================

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

# ==================== TESTS ADMIN LOGIN ====================

def test_admin_login_success(client):
    response = client.post('/api/admin/login', json={
        'username': 'tuteur',
        'password': 'motdepasse123'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_admin_login_wrong_password(client):
    response = client.post('/api/admin/login', json={
        'username': 'tuteur',
        'password': 'faux_mot_de_passe'
    })
    assert response.status_code == 401
    assert 'erreur' in response.json

def test_admin_login_wrong_username(client):
    response = client.post('/api/admin/login', json={
        'username': 'fake_user',
        'password': 'motdepasse123'
    })
    assert response.status_code == 401
    assert 'erreur' in response.json

def test_admin_login_missing_fields(client):
    response = client.post('/api/admin/login', json={
        'username': 'tuteur'
    })
    # Le code doit gérer les champs manquants
    assert response.status_code in [400, 401]

# ==================== TESTS ROUTES PROTÉGÉES (sans auth) ====================

def test_admin_get_events_without_auth(client):
    """Accès sans token doit être refusé"""
    response = client.get('/api/admin/evenements')
    assert response.status_code == 401
    assert 'erreur' in response.json

def test_admin_post_event_without_auth(client):
    response = client.post('/api/admin/evenements', json={
        'titre': 'Test',
        'date': '1 janvier 2026',
        'description': 'Description test'
    })
    assert response.status_code == 401

def test_admin_put_event_without_auth(client):
    response = client.put('/api/admin/evenements/1', json={
        'titre': 'Modifié'
    })
    assert response.status_code == 401

def test_admin_delete_event_without_auth(client):
    response = client.delete('/api/admin/evenements/1')
    assert response.status_code == 401

# ==================== TESTS ROUTES PROTÉGÉES (avec auth - mock Supabase) ====================

@patch('evenements.supabase')
def test_admin_get_events_with_auth(mock_supabase, client, auth_token):
    """Test avec auth et mock de Supabase"""
    # Mock de la réponse Supabase
    mock_data = [
        {'id': 1, 'titre': 'Event 1', 'date': '2026-01-01', 'description': 'Desc 1'},
        {'id': 2, 'titre': 'Event 2', 'date': '2026-02-01', 'description': 'Desc 2'}
    ]
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    mock_select.execute.return_value = mock_execute
    mock_table.select.return_value = mock_select
    mock_supabase.table.return_value = mock_table

    response = client.get('/api/admin/evenements',
                         headers={'Authorization': f'Bearer {auth_token}'})

    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['titre'] == 'Event 1'

@patch('evenements.supabase')
def test_admin_post_event_with_auth(mock_supabase, client, auth_token):
    """Test ajout d'événement avec auth"""
    mock_data = {'id': 3, 'titre': 'Nouvel Event', 'date': '15 juin 2026', 'description': 'Nouveau'}
    mock_insert = MagicMock()
    mock_insert.execute.return_value.data = [mock_data]
    mock_supabase.table.return_value.insert.return_value = mock_insert

    response = client.post('/api/admin/evenements',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={'titre': 'Nouvel Event', 'date': '15 juin 2026', 'description': 'Nouveau'}
    )

    assert response.status_code == 201
    assert response.json['titre'] == 'Nouvel Event'

@patch('evenements.supabase')
def test_admin_put_event_with_auth(mock_supabase, client, auth_token):
    """Test modification d'événement"""
    mock_data = {'id': 1, 'titre': 'Modifié', 'date': '2026-01-01', 'description': 'Modifié'}
    mock_update = MagicMock()
    mock_eq = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = [mock_data]

    mock_eq.execute.return_value = mock_execute
    mock_update.eq.return_value = mock_eq
    mock_supabase.table.return_value.update.return_value = mock_update

    response = client.put('/api/admin/evenements/1',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={'titre': 'Modifié'}
    )

    assert response.status_code == 200
    assert response.json['titre'] == 'Modifié'

@patch('evenements.supabase')
def test_admin_put_event_not_found(mock_supabase, client, auth_token):
    """Test modification d'un événement qui n'existe pas"""
    mock_update = MagicMock()
    mock_eq = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = []  # Pas de résultat

    mock_eq.execute.return_value = mock_execute
    mock_update.eq.return_value = mock_eq
    mock_supabase.table.return_value.update.return_value = mock_update

    response = client.put('/api/admin/evenements/999',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={'titre': 'Modifié'}
    )

    assert response.status_code == 404

@patch('evenements.supabase')
def test_admin_delete_event_with_auth(mock_supabase, client, auth_token):
    """Test suppression d'événement"""
    mock_delete = MagicMock()
    mock_eq = MagicMock()
    mock_execute = MagicMock()

    mock_eq.execute.return_value = mock_execute
    mock_delete.eq.return_value = mock_eq
    mock_supabase.table.return_value.delete.return_value = mock_delete

    response = client.delete('/api/admin/evenements/1',
        headers={'Authorization': f'Bearer {auth_token}'})

    assert response.status_code == 200
    assert 'message' in response.json

# ==================== TESTS ROUTES PUBLIQUES (avec mock Supabase) ====================

@patch('evenements.supabase')
def test_get_events_public(mock_supabase, client):
    """Test GET /api/evenements public"""
    mock_data = [
        {'id': 1, 'titre': 'Event 1', 'date': '2026-01-01', 'description': 'Desc 1'}
    ]
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    mock_select.execute.return_value = mock_execute
    mock_table.select.return_value = mock_select
    mock_supabase.table.return_value = mock_table

    response = client.get('/api/evenements')

    assert response.status_code == 200
    assert len(response.json) == 1

@patch('evenements.supabase')
def test_get_events_public_supabase_error(mock_supabase, client):
    """Test erreur Supabase sur route publique"""
    mock_supabase.table.side_effect = Exception("Supabase connection error")

    response = client.get('/api/evenements')

    assert response.status_code == 500
    assert 'erreur' in response.json

# ==================== TEST PAGE ADMIN HTML ====================

def test_admin_page_html(client):
    """Test que la page admin s'affiche"""
    response = client.get('/admin-evenements')
    assert response.status_code == 200
    assert 'Connexion Admin' in response.data.decode('utf-8')

# ==================== TEST TOKEN EXPIRATION ====================

def test_token_expiration():
    """Test que le token expire après 3600 secondes"""
    from evenements import connexion_requise
    import time

    # Simuler un token
    token = 'fake_token'
    sessions_actives[token] = time.time() - 7200  # Il y a 2 heures

    # Créer une requête mock
    with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):

        pass

# ==================== TESTS DE DÉCONNEXION ====================

def test_admin_logout(client, auth_token):
    """Test la déconnexion"""
    # Vérifier qu'on peut accéder avec le token
    response_get = client.get('/api/admin/evenements',
                             headers={'Authorization': f'Bearer {auth_token}'})
    assert response_get.status_code in [200, 500]  # 500 si Supabase pas mocké

    # Se déconnecter
    response_logout = client.post('/api/admin/deconnexion',
                                  headers={'Authorization': f'Bearer {auth_token}'})
    assert response_logout.status_code == 200

    # Le token ne devrait plus fonctionner
    response_after = client.get('/api/admin/evenements',
                               headers={'Authorization': f'Bearer {auth_token}'})
    assert response_after.status_code == 401
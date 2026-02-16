import os
import pytest

from App.main import create_app
from App.database import db, create_db


@pytest.fixture(scope='module')
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_routes.db'})
    create_db()
    with app.test_client() as client:
        yield client
    db.drop_all()
    try:
        os.remove('test_routes.db')
    except OSError:
        pass


def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json() == {'status': 'healthy'}


def test_get_users_empty(client):
    resp = client.get('/api/users')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_user_api(client):
    resp = client.post('/api/users', json={'username': 'alice', 'password': 'pass'})
    assert resp.status_code in (200, 201)
    data = resp.get_json()
    assert 'message' in data


def test_get_users_nonempty(client):
    resp = client.get('/api/users')
    assert resp.status_code == 200
    users = resp.get_json()
    assert isinstance(users, list)
    assert len(users) >= 1

import pytest
from JYPNB.WebPage import main
from unittest.mock import patch
from flask import url_for

@pytest.fixture
def client():
    main.application.config['TESTING'] = True
    with main.application.test_client() as client:
        yield client

# Test case for home route
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

# Test case for signup route
def test_signup(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data

# Test case for user login
def test_login(client):
    with patch('WebPage.Week1.get_db_connection') as mock_get_db:
        mock_conn = mock_get_db.return_value
        mock_conn.execute.return_value.fetchone.return_value = {
            'username': 'test_user',
            'password': main.generate_password_hash('test_password')
        }
        response = client.post('/login', data=dict(username='test_user', password='test_password'))
        assert response.status_code == 302  # Redirect to homepage
        assert response.headers['Location'] == url_for('homepage', _external=True)

# Test case for coverage report route
def test_coverage_report(client):
    response = client.get('/coverage')
    assert response.status_code == 200
    assert b'Coverage Report' in response.data

# More test cases...

# Example of using a fixture
@pytest.fixture
def new_user():
    return {'first_name': 'John', 'last_name': 'Doe', 'username': 'johndoe', 'password': 'password123'}

# Test case using fixture
def test_user_signup(client, new_user):
    response = client.post('/submit_signup', data=new_user)
    assert response.status_code == 302  # Redirect after signup
    assert response.headers['Location'] == url_for('login', _external=True)

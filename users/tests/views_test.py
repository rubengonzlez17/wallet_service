import pytest
from rest_framework import status


@pytest.mark.django_db
def test_create_user(client):
    url = '/api/users/register/'
    data = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'password123'
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'token' in response.data
    assert response.data['message'] == 'User successfully registered.'


@pytest.mark.django_db
def test_create_user_invalid_data(client):
    url = '/api/users/register/'
    data = {
        'fake_field': 'john_doe',
        'password': 'password123'
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data


@pytest.mark.django_db
def test_create_user_missing_username(client):
    url = '/api/users/register/'
    data = {
        'email': 'john@example.com',
        'password': 'password123',
        'user_type': 'CLIENT'
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data


@pytest.mark.django_db
def test_create_user_missing_password(client):
    url = '/api/users/register/'
    data = {
        'username': 'john_doe',
        'email': 'john@example.com',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data


@pytest.mark.django_db
def test_create_user_duplicate_username(client):
    url = '/api/users/register/'
    data = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'password123'
    }
    client.post(url, data, format='json')

    data['email'] = 'john2@example.com'
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data


@pytest.mark.django_db
def test_create_user_invalid_email(client):
    url = '/api/users/register/'
    data = {
        'username': 'john_doe',
        'email': 'fake_email',
        'password': 'password123'
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data

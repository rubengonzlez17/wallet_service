import pytest
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError
from users.serializers import UserSerializer


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'securepassword123',
        'user_type': 'CLIENT'
    }


@pytest.fixture
def user():
    return get_user_model().objects.create_user(username='testuser',
                                                email='testuser@example.com',
                                                password='securepassword123',
                                                user_type='CLIENT')


@pytest.mark.django_db
def test_user_serializer_create(user_data):
    serializer = UserSerializer(data=user_data)

    assert serializer.is_valid()

    user = serializer.save()

    assert user.username == user_data['username']
    assert user.email == user_data['email']
    assert user.user_type == user_data['user_type']

    assert user.check_password(user_data['password']) is True


@pytest.mark.django_db
def test_user_serializer_missing_email():
    user_data = {
        'username': 'testuser',
        'password': 'securepassword123',
        'user_type': 'CLIENT'
    }

    serializer = UserSerializer(data=user_data)

    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_user_serializer_missing_username():
    user_data = {
        'email': 'testuser@example.com',
        'password': 'securepassword123',
        'user_type': 'CLIENT'
    }

    serializer = UserSerializer(data=user_data)

    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_user_serializer_password_is_write_only(user_data):
    serializer = UserSerializer(data=user_data)
    serializer.is_valid()

    validated_data = serializer.validated_data

    assert 'password' in validated_data

    user = serializer.save()
    user_serializer = UserSerializer(user)

    assert 'password' not in user_serializer.data


@pytest.mark.django_db
def test_user_serializer_create_invalid_data():
    invalid_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': None
    }

    serializer = UserSerializer(data=invalid_data)

    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_user_serializer_serialization(user):
    serializer = UserSerializer(user)

    data = serializer.data
    assert data['username'] == user.username
    assert data['email'] == user.email
    assert 'password' not in data
    assert data['user_type'] == user.user_type

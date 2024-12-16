import pytest
from django.core.exceptions import ValidationError
from users.models import CustomUser


@pytest.mark.django_db
def test_create_custom_user_with_default_user_type():
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='securepassword123'
    )

    assert user.user_type == 'CLIENT'


@pytest.mark.django_db
def test_create_custom_user_with_commerce_user_type():
    user = CustomUser.objects.create_user(
        username='testcommerce',
        email='testcommerce@example.com',
        password='securepassword123',
        user_type='COMMERCE'
    )

    assert user.user_type == 'COMMERCE'


@pytest.mark.django_db
def test_create_custom_user_with_invalid_user_type():
    with pytest.raises(ValidationError):
        user = CustomUser.objects.create_user(
            username='invaliduser',
            email='invaliduser@example.com',
            password='securepassword123',
            user_type='INVALID_TYPE'
        )
        user.full_clean()


@pytest.mark.django_db
def test_create_custom_user_without_user_type():
    user = CustomUser.objects.create_user(
        username='no_user_type',
        email='no_user_type@example.com',
        password='securepassword123'
    )

    assert user.user_type == 'CLIENT'


@pytest.mark.django_db
def test_user_type_choices():
    user_client = CustomUser.objects.create_user(
        username='clientuser',
        email='clientuser@example.com',
        password='securepassword123',
        user_type='CLIENT'
    )

    user_commerce = CustomUser.objects.create_user(
        username='commerceuser',
        email='commerceuser@example.com',
        password='securepassword123',
        user_type='COMMERCE'
    )

    assert user_client.user_type == 'CLIENT'
    assert user_commerce.user_type == 'COMMERCE'

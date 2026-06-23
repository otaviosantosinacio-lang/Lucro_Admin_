from jwt import decode

from lucro_admin.api.security import create_access_token


def test_jwt(settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == 401
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_invalid_user(client, user, token):

    user.email = ''
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 401
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_invalid_subjetc_email(client, user):
    data = {'no-email': 'test'}
    token = create_access_token(data)
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 401
    assert response.json() == {'detail': 'Could not validate credentials'}

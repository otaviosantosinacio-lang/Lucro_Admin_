from freezegun import freeze_time

def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == 200
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_email_incorrect(client, user):
    user.email_fail = 'test@testlucroadmin.com'
    response = client.post(
        '/auth/token',
        data={'username': user.email_fail, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == 401
    assert token['detail'] == {'message': 'Incorrect email or password'}


def test_get_token_password_incorrect(client, user):
    user.password_fail = 'test13579857'
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.password_fail},
    )

    token = response.json()

    assert response.status_code == 401
    assert token['detail'] == {'message': 'Incorrect email or password'}

def test_token_expired_after_time(client, user):
    with freeze_time('2025-04-01 13:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password
            }
        )

        assert response.status_code == 200
        token = response.json()['access_token']

    with freeze_time('2025-04-01 13:35:00'):
        response = client.put(
            f'users/{user.id_usuario}',
            headers= {'Authorization': f'Bearer {token}'},
            json={
            'nome_usuario': 'lucroadmintestauth',
            'email': 'lucroadmintestauth',
            'senha_hash': 'lucro_admin_test_auth'
        }
        )

        assert response.status_code == 401
        assert response.json() == {'detail': 'Could not validate credentials'}

def test_refresh_token(client, token):
    response= client.post(
        'auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'}
    )

    data= response.json()

    assert response.status_code == 200
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'

def test_token_expired_dont_refresh(client, user):
    with freeze_time('2025-04-01 13:00:00'):
        response= client.post(
            '/auth/token',
            data={
                'username': user.email, 'password': user.clean_password
            }
        )
        assert response.status_code == 200
        token= response.json()['access_token']

    with freeze_time('2025-04-01 13:32:00'):
        response= client.post(
            'auth/refresh_token',
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        assert response.status_code == 401
        assert response.json() == {'detail': 'Could not validate credentials'}
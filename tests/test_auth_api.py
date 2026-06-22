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

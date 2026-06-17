from http import HTTPStatus

from fastapi.testclient import TestClient
from lucro_admin.api.schemas import UserPublic

def test_create_user(client):

    response= client.post(
        '/users',
        json={
            'nome_usuario': 'testussername',
            'email': 'test@test.com',
            'senha_hash': 'senha_hash'
        }
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'id_usuario': 1,
        'nome_usuario': 'testussername',
        'email': 'test@test.com',
    }

def test_read_users(client):
    response= client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}

def test_read_users_with_user(client, user):
    user_schema= UserPublic.model_validate(user).model_dump()
    response= client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}
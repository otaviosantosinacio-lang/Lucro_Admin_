from http import HTTPStatus

from fastapi.testclient import TestClient
from lucro_admin.api.schemas import UserPublic


def test_create_user(client):

    response = client.post(
        '/users',
        json={
            'nome_usuario': 'testussername',
            'email': 'test@test.com',
            'senha_hash': 'senha_hash',
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'id_usuario': 1,
        'nome_usuario': 'testussername',
        'email': 'test@test.com',
    }


def test_create_user_exists_username(client, user):

    response = client.post(
        '/users',
        json={
            'nome_usuario': 'lucroadmintest',
            'email': 'test1@lucroadmin.com',
            'senha_hash': 'lucro_admin_test',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': {'message': 'Username already exists'}
    }


def test_create_user_exists_email(client, user):

    response = client.post(
        '/users',
        json={
            'nome_usuario': 'lucroadmintest1',
            'email': 'test@lucroadmin.com',
            'senha_hash': 'lucro_admin_test',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': {'message': 'Email already exists'}}


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'id_usuario': 1,
        'nome_usuario': 'lucroadmintestupdate',
        'email': 'test_update@lucroadmin.com',
    }


def test_update_user_notfound(client, user):
    response = client.put(
        '/users/2',
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 404
    assert response.json() == {'detail': {'message': 'User Not Found'}}


def test_update_user_exist_username(client, user):
    response = client.put(
        '/users/1',
        json={
            'nome_usuario': 'lucroadmintest',
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': {'message': 'Username already exists'}
    }


def test_update_user_exist_email(client, user):
    response = client.put(
        '/users/1',
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': 'test@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': {'message': 'Email already exists'}}


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == 200
    assert response.json() == {'message': 'User delete'}


def test_delete_user_exist(client, user):
    response = client.delete('/users/2')

    assert response.status_code == 404
    assert response.json() == {'detail': {'message': 'User not found'}}

from http import HTTPStatus

from lucro_admin.api.schemas import UserPublic


def test_create_user(client):

    response = client.post(
        '/users',
        json={
            'nome_usuario': 'testlucroadmin',
            'email': 'test1@lucroadmin.com',
            'senha_hash': 'lucro_admin_test',
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'id_usuario': 1,
        'nome_usuario': 'testlucroadmin',
        'email': 'test1@lucroadmin.com',
    }


def test_create_user_exists_username(client, user):

    response = client.post(
        '/users',
        json={
            'nome_usuario': user.nome_usuario,
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
            'email': user.email,
            'senha_hash': 'lucro_admin_test',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': {'message': 'Email already exists'}}


def test_read_user(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id_usuario}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'id_usuario': user.id_usuario,
        'nome_usuario': 'lucroadmintestupdate',
        'email': 'test_update@lucroadmin.com',
    }


def test_update_user_notfound(client, user, token):
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_exist_username(client, user, other_user, token):
    response = client.put(
        f'/users/{user.id_usuario}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'nome_usuario': other_user.nome_usuario,
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': {'message': 'Username already exists'}
    }


def test_update_user_exist_email(client, user, other_user, token):
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': user.email,
            'senha_hash': 'lucro_admin_test_update',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': {'message': 'Email already exists'}}


def test_update_user_with_wrong_user(client, token, other_user):
    response= client.put(
        f'/users/{other_user.id_usuario}',
        headers= {'Authorization': f'Bearer {token}'},
        json={
            'nome_usuario': 'lucroadmintestupdate',
            'email': 'test_update@lucroadmin.com',
            'senha_hash': 'lucro_admin_test_update'
        }
    )

    assert response.json() == {'detail': 'Not enough permissions'}
    assert response.status_code == 403
    

def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id_usuario}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'User delete'}


def test_delete_user_enougth_permission(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id_usuario}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    assert response.json() == {'detail': 'Not enough permissions'}



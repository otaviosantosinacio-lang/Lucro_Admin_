from fastapi import FastAPI, APIRouter
from lucro_admin.infra import repositorio_api

router = APIRouter()


@router.get('/')
def home():
    boas_vindas = {
        'Olá usuário, seja bem-vindo ao Lucro Admin, um sistema financeiro para gerenciamento das suas vendas'
    }
    return boas_vindas


@router.get('/pedidos')
def pedidos_por_data(data_inicial, data_final):
    pedidos = repositorio_api.consulta_por_data(
        data_inicial=data_inicial, data_final=data_final
    )
    return pedidos

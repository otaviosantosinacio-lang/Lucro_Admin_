import logging
from logging.config import dictConfig
from pathlib import Path

from fastapi import FastAPI

from lucro_admin.adapters.bling.bling_credenciais import Refresh
from lucro_admin.adapters.bling.bling_pedidos import GetBling
from lucro_admin.adapters.mercado_livre.mercado_livre_credenciais import (
    RefreshML,
)
from lucro_admin.adapters.mercado_livre.mercado_livre_pedidos import (
    GetMercadoLivre,
)
from lucro_admin.api import pedidos
from lucro_admin.infra.logging.config import Logging_Config
from lucro_admin.infra.logging.contexto import (
    correlation_id,
    generate_correlation_id,
)
from lucro_admin.infra.repositorio_bling import (
    CredenciaisDB_bling,
    DadosGerais,
)
from lucro_admin.infra.repositorio_pedidos import InsertPedidos
from lucro_admin.infra.repositorio_produtos_pedido import InsertPedidosProdutos
from lucro_admin.infra.repositorioMercadoLivre.repositorio_mercadolivre import (
    CredenciaisMercadoLivre,
)
from lucro_admin.services.bling.credenciais.tokens.providers.bling_provider import (
    BlingProvider,
)
from lucro_admin.services.bling.pedidos.provider.provider_pedidos import (
    PedidosProviderBling,
)
from lucro_admin.services.mercado_livre.pedidos.service_mercadolivre_pedidos import (
    ExtraiCustoMercadoLivre,
)
from lucro_admin.services.mercado_livre.tokens.ml_provider import MLProvider
from lucro_admin.services.token_service import TokenService


def main():
    """
    Iniciando a aplicação, estamos configurando os objetos que serão necessário para seguir com a aplicação
    Esta def não solicita nenhum atributo pois é ela quem fará as requisições a outros pacotes do app
    """
    Path('logs').mkdir(exist_ok=True)
    cid = generate_correlation_id()
    correlation_id.set(cid)
    dictConfig(Logging_Config)

    logger = logging.getLogger('lucroadmin.main')
    logger.info('Iniciando o fluxo principal da aplicação')

    # Repositórios
    repo_credent_bling = CredenciaisDB_bling()
    repo_pedidos_bling = DadosGerais()
    repo_credent_ML = CredenciaisMercadoLivre()
    repo_pedidos = InsertPedidos()
    repo_pedidos_produtos = InsertPedidosProdutos()

    # Adapters
    adapter_refresh_bling = Refresh()
    adapt_pedidos_bling = GetBling()
    adapt_refresh_ML = RefreshML()
    adapt_pedidos_ML = GetMercadoLivre()

    # Providers
    bling_provider_credenciais = BlingProvider(
        repo_credent_bling, adapter_refresh_bling
    )
    mercadolivre_provider_credenciais = MLProvider(
        repo_credent_ML, adapt_refresh_ML
    )

    # Token Services
    token_service_bling = TokenService(bling_provider_credenciais)
    token_service_ML = TokenService(mercadolivre_provider_credenciais)
    """Aqui e¨ chamando o metodo valida_access que esta dentro da classe TokenService,
    você pode observar que eu estou usando o objeto token_service_bling para chamar o metodo"""
    # Bling
    access_token_bling = token_service_bling.valida_access()

    # Mercado Livre
    access_token_ML = token_service_ML.valida_access()

    mercadolivre_pedidos = ExtraiCustoMercadoLivre(
        access_token=access_token_ML, adapt_pedido=adapt_pedidos_ML
    )
    bling_provider_pedidos = PedidosProviderBling(
        adapt_pedidos_bling, repo_pedidos_bling, access_token_bling
    )

    pedidos = bling_provider_pedidos.processa_ids()

    custos_ml = mercadolivre_pedidos.extraindo_custos(pedidos=pedidos)

    insert_pedidos = repo_pedidos.insert_pedidos(custos_ml.pedidos)

    insert_pedidos_produtos = repo_pedidos_produtos.insert_pedidos_produtos(
        custos_ml.produtos
    )

    logger.info('Fluxo finalizado')


if __name__ == '__main__':
    main()


app = FastAPI()

app.include_router(pedidos.router)

import asyncio
import logging
from logging.config import dictConfig
from pathlib import Path

from lucro_admin.infra.logging.config import Logging_Config
from lucro_admin.infra.logging.contexto import (
    correlation_id,
    generate_correlation_id,
)
from lucro_admin.services.orchestrator import PipelineOrchestrator


async def main():
    """
    Iniciando a aplicação, estamos configurando os objetos
    que serão necessário para seguir com a aplicação.
    Esta def não solicita nenhum atributo pois é ela quem fará as requisições
    a outros pacotes do app
    """

    Path('logs').mkdir(exist_ok=True)
    cid = generate_correlation_id()
    correlation_id.set(cid)
    dictConfig(Logging_Config)

    logger = logging.getLogger('lucroadmin.main')
    logger.info('Iniciando o fluxo principal da aplicação')

    await PipelineOrchestrator().execute()

    logger.info('Fluxo finalizado')


if __name__ == '__main__':
    asyncio.run(main())

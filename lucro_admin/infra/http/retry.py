import time
import logging
from functools import wraps
from typing import Callable, Iterable, Any

logger = logging.getLogger('lucroadmin.infra.retry')


class RetryPolicy:
    """
    Tratamento de erros para requisições https

    """

    def __init__(
        self,
        # Máximo de 6 tentativas para que o python execute 5 vezes
        max_tentativas: int = 6,
        delay_inicial: float = 0.8,
        fator_exponencial: float = 2.0,
        status_retry: Iterable[int] = (429, 500, 502, 503, 504),
    ):
        self.max_tentativas = max_tentativas
        self.delay_inicial = delay_inicial
        self.fator_exponencial = fator_exponencial
        self.status_retry = set(status_retry)

    def executa(self, func: Callable[[], Any]):
        """
        Docstring para executa

        :param self: Objeto
        :param func: Função chamada
        :type func: Callable[[], Any]
        """
        logger.info('Retry Policy | Iniciando fluxo retry.')
        delay = self.delay_inicial
        #              aqui o porque max_tentativa é 6
        for t in range(1, self.max_tentativas + 1):
            response = func()

            logger.info(
                'Retry Policy | Request status %s', response.status_code
            )
            if response.status_code not in self.status_retry:
                time.sleep(self.delay_inicial)
                return response

            if t == self.max_tentativas:
                logger.critical(
                    'Retry Policy | Tentativas esgotadas %s | status %s',
                    self.max_tentativas,
                    response.status_code,
                )
                return response

            logger.warning(
                'Retry Policy | Tentativa %s/%s | Status = %s | Aguardando = %.1f',
                t,
                self.max_tentativas,
                response.status_code,
                delay,
            )
            time.sleep(delay)
            delay *= self.fator_exponencial

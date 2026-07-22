import logging
import time
from typing import Any, Callable, Iterable

logger = logging.getLogger('lucroadmin.infra.retry')


class RetryPolicy:
    """
    Error handling for https requests

    """

    def __init__(
        self,
        # Maximum attempts 5
        max_attempts: int = 6,
        initial_delay: float = 0.8,
        exponential_factor: float = 2.0,
        success_delay: float = 0.0,
        status_retry: Iterable[int] = (429, 500, 502, 503, 504),
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.exponencial_factor = exponential_factor
        self.status_retry = set(status_retry)
        self.success_delay = success_delay

    def execute(self, func: Callable[[], Any]):
        """
        execute

        :param self: Object
        :param func: Function Called
        :type func: Callable[[], Any]
        """
        logger.info('Retry Policy | Starting retry flow.')
        delay = self.initial_delay

        for t in range(1, self.max_attempts + 1):
            response = func()

            logger.info(
                'Retry Policy | Request status %s', response.status_code
            )
            if response.status_code not in self.status_retry:
                time.sleep(self.success_delay)
                return response

            if t == self.max_attempts:
                logger.critical(
                    'Retry Policy | Attempts exhausted %s | status %s',
                    self.max_attempts,
                    response.status_code,
                )
                return response

            logger.warning(
                'Retry Policy | Attempt %s/%s | Status = %s | Waiting'
                '= %.1f',
                t,
                self.max_attempts,
                response.status_code,
                delay,
            )
            time.sleep(delay)
            delay *= self.exponencial_factor

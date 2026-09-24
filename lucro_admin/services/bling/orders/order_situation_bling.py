import logging

from lucro_admin.core.entities_pedidos import BlingSituation, BlingSituationDB
from lucro_admin.infra.database import SessionLocal
from lucro_admin.infra.repository.repository_bling_order_situation import (
    BlingOrderSituation,
)
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.ordersituationbling')


class OrderSituationBling:

    def __init__(self, adapt_order, access_token):
        self.adapt_order = adapt_order
        self.access_token = access_token
        self.service_base = BaseRequestHTTP(
            self.adapt_order,
            self.access_token
        )
        self.base_url = 'https://api.bling.com.br/Api/v3'

    async def situation_data_base(self, situation: str) -> BlingSituationDB:
        """
        situacao_data_base -> extracts situations from the database

        :param self: Object
        :param situation: The name of the situation we want to acquire
        :type situation: str
        :return: Situation containing the name and id
        :rtype: BlingSituation
        """
        async with SessionLocal() as session:
            repository = BlingOrderSituation(session=session)

            result = await repository.extract_situation(
                situation_name=situation
            )

            situation_data: BlingSituationDB = BlingSituationDB(
                situation_id=result[0][0],
                situation_bling_id=result[0][1],
                situation_name=result[0][2],
                situation_color=result[0][3]
            )

            return situation_data

    def build_url_situation(self, id: int) -> str:

        url: str = f'{self.base_url}/situacoes/modulos/{id}'
        return url

    async def get_bling_situations_modules(self):

        logger.info(
            'Bling Orders Situation | Starting request situation endpoint'
        )

        url: str = f'{self.base_url}/situacoes/modulos'

        response = self.service_base.organiza_get_request(url)

        data = response.data.get('data', [])

        if response.status == 'ok':
            situations_modules = [id['id'] for id in data]

        elif response.status == 'rated_limit':
            logger.warning(
            'Bling Orders Situation | The request return %s',
            response.status
            )
            return None

        else:
            logger.critical(
                    'Bling Orders Situation | error request %s',
                    response.error,
                )
            return None

        if len(situations_modules) > 0:
            situations = self.get_bling_situation(ids=situations_modules)
            logger.info(
            'Bling Orders Situation | '
            '%s situations modules were found and were recorded ->'
            ' Complete Situations %s',
            len(situations), situations
        )
            async with SessionLocal() as session:
                repository = BlingOrderSituation(session=session)

                await repository.insert_situations(situations=situations)
                await session.commit()
                await session.close()

    def get_bling_situation(self, ids: list[int]):

        situations = []
        for id in ids:
            url: str = self.build_url_situation(id=id)
            response = self.service_base.organiza_get_request(url)
            if response.status == 'ok':
                data = response.data.get('data', [])
                for situation in data:
                    situation_details: BlingSituation = BlingSituation(
                        situation_bling_id=situation['id'],
                        situation_name=situation['nome'],
                        situation_color=situation['cor']
                    )

                    situations.append(situation_details)

            elif response.status == 'rated_limit':
                logger.warning(
                    'Bling Orders Situation | '
                    'The request situation id %s, return %s status code',
                    id, response.status
                )
                continue

            else:
                logger.critical(
                    'Bling Orders Situation | '
                    'Response request returning critical status ->'
                    f'{response.status}',
                )
                return None

            return situations

    async def change_bling_order_situation(
        self,
        order_bling_id: int,
        new_order_situation: str
        ):

        situation_id = await self.situation_data_base(
            situation=new_order_situation
        )

        url: str = (f'{self.base_url}/pedidos/vendas/'
            f'{order_bling_id}/situacoes/{situation_id.situation_bling_id}'
        )

        logger.info(
            'Bling Orders Situation | '
            'Starting to change the order situation, '
            'sending request to endpoint %s',
            url
            )
        response = self.service_base.organiza_patch_request(
            url=url
        )

        if response.status == 'ok':
            logger.info(
                'Bling Orders Situation | '
                'Order situation successfully changed -> '
                'Order ID %s -> Changed to %s',
                order_bling_id, new_order_situation
            )
            return response.status

        elif response.status == 'rated_limit':
            logger.warning(
                'Bling Orders Situation | '
                'The limit of requests has been '
                'reached when changing the situation, %s ->'
                'Order ID %s -> Changed to %s',
                response.status, order_bling_id, new_order_situation
            )
            return response.status

        else:
            logger.critical(
                'Bling Orders Situation | '
                'Request returned a critical error '
                'when trying to change the situation, %s ->'
                'Order ID %s -> Changed to %s',
                response.error['status'], order_bling_id, new_order_situation
            )
            return response.status

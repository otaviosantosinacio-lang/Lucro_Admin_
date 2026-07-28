import logging

from lucro_admin.core.entities_pedidos import BlingSituation
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.ordersituationbling')


class OrderSituationBling:

    def __init__(self, repo_order, adapt_order, access_token):
        self.repo_order = repo_order
        self.adapt_order = adapt_order
        self.access_token = access_token
        self.service_base = BaseRequestHTTP(self.adapt_order, self.access_token)
        self.base_url = 'https://api.bling.com.br/Api/v3'

    def situation_data_base(self, situation: str) -> BlingSituation:
        """
        situacao_data_base -> extracts situations from the database

        :param self: Object
        :param situation: The name of the situation we want to acquire
        :type situation: str
        :return: Situation containing the name and id
        :rtype: BlingSituation
        """
        situations = self.repo_order.situacoes()
        logger.info('Bling Orders Situation | Situations %s', situations)
        for sit in situations:
            if sit[1] == situation:
                cod_sit = sit[0]
                name_sit = sit[1]
                break
        logger.info(
            f'Bling Orders Situation | Return Situation {cod_sit} -> '
            f'{name_sit}'
        )
        return BlingSituation(cod_sit=cod_sit, name_sit=name_sit)

    def build_url_situation(self, id: int) -> str:

        url: str = f'{self.base_url}/situacoes/modulos/{id}'
        return url

    def get_bling_situations_modules(self):

        breakpoint()
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
            return f'Situations retuned {situations}'

    def get_bling_situation(self, ids: list[int]):

        situations = []
        for id in ids:
            url: str = self.build_url_situation(id=id)
            response = self.service_base.organiza_get_request(url)
            if response.status == 'ok':
                data = response.data.get('data', [])
                for situation in data:
                    situation_details: BlingSituation = BlingSituation(
                        cod_sit=situation['id'],
                        name_sit=situation['nome'],
                        color_sit=situation['cor']
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

    def change_bling_order_situation(
        self,
        order_bling_id: int,
        new_order_situation: str
        ):

        situation_id = self.situation_data_base(
            situation=new_order_situation
        ).cod_sit

        url: str = (f'{self.base_url}/pedidos/vendas/'
            f'{order_bling_id}/situacoes/{situation_id}'
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

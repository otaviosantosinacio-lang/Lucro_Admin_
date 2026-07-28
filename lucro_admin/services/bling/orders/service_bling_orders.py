import logging
from datetime import date, datetime

from lucro_admin.core.entities_pedidos import (
    ErrorHTTP,
    GetDetailsResult,
    GetPagesResult,
    OrderData,
)
from lucro_admin.core.marketplace import nome_marketplace
from lucro_admin.services.bling.orders.order_situation_bling import (
    OrderSituationBling,
)
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)

logger = logging.getLogger('lucroadmin.services.blingpedidos')


class Attended:
    """
    Attended -> Getting orders in the served status

    """

    def __init__(self, access_token, adapt_pedidos, repo_pedidos):
        self.access_token = access_token
        self.repo_pedidos = repo_pedidos
        self.adapt_pedidos = adapt_pedidos
        self.service_base = BaseRequestHTTP(
            self.adapt_pedidos, self.access_token
        )
        self.base_url = 'https://api.bling.com.br/Api/v3'
        self.order_situation = OrderSituationBling(
            repo_order=self.repo_pedidos,
            adapt_order=self.adapt_pedidos,
            access_token=self.access_token
        )

    def url_endpoint_pag(
        self, pagina: int, sit: int, data_inicial: date, data_final: date
    ) -> str:
        """
        url_endpoint_pag -> URL Assembly

        :param self: Object
        :param pagina: Page for endpoint
        :type pagina: int
        :param sit: Bling situation number
        :type sit: int
        :param data_inicial: Orders that were placed from this date
        :type data_inicial: date
        :param data_final: Orders placed until this date
        :type data_final: date
        :return: Properly assembled endpoint
        :rtype: str
        """
        url: str = (
            f'{self.base_url}/pedidos/vendas?pagina={pagina}&limite=20&'
            f'idsSituacoes%5B%5D={sit}&dataInicial={data_inicial}'
            f'&dataFinal={data_final}'
        )
        return url

    def get_id_by_page(self) -> GetPagesResult:
        """
        get_id_por_pag -> Orquestrando as requisições para obter ids das vendas

        :param self: Objeto
        :return: Ids das vendas
        :rtype: ResultadoGetPaginas
        """
        max_pedidos_pag: int = 100
        sit = self.order_situation.situation_data_base('Atendido')
        mais_pagina: bool = True
        pagina = 1
        data_inicial = self.data_inicial_repo()
        if data_inicial is None:
            data_inicial = datetime.now().date()

        data_final = datetime.now().date
        vendas_id = []
        error429 = []

        while mais_pagina:
            url = self.url_endpoint_pag(
                pagina, sit.cod_sit, data_inicial, data_final
            )
            logger.info('Bling Pedidos get_id_por_pag | Url montada %s', url)
            response = self.service_base.organiza_get_request(url)

            if response.status == 'ok':
                data = response.data.get('data', [])
                id = [item['id'] for item in data]
                vendas_id.extend(id)

                if len(data) < max_pedidos_pag:
                    mais_pagina = False
                else:
                    pagina += 1

            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Pedidos get_id_por_pag | Erro na requisição %s',
                    response.error,
                )
                erro = ErrorHTTP(
                    status=response.error['status'],
                    error=response.error['body'],
                    method='get_id_por_pag',
                    class_name='Atendidos',
                    module='service_bling_pedidos.py',
                    endpoint=url,
                    data=datetime.now(),
                )
                error429.append(erro)
                pagina += 1

            else:
                logger.critical(
                    'Bling Pedidos get_id_por_pag | Erro na requisição %s',
                    response.error,
                )
                raise Exception(
                    f'Erro na requisição: {response.status} - {response.error}'
                )

        return GetPagesResult(
            sales_id=vendas_id, endpointerro=error429, situation=sit.name_sit
        )

    def data_inicial_repo(self) -> datetime:
        """
        data_inicial_repo -> Extraindo data do ultimo pedido registrado
        no banco de dados

        :param self: Objeto
        :return: Data do ultimo pedido
        :rtype: datetime
        """
        logger.info('Bling data inicio | Chamando repositório')
        data_inicio = self.repo_pedidos.data_ultimo_pedido()
        logger.info(
            'Bling data inicio | Retorno do repositório %s', data_inicio
        )
        return data_inicio


class ProcessaId:
    """
    ProcessaId ->
    Processas os ids passados para obtenção de maiores detalhes da venda

    """

    def __init__(self, access_token, adapt_pedidos, repo_pedidos):
        self.access_token = access_token
        self.adapt_pedidos = adapt_pedidos
        self.repo_pedidos = repo_pedidos
        self.service_base = BaseRequestHTTP(
            self.adapt_pedidos, self.access_token
        )
        self.base_url = 'https://api.bling.com.br/Api/v3'

    def url_id(self, id) -> str:
        """
        url_id -> Montage da URL endpoint

        :param self: Objeto
        :param id: Id único por venda gerado pelo Bling
        :return: URL endpoint com id
        :rtype: str
        """
        return f'{self.base_url}/pedidos/vendas/{id}'

    def get_id_detalhes(
        self, ids_list: list[int], situacao
    ) -> GetDetailsResult:
        """
        get_id_detalhes

        :param self: Objeto
        :param ids_list: Lista de ids da situação selecionada
        :type ids_list: list[int]
        """
        error429 = []
        pedidos = []
        for id in ids_list:
            url = self.url_id(id)
            response = self.service_base.organiza_get_request(url)

            if response.status == 'ok':
                data = response.data.get('data', [])
                id_loja = data['loja']['id']
                nome_mkt = nome_marketplace(id_loja)
                transporte = data.get('transporte') or {}
                volumes = transporte.get('volumes') or []

                pedido = OrderData(
                    id_bling=id,
                    num_bling=data['numero'],
                    id_mkt=data['numeroLoja'],
                    data=data['data'],
                    name_store=nome_mkt,
                    nf_id=data['notaFiscal']['id'],
                    value_sale=data['total'],
                    items=data['itens'],
                    uf_dest=data['transporte']['etiqueta']['uf'],
                    servico_trans=volumes[0].get('servico')
                    if volumes
                    else 'SEM_SERVIÇO',
                )
                logger.info(
                    'Bling Service get_id_detalhes | Dados do pedido %s',
                    pedido,
                )
                pedidos.append(pedido)

                logger.info(
                    'Bling Service get_id_detalhes | Endpoint %s / Retorno %s',
                    url,
                    response.data,
                )
            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Pedidos get_id_detalhes | Erro na requisição %s',
                    response.error,
                )
                erro = ErrorHTTP(
                    status=response.error['status'],
                    error=response.error['body'],
                    method='get_id_detalhes',
                    class_name='ProcessaId',
                    module='service_bling_pedidos.py',
                    endpoint=url,
                    data=datetime.now(),
                )
                error429.append(erro)
        return GetDetailsResult(
            orders=pedidos, endpointerror=error429, situation=situacao
        )

from datetime import date, datetime
import logging

from lucro_admin.services.bling.pedidos.service_bling_base_pedidos import (
    BaseHTTPBling,
)
from lucro_admin.core.entities_pedidos import (
    ResultadoGetDetalhes,
    SituacaoBling,
    ResultadoGetPaginas,
    DadosPedidos,
    ErrorHTTP,
)
from lucro_admin.core.marketplace import nome_marketplace

base_url = 'https://api.bling.com.br/Api/v3'
logger = logging.getLogger('lucroadmin.services.blingpedidos')


class Atendidos:
    """
    Atendidos -> Obtenção de pedidos na situação de atendido

    """

    def __init__(self, access_token, adapt_pedidos, repo_pedidos):
        self.access_token = access_token
        self.repo_pedidos = repo_pedidos
        self.adapt_pedidos = adapt_pedidos
        self.service_base = BaseHTTPBling(
            self.adapt_pedidos, self.access_token
        )

    def url_endpoint_pag(
        self, pagina: int, sit: int, data_inicial: date, data_final: date
    ) -> str:
        """
        url_endpoint_pag -> Montagem da URL

        :param self: Objeto
        :param pagina: Página para end point
        :type pagina: int
        :param sit: Número da situação Bling
        :type sit: int
        :param data_inicial: Pedido que tenham saído a partir desta data
        :type data_inicial: date
        :param data_final: Pedidos que saíram até essa data
        :type data_final: date
        :return: Endpoint montada corretamente
        :rtype: str
        """
        return f'{base_url}/pedidos/vendas?pagina={pagina}&limite=20&idsSituacoes%5B%5D={sit}&dataInicial={data_inicial}&dataFinal={data_final}'

    def get_id_por_pag(self) -> ResultadoGetPaginas:
        """
        get_id_por_pag -> Orquestrando as requisições para obter ids das vendas

        :param self: Objeto
        :return: Ids das vendas
        :rtype: ResultadoGetPaginas
        """
        sit = self.situacao('Atendido')
        mais_pagina: bool = True
        pagina = 1
        data_inicial = self.data_inicial_repo()
        if data_inicial == None:
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
                id = [item['id'] for item in response.data]
                vendas_id.extend(id)

                if len(response.data) < 100:
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
                    metodo='get_id_por_pag',
                    classe='Atendidos',
                    local='service_bling_pedidos.py',
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

        return ResultadoGetPaginas(
            vendas_id=vendas_id, endpointerro=error429, situacao=sit.nome_sit
        )

    def situacao(self, situacao: str) -> SituacaoBling:
        """
        situacao -> extrai situações do banco de dados

        :param self: Objeto
        :param situacao: O nome da situação que queremos adquirir
        :type situacao: str
        :return: Situação contendo o nome e id
        :rtype: SituacaoBling
        """
        situacoes = self.repo_pedidos.situacoes()
        logger.info('Bling Pedidos situacao | Situações %s', situacoes)
        for sit in situacoes:
            if sit[1] == situacao:
                cod_sit = sit[0]
                nome_sit = sit[1]
                break
        logger.info(
            f'Bling Pedidos situacao | Situação retornada {cod_sit} -> {nome_sit}'
        )
        return SituacaoBling(cod_sit=cod_sit, nome_sit=nome_sit)

    def data_inicial_repo(self) -> datetime:
        """
        data_inicial_repo -> Extraindo data do ultimo pedido registrado no banco de dados

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
    ProcessaId -> Processas os ids passados para obtenção de maiores detalhes da venda

    """

    def __init__(self, access_token, adapt_pedidos, repo_pedidos):
        self.access_token = access_token
        self.adapt_pedidos = adapt_pedidos
        self.repo_pedidos = repo_pedidos
        self.service_base = BaseHTTPBling(
            self.adapt_pedidos, self.access_token
        )

    def url_id(self, id) -> str:
        """
        url_id -> Montage da URL endpoint

        :param self: Objeto
        :param id: Id único por venda gerado pelo Bling
        :return: URL endpoint com id
        :rtype: str
        """
        return f'{base_url}/pedidos/vendas/{id}'

    def get_id_detalhes(
        self, ids_list: list[int], situacao
    ) -> ResultadoGetDetalhes:
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
                id_loja = response.data['loja']['id']
                nome_mkt = nome_marketplace(id_loja)
                transporte = response.data.get('transporte') or {}
                volumes = transporte.get('volumes') or []

                pedido = DadosPedidos(
                    id_bling=id,
                    num_bling=response.data['numero'],
                    id_mkt=response.data['numeroLoja'],
                    data=response.data['data'],
                    nome_loja=nome_mkt,
                    nf_id=response.data['notaFiscal']['id'],
                    valor_pedido=response.data['total'],
                    itens=response.data['itens'],
                    uf_dest=response.data['transporte']['etiqueta']['uf'],
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
                    metodo='get_id_detalhes',
                    classe='ProcessaId',
                    local='service_bling_pedidos.py',
                    endpoint=url,
                    data=datetime.now(),
                )
                error429.append(erro)
        return ResultadoGetDetalhes(
            pedidos=pedidos, endpointerror=error429, situacao=situacao
        )

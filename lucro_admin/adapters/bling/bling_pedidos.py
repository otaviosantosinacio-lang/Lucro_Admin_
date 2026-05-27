from requests import get
import requests
import logging
from lucro_admin.infra.http.retry import RetryPolicy

retry_policy = RetryPolicy()
logger = logging.getLogger('lucroadmin.adapters.bling')


class Request:
    """

    Base para os requests get do bling

    """

    def request_endpoint(
        self, url: str, headers: dict[str, str]
    ) -> requests.Response:
        """
        request_endpoint

        Request básico individualizado para CRUD Get do Bling

        :param self:
        :param url: EndPoint Bling
        :type url: str
        :param headers: Headers para validação obtenção das credenciais
        :type headers: dict[str, str]
        :return: Retorno formatado da endpoint
        :rtype: Response
        """
        logger.info(
            'Bling request_pedidos | Enviando requisição para o end point %s',
            url,
        )
        return get(url=url, headers=headers, timeout=20)


class GetBling:
    def get_endpoints_bling(self, access_token: str, url: str):
        """
        :param self: Objeto
        :param access_token: Credencial de acesso válida
        :type access_token: string
        :param url: Endpoint Bling V3
        :type url: String

        Headers e request para endpoint bling para retornar ao service o json.
        """
        logger.info('Bling get_endpoints_bling | Iniciando o Request')
        headers: dict[str, str] = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'enable_jwt': '1',
        }

        request = Request()
        response = retry_policy.executa(
            lambda: request.request_endpoint(url, headers)
        )
        logger.info(
            'Bling get_endpoints_bling | Retorno da requisição é %s',
            response.status_code,
        )

        return response


class GetUrlXML:
    """
    Metodo GET apenas para baixarmos o XML

    """

    def request_xml_endpoint(self, url):
        """
        request_xml_endpoint

        Metodo GET

        :param self:
        :param url: EndPoint
        """
        return get(url=url)

    def request_xml(self, url: str):
        """
        request_xml

        Organizando Request XML

        :param self:
        :param url: EndPoint XML
        :type url: str
        """
        response = retry_policy.executa(lambda: self.request_xml_endpoint(url))
        logger.info('XML EndPoint | Retorno HTTP %s', response.status_code)

        return response.text

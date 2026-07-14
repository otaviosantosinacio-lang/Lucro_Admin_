import logging

import requests

from lucro_admin.infra.http.retry import RetryPolicy

retry_policy = RetryPolicy()
logger = logging.getLogger('lucroadmin.adapters.bling')


class Request:
    """

    Base for Bling GET requests

    """

    def __init__(self):
        self.timeout: int = 30

    def request_endpoint(
        self, url: str, headers: dict[str, str]
    ) -> requests.Response:
        """
        request_endpoint

        Individualized basic request for Bling CRUD Get

        :param self:
        :param url: Bling Endpoint
        :type url: str
        :param headers: Headers for credential validation
        :type headers: dict[str, str]
        :return: Formatted return from the endpoint
        :rtype: Response

        """
        logger.info(
            'Bling request_pedidos | Sending a request to the endpoint %s',
            url,
        )
        return requests.get(url=url, headers=headers, timeout=self.timeout)


class GetBling:
    def __init__(self):
        self.request = Request()

    def get_endpoint(self, access_token: str, url: str):
        """
        :param self: Object
        :param access_token: Valid access credential
        :type access_token: string
        :param url: Bling V3 Endpoint
        :type url: String

        Headers and request to Bling endpoint to return the JSON to the service.
        """
        logger.info('Bling get_endpoints_bling | Starting the Request')
        headers: dict[str, str] = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'enable-jwt': '1',
        }

        response = retry_policy.executa(
            lambda: self.request.request_endpoint(url, headers)
        )
        logger.warning(
            'Bling get_endpoints_bling | The request return is %s',
            response.status_code,
        )
        return response


class GetUrlXML:
    """
    GET method only to download the XML

    """

    def __init__(self):
        self.timeout: int = 30

    def request_xml_endpoint(self, url):
        """
        request_xml_endpoint

        Method GET

        :param self:
        :param url: EndPoint
        """
        return requests.get(url=url, timeout=self.timeout)

    def request_xml(self, url: str):
        """
        request_xml

        Organizing XML Request

        :param self:
        :param url: EndPoint XML
        :type url: str
        """
        response = retry_policy.executa(lambda: self.request_xml_endpoint(url))
        logger.info('XML EndPoint | Return HTTP %s', response.status_code)

        return response.text

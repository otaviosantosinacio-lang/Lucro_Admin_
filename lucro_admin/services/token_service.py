from datetime import datetime
import logging

logger = logging.getLogger('lucroadmin.services.bling')


class TokenService:
    """Definindo os atribustos do construtor da classe TokenServiceBling,
    onde repositorio é um objeto que traz a classe CredenciaisDB_bling e adapter_refresh é um objeto que traz a classe Refresh.
    O expire é um atribusto que esta pegando o valor do metodo get_expire_token que esta dentro da classe CredenciaisDB_bling"""

    def __init__(self, provider):
        self.provider = provider

    def valida_access(self) -> str:
        """
        valida_access -> Definindo a validade do access token, se for inválido ele já inicia fluxo para obter um válido

        :param self: Objeto
        :return: Access Token válido
        :rtype: str
        """
        expire = self.provider.get_expire()
        expirado: bool = datetime.now() > expire
        if expirado:
            logger.info(
                'Bling Token Service | Token expirado, iniciando fluxo de refresh'
            )
            access_token: str = self.provider.use_refresh_token()
            return access_token
        else:
            logger.info('Bling Token Service | Token válido')
            access_token: str = self.provider.get_access_token()
            return access_token

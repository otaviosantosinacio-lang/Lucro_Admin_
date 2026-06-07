import logging
import webbrowser

from lucro_admin.adapters.bling.bling_credenciais import Code
from lucro_admin.core.entities_credenciais import Credencial
from lucro_admin.utils.code_state import code_string
from lucro_admin.utils.cript_state import cript_state

logger = logging.getLogger('lucroadmin.services.bling')


class oAuthCodeBling:
    """
    oAuthCodeBling -> Orquestração do fluxo para troca do Code por Tokens

    """

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def fluxo_oAuthCode_bling(self) -> str:
        """
        fluxo_oAuthCode_bling

        :param self: Objeto
        :return: Access Token válido
        :rtype: str
        """
        logger.info('Bling oAuth Code | Iniciando fluxo com o code')

        client_id: str = self.repositorio.get_client_id()
        client_secret: str = self.repositorio.get_client_secret()

        adapt_code = Code()
        if not client_id or not client_secret:
            raise Exception('Credenciais não encontradas')

        state: str = cript_state()
        url: str = adapt_code.gerando_url_request(client_id, state=state)

        webbrowser.open(url)

        codestate: dict[str, str] = code_string()

        code: str = codestate['code']
        state_request: str = codestate['state']

        if state != state_request:
            logger.critical(
                'Bling oAuth Code | State retornado na url é invalido - Parando requisições. '
            )
            raise Exception('O state retornado não é válido.')

        logger.info('Bling oAuth Code | Code salvo e state validado')

        tokens_dict = adapt_code.troca_code_por_tokens(
            client_id, client_secret, code
        )
        tokens: Credencial = Credencial.from_api_response(tokens_dict)
        atualiza = self.repositorio.salva_token(
            tokens.access_token, tokens.refresh_token, tokens.expire
        )

        if not atualiza:
            logger.critical(
                'Bling oAuth Code | Credenciais não atualizadas por falha no banco de dados'
            )
        else:
            logger.info(
                'Bling oAuth Code | Credenciais atualizadas com sucesso'
            )
        return tokens.access_token


class oAuthRefreshBling:
    """
    oAuthRefreshBling -> Orquestração do fluxo usando Refresh Token para obter o Access Token Válido

    """

    def __init__(self, repositorio, adapt_refresh):
        self.repositorio = repositorio
        self.adapt_refresh = adapt_refresh

    def fluxo_refresh_token(self) -> str:
        """
        fluxo_refresh_token

        :param self: Objeto
        :return: Access Token válido
        :rtype: str
        """
        logger.info(
            'Bling oAuth Refresh | Iniciando fluxo com o Refresh Token'
        )

        logger.info('Bling oAuth Refresh | Buscando credenciais')
        client_id: str = self.repositorio.get_client_id()
        client_secret: str = self.repositorio.get_client_secret()
        refresh_token: str = self.repositorio.get_refresh_token()

        if not client_id or not client_secret or not refresh_token:
            raise Exception('Credenciais não encontradas')
        else:
            logger.info(
                'Bling oAuth Refresh | Credenciais validadas iniciando request'
            )

            tokens_dict = self.adapt_refresh.usando_refresh_token(
                client_id, client_secret, refresh_token
            )

            tokens: Credencial = Credencial.from_api_response(tokens_dict)

        if tokens.response_status_code == 200:
            atualiza = self.repositorio.salva_token(
                tokens.access_token, tokens.refresh_token, tokens.expire
            )
            if atualiza:
                logger.info('Bling oAuth Refresh | Credenciais atualizadas')
            else:
                logger.critical(
                    'Bling oAuth Refresh | Credenciais não atualizadas por falha no banco de dados'
                )
            return tokens.access_token

        elif tokens.response_status_code != 200:
            logger.critical(
                'Bling oAuth Refresh | Erro na requisição: %s',
                tokens.response_status_code,
            )
            fluxo_code = oAuthCodeBling(self.repositorio)
            logger.warning(
                'Bling oAuth Refresh | Foi necessário forçar o inicio do fluxo code'
            )
            return fluxo_code.fluxo_oAuthCode_bling()

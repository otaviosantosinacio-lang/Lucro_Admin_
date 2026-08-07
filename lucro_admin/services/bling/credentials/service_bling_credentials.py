import logging
import webbrowser
from http import HTTPStatus

from lucro_admin.adapters.bling.bling_credentials import Code
from lucro_admin.core.entities_credential import Credential
from lucro_admin.settings import BlingSettings
from lucro_admin.utils.code_state import code_string
from lucro_admin.utils.cript_state import cript_state

logger = logging.getLogger('lucroadmin.services.bling')


class oAuthCodeBling:

    """
    oAuthCodeBling -> Flow orchestration for exchanging the Code for Tokens
    """

    def __init__(self):
        self.settings_credentials = BlingSettings()
        self.adapter_code = Code()
        self.repository = 

    def oAuthCode_flow_bling(self) -> str:
        """
        oAuthCode_flow_bling

        :param self: Object
        :return: Valid Access Token
        :rtype: str
        """
        logger.info('Bling oAuth Code | Starting the flow with the code')

        client_id: str = self.settings_credentials.CLIENT_ID()
        client_secret: str = self.settings_credentials.CLIENT_SECRET()

        if not client_id or not client_secret:
            raise Exception('Credentials not found')

        state: str = cript_state()
        url: str = self.adapter_code.generate_url_request(
            client_id,
            state=state
            )

        webbrowser.open(url)

        codestate: dict[str, str] = code_string()

        code: str = codestate['code']
        state_request: str = codestate['state']

        if state != state_request:
            logger.critical(
                'Bling oAuth Code | Returned state in the URL is invalid - '
                'Stopping requests. '
            )
            raise Exception('The returned state is not valid.')

        logger.info('Bling oAuth Code | Code saved and state validated')

        tokens_dict = self.adapter_code.exchange_code_for_tokens(
            client_id, client_secret, code
        )
        tokens: Credential = Credential.from_api_response(tokens_dict)
        update = self.repository.salva_token(
            tokens.access_token, tokens.refresh_token, tokens.expire
        )

        if not update:
            logger.critical(
                'Bling oAuth Code | Credentials not updated due to database'
                ' failure'
            )
        else:
            logger.info(
                'Bling oAuth Code | Credentials successfully updated'
            )
        return tokens.access_token


class oAuthRefreshBling:
    """
    oAuthRefreshBling -> Flow orchestration using Refresh Token to obtain a
    valid Access Token
    """

    def __init__(self, repository, adapt_refresh):
        self.repository = repository
        self.adapt_refresh = adapt_refresh

    def refresh_token_flow_bling(self) -> str:
        """
        refresh_token_flow

        :param self: Object
        :return: Valid Access Token
        :rtype: str
        """
        logger.info(
            'Bling oAuth Refresh | Starting flow with the Refresh Token'
        )

        logger.info('Bling oAuth Refresh | Searching for credentials')
        client_id: str = self.repository.get_client_id()
        client_secret: str = self.repository.get_client_secret()
        refresh_token: str = self.repository.get_refresh_token()

        if not client_id or not client_secret or not refresh_token:
            raise Exception('Credentials not found')
        else:
            logger.info(
            'Bling oAuth Refresh | Validated credentials initiating request'
            )

            tokens_dict = self.adapt_refresh.refresh_access_token(
                client_id, client_secret, refresh_token
            )

            tokens: Credential = Credential.from_api_response(tokens_dict)

        if tokens.response_status_code == HTTPStatus.OK:
            update = self.repository.salva_token(
                tokens.access_token, tokens.refresh_token, tokens.expire
            )
            if update:
                logger.info('Bling oAuth Refresh | Updated credentials')
            else:
                logger.critical(
                    'Credentials not updated due to database'
                    ' failure'
                )
            return tokens.access_token

        elif tokens.response_status_code != HTTPStatus.OK:
            logger.critical(
                'Bling oAuth Refresh | Request error: %s',
                tokens.response_status_code,
            )
            fluxo_code = oAuthCodeBling(self.repository)
            logger.warning(
                'Bling oAuth Refresh |'
                ' Foi necessário forçar o inicio do fluxo code'
            )
            return fluxo_code.oAuthCode_flow_bling()

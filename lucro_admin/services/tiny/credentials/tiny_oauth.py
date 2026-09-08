import datetime
import logging
import webbrowser
from http import HTTPStatus

from lucro_admin.adapters.tiny.tiny_credentials import Code
from lucro_admin.core.entities_credential import CredentialTiny
from lucro_admin.infra.repository_credentials import SaveCredentials
from lucro_admin.settings import TinySettings
from lucro_admin.utils.code_state import code_string_tiny

logger = logging.getLogger('lucroadmin.services.credentials.tiny')


class oAuthCodeTiny:
    def __init__(self):
        self.credentials = TinySettings()
        self.adapter = Code()
        self.repository = SaveCredentials('tiny.env')

    def oauth_flow_tiny(self):

        logger.info('Tiny oAuth Code | Starting the flow with the code')

        # Set credentials app
        client_id: str = self.credentials.CLIENT_ID
        client_secret: str = self.credentials.CLIENT_SECRET
        redirect_uri: str = self.credentials.REDIRECT_URI
        if not client_id or not client_secret:
            raise Exception('Credentials Not Found')

        url: str = (
            'https://accounts.tiny.com.br/realms/tiny/protocol/'
            f'openid-connect/auth?client_id={client_id}&'
            f'redirect_uri={redirect_uri}&'
            'scope=openid&response_type=code'
        )

        webbrowser.open(url)

        code_str = code_string_tiny()

        code = code_str['code']
        state = code_str['state']

        tokens_dict = self.adapter.exchange_code_for_tokens(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            code=code
        )

        if tokens_dict['state'] != state:
            logger.critical('Tiny oAuth Code | '
                            'Response request not equal state session'
            )
            raise Exception('Response state not equals')

        tokens: CredentialTiny = CredentialTiny.from_api_response(
            response_data=tokens_dict
        )

        update = self.repository.save_credentials_tiny(
            access_token=tokens.access_token,
            expire_access=tokens.expire_access,
            refresh_token=tokens.refresh_token,
            expire_refresh=tokens.expire_refresh
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


class oAuthRefreshTiny:
    def __init__(self, adapt_refresh):
        self.repository = SaveCredentials('tiny.env')
        self.adapter = adapt_refresh
        self.credentials = TinySettings()

    def refresh_token_flow_tiny(self) -> str:

        logger.info(
            'Tiny oAuth Refresh | Starting flow with the Refresh Token'
        )
        logger.info('Tiny oAuth Refresh | Searching for credentials')
        client_id: str = self.credentials.CLIENT_ID
        client_secret: str = self.credentials.CLIENT_SECRET
        refresh_token: str = self.credentials.REFRESH_TOKEN
        expire_refresh = datetime.datetime.fromisoformat(
            self.credentials.EXPIRE_REFRESH
        )

        if not client_id or not client_secret or not refresh_token:
            raise Exception('Credentials not found')

        if datetime.datetime.now(datetime.timezone.utc) >= expire_refresh:
            code_flow = oAuthCodeTiny()
            access_token = code_flow.oauth_flow_tiny()
            return access_token

        tokens_dict = self.adapter.refresh_access_token(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

        tokens: CredentialTiny = CredentialTiny.from_api_response(
            response_data=tokens_dict
        )

        if tokens.response_status_code == HTTPStatus.OK:
            update = self.repository.save_credentials_tiny(
                access_token=tokens.access_token,
                expire_access=tokens.expire_access,
                refresh_token=tokens.refresh_token,
                expire_refresh=tokens.expire_refresh
            )
            if update:
                logger.info('Tiny oAuth Refresh | Updated credentials')
            else:
                logger.critical(
                    'Credentials not updated due to database'
                    ' failure'
                )
            return tokens.access_token

        elif tokens.response_status_code != HTTPStatus.OK:
            logger.critical(
                'Tiny oAuth Refresh | Request error: %s',
                tokens.response_status_code,
            )
            fluxo_code = oAuthCodeTiny()
            logger.warning(
                'Tiny oAuth Refresh |'
                ' It was necessary to force the start of the code flow.'
            )
            return fluxo_code.oauth_flow_tiny()

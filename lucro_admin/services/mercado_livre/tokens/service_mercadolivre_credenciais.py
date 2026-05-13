import os
import subprocess
import logging

from lucro_admin.utils.cript_state import cript_state
from lucro_admin.utils.code_state import code_string
from lucro_admin.core.entities_credenciais import Credencial
from lucro_admin.adapters.mercado_livre.mercado_livre_credenciais import Code

logger = logging.getLogger('lucroadmin.services.mercadolivre')


class oAuthCodeMercadoLivre:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def abrindo_edge(self, url: str) -> bool:
        """
        abrindo_edge -> Apenas por motivo de que a conta admin do ML esta logada no Edge

        :param self: Objeto
        :param url: EndPoint para obter o Code
        :type url: str
        :return: Se abriu - True - Se não - False
        :rtype: bool
        """
        caminho_edge: str = (
            'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
        )
        if os.path.exists(caminho_edge):
            comando = [caminho_edge, url]
            subprocess.Popen(comando)
        return True

    def url_code(self, client_id: str, redirect_url: str, state: str) -> str:
        """
        url_code -> Montagem da URL para obtenção do CODE

        :param self: Objeto
        :param client_id: Credencial de acesso gerado pelo app do Mercado Livre
        :type client_id: str
        :param redirect_url: URL de redirecionamento
        :type redirect_url: str
        :param state: State aleatório criptografado
        :type state: str
        :return: URL montada
        :rtype: str
        """
        url: str = f'https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&state={state}'
        return url

    def fluxo_oAuth_code_mercadolivre(self) -> str:
        """
        fluxo_oAuth_code_mercadolivre -> Orquestração do fluxo para trocarmos o CODE por credenciais de maior duração

        :param self: Objeto
        :return: Access Token válido
        :rtype: str
        """
        client_id: str = self.repositorio.get_client_id()
        client_secret: str = self.repositorio.get_client_secret()
        if not client_id or not client_secret:
            logger.exception(
                'Mercado Livre oAuth Code | Credenciais não encontradas'
            )
            raise Exception('Credenciais não encontradas')

        adapt_code = Code()

        redirect_url: str = 'https://www.albhastore.com.br'
        state: str = cript_state()

        url: str = self.url_code(
            client_id=client_id, redirect_url=redirect_url, state=state
        )

        self.abrindo_edge(url=url)

        codestate: dict[str, str] = code_string()

        code: str = codestate['code']
        state_request: str = codestate['state']

        if state != state_request:
            logger.critical(
                'Mercado Livre oAuth Code | State retornado na url é invalido - Parando requisições. '
            )
            raise Exception('O state retornado não é válido.')

        logger.info('Mercado Livre oAuth Code | Code salvo e state validado')

        tokens_dict: dict[str, int] = adapt_code.troca_code_por_tokens(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_url=redirect_url,
        )
        tokens: Credencial = Credencial.from_api_response(tokens_dict)

        atualiza: bool = self.repositorio.salva_token(
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


class oAuthRefreshMercadoLivre:
    """
    oAuthRefreshMercadoLivre -> Fluxo completo de utilização do Refresh Token do Mercado Livre

    """

    def __init__(self, repositorio, adapt_refresh):
        self.repositorio = repositorio
        self.adapt_refresh = adapt_refresh

    def fluxo_refresh_token(self) -> str | None:
        """
        fluxo_refresh_token

        :param self: Objeto
        :return: Access Token válido
        :rtype: str | None
        """
        logger.info(
            'Mercado Livre oAuth Refresh | Iniciando fluxo com o Refresh Token'
        )

        logger.info('Mercado Livre oAuth Refresh | Buscando credenciais')
        client_id: str = self.repositorio.get_client_id()
        client_secret: str = self.repositorio.get_client_secret()
        refresh_token: str = self.repositorio.get_refresh_token()

        if not client_id or not client_secret or not refresh_token:
            logger.exception(
                'Mercado Livre oAuth Refresh | Credenciais não encontradas ou não retornadas do banco de dados'
            )
            raise Exception('Credenciais não encontradas')
        else:
            logger.info(
                'Mercado Livre oAuth Refresh | Credenciais validadas iniciando request'
            )

            tokens_dict: dict[str, int] = (
                self.adapt_refresh.usando_refresh_token(
                    client_id, client_secret, refresh_token
                )
            )
            tokens: Credencial = Credencial.from_api_response(tokens_dict)

        if tokens.response_status_code == 200:
            atualiza = self.repositorio.salva_token(
                tokens.access_token, tokens.refresh_token, tokens.expire
            )
            if atualiza:
                logger.info(
                    'Mercado Livre oAuth Refresh | Credenciais atualizadas'
                )
            else:
                logger.critical(
                    'Mercado Livre oAuth Refresh | Credenciais não atualizadas por falha no banco de dados'
                )
            return tokens.access_token

        elif tokens.response_status_code != 200:
            logger.critical(
                'MErcado Livre oAuth Refresh | Erro na requisição: %s',
                tokens.response_status_code,
            )
            fluxo_code = oAuthCodeMercadoLivre(repositorio=self.repositorio)
            logger.warning(
                'Mercado Livre oAuth Refresh | Foi necessário forçar o inicio do fluxo code'
            )
            return fluxo_code.fluxo_oAuth_code_mercadolivre()

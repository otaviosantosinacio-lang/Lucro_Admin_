import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from lucro_admin.adapters.bling.bling_pedidos import GetUrlXML
from lucro_admin.core.entities_pedidos import ErrorHTTP, ResultadoPagina
from lucro_admin.core.entities_produtos import ConfigSku
from lucro_admin.core.imposto.calcula_imposto import CalculadoraDeImposto
from lucro_admin.core.imposto.entities_imposto import (
    ErrorParse,
    ImpostosDaVenda,
    ProdutoComImposto,
    RetornoImpostos,
)
from lucro_admin.core.imposto.regras_fiscais import uf_sem_fcp
from lucro_admin.infra.repositorio_produtos import Produtos
from lucro_admin.services.bling.pedidos.service_bling_base_pedidos import (
    BaseHTTPBling,
)

logger = logging.getLogger('lucroadmin.services.blingpedidos')
base_url = 'https://api.bling.com.br/Api/v3'


class ParseXML:
    """
    ParseXML -> Parse do XML para extração de impostos
    """

    def __init__(self, access_token, adapt_pedidos) -> None:
        self.access_token = access_token
        self.adapt_pedidos = adapt_pedidos
        self.service_base = BaseHTTPBling(
            self.adapt_pedidos, self.access_token
        )
        self.calculadora = CalculadoraDeImposto()

    def url_nf(self, id_nf) -> str:
        """
        url_nf

        :param self: Objeto
        :param id_nf: Id único gerado pelo Bling para identificação da NF
        :return: URL endpoint para requisição da NF
        :rtype: str
        """
        return f'{base_url}/nfe/{id_nf}'

    def get_xml(self, pedido, situacao) -> RetornoImpostos | Any:
        """
        get_xml -> Get do XML por endpoint Bling

        :param self: Objeto
        :param pedido: Pedido completo de onde será feito a extração dos impostos
        :param situacao: Situação do pedido dentro do Bling (Ex: Atendido)
        :return: Impostos por produtos e imposto total da venda
        :rtype: RetornoImpostos | Any
        """

        url: str = self.url_nf(pedido.nf_id)
        adapt_xml = GetUrlXML()
        response: ResultadoPagina = self.service_base.organiza_get_request(url)

        if response.status == 'ok':
            url_xml = response.data['xml']
            response_xml = adapt_xml.request_xml(url_xml)
            logger.info('Bling get_xml | Xml extraído %s', response_xml)
            parse = self.parse_xml(
                xml=response_xml, id_bling=pedido.id_bling, situacao=situacao
            )
            if isinstance(parse, ErrorParse):
                parse = self.calculadora.calculadora_de_tributos(
                    itens=pedido.itens,
                    id_bling=pedido.id_bling,
                    sit=situacao,
                    uf_dest=pedido.uf_dest,
                )
            return parse
        if response.status == 'rated_limit':
            erro = ErrorHTTP(
                status=response.error['status'],
                error=response.error['body'],
                metodo='get_xml',
                classe='ParseXML',
                local='parse_xml.py',
                endpoint=url,
                data=datetime.now(),
            )
            logger.error(
                'Bling get_xml | Erro ao buscar informações na endpoint %s -> %s',
                url,
                erro.status,
            )

            return self.calculadora.calculadora_de_tributos(
                itens=pedido.itens,
                id_bling=pedido.id_bling,
                sit=situacao,
                uf_dest=pedido.uf_dest,
            )

    def parse_xml(
        self, xml, id_bling, situacao
    ) -> RetornoImpostos | ErrorParse:
        """
        parse_xml -> Extração de impostos por tags XML

        :param self: Objeto
        :param xml: Texto XML
        :param id_bling: Id único gerado pelo Bling por venda
        :param situacao: Situação do pedido dentro do Bling (Ex: Atendido)
        :return: Impostos individualizado por produto e total de impostos da venda
        :rtype: ProdutoComImposto | ErrorParse
        """
        vICMS_n = vPIS_n = vCOFINS_n = vICMS_dest_n = vFCP_n = 0
        namespace = '{http://www.portalfiscal.inf.br/nfe}'
        parse_xml = ET.fromstring(xml)
        produtos = Produtos()
        logger.info('Bling debug_xml | Iniciando extração de dados do xml')
        # Começando a extração de dados do XML
        Nfe = parse_xml.find(f'{namespace}NFe')
        infNFe = Nfe.find(f'{namespace}infNFe')
        if infNFe is None:
            return ErrorParse(tag='infNFe', error='Tag não encontrada')
        dest = infNFe.find(f'{namespace}dest')
        if dest is None:
            return ErrorParse(tag='dest', error='Tag não encontrada')
        ender_dest = dest.find(f'{namespace}enderDest')
        if ender_dest is None:
            return ErrorParse(tag='enderDest', error='Tag não encontrada')
        uf_dest = ender_dest.find(f'{namespace}UF')
        if uf_dest is None:
            return ErrorParse(tag='UF', error='Tag não encontrada')
        else:
            uf_dest = ender_dest.find(f'{namespace}UF').text
        sem_fcp = uf_sem_fcp(uf_dest)
        # Pegando as dets(produtos) do XML
        dets = infNFe.findall(f'{namespace}det')
        if dets is None:
            return ErrorParse(tag='det', error='Tag não encontrada')
        produtos_com_imposto = []
        for det in dets:
            prod = det.find(f'{namespace}prod')
            if prod is not None:
                produto_NF = prod.find(f'{namespace}cProd')
                if produto_NF is None:
                    return ErrorParse(tag='cProd', error='Tag não encontrada')
                else:
                    produto_NF = prod.find(f'{namespace}cProd').text
                sku = ConfigSku.configsku(produto_NF)
                vProd = prod.find(f'{namespace}vProd')
                if vProd is None:
                    return ErrorParse(tag='vProd', error='Tag não encontrada')
                else:
                    vProd = prod.find(f'{namespace}vProd').text
                qCom = prod.find(f'{namespace}qCom')
                if qCom is None:
                    return ErrorParse(tag='qCom', error='Tag não encontrada')
                else:
                    qCom = prod.find(f'{namespace}qCom').text
                qCom_n = self.parse_int_from_xml_quantity(qCom)
                vProd_n = float(vProd)
            else:
                return ErrorParse(tag='prod', error='Tag não encontrada')
            imposto = det.find(f'{namespace}imposto')

            # Encontrando valor do ICMS
            if imposto is None:
                return ErrorParse(tag='imposto', error='Tag não encontrada')
            else:
                ICMS0 = imposto.find(f'{namespace}ICMS')
                if ICMS0 is None:
                    return ErrorParse(tag='ICMS', error='Tag não encontrada')

                ICMS00 = ICMS0.find(f'{namespace}ICMS00')
                if ICMS00 is None:
                    return ErrorParse(tag='ICMS', error='Tag não encontrada')
                else:
                    vICMS = ICMS00.find(f'{namespace}vICMS')
                    if vICMS is None:
                        return ErrorParse(
                            tag='vICMS', error='Tag não encontrada'
                        )
                    else:
                        vICMS = ICMS00.find(f'{namespace}vICMS').text
                        vICMS_n = float(vICMS)

                # Encontrando valor do PIS
            PIS = imposto.find(f'{namespace}PIS')
            if PIS is None:
                return ErrorParse(tag='PIS', error='Tag não encontrada')
            PISAliq = PIS.find(f'{namespace}PISAliq')
            if PISAliq is None:
                return ErrorParse(tag='PISAliq', error='Tag não encontrada')
            vPIS = PISAliq.find(f'{namespace}vPIS')
            if vPIS is None:
                return ErrorParse(tag='vPIS', error='Tag não encontrada')
            else:
                vPIS = PISAliq.find(f'{namespace}vPIS').text
                vPIS_n = float(vPIS)

                # Encontrando o Valor do COFINS
            COFINS = imposto.find(f'{namespace}COFINS')
            if COFINS is None:
                return ErrorParse(tag='COFINS', error='Tag não encontrada')
            COFINSAliq = COFINS.find(f'{namespace}COFINSAliq')
            if COFINSAliq is None:
                return ErrorParse(tag='COFINSAliq', error='Tag não encontrada')
            vCOFINS = COFINSAliq.find(f'{namespace}vCOFINS')
            if vCOFINS is None:
                return ErrorParse(tag='vCOFINS', error='Tag não encontrada')
            else:
                vCOFINS = COFINSAliq.find(f'{namespace}vCOFINS').text
                vCOFINS_n = float(vCOFINS)

                # Se for uma transação interestadual temos o DIFAL
            if uf_dest != 'SP':
                ICMS_dest = imposto.find(f'{namespace}ICMSUFDest')
                if ICMS_dest is None:
                    return ErrorParse(
                        tag='ICMS_dest', error='Tag não encontrada'
                    )
                vICMS_dest = ICMS_dest.find(f'{namespace}vICMSUFDest')
                if vICMS_dest is None:
                    return ErrorParse(
                        tag='vICMS_dest', error='Tag não encontrada'
                    )
                else:
                    vICMS_dest = ICMS_dest.find(f'{namespace}vICMSUFDest').text
                    vICMS_dest_n = float(vICMS_dest)

                if sem_fcp == False:
                    vFCP = ICMS_dest.find(f'{namespace}vFCPUFDest')
                    if vFCP is None:
                        return ErrorParse(
                            tag='vICMS_dest', error='Tag não encontrada'
                        )
                    else:
                        vFCP = ICMS_dest.find(f'{namespace}vFCPUFDest').text
                        vFCP_n = float(vFCP)
                    if vFCP_n == 0:
                        vFCP_n = vProd_n * (2 / 100)
            total_imposto = (
                vICMS_n + vPIS_n + vCOFINS_n + vICMS_dest_n + vFCP_n
            )

            preco_custo = produtos.consulta_custo(SKU=sku)
            preco_custo *= qCom_n
            imposto_produto = ProdutoComImposto(
                id_bling=id_bling,
                situacao_pedido=situacao,
                sku=sku,
                quantidade=qCom_n,
                preco_custo=preco_custo,
                valor=vProd_n,
                icms=vICMS_n,
                pis=vPIS_n,
                cofins=vCOFINS_n,
                difal=vICMS_dest_n,
                fcp=vFCP_n,
                total=total_imposto,
            )
            produtos_com_imposto.append(imposto_produto)

        imposto_venda = ImpostosDaVenda.soma_impostos(
            produtos_imposto=produtos_com_imposto, id_bling=id_bling
        )
        logger.info(
            'Bling debug_xml | Produto com impostos individualizado -> %s',
            produtos_com_imposto,
        )
        return RetornoImpostos(
            produto_imposto=produtos_com_imposto, venda_imposto=imposto_venda
        )

    def parse_decimal(self, text: str | None) -> Decimal:
        """
        Converte uma string numérica para Decimal de forma segura.
        Aceita '1', '1.0000' e também '1,0000' (troca vírgula por ponto).
        """
        if text is None:
            raise ValueError('texto None')

        s = text.strip()
        if not s:
            raise ValueError('texto vazio')

        # alguns XMLs/integrações podem trazer vírgula
        s = s.replace(',', '.')

        try:
            return Decimal(s)
        except InvalidOperation as e:
            raise ValueError(f'número inválido: {text!r}') from e

    def parse_int_from_xml_quantity(self, text: str | None) -> int:
        """
        Regra: qCom deve ser unidade (inteiro).
        Aceita '1' e '1.0000' como 1.
        Rejeita '1.5' (pois isso seria fracionado).
        """
        q = self.parse_decimal(text)

        # to_integral_value() retorna o Decimal arredondado para inteiro
        # Só aceitamos se não houver parte fracionária:
        if q != q.to_integral_value():
            raise ValueError(f'quantidade fracionada não permitida: {q}')

        return int(q)

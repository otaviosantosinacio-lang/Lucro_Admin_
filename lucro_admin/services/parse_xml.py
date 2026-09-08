import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from lucro_admin.core.imposto.entities_imposto import ErrorParse, TaxItem
from lucro_admin.core.imposto.regras_fiscais import uf_without_fcp

logger = logging.getLogger('lucroadmin.services.parseXML')


class ParseXML:

    def __init__(self):
        self.namespace: str = '{http://www.portalfiscal.inf.br/nfe}'

    def parse_xml(
        self,
        xml,
        order_items
    ) -> ErrorParse | Any:
        """
        parse_xml -> Extraction of taxes by XML tags

        :param self: Object
        :param xml: XML text
        :return: Taxes broken down by product and total taxes for the sale
        :rtype: ProdutoComImposto | ErrorParse
        """
        difal = fcp = 0

        parse_xml = ET.fromstring(xml)
        logger.info(
            'Lucro Admin Parse XML| Starting XML data extraction'
        )

        Nfe = parse_xml.find(f'{self.namespace}NFe')

        infNFe = Nfe.find(f'{self.namespace}infNFe')
        if infNFe is None:
            return ErrorParse(tag='infNFe', error='Tag Not Found')

        dest = infNFe.find(f'{self.namespace}dest')
        if dest is None:
            return ErrorParse(tag='dest', error='Tag Not Found')

        ender_dest = dest.find(f'{self.namespace}enderDest')
        if ender_dest is None:
            return ErrorParse(tag='enderDest', error='Tag Not Found')

        uf_recipient = ender_dest.find(f'{self.namespace}UF')
        if uf_recipient is None:
            return ErrorParse(tag='UF', error='Tag Not Found')

        else:
            uf_recipient = ender_dest.find(f'{self.namespace}UF').text
        without_fcp = uf_without_fcp(uf=uf_recipient)

        dets = infNFe.findall(f'{self.namespace}det')

        if dets is None:
            return ErrorParse(tag='det', error='Tag Not Found')

        taxes_products = []

        for det in dets:
            prod = det.find(f'{self.namespace}prod')
            if prod is not None:
                product = self.parse_det_product(
                    det_prod=prod
                )
                sproduct = prod.find(f'{self.namespace}vUnTrib').text
                vproduct = float(sproduct)
            else:
                return ErrorParse(tag='prod', error='Tag Not Found')
            tax = det.find(f'{self.namespace}imposto')

            if tax is None:
                return ErrorParse(tag='imposto', error='Tag Not Found')
            else:
                # ICMS Tax
                icms0 = tax.find(f'{self.namespace}ICMS')
                if icms0 is None:
                    return ErrorParse(tag='ICMS', error='Tag não encontrada')
                icms = self.parse_det_tax_icms(det_tax_icms=icms0)
                if isinstance(icms, ErrorParse):
                    return icms

                # PIS Tax
                pis0 = tax.find(f'{self.namespace}PIS')
                if pis0 is None:
                    return ErrorParse(tag='PIS', error='Tag Not Found')
                pis = self.parse_det_tax_pis(det_tax_pis=pis0)
                if isinstance(pis, ErrorParse):
                    return pis

                # COFINS Tax
                cofins0 = tax.find(f'{self.namespace}COFINS')
                if cofins0 is None:
                    return ErrorParse(tag='COFINS', error='Tag Not Found')
                cofins = self.parse_det_tax_cofins(det_tax_cofins=cofins0)
                if isinstance(cofins, ErrorParse):
                    return cofins

                # IBS CBS Tax
                ibscbs0 = tax.find(f'{self.namespace}IBSCBS')
                if ibscbs0 is None:
                    return ErrorParse(tag='IBSCBS', error='Tag Not Found')
                ibscbs = self.parse_det_tax_ibscbs(det_tax_ibscbs=ibscbs0)

                # If it's an interstate transaction, we have the DIFAL
                if uf_recipient != 'SP':
                    icms_dest = tax.find(f'{self.namespace}ICMSUFDest')
                    if icms_dest is None:
                        return ErrorParse(
                        tag='ICMS_dest', error='Tag Not Found'
                    )
                    difal = self.parse_det_tax_difal(det_tax_difal=icms_dest)
                    if isinstance(difal, ErrorParse):
                        return difal

                    if not without_fcp:
                        fcp = self.parse_det_tax_fcp(
                            det_tax_fcp=icms_dest,
                            product_value=vproduct
                        )

            taxes_products.append(
                {
                    'SKU': product,
                    'ICMS': icms,
                    'PIS': pis,
                    'COFINS': cofins,
                    'IBS': ibscbs[0]['ibs'],
                    'CBS': ibscbs[0]['cbs'],
                    'DIFAL': difal,
                    'FCP': fcp
                }
            )
        tax_item = []
        for item_tax in taxes_products:
            for item in order_items:
                if item_tax['SKU'] == item[2]:
                    for key, value in item_tax.items():
                        if key == 'SKU':
                            continue
                        else:
                            tax_item.append(
                                TaxItem(
                                order_item_id=item[0],
                                tax_type=key,
                                tax_value=value,
                                calculation_source='XML'
                            )
                        )
                elif item_tax['SKU'] == item[3]:
                    for key, value in item_tax.items():
                        if key == 'SKU':
                            continue
                        else:
                            tax_item.append(
                                TaxItem(
                                order_item_id=item[0],
                                tax_type=key,
                                tax_value=value,
                                calculation_source='XML'
                            )
                        )
                else:
                    continue
        logger.info(
            'Lucro Admin Parse XML | Product with itemized taxes -> %s',
            tax_item
        )
        return tax_item

    def parse_det_product(self, det_prod):
        product_invoice = det_prod.find(f'{self.namespace}cProd')
        if product_invoice is None:
            return ErrorParse(tag='cProd', error='Tag Not Found')
        else:
            product_invoice = det_prod.find(f'{self.namespace}cProd').text
            return product_invoice

    def parse_det_tax_icms(self, det_tax_icms):
        ICMS00 = det_tax_icms.find(f'{self.namespace}ICMS00')

        if ICMS00 is None:
            return ErrorParse(tag='ICMS', error='Tag Not Found')
        else:
            vICMS = ICMS00.find(f'{self.namespace}vICMS')

            if vICMS is None:
                return ErrorParse(
                    tag='vICMS', error='Tag Not Found'
                )
            else:
                vICMS = ICMS00.find(f'{self.namespace}vICMS').text
                vICMS_n = float(vICMS)

        return vICMS_n

    def parse_det_tax_pis(self, det_tax_pis):
        PISAliq = det_tax_pis.find(f'{self.namespace}PISAliq')
        if PISAliq is None:
            return ErrorParse(tag='PISAliq', error='Tag Not Found')

        vPIS = PISAliq.find(f'{self.namespace}vPIS')

        if vPIS is None:
            return ErrorParse(tag='vPIS', error='Tag Not Found')
        else:
            vPIS = PISAliq.find(f'{self.namespace}vPIS').text
            vPIS_n = float(vPIS)

        return vPIS_n

    def parse_det_tax_cofins(self, det_tax_cofins):
        COFINSAliq = det_tax_cofins.find(f'{self.namespace}COFINSAliq')
        if COFINSAliq is None:
            return ErrorParse(tag='COFINSAliq', error='Tag Not Found')
        vCOFINS = COFINSAliq.find(f'{self.namespace}vCOFINS')

        if vCOFINS is None:
            return ErrorParse(tag='vCOFINS', error='Tag Not Found')
        else:
            vCOFINS = COFINSAliq.find(f'{self.namespace}vCOFINS').text
            vCOFINS_n = float(vCOFINS)

        return vCOFINS_n

    def parse_det_tax_difal(self, det_tax_difal):
        vICMS_dest = det_tax_difal.find(f'{self.namespace}vICMSUFDest')
        if vICMS_dest is None:
            return ErrorParse(
                tag='vICMS_dest', error='Tag Not Found'
            )
        else:
            vICMS_dest = det_tax_difal.find(
                f'{self.namespace}vICMSUFDest'
            ).text
            vICMS_dest_n = float(vICMS_dest)

        return vICMS_dest_n

    def parse_det_tax_fcp(self, det_tax_fcp, product_value):
        vFCP = det_tax_fcp.find(f'{self.namespace}vFCPUFDest')
        if vFCP is None:
            return ErrorParse(
                tag='vFCPUFDest', error='Tag Not Found'
            )

        else:
            vFCP = det_tax_fcp.find(f'{self.namespace}vFCPUFDest').text
            vFCP_n = float(vFCP)

        if vFCP_n == 0:
            vFCP_n = product_value * (2 / 100)

        return vFCP_n

    def parse_det_tax_ibscbs(self, det_tax_ibscbs):
        gibscbs = det_tax_ibscbs.find(f'{self.namespace}gIBSCBS')
        if gibscbs is not None:
            ibs = gibscbs.find(f'{self.namespace}vIBS').text

            gcbs = gibscbs.find(f'{self.namespace}gCBS')
            cbs = gcbs.find(f'{self.namespace}vCBS').text

            ibscbs = [
                {
                    'ibs': float(ibs),
                    'cbs': float(cbs)
                }
            ]

        else:
            ibscbs = [
                {
                    'ibs': 0.0,
                    'cbs': 0.0
                }
            ]

        return ibscbs

    def parse_decimal(self, text: str | None) -> Decimal:
        """
        Safely converts a numeric string to Decimal. Accepts '1', '1.0000',
        and also '1,0000' (replaces comma with a dot).
        """
        if text is None:
            raise ValueError('text None')

        s = text.strip()
        if not s:
            raise ValueError('text vazio')

        s = s.replace(',', '.')

        try:
            return Decimal(s)
        except InvalidOperation as e:
            raise ValueError(f'número inválido: {text!r}') from e

    def parse_int_from_xml_quantity(self, text: str | None) -> int:
        """
        Rule: qCom must be a whole number (integer).
        Accepts '1' and '1.0000' as 1.
        Rejects '1.5' (because that would be fractional).
        """
        q = self.parse_decimal(text)

        # to_integral_value() retorna o Decimal arredondado para inteiro
        # Só aceitamos se não houver parte fracionária:
        if q != q.to_integral_value():
            raise ValueError(f'quantidade fracionada não permitida: {q}')

        return int(q)

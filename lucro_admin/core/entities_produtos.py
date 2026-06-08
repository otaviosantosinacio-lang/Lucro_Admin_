from dataclasses import dataclass
from typing import Literal


@dataclass
class ConfigSku:
    """
    ConfigSku -> Tratamento do SKU retornado das vendas

    Attributes:
        sku: Código de identificação do produto.
        :type sku: str

    """

    sku: str | Literal['MCB002']

    @classmethod
    def configsku(cls, sku) -> 'ConfigSku':
        """
        configsku -> Configuração do SKU para ficar padronizado,
        FBA Classic e DBA da Amazon fazem alterações no SKU.

        Attributes:&nome=%20
            sku: Código de identificação do produto.
            :type sku: str

        """
        if sku == 'MCB002-preta':
            return 'MCB002'
        tam = len(sku)
        tam_final1 = 8
        tam_final2 = 4
        final1 = sku[-tam_final1:]
        final2 = sku[-tam_final2:]
        finais = ['_Classic', '-Classic', '-classic', '-DBA']
        if final1 in finais:
            sku_tam = tam - tam_final1
            sku_tratado = sku[:sku_tam]
            return sku_tratado
        elif final2 in finais:
            sku_tam = tam - tam_final2
            sku_tratado = sku[:sku_tam]
            return sku_tratado
        else:
            return sku


@dataclass
class Produto:
    sku: str
    nome: str
    preco_custo: float

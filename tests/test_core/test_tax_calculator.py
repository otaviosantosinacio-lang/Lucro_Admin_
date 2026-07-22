import pytest

from lucro_admin.core.imposto import tax_calculator
from lucro_admin.core.imposto.tax_calculator import TaxCalculator


@pytest.fixture
def fake_product_cost(monkeypatch):
    def fake_consulta_custo(self, *, SKU: str):
        return 10.0
    monkeypatch.setattr(
        tax_calculator.Produtos,
        'consulta_custo',
        fake_consulta_custo
    )


def test_tax_calculator_internal_operation(products_list, fake_product_cost):

    calculator = TaxCalculator()
    taxes = calculator.tax_calculator(
        items=products_list,
        id_bling=123456,
        sit='Atendido',
        uf_dest='SP'
        )
    for c, item in enumerate(taxes.product_tax):
        if c == 0:
            assert item.icms == pytest.approx(18.09)
            assert item.cofins == pytest.approx(6.26316)
            assert item.pis == pytest.approx(1.3597650000000001)
            assert item.difal == 0.0
            assert item.fcp == 0.0
            assert item.sku == 'lucro_admin_test'
        else:
            assert item.icms == pytest.approx(4.14)
            assert item.cofins == pytest.approx(1.43336)
            assert item.pis == pytest.approx(0.31119)
            assert item.difal == 0.0
            assert item.fcp == 0.0
            assert item.sku == 'lucro_admin_test2'

    assert taxes.sale_tax.icms == pytest.approx(22.23)
    assert taxes.sale_tax.difal == 0.0
    assert taxes.sale_tax.pis == pytest.approx(1.670955)
    assert taxes.sale_tax.cofins == pytest.approx(7.69652)
    assert taxes.sale_tax.fcp == 0.0
    assert taxes.sale_tax.total == pytest.approx(31.597474)


def test_tax_calculator_interstate_operation(products_list, fake_product_cost):

    calculator = TaxCalculator()
    taxes = calculator.tax_calculator(
        items=products_list,
        id_bling=123456,
        sit='Atendido',
        uf_dest='RJ'
        )

    for c, item in enumerate(taxes.product_tax):
        if c == 0:
            assert item.icms == pytest.approx(4.02)
            assert item.cofins == pytest.approx(5.95764)
            assert item.pis == pytest.approx(1.2934350000000001)
            assert item.difal == pytest.approx(18.09)
            assert item.fcp == pytest.approx(2.0100000000000002)
            assert item.sku == 'lucro_admin_test'
        else:
            assert item.icms == pytest.approx(0.92)
            assert item.cofins == pytest.approx(1.36343999)
            assert item.pis == pytest.approx(0.29601)
            assert item.difal == pytest.approx(4.14)
            assert item.fcp == pytest.approx(0.46)
            assert item.sku == 'lucro_admin_test2'

    assert taxes.sale_tax.icms == pytest.approx(4.94)
    assert taxes.sale_tax.difal == pytest.approx(22.23)
    assert taxes.sale_tax.pis == pytest.approx(1.589445)
    assert taxes.sale_tax.cofins == pytest.approx(7.321079)
    assert taxes.sale_tax.fcp == pytest.approx(2.47)
    assert taxes.sale_tax.total == pytest.approx(38.5505)


def test_tax_calculator_interstate_operation_without_fcp(
        products_list, fake_product_cost
):

    calculator = TaxCalculator()
    taxes = calculator.tax_calculator(
        items=products_list,
        id_bling=123456,
        sit='Atendido',
        uf_dest='AC'
        )

    for c, item in enumerate(taxes.product_tax):
        if c == 0:
            assert item.fcp == 0.0

        else:
            assert item.fcp == 0.0

    assert taxes.sale_tax.fcp == pytest.approx(0.0)

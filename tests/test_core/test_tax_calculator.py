from lucro_admin.core.imposto import tax_calculator
from lucro_admin.core.imposto.tax_calculator import TaxCalculator


def test_tax_calculator_iternal_operation(products_list, monkeypatch):
    def fake_consulta_custo(self, *, SKU: str):
        return 10.0

    monkeypatch.setattr(
        tax_calculator.Produtos,
        'consulta_custo',
        fake_consulta_custo
    )
    calculator = TaxCalculator()
    taxes = calculator.tax_calculator(
        items=products_list,
        id_bling=123456,
        sit='Atendido',
        uf_dest='SP'
        )

    expected_sale_icms_tax = 22.23
    expected_sale_difal_tax = 0.0
    expected_sale_pis_tax = 1.6709550000000002
    expected_sale_cofins_tax = 7.69652
    expected_sale_fcp_tax = 0.0
    expected_sale_total_tax = 31.597474999999996

    print(taxes)
    assert taxes.sale_tax.icms == expected_sale_icms_tax
    assert taxes.sale_tax.difal == expected_sale_difal_tax
    assert taxes.sale_tax.pis == expected_sale_pis_tax
    assert taxes.sale_tax.cofins == expected_sale_cofins_tax
    assert taxes.sale_tax.fcp == expected_sale_fcp_tax
    assert taxes.sale_tax.total == expected_sale_total_tax
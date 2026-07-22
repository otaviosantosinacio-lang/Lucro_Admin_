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

    for c, item in enumerate(taxes.product_tax):
        if c == 0:
            assert item.icms == 18.09  # noqa: PLR2004
            assert item.cofins == 6.263159999999999  # noqa: PLR2004
            assert item.pis == 1.3597650000000001   # noqa: PLR2004
            assert item.difal == 0.0
            assert item.fcp == 0.0
            assert item.sku == 'lucro_admin_test'
        else:
            assert item.icms == 4.14  # noqa: PLR2004
            assert item.cofins == 1.43336  # noqa: PLR2004
            assert item.pis == 0.31119   # noqa: PLR2004
            assert item.difal == 0.0
            assert item.fcp == 0.0
            assert item.sku == 'lucro_admin_test2'

    expected_sale_icms_tax = 22.23
    expected_sale_difal_tax = 0.0
    expected_sale_pis_tax = 1.6709550000000002
    expected_sale_cofins_tax = 7.69652
    expected_sale_fcp_tax = 0.0
    expected_sale_total_tax = 31.597474999999996

    assert taxes.sale_tax.icms == expected_sale_icms_tax
    assert taxes.sale_tax.difal == expected_sale_difal_tax
    assert taxes.sale_tax.pis == expected_sale_pis_tax
    assert taxes.sale_tax.cofins == expected_sale_cofins_tax
    assert taxes.sale_tax.fcp == expected_sale_fcp_tax
    assert taxes.sale_tax.total == expected_sale_total_tax


def test_tax_calculator_iterstate_operation(products_list, monkeypatch):
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
        uf_dest='RJ'
        )

    print(taxes)

    for c, item in enumerate(taxes.product_tax):
        if c == 0:
            assert item.icms == 4.0200000000000005  # noqa: PLR2004
            assert item.cofins == 5.95764  # noqa: PLR2004
            assert item.pis == 1.2934350000000001  # noqa: PLR2004
            assert item.difal == 18.09  # noqa: PLR2004
            assert item.fcp == 2.0100000000000002   # noqa: PLR2004
            assert item.sku == 'lucro_admin_test'
        else:
            assert item.icms == 0.92  # noqa: PLR2004
            assert item.cofins == 1.3634399999999998    # noqa: PLR2004
            assert item.pis == 0.29601   # noqa: PLR2004
            assert item.difal == 4.14   # noqa: PLR2004
            assert item.fcp == 0.46     # noqa: PLR2004
            assert item.sku == 'lucro_admin_test2'

    expected_sale_icms_tax = 4.94
    expected_sale_difal_tax = 22.23
    expected_sale_pis_tax = 1.589445
    expected_sale_cofins_tax = 7.321079999999999
    expected_sale_fcp_tax = 2.47
    expected_sale_total_tax = 38.550525

    assert taxes.sale_tax.icms == expected_sale_icms_tax
    assert taxes.sale_tax.difal == expected_sale_difal_tax
    assert taxes.sale_tax.pis == expected_sale_pis_tax
    assert taxes.sale_tax.cofins == expected_sale_cofins_tax
    assert taxes.sale_tax.fcp == expected_sale_fcp_tax
    assert taxes.sale_tax.total == expected_sale_total_tax


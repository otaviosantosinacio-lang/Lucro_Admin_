from lucro_admin.core.imposto.entities_imposto import SalesTaxes


def test_entity_salestax(products_tax):

    sales_cost = SalesTaxes.sum_taxes(
        products_tax=products_tax,
        id_bling=1
    )

    assert sales_cost.icms == 10.93
    assert sales_cost.pis == 3.02
    assert sales_cost.cofins == 4.79
    assert sales_cost.difal == 23.39
    assert sales_cost.fcp == 2.16
    assert sales_cost.total == 44.29
    assert sales_cost.cost == 26.98

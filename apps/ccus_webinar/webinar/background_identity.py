"""Explicit product boundary for slide 9's per-unit climate indicators."""

LOW_VOLTAGE = ("market group for electricity, low voltage",
               "electricity, low voltage", "kilowatt hour", "ENC")


def indicator_identity(mix_row):
    if mix_row["sector"] == "Electricity":
        return LOW_VOLTAGE
    return tuple(mix_row[k] for k in
                 ("market_name", "reference_product", "market_unit", "location"))

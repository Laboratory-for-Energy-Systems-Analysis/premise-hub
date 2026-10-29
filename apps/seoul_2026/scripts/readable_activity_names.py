"""Decode timing-carrier names without exporting private inventory comments."""

import re


def historical_carrier_names(path):
    import openpyxl

    result = {}
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for sheet in wb:
        name, columns = "", None
        for row in sheet.values:
            if row[0] == "Activity":
                name, columns = str(row[1]), None
            elif row[0] == "name" and row[1] == "amount":
                columns = {v:i for i,v in enumerate(row) if v}
            elif columns and "dated flow" in name and row[0] and row[columns["type"]] == "biosphere":
                comment = str(row[columns["comment"]] or "")
                match = re.match(r"Historical uptake allocated to ([^:]+):", comment)
                if not match:
                    continue
                fuel = match.group(1).strip()
                assert len(fuel) < 120
                role = "reference" if " | BAU | " in name else "CCS" if " | CCS | " in name else "CCUS"
                sign = "uptake" if row[columns["amount"]] < 0 else "adjustment"
                result[name] = f"{fuel}: historical non-fossil CO₂ {sign} ({role})"
    wb.close()
    return result

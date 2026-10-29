"""Extract selected ERW process-map quantities; no LCA or source mutation."""

from pathlib import Path
import hashlib
import json
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data/coastal_erw_ei312.xlsx"
rows = list(
    openpyxl.load_workbook(source, read_only=True, data_only=True).active.values
)
start = next(i for i, row in enumerate(rows) if row[0] == "name" and row[1] == "amount")
end = next(i for i in range(start + 1, len(rows)) if rows[i][0] == "Activity")
exchanges = [dict(zip(rows[start], r)) for r in rows[start + 1 : end] if r[0]]


def amount(name, unit):
    matches = [e for e in exchanges if e["name"] == name and e["unit"] == unit]
    if len(matches) != 1:
        raise ValueError((name, matches))
    return float(matches[0]["amount"]) * 1000


payload = {
    "basis": "One deployment: 1.25 tonnes rock, source reference potential 1 tonne eventual atmospheric CO2 uptake",
    "source": "coastal_erw_ei312.xlsx, static reference; scale per-unit exchanges by 1000",
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "quantities": {
        "rock_kg": amount("Olivine", "kilogram"),
        "eventual_uptake_kg": amount("Carbon dioxide, in air", "kilogram"),
        "electricity_kwh": amount(
            "market group for electricity, medium voltage", "kilowatt hour"
        ),
        "direct_diesel_mj": sum(
            float(e["amount"]) * 1000
            for e in exchanges
            if e["unit"] == "megajoule" and "diesel" in e["name"]
        ),
        "truck_tkm": sum(
            float(e["amount"]) * 1000 for e in exchanges if e["unit"] == "ton kilometer"
        ),
        "water_m3": amount("Water, well, in ground", "cubic meter"),
        "nickel_upper_bound_kg": amount("Nickel II", "kilogram"),
    },
    "interpretation": "Electricity is aggregate foreground demand, not grinding alone. Direct machinery diesel excludes fuel embedded in haulage/spreading providers. Truck quantity is freight service, not diesel mass. Uptake is eventual gross source potential, not a deadline or net climate score. Ni is a conservative mobilization bound, not measured release. Alkalinity is not independently quantified.",
}
(ROOT / "data/erw_process_quantities.json").write_text(
    json.dumps(payload, indent=2) + "\n"
)

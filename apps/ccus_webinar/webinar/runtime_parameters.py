"""Display constants shared with the reviewed, offline calculation contract."""
ELECTRICITY_OPTIONS = ('ENC market', 'wind', 'photovoltaic', 'natural gas', 'coal')
FUEL_SHARES = tuple(range(0, 101, 10))
SYSTEMS = ('BAU', 'CCS', 'CCUS')
# MJ/kg, used only to show individual fuel uptake profiles per GJ on slide 11.
UPTAKE_FUEL_LHV = {56: 22.0, 57: 2.51, 58: 10.97, 59: 16.62, 60: 3.83, 61: 12.5}

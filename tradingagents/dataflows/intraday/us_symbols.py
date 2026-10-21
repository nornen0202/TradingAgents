"""Explicit equivalent share-class symbols; never drop a class suffix."""


def canonical_symbol(symbol):
    value = str(symbol).strip().upper()
    return {"BRK/B": "BRK-B", "BRK.B": "BRK-B", "BRK B": "BRK-B"}.get(value, value)


def kis_symbol(symbol):
    value = canonical_symbol(symbol)
    return {"BRK-B": "BRK/B"}.get(value, value)

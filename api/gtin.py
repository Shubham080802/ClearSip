"""Representations of the same GTIN-12, GTIN-13, or GTIN-14 package code."""


def equivalent_gtins(code: str) -> tuple[str, ...]:
    """Return exact code first, then legal leading-zero representations.

    UPC-E uses a different compression scheme, so eight-digit codes remain exact.
    """
    if not code.isdigit() or len(code) not in (12, 13, 14):
        return (code,)
    significant = code.lstrip("0") or "0"
    return tuple(dict.fromkeys((code, *(
        significant.zfill(width)
        for width in (12, 13, 14)
        if len(significant) <= width
    ))))

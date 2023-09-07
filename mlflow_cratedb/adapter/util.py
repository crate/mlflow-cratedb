from vasuki import generate_nagamani19_int


def generate_unique_integer() -> int:
    """
    Produce a short, unique, non-sequential identifier based on Hashids.
    """
    return generate_nagamani19_int(size=10)

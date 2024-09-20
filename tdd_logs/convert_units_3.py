def convert(value, to_unit):
    if isinstance(value, str) and value.endswith("in") and to_unit == "cm":
        inches = float(value[:-2])
        return inches * 2.54
    elif isinstance(value, (int, float)) and to_unit == "in":
        return value / 2.54
    return None
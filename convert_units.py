def convert(value, to_unit):
    if to_unit == "cm" and value.endswith("in"):
        inches = float(value[:-2])
        return round(inches * 2.54, 2)
    elif to_unit == "in" and value.endswith("cm"):
        centimeters = float(value[:-2])
        return round(centimeters / 2.54, 2)
    elif to_unit == "m" and value.endswith("yd"):
        yards = float(value[:-2])
        return round(yards * 0.9144, 4)
    elif to_unit == "yd" and value.endswith("m"):
        meters = float(value[:-1])
        return round(meters / 0.9144, 4)
    return None
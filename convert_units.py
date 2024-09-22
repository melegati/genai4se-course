def convert(value, to_unit):
    if to_unit == "cm":
        inches = float(value[:-2])  # Remove the "in" and convert to float
        return round(inches * 2.54, 2)  # Convert inches to centimeters
    elif to_unit == "in":
        centimeters = float(value[:-2])  # Remove the "cm" and convert to float
        return round(centimeters / 2.54, 2)  # Convert centimeters to inches
    elif to_unit == "m":
        yards = float(value[:-2])  # Remove the "yd" and convert to float
        return round(yards * 0.9144, 4)  # Convert yards to meters
    elif to_unit == "yd":
        meters = float(value[:-1])  # Remove the "m" and convert to float
        return round(meters / 0.9144, 4)  # Convert meters to yards
    return None
def convert(value, to_unit):
    import re

    # Conversion factors
    conversions = {
        'in': 2.54,         # inches to centimeters
        'cm': 1 / 2.54,    # centimeters to inches
        'yd': 0.9144,      # yards to meters
        'm': 1              # meters to meters
    }

    match = re.match(r"(\d+\.?\d*)([a-zA-Z]+)", value)
    if match:
        amount = float(match.group(1))
        from_unit = match.group(2)

        # Convert to standard unit (meters)
        if from_unit == 'in':
            amount_m = amount * conversions['in'] / 100
        elif from_unit == 'cm':
            amount_m = amount / 100
        elif from_unit == 'yd':
            amount_m = amount * conversions['yd']
        elif from_unit == 'm':
            amount_m = amount
        else:
            raise ValueError("Unknown from_unit")

        # Convert to required unit
        if to_unit == 'in':
            return round(amount_m * 100 / conversions['in'], 2)
        elif to_unit == 'cm':
            return round(amount_m * 100, 2)
        elif to_unit == 'yd':
            return round(amount_m / conversions['yd'], 4)
        elif to_unit == 'm':
            return round(amount_m, 4)
        else:
            raise ValueError("Unknown to_unit")
    else:
        raise ValueError("Invalid input format")
import math

def relative_humidity(temp_c, dew_point_c):
    numerator = math.exp((17.67 * dew_point_c) / (dew_point_c + 243.5))
    denominator = math.exp((17.67 * temp_c) / (temp_c + 243.5))
    rh = 100 * (numerator / denominator)
    return rh

# Example
T = 30  # Temperature in °C
Td = 24  # Dew point in °C

print(f"Relative Humidity: {relative_humidity(T, Td):.2f}%")

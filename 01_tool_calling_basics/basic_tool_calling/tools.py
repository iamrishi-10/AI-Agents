"""Tool implementations. Pure Python — no LLM/client logic here."""

_MOCK_WEATHER = {
    "hyderabad": {"temperature_c": 32, "condition": "Sunny"},
    "mumbai": {"temperature_c": 29, "condition": "Humid"},
    "delhi": {"temperature_c": 38, "condition": "Hot and dry"},
    "bangalore": {"temperature_c": 24, "condition": "Cloudy"},
}


def calculate(number1: float, number2: float, operation: str) -> dict:
    """Perform a basic arithmetic calculation on two numbers."""
    if operation == "add":
        return {"result": number1 + number2}
    elif operation == "subtract":
        return {"result": number1 - number2}
    elif operation == "multiply":
        return {"result": number1 * number2}
    elif operation == "divide":
        if number2 == 0:
            return {"error": "Cannot divide by zero"}
        return {"result": number1 / number2}
    else:
        return {"error": "Unsupported operation"}


def get_weather(city: str) -> dict:
    """Return mocked weather data for a city."""
    key = city.strip().lower()
    data = _MOCK_WEATHER.get(key)
    if data is None:
        return {"city": city, "error": "No mock data available for this city"}
    return {"city": city, **data}


def convert_distance(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert distance from one unit to another."""
    conversion_factors = {
        "meters": 1.0,
        "kilometers": 1000.0,
        "miles": 1609.34,
        "centimeters": 0.01,
        "inches": 0.0254,
        "feet": 0.3048,
    }

    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    if from_unit not in conversion_factors or to_unit not in conversion_factors:
        raise ValueError(
            f"Unsupported conversion. Supported units: {list(conversion_factors.keys())}"
        )

    # convert value into base unit (meters)
    value_in_meters = value * conversion_factors[from_unit]

    # convert value from base unit to target unit
    target_unit = value_in_meters / conversion_factors[to_unit]

    return {"result": target_unit}

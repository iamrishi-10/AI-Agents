"""Tool implementations. Pure Python — no LLM/client logic here."""

MOCK_WEATHER = {
    "hyderabad": {"temperature_c": 32, "condition": "Sunny"},
    "mumbai": {"temperature_c": 29, "condition": "Humid"},
    "delhi": {"temperature_c": 38, "condition": "Hot and dry"},
    "bangalore": {"temperature_c": 24, "condition": "Cloudy"},
}

# Stores the result already produced for each idempotency_key, so a repeated
# send_email call returns the original result instead of sending again.
PROCESSED_EMAILS = {}


def get_weather(city: str) -> dict:
    key = city.strip().lower()
    if key.replace(" ", "") == "timeoutcity":
        # Deterministic mock of a transient provider failure, for testing retries.
        raise TimeoutError("Weather provider timed out")

    data = MOCK_WEATHER.get(key)
    if data is None:
        raise ValueError(f"No mock weather data available for '{city}'")
    return {"city": city, **data}


def calculate(number1: float, number2: float, operation: str) -> dict:
    if operation == "add":
        return {"result": number1 + number2}
    elif operation == "subtract":
        return {"result": number1 - number2}
    elif operation == "multiply":
        return {"result": number1 * number2}
    elif operation == "divide":
        if number2 == 0:
            raise ValueError("Cannot divide by zero")
        return {"result": number1 / number2}
    else:
        raise ValueError(f"Unsupported operation: {operation}")


def convert_distance(value: float, from_unit: str, to_unit: str) -> float:
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

    value_in_meters = value * conversion_factors[from_unit]
    return value_in_meters / conversion_factors[to_unit]


def send_email(recipient: str, subject: str, body: str, idempotency_key: str) -> dict:
    """Mock-send an email. Side-effecting — a repeated call with the same
    idempotency_key does not send again; it reports the request as a duplicate."""
    if recipient.strip().lower() == "timeout@example.com":
        # Deterministic mock of a transient provider failure, for testing retries.
        raise TimeoutError("Email provider timed out")

    if idempotency_key in PROCESSED_EMAILS:
        original = PROCESSED_EMAILS[idempotency_key]
        return {
            "status": "duplicate",
            "recipient": original["recipient"],
            "subject": original["subject"],
            "message": f"Email already sent for idempotency_key '{idempotency_key}'; not sent again.",
        }

    result = {
        "status": "sent",
        "recipient": recipient,
        "subject": subject,
    }

    PROCESSED_EMAILS[idempotency_key] = result
    return result

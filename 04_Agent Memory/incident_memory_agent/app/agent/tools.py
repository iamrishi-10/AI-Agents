"""Mock current-evidence tools: live health/log signal, distinct from historical memory."""

from langchain_core.tools import tool

_SERVICE_HEALTH = {
    "payments-api": "degraded: high DB latency",
    "orders-api": "healthy: all systems normal",
    "auth-api": "healthy: all systems normal",
}

_SERVICE_LOGS = {
    "payments-api": "TimeoutError: connection pool exhausted",
    "orders-api": "INFO: order created successfully (order_id=8841)",
    "auth-api": "INFO: token refresh succeeded (user_id=203)",
}


@tool
def get_service_health(service_name: str) -> str:
    """Return the current health status of a service."""
    return _SERVICE_HEALTH.get(
        service_name, f"unknown: no health data for service '{service_name}'"
    )


@tool
def get_recent_logs(service_name: str) -> str:
    """Return a recent representative log line for a service."""
    return _SERVICE_LOGS.get(
        service_name, f"unknown: no recent logs for service '{service_name}'"
    )

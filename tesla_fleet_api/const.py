"""Tesla Fleet API constants."""
from enum import StrEnum


class Errors(StrEnum):
    """Tesla Fleet API error codes."""

    INVALID_COMMAND = "invalid_command"
    INVALID_FIELD = "invalid_field"
    INVALID_REQUEST = "invalid_request"
    INVALID_TOKEN = "invalid_token"  # Teslemetry specific
    INVALID_AUTH_CODE = "invalid_auth_code"
    INVALID_REDIRECT_URL = "invalid_redirect_url"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    MOBILE_ACCESS_DISABLED = "mobile_access_disabled"


SERVERS = {
    "na": "https://fleet-api.prd.na.vn.cloud.tesla.com",
    "eu": "https://fleet-api.prd.eu.vn.cloud.tesla.com",
    "cn": "https://fleet-api.prd.cn.vn.cloud.tesla.cn",
}

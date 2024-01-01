"""Tesla Fleet API constants."""
from enum import StrEnum


class TeslaErrors(StrEnum):
    INVALID_COMMAND = "invalid_command"
    INVALID_FIELD = "invalid_field"
    INVALID_REQUEST = "invalid_request"
    INVALID_AUTH_CODE = "invalid_auth_code"
    INVALID_REDIRECT_URL = "invalid_redirect_url"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    MOBILE_ACCESS_DISABLED = "mobile_access_disabled"
    NO_RESPONSE_BODY = "no response body"

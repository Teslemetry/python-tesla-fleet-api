import aiohttp
from .const import LOGGER


class TeslaFleetError(BaseException):
    """Base class for all Tesla exceptions."""

    message: str = "An unknown error has occurred."
    status: int | None = None
    data: dict | None = None

    def __init__(self, data: dict | None = None, status: int | None = None):
        LOGGER.debug(self.message)
        self.data = data
        self.status = status or self.status
        super().__init__(self.message)


class ResponseError(TeslaFleetError):
    """The response from the server was not JSON."""

    message = "The response from the server was not JSON."


class InvalidCommand(TeslaFleetError):
    """The data request or command is unknown."""

    message = "The data request or command is unknown."
    status = 400
    key = "invalid_command"


class InvalidField(TeslaFleetError):
    """A field in the input is not valid."""

    message = "A field in the input is not valid."
    status = 400
    key = "invalid_field"


class InvalidRequest(TeslaFleetError):
    """The request body is not valid, a description giving a more specific error message may be returned."""

    message = "The request body is not valid"
    status = 400
    key = "invalid_request"


class InvalidAuthCode(TeslaFleetError):
    """The "code" in request body is invalid, generate a new one and try again."""

    message = "The 'code' in request body is invalid, generate a new one and try again."
    status = 400
    key = "invalid_auth_code"


class InvalidRedirectUrl(TeslaFleetError):
    """Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."""

    message = "Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."
    status = 400
    key = "invalid_redirect_url"


class UnauthorizedClient(TeslaFleetError):
    """We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."""

    message = "We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."
    status = 400
    key = "unauthorized_client"


class MobileAccessDisabled(TeslaFleetError):
    """The vehicle has turned off remote access."""

    message = "The vehicle has turned off remote access."
    status = 401
    key = "mobile_access_disabled"


class InvalidToken(TeslaFleetError):  # Teslemetry specific
    """Teslemetry specific error for invalid access token."""

    message = "Invalid Teslemetry access token."
    status = 401
    key = "invalid_token"


class OAuthExpired(TeslaFleetError):
    """The OAuth token has expired."""

    message = "The OAuth token has expired."
    status = 401
    key = "token expired (401)"


class PaymentRequired(TeslaFleetError):
    """Payment is required in order to use the API (non-free account only)."""

    message = "Payment is required in order to use the API (non-free account only)."
    status = 402


class SubscriptionRequired(TeslaFleetError):
    """Subscription is required in order to use Teslemetry."""

    message = "Subscription is required in order to use Teslemetry."
    status = 402
    key = "subscription_required"


class Forbidden(TeslaFleetError):
    """Access to this resource is not authorized, developers should check required Scope."""

    message = "Access to this resource is not authorized, developers should check required Scope."
    status = 403
    key = "Unauthorized missing scopes"


class UnsupportedVehicle(TeslaFleetError):
    """The vehicle is unsupported."""

    message = "The vehicle is unsupported."
    status = 403
    key = "unsupported vehicle"


class NotFound(TeslaFleetError):
    """The requested resource does not exist."""

    message = "The requested resource does not exist."
    status = 404


class NotAllowed(TeslaFleetError):
    """The operation is not allowed."""

    message = "The operation is not allowed."
    status = 405


class NotAcceptable(TeslaFleetError):
    """The HTTP request does not have a Content-Type header set to application/json."""

    message = (
        "The HTTP request does not have a Content-Type header set to application/json."
    )
    status = 406


class VehicleOffline(TeslaFleetError):
    """The vehicle is not "online."""

    message = "The vehicle is not 'online'."
    status = 408


class PreconditionFailed(TeslaFleetError):
    """A condition has not been met to process the request."""

    message = "A condition has not been met to process the request."
    status = 412


class InvalidRegion(TeslaFleetError):
    """This user is not present in the current region."""

    message = "This user is not present in the current region."
    status = 421


class InvalidResource(TeslaFleetError):
    """There is a semantic problem with the data, e.g. missing or invalid data."""

    message = "There is a semantic problem with the data, e.g. missing or invalid data."
    status = 422


class Locked(TeslaFleetError):
    """Account is locked, and must be unlocked by Tesla."""

    message = "Account is locked, and must be unlocked by Tesla."
    status = 423


class RateLimited(TeslaFleetError):
    """Account or server is rate limited."""

    message = "Account or server is rate limited."
    status = 429


class ResourceUnavailableForLegalReasons(TeslaFleetError):
    """Querying for a user/vehicle without proper privacy settings."""

    message = "Querying for a user/vehicle without proper privacy settings."
    status = 451


class ClientClosedRequest(TeslaFleetError):
    """Client has closed the request before the server could send a response."""

    message = "Client has closed the request before the server could send a response."
    status = 499


class InternalServerError(TeslaFleetError):
    """An error occurred while processing the request."""

    message = "An error occurred while processing the request."
    status = 500


class ServiceUnavailable(TeslaFleetError):
    """Either an internal service or a vehicle did not respond (timeout)."""

    message = "Either an internal service or a vehicle did not respond (timeout)."
    status = 503


class GatewayTimeout(TeslaFleetError):
    """Server did not receive a response."""

    message = "Server did not receive a response."
    status = 504


class DeviceUnexpectedResponse(TeslaFleetError):
    """Vehicle responded with an error - might need a reboot, OTA update, or service."""

    message = (
        "Vehicle responded with an error - might need a reboot, OTA update, or service."
    )
    status = 540


class LibraryError(Exception):
    """Errors related to this library."""


async def raise_for_status(resp: aiohttp.ClientResponse) -> None:
    """Raise an exception if the response status code is >=400."""
    # https://developer.tesla.com/docs/fleet-api#response-codes

    if resp.status < 400:
        return

    data = None
    error = None
    if resp.content_type == "application/json":
        data = await resp.json()
        error = data.get("error")

    if resp.status == 400:
        if error:
            for exception in [
                InvalidCommand,
                InvalidField,
                InvalidRequest,
                InvalidAuthCode,
                InvalidRedirectUrl,
                UnauthorizedClient,
            ]:
                if error == exception.key:
                    raise exception(data)
        raise InvalidRequest(data)
    elif resp.status == 401:
        if error:
            for exception in [OAuthExpired, MobileAccessDisabled]:
                if error == exception.key:
                    raise exception(data)
            raise InvalidToken(data)
        # This error does not return a body
        raise OAuthExpired()
    elif resp.status == 402:
        if error == SubscriptionRequired.key:
            raise SubscriptionRequired(data)
        raise PaymentRequired(data)
    elif resp.status == 403:
        if error == UnsupportedVehicle.key:
            raise UnsupportedVehicle(data)
        raise Forbidden(data)
    elif resp.status == 404:
        raise NotFound(data)
    elif resp.status == 405:
        raise NotAllowed(data)
    elif resp.status == 406:
        raise NotAcceptable(data)
    elif resp.status == 408:
        raise VehicleOffline(data)
    elif resp.status == 412:
        raise PreconditionFailed(data)
    elif resp.status == 421:
        raise InvalidRegion(data)
    elif resp.status == 422:
        raise InvalidResource(data)
    elif resp.status == 423:
        raise Locked(data)
    elif resp.status == 429:
        raise RateLimited(data)
    elif resp.status == 451:
        raise ResourceUnavailableForLegalReasons(data)
    elif resp.status == 499:
        raise ClientClosedRequest(data)
    elif resp.status == 500:
        raise InternalServerError(data)
    elif resp.status == 503:
        raise ServiceUnavailable(data)
    elif resp.status == 504:
        raise GatewayTimeout(data)
    elif resp.status == 540:
        raise DeviceUnexpectedResponse(data)
    elif data is None:
        raise ResponseError(status=resp.status)
    resp.raise_for_status()

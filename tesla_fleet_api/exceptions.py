import aiohttp
from .const import Errors


class TeslaFleetError(BaseException):
    """Base class for all Tesla exceptions."""

    message: str
    status: int
    error: str | None
    error_description: str | None

    def __init__(self, status: int, data: dict[str, str] | None = None):
        self.status = status
        self.error = data.get("error") or data.get("message")
        self.error_description = data.get("error_description")


class InvalidCommand(TeslaFleetError):
    """The data request or command is unknown."""

    message = "The data request or command is unknown."


class InvalidField(TeslaFleetError):
    """A field in the input is not valid."""

    message = "A field in the input is not valid."


class InvalidRequest(TeslaFleetError):
    """The request body is not valid, a description giving a more specific error message may be returned."""

    message = "The request body is not valid"


class InvalidAuthCode(TeslaFleetError):
    """The "code" in request body is invalid, generate a new one and try again."""

    message = "The 'code' in request body is invalid, generate a new one and try again."


class InvalidRedirectUrl(TeslaFleetError):
    """Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."""

    message = "Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."


class UnauthorizedClient(TeslaFleetError):
    """We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."""

    message = "We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."


class MobileAccessDisabled(TeslaFleetError):
    """The vehicle has turned off remote access."""

    message = "The vehicle has turned off remote access."


class AuthExpired(TeslaFleetError):
    """The OAuth token has expired."""

    message = "The OAuth token has expired."


class PaymentRequired(TeslaFleetError):
    """Payment is required in order to use the API (non-free account only)."""

    message = "Payment is required in order to use the API (non-free account only)."


class Forbidden(TeslaFleetError):
    """Access to this resource is not authorized, developers should check required scopes."""

    message = "Access to this resource is not authorized, developers should check required scopes."


class NotFound(TeslaFleetError):
    """The requested resource does not exist."""

    message = "The requested resource does not exist."


class NotAllowed(TeslaFleetError):
    """The operation is not allowed."""

    message = "The operation is not allowed."


class NotAcceptable(TeslaFleetError):
    """The HTTP request does not have a Content-Type header set to application/json."""

    message = (
        "The HTTP request does not have a Content-Type header set to application/json."
    )


class VehicleOffline(TeslaFleetError):
    """The vehicle is not "online."""

    message = "The vehicle is not 'online'."


class PreconditionFailed(TeslaFleetError):
    """A condition has not been met to process the request."""

    message = "A condition has not been met to process the request."


class InvalidRegion(TeslaFleetError):
    """This user is not present in the current region."""

    message = "This user is not present in the current region."


class InvalidResource(TeslaFleetError):
    """There is a semantic problem with the data, e.g. missing or invalid data."""

    message = "There is a semantic problem with the data, e.g. missing or invalid data."


class Locked(TeslaFleetError):
    """Account is locked, and must be unlocked by Tesla."""

    message = "Account is locked, and must be unlocked by Tesla."


class RateLimited(TeslaFleetError):
    """Account or server is rate limited."""

    message = "Account or server is rate limited."


class ResourceUnavailableForLegalReasons(TeslaFleetError):
    """Querying for a user/vehicle without proper privacy settings."""

    message = "Querying for a user/vehicle without proper privacy settings."


class ClientClosedRequest(TeslaFleetError):
    """Client has closed the request before the server could send a response."""

    message = "Client has closed the request before the server could send a response."


class InternalServerError(TeslaFleetError):
    """An error occurred while processing the request."""

    message = "An error occurred while processing the request."


class ServiceUnavailable(TeslaFleetError):
    """Either an internal service or a vehicle did not respond (timeout)."""

    message = "Either an internal service or a vehicle did not respond (timeout)."


class GatewayTimeout(TeslaFleetError):
    """Server did not receive a response."""

    message = "Server did not receive a response."


class DeviceUnexpectedResponse(TeslaFleetError):
    """Vehicle responded with an error - might need a reboot, OTA update, or service."""

    message = (
        "Vehicle responded with an error - might need a reboot, OTA update, or service."
    )


async def raise_for_status(resp: aiohttp.ClientResponse) -> None:
    """Raise an exception if the response status code is >=400."""
    # https://developer.tesla.com/docs/fleet-api#response-codes

    data = await resp.json()

    try:
        resp.raise_for_status()
    except aiohttp.ClientResponseError as e:
        if e.status == 400:
            if data.error == Errors.INVALID_COMMAND:
                raise InvalidCommand(e.status, data) from e
            elif data.error == Errors.INVALID_FIELD:
                raise InvalidField(e.status, data) from e
            elif data.error == Errors.INVALID_REQUEST:
                raise InvalidRequest(e.status, data) from e
            elif data.error == Errors.INVALID_AUTH_CODE:
                raise InvalidAuthCode(e.status, data) from e
            elif data.error == Errors.INVALID_REDIRECT_URL:
                raise InvalidRedirectUrl(e.status, data) from e
            elif data.error == Errors.UNAUTHORIZED_CLIENT:
                raise UnauthorizedClient(e.status, data) from e
        elif e.status == 401:
            if data.error == Errors.MOBILE_ACCESS_DISABLED:
                raise MobileAccessDisabled(e.status, data) from e
            elif data.error == Errors.NO_RESPONSE_BODY:
                raise AuthExpired(e.status, data) from e
        elif e.status == 402:
            raise PaymentRequired(e.status, data) from e
        elif e.status == 403:
            raise Forbidden(e.status, data) from e
        elif e.status == 404:
            raise NotFound(e.status, data) from e
        elif e.status == 405:
            raise NotAllowed(e.status, data) from e
        elif e.status == 406:
            raise NotAcceptable(e.status, data) from e
        elif e.status == 408:
            raise VehicleOffline(e.status, data) from e
        elif e.status == 412:
            raise PreconditionFailed(e.status, data) from e
        elif e.status == 421:
            raise InvalidRegion(e.status, data) from e
        elif e.status == 422:
            raise InvalidResource(e.status, data) from e
        elif e.status == 423:
            raise Locked(e.status, data) from e
        elif e.status == 429:
            raise RateLimited(e.status, data) from e
        elif e.status == 451:
            raise ResourceUnavailableForLegalReasons(e.status, data) from e
        elif e.status == 499:
            raise ClientClosedRequest(e.status, data) from e
        elif e.status == 500:
            raise InternalServerError(e.status, data) from e
        elif e.status == 503:
            raise ServiceUnavailable(e.status, data) from e
        elif e.status == 504:
            raise GatewayTimeout(e.status, data) from e
        elif e.status == 540:
            raise DeviceUnexpectedResponse(e.status, data) from e
        else:
            raise e

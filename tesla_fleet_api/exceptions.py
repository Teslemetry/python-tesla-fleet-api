import aiohttp
from .const import Errors


class TeslaError:
    """Base class for all Tesla exceptions."""

    message: str = "Something went wrong"

    def __init__(self, status, error, error_message):
        self.status = status
        self.error = error
        self.error_message = error_message


class TeslaInvalidCommand(TeslaError):
    """The data request or command is unknown."""

    message = "The data request or command is unknown."


class TeslaInvalidField(TeslaError):
    """A field in the input is not valid."""

    message = "A field in the input is not valid."


class TeslaInvalidRequest(TeslaError):
    """The request body is not valid, a description giving a more specific error message may be returned."""

    message = "The request body is not valid"


class TeslaInvalidAuthCode(TeslaError):
    """The "code" in request body is invalid, generate a new one and try again."""

    message = "The 'code' in request body is invalid, generate a new one and try again."


class TeslaInvalidRedirectUrl(TeslaError):
    """Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."""

    message = "Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."


class TeslaUnauthorizedClient(TeslaError):
    """We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."""

    message = "We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."


class TeslaMobileAccessDisabled(TeslaError):
    """The vehicle has turned off remote access."""

    message = "The vehicle has turned off remote access."


class TeslaNoResponseBody(TeslaError):
    """The OAuth token has expired."""

    message = "The OAuth token has expired."


class TeslaPaymentRequired(TeslaError):
    """Payment is required in order to use the API (non-free account only)."""

    message = "Payment is required in order to use the API (non-free account only)."


class TeslaForbidden(TeslaError):
    """Access to this resource is not authorized, developers should check required scopes."""

    message = "Access to this resource is not authorized, developers should check required scopes."


class TeslaNotFound(TeslaError):
    """The requested resource does not exist."""

    message = "The requested resource does not exist."


class TeslaNotAllowed(TeslaError):
    """The operation is not allowed."""

    message = "The operation is not allowed."


class TeslaNotAcceptable(TeslaError):
    """The HTTP request does not have a Content-Type header set to application/json."""

    message = (
        "The HTTP request does not have a Content-Type header set to application/json."
    )


class TeslaVehicleOffline(TeslaError):
    """The vehicle is not "online."""

    message = "The vehicle is not 'online'."


class TeslaPreconditionFailed(TeslaError):
    """A condition has not been met to process the request."""

    message = "A condition has not been met to process the request."


class TeslaInvalidRegion(TeslaError):
    """This user is not present in the current region."""

    message = "This user is not present in the current region."


class TeslaInvalidResource(TeslaError):
    """There is a semantic problem with the data, e.g. missing or invalid data."""

    message = "There is a semantic problem with the data, e.g. missing or invalid data."


class TeslaLocked(TeslaError):
    """Account is locked, and must be unlocked by Tesla."""

    message = "Account is locked, and must be unlocked by Tesla."


class TeslaRateLimited(TeslaError):
    """Account or server is rate limited."""

    message = "Account or server is rate limited."


class TeslaResourceUnavailableForLegalReasons(TeslaError):
    """Querying for a user/vehicle without proper privacy settings."""

    message = "Querying for a user/vehicle without proper privacy settings."


class TeslaClientClosedRequest(TeslaError):
    """Client has closed the request before the server could send a response."""

    message = "Client has closed the request before the server could send a response."


class TeslaInternalServerError(TeslaError):
    """An error occurred while processing the request."""

    message = "An error occurred while processing the request."


class TeslaServiceUnavailable(TeslaError):
    """Either an internal service or a vehicle did not respond (timeout)."""

    message = "Either an internal service or a vehicle did not respond (timeout)."


class TeslaGatewayTimeout(TeslaError):
    """Server did not receive a response."""

    message = "Server did not receive a response."


class TeslaDeviceUnexpectedResponse(TeslaError):
    """Vehicle responded with an error - might need a reboot, OTA update, or service."""

    message = (
        "Vehicle responded with an error - might need a reboot, OTA update, or service."
    )


async def raise_for_status(resp: aiohttp.ClientResponse) -> None:
    """Raise an exception if the response status code is >=400."""
    # https://developer.tesla.com/docs/fleet-api#response-codes

    payload = await resp.json()
    try:
        resp.raise_for_status()
    except aiohttp.ClientResponseError as e:
        print(e)
        if e.status == 400:
            if payload.error == Errors.INVALID_COMMAND:
                raise TeslaInvalidCommand from e
            elif payload.error == Errors.INVALID_FIELD:
                raise TeslaInvalidField from e
            elif payload.error == Errors.INVALID_REQUEST:
                raise TeslaInvalidRequest from e
            elif payload.error == Errors.INVALID_AUTH_CODE:
                raise TeslaInvalidAuthCode from e
            elif payload.error == Errors.INVALID_REDIRECT_URL:
                raise TeslaInvalidRedirectUrl from e
            elif payload.error == Errors.UNAUTHORIZED_CLIENT:
                raise TeslaUnauthorizedClient from e
        elif e.status == 401:
            if payload.error == Errors.MOBILE_ACCESS_DISABLED:
                raise TeslaMobileAccessDisabled from e
            elif payload.error == Errors.NO_RESPONSE_BODY:
                raise TeslaNoResponseBody from e
        elif e.status == 402:
            raise TeslaPaymentRequired from e
        elif e.status == 403:
            raise TeslaForbidden from e
        elif e.status == 404:
            raise TeslaNotFound from e
        elif e.status == 405:
            raise TeslaNotAllowed from e
        elif e.status == 406:
            raise TeslaNotAcceptable from e
        elif e.status == 408:
            raise TeslaVehicleOffline from e
        elif e.status == 412:
            raise TeslaPreconditionFailed from e
        elif e.status == 421:
            raise TeslaInvalidRegion from e
        elif e.status == 422:
            raise TeslaInvalidResource from e
        elif e.status == 423:
            raise TeslaLocked from e
        elif e.status == 429:
            raise TeslaRateLimited from e
        elif e.status == 451:
            raise TeslaResourceUnavailableForLegalReasons from e
        elif e.status == 499:
            raise TeslaClientClosedRequest from e
        elif e.status == 500:
            raise TeslaInternalServerError from e
        elif e.status == 503:
            raise TeslaServiceUnavailable from e
        elif e.status == 504:
            raise TeslaGatewayTimeout from e
        elif e.status == 540:
            raise TeslaDeviceUnexpectedResponse from e
        else:
            raise e

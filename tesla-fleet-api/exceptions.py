import aiohttp
from .const import TeslaErrors


class TeslaError(aiohttp.web.HTTPError):
    """Base class for all Tesla exceptions."""


class TeslaInvalidCommand(TeslaError, aiohttp.web.HTTPBadRequest):
    """The data request or command is unknown."""

    message = "The data request or command is unknown."


class TeslaInvalidField(TeslaError, aiohttp.web.HTTPBadRequest):
    """A field in the input is not valid."""

    message = "A field in the input is not valid."


class TeslaInvalidRequest(TeslaError, aiohttp.web.HTTPBadRequest):
    """The request body is not valid, a description giving a more specific error message may be returned."""

    message = "The request body is not valid"


class TeslaInvalidAuthCode(TeslaError, aiohttp.web.HTTPBadRequest):
    """The "code" in request body is invalid, generate a new one and try again."""

    message = "The 'code' in request body is invalid, generate a new one and try again."


class TeslaInvalidRedirectUrl(TeslaError, aiohttp.web.HTTPBadRequest):
    """Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."""

    message = "Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."


class TeslaUnauthorizedClient(TeslaError, aiohttp.web.HTTPBadRequest):
    """We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."""

    message = "We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."


class TeslaMobileAccessDisabled(TeslaError, aiohttp.web.HTTPUnauthorized):
    """The vehicle has turned off remote access."""

    message = "The vehicle has turned off remote access."


class TeslaNoResponseBody(TeslaError, aiohttp.web.HTTPUnauthorized):
    """The OAuth token has expired."""

    message = "The OAuth token has expired."


class TeslaPaymentRequired(TeslaError, aiohttp.web.HTTPPaymentRequired):
    """Payment is required in order to use the API (non-free account only)."""

    message = "Payment is required in order to use the API (non-free account only)."


class TeslaForbidden(TeslaError, aiohttp.web.HTTPForbidden):
    """Access to this resource is not authorized, developers should check required scopes."""

    message = "Access to this resource is not authorized, developers should check required scopes."


class TeslaNotFound(TeslaError, aiohttp.web.HTTPNotFound):
    """The requested resource does not exist."""

    message = "The requested resource does not exist."


class TeslaNotAllowed(TeslaError, aiohttp.web.HTTPMethodNotAllowed):
    """The operation is not allowed."""

    message = "The operation is not allowed."


class TeslaNotAcceptable(TeslaError, aiohttp.web.HTTPNotAcceptable):
    """The HTTP request does not have a Content-Type header set to application/json."""

    message = (
        "The HTTP request does not have a Content-Type header set to application/json."
    )


class TeslaVehicleOffline(TeslaError, aiohttp.web.HTTPError):
    """The vehicle is not "online."""

    message = "The vehicle is not 'online'."


class TeslaPreconditionFailed(TeslaError, aiohttp.web.HTTPPreconditionFailed):
    """A condition has not been met to process the request."""

    message = "A condition has not been met to process the request."


class TeslaInvalidRegion(TeslaError, aiohttp.web.HTTPMisdirectedRequest):
    """This user is not present in the current region."""

    message = "This user is not present in the current region."


class TeslaInvalidResource(TeslaError, aiohttp.web.HTTPUnprocessableEntity):
    """There is a semantic problem with the data, e.g. missing or invalid data."""

    message = "There is a semantic problem with the data, e.g. missing or invalid data."


class TeslaLocked(TeslaError, aiohttp.web.HTTPClientError):
    """Account is locked, and must be unlocked by Tesla."""

    message = "Account is locked, and must be unlocked by Tesla."


class TeslaRateLimited(TeslaError, aiohttp.web.HTTPTooManyRequests):
    """Account or server is rate limited."""

    message = "Account or server is rate limited."


class TeslaResourceUnavailableForLegalReasons(
    TeslaError, aiohttp.web.HTTPUnavailableForLegalReasons
):
    """Querying for a user/vehicle without proper privacy settings."""

    message = "Querying for a user/vehicle without proper privacy settings."


class TeslaClientClosedRequest(TeslaError, aiohttp.web.HTTPClientError):
    """Client has closed the request before the server could send a response."""

    message = "Client has closed the request before the server could send a response."


class TeslaInternalServerError(TeslaError, aiohttp.web.HTTPInternalServerError):
    """An error occurred while processing the request."""

    message = "An error occurred while processing the request."


class TeslaServiceUnavailable(TeslaError, aiohttp.web.HTTPServiceUnavailable):
    """Either an internal service or a vehicle did not respond (timeout)."""

    message = "Either an internal service or a vehicle did not respond (timeout)."


class TeslaGatewayTimeout(TeslaError, aiohttp.web.HTTPGatewayTimeout):
    """Server did not receive a response."""

    message = "Server did not receive a response."


class TeslaDeviceUnexpectedResponse(TeslaError, aiohttp.web.HTTPServerError):
    """Vehicle responded with an error - might need a reboot, OTA update, or service."""

    message = (
        "Vehicle responded with an error - might need a reboot, OTA update, or service."
    )


async def raise_for_status(resp: aiohttp.ClientResponse) -> None:
    """Raise an exception if the response status code is >=400."""
    # https://developer.tesla.com/docs/fleet-api#response-codes

    if resp.status < 400:
        return

    payload = await resp.json()
    if resp.status == 400:
        if payload.error == TeslaErrors.INVALID_COMMAND:
            raise TeslaInvalidCommand()
        elif payload.error == TeslaErrors.INVALID_FIELD:
            raise TeslaInvalidField()
        elif payload.error == TeslaErrors.INVALID_REQUEST:
            raise TeslaInvalidRequest()
        elif payload.error == TeslaErrors.INVALID_AUTH_CODE:
            raise TeslaInvalidAuthCode()
        elif payload.error == TeslaErrors.INVALID_REDIRECT_URL:
            raise TeslaInvalidRedirectUrl()
        elif payload.error == TeslaErrors.UNAUTHORIZED_CLIENT:
            raise TeslaUnauthorizedClient()
    elif resp.status == 401:
        if payload.error == TeslaErrors.MOBILE_ACCESS_DISABLED:
            raise TeslaMobileAccessDisabled()
        elif payload.error == TeslaErrors.NO_RESPONSE_BODY:
            raise TeslaNoResponseBody()
    elif resp.status == 402:
        raise TeslaPaymentRequired()
    elif resp.status == 403:
        raise TeslaForbidden()
    elif resp.status == 404:
        raise TeslaNotFound()
    elif resp.status == 405:
        raise TeslaNotAllowed()
    elif resp.status == 406:
        raise TeslaNotAcceptable()
    elif resp.status == 408:
        raise TeslaVehicleOffline()
    elif resp.status == 412:
        raise TeslaPreconditionFailed()
    elif resp.status == 421:
        raise TeslaInvalidRegion()
    elif resp.status == 422:
        raise TeslaInvalidResource()
    elif resp.status == 423:
        raise TeslaLocked()
    elif resp.status == 429:
        raise TeslaRateLimited()
    elif resp.status == 451:
        raise TeslaResourceUnavailableForLegalReasons()
    elif resp.status == 499:
        raise TeslaClientClosedRequest()
    elif resp.status == 500:
        raise TeslaInternalServerError()
    elif resp.status == 503:
        raise TeslaServiceUnavailable()
    elif resp.status == 504:
        raise TeslaGatewayTimeout()
    elif resp.status == 540:
        raise TeslaDeviceUnexpectedResponse()
    else:
        aiohttp.raise_for_status(resp)

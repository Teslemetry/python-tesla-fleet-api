import aiohttp
from .const import Errors


class TeslaFleetError:
    """Base class for all Tesla exceptions."""

    class Base(BaseException):
        message: str
        status: int
        error: str | None
        error_description: str | None

        def __init__(self, status: int, data: dict[str, str] | None = None):
            self.status = status
            self.error = data.get("error") or data.get("message")
            self.error_description = data.get("error_description")

    class InvalidCommand(Base):
        """The data request or command is unknown."""

        message = "The data request or command is unknown."

    class InvalidField(Base):
        """A field in the input is not valid."""

        message = "A field in the input is not valid."

    class InvalidRequest(Base):
        """The request body is not valid, a description giving a more specific error message may be returned."""

        message = "The request body is not valid"

    class InvalidAuthCode(Base):
        """The "code" in request body is invalid, generate a new one and try again."""

        message = (
            "The 'code' in request body is invalid, generate a new one and try again."
        )

    class InvalidRedirectUrl(Base):
        """Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."""

        message = "Invalid redirect URI/URL. The authorize redirect URI and token redirect URI must match."

    class UnauthorizedClient(Base):
        """We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."""

        message = "We don't recognize this client_id and client_secret combination. Use the client_id and client_secret that has been granted for the application."

    class MobileAccessDisabled(Base):
        """The vehicle has turned off remote access."""

        message = "The vehicle has turned off remote access."

    class NoResponseBody(Base):
        """The OAuth token has expired."""

        message = "The OAuth token has expired."

    class PaymentRequired(Base):
        """Payment is required in order to use the API (non-free account only)."""

        message = "Payment is required in order to use the API (non-free account only)."

    class Forbidden(Base):
        """Access to this resource is not authorized, developers should check required scopes."""

        message = "Access to this resource is not authorized, developers should check required scopes."

    class NotFound(Base):
        """The requested resource does not exist."""

        message = "The requested resource does not exist."

    class NotAllowed(Base):
        """The operation is not allowed."""

        message = "The operation is not allowed."

    class NotAcceptable(Base):
        """The HTTP request does not have a Content-Type header set to application/json."""

        message = "The HTTP request does not have a Content-Type header set to application/json."

    class VehicleOffline(Base):
        """The vehicle is not "online."""

        message = "The vehicle is not 'online'."

    class PreconditionFailed(Base):
        """A condition has not been met to process the request."""

        message = "A condition has not been met to process the request."

    class InvalidRegion(Base):
        """This user is not present in the current region."""

        message = "This user is not present in the current region."

    class InvalidResource(Base):
        """There is a semantic problem with the data, e.g. missing or invalid data."""

        message = (
            "There is a semantic problem with the data, e.g. missing or invalid data."
        )

    class Locked(Base):
        """Account is locked, and must be unlocked by Tesla."""

        message = "Account is locked, and must be unlocked by Tesla."

    class RateLimited(Base):
        """Account or server is rate limited."""

        message = "Account or server is rate limited."

    class ResourceUnavailableForLegalReasons(Base):
        """Querying for a user/vehicle without proper privacy settings."""

        message = "Querying for a user/vehicle without proper privacy settings."

    class ClientClosedRequest(Base):
        """Client has closed the request before the server could send a response."""

        message = (
            "Client has closed the request before the server could send a response."
        )

    class InternalServerError(Base):
        """An error occurred while processing the request."""

        message = "An error occurred while processing the request."

    class ServiceUnavailable(Base):
        """Either an internal service or a vehicle did not respond (timeout)."""

        message = "Either an internal service or a vehicle did not respond (timeout)."

    class GatewayTimeout(Base):
        """Server did not receive a response."""

        message = "Server did not receive a response."

    class DeviceUnexpectedResponse(Base):
        """Vehicle responded with an error - might need a reboot, OTA update, or service."""

        message = "Vehicle responded with an error - might need a reboot, OTA update, or service."


async def raise_for_status(resp: aiohttp.ClientResponse) -> None:
    """Raise an exception if the response status code is >=400."""
    # https://developer.tesla.com/docs/fleet-api#response-codes

    try:
        data = await resp.json()
    except json.decoder.JSONDecodeError as error:
        raise TeslaFleetError.NotFound() from error
    try:
        resp.raise_for_status()
    except aiohttp.ClientResponseError as e:
        if e.status == 400:
            if data.error == Errors.INVALID_COMMAND:
                raise TeslaFleetError.InvalidCommand(e.status, data) from e
            elif data.error == Errors.INVALID_FIELD:
                raise TeslaFleetError.InvalidField(e.status, data) from e
            elif data.error == Errors.INVALID_REQUEST:
                raise TeslaFleetError.InvalidRequest(e.status, data) from e
            elif data.error == Errors.INVALID_AUTH_CODE:
                raise TeslaFleetError.InvalidAuthCode(e.status, data) from e
            elif data.error == Errors.INVALID_REDIRECT_URL:
                raise TeslaFleetError.InvalidRedirectUrl(e.status, data) from e
            elif data.error == Errors.UNAUTHORIZED_CLIENT:
                raise TeslaFleetError.UnauthorizedClient(e.status, data) from e
        elif e.status == 401:
            if data.error == Errors.MOBILE_ACCESS_DISABLED:
                raise TeslaFleetError.MobileAccessDisabled(e.status, data) from e
            elif data.error == Errors.NO_RESPONSE_BODY:
                raise TeslaFleetError.NoResponseBody(e.status, data) from e
        elif e.status == 402:
            raise TeslaFleetError.PaymentRequired(e.status, data) from e
        elif e.status == 403:
            raise TeslaFleetError.Forbidden(e.status, data) from e
        elif e.status == 404:
            raise TeslaFleetError.NotFound(e.status, data) from e
        elif e.status == 405:
            raise TeslaFleetError.NotAllowed(e.status, data) from e
        elif e.status == 406:
            raise TeslaFleetError.NotAcceptable(e.status, data) from e
        elif e.status == 408:
            raise TeslaFleetError.VehicleOffline(e.status, data) from e
        elif e.status == 412:
            raise TeslaFleetError.PreconditionFailed(e.status, data) from e
        elif e.status == 421:
            raise TeslaFleetError.InvalidRegion(e.status, data) from e
        elif e.status == 422:
            raise TeslaFleetError.InvalidResource(e.status, data) from e
        elif e.status == 423:
            raise TeslaFleetError.Locked(e.status, data) from e
        elif e.status == 429:
            raise TeslaFleetError.RateLimited(e.status, data) from e
        elif e.status == 451:
            raise TeslaFleetError.ResourceUnavailableForLegalReasons(
                e.status, data
            ) from e
        elif e.status == 499:
            raise TeslaFleetError.ClientClosedRequest(e.status, data) from e
        elif e.status == 500:
            raise TeslaFleetError.InternalServerError(e.status, data) from e
        elif e.status == 503:
            raise TeslaFleetError.ServiceUnavailable(e.status, data) from e
        elif e.status == 504:
            raise TeslaFleetError.GatewayTimeout(e.status, data) from e
        elif e.status == 540:
            raise TeslaFleetError.DeviceUnexpectedResponse(e.status, data) from e
        else:
            raise e

import aiohttp
from .const import LOGGER


class TeslaFleetError(BaseException):
    """Base class for all Tesla exceptions."""

    message: str = "An unknown error has occurred."
    status: int | None = None
    data: dict | str | None = None
    key: str | None = None

    def __init__(self, data: dict | str | None = None, status: int | None = None):
        LOGGER.debug(self.message)
        self.data = data
        self.status = status or self.status
        super().__init__(self.message)


class ResponseError(TeslaFleetError):
    """The response from the server was not JSON."""

    message = "The response from the server was not JSON."
    data: str | None = None


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


class MissingToken(TeslaFleetError):
    """Third party specific error when no access token is provided."""

    message = "Missing access token."
    status = 401


class MissingTeslemetryToken(MissingToken):
    """Teslemetry specific error when no access token is provided."""

    key = "missing_token"


class MissingTessieToken(MissingToken):
    """Tessie specific error when no access token is provided."""

    key = "Access token is required"


class InvalidToken(TeslaFleetError):
    """Third party specific error for invalid access token."""

    message = "Invalid access token."
    status = 401


class InvalidTeslemetryToken(InvalidToken):
    """Teslemetry specific error for invalid access token."""

    key = "invalid_token"


class InvalidTessieToken(InvalidToken):
    """Tessie specific error for invalid access token."""

    key = "Invalid access token"


class OAuthExpired(TeslaFleetError):
    """The OAuth token has expired."""

    message = "The OAuth token has expired."
    status = 401
    key = "token expired (401)"


class LoginRequired(TeslaFleetError):  # Native and Teslemetry
    """The user has reset their password and a new auth code is required, or the refresh_token has already been used."""

    message = "The user has reset their password and a new auth code is required, or the refresh_token has already been used."
    status = 401
    key = "login_required"


class PaymentRequired(TeslaFleetError):
    """Payment is required in order to use the API (non-free account only)."""

    message = "Payment is required in order to use the API (non-free account only)."
    status = 402


class SubscriptionRequired(TeslaFleetError):  # Teslemetry specific
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


class InvalidMethod(TeslaFleetError):
    """The HTTP method is not allowed."""

    message = "The HTTP method is not allowed."
    status = 405
    key = "invalid_method"


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


class InvalidResponse(TeslaFleetError):
    """The response from Tesla was invalid."""

    message = "The response from Tesla was invalid."
    status = 424


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


class TeslaFleetInformationFault(TeslaFleetError):
    """Vehicle has responded with an error when sending a signed command"""

    message = "Vehicle has responded with an error when sending a signed command"


class UnknownFault(TeslaFleetInformationFault):
    """Unknown fault on signed command."""

    message = "Unknown fault on signed command."
    code = 1


class NotOnWhitelistFault(TeslaFleetInformationFault):
    """Not on whitelist fault on signed command."""

    message = "Not on whitelist fault on signed command."
    code = 2


class IVSmallerThanExpectedFault(TeslaFleetInformationFault):
    """IV smaller than expected fault on signed command."""

    message = "IV smaller than expected fault on signed command."
    code = 3


class InvalidTokenFault(TeslaFleetInformationFault):
    """Invalid token fault on signed command."""

    message = "Invalid token fault on signed command."
    code = 4


class TokenAndCounterInvalidFault(TeslaFleetInformationFault):
    """Token and counter invalid fault on signed command."""

    message = "Token and counter invalid fault on signed command."
    code = 5


class AESDecryptAuthFault(TeslaFleetInformationFault):
    """AES decrypt auth fault on signed command."""

    message = "AES decrypt auth fault on signed command."
    code = 6


class ECDSAInputFault(TeslaFleetInformationFault):
    """ECDSA input fault on signed command."""

    message = "ECDSA input fault on signed command."
    code = 7


class ECDSASignatureFault(TeslaFleetInformationFault):
    """ECDSA signature fault on signed command."""

    message = "ECDSA signature fault on signed command."
    code = 8


class LocalEntityStartFault(TeslaFleetInformationFault):
    """Local entity start fault on signed command."""

    message = "Local entity start fault on signed command."
    code = 9


class LocalEntityResultFault(TeslaFleetInformationFault):
    """Local entity result fault on signed command."""

    message = "Local entity result fault on signed command."
    code = 10


class CouldNotRetrieveKeyFault(TeslaFleetInformationFault):
    """Could not retrieve key fault on signed command."""

    message = "Could not retrieve key fault on signed command."
    code = 11


class CouldNotRetrieveTokenFault(TeslaFleetInformationFault):
    """Could not retrieve token fault on signed command."""

    message = "Could not retrieve token fault on signed command."
    code = 12


class SignatureTooShortFault(TeslaFleetInformationFault):
    """Signature too short fault on signed command."""

    message = "Signature too short fault on signed command."
    code = 13


class TokenIsIncorrectLengthFault(TeslaFleetInformationFault):
    """Token is incorrect length fault on signed command."""

    message = "Token is incorrect length fault on signed command."
    code = 14


class IncorrectEpochFault(TeslaFleetInformationFault):
    """Incorrect epoch fault on signed command."""

    message = "Incorrect epoch fault on signed command."
    code = 15


class IVIncorrectLengthFault(TeslaFleetInformationFault):
    """IV incorrect length fault on signed command."""

    message = "IV incorrect length fault on signed command."
    code = 16


class TimeExpiredFault(TeslaFleetInformationFault):
    """Time expired fault on signed command."""

    message = "Time expired fault on signed command."
    code = 17


class NotProvisionedWithIdentityFault(TeslaFleetInformationFault):
    """Not provisioned with identity fault on signed command."""

    message = "Not provisioned with identity fault on signed command."
    code = 18


class CouldNotHashMetadataFault(TeslaFleetInformationFault):
    """Could not hash metadata fault on signed command."""

    message = "Could not hash metadata fault on signed command."
    code = 19


INFORMATION_FAULTS = [
    None,
    UnknownFault,
    NotOnWhitelistFault,
    IVSmallerThanExpectedFault,
    InvalidTokenFault,
    TokenAndCounterInvalidFault,
    AESDecryptAuthFault,
    ECDSAInputFault,
    ECDSASignatureFault,
    LocalEntityStartFault,
    LocalEntityResultFault,
    CouldNotRetrieveKeyFault,
    CouldNotRetrieveTokenFault,
    SignatureTooShortFault,
    TokenIsIncorrectLengthFault,
    IncorrectEpochFault,
    IVIncorrectLengthFault,
    TimeExpiredFault,
    NotProvisionedWithIdentityFault,
    CouldNotHashMetadataFault,
]


class TeslaFleetMessageFault(TeslaFleetError):
    """Vehicle has responded with an error when sending a signed command"""

    message = "Vehicle has responded with an error when sending a signed command"


class TeslaFleetMessageFaultBusy(TeslaFleetMessageFault):
    """Vehicle is busy"""

    message = "Vehicle is busy"
    code = 1


class TeslaFleetMessageFaultTimeout(TeslaFleetMessageFault):
    """Vehicle timed out"""

    message = "Vehicle timed out"
    code = 2


class TeslaFleetMessageFaultUnknownKeyId(TeslaFleetMessageFault):
    """Unknown Key ID"""

    message = "Unknown Key ID"
    code = 3


class TeslaFleetMessageFaultInactiveKey(TeslaFleetMessageFault):
    """Inactive Key"""

    message = "Inactive Key"
    code = 4


class TeslaFleetMessageFaultInvalidSignature(TeslaFleetMessageFault):
    """Invalid Signature"""

    message = "Invalid Signature"
    code = 5


class TeslaFleetMessageFaultInvalidTokenOrCounter(TeslaFleetMessageFault):
    """Invalid Token or Counter"""

    message = "Invalid Token or Counter"
    code = 6


class TeslaFleetMessageFaultInsufficientPrivileges(TeslaFleetMessageFault):
    """Insufficient Privileges"""

    message = "Insufficient Privileges"
    code = 7


class TeslaFleetMessageFaultInvalidDomains(TeslaFleetMessageFault):
    """Invalid Domains"""

    message = "Invalid Domains"
    code = 8


class TeslaFleetMessageFaultInvalidCommand(TeslaFleetMessageFault):
    """Invalid Command"""

    message = "Invalid Command"
    code = 9


class TeslaFleetMessageFaultDecoding(TeslaFleetMessageFault):
    """Decoding Error"""

    message = "Decoding Error"
    code = 10


class TeslaFleetMessageFaultInternal(TeslaFleetMessageFault):
    """Internal Error"""

    message = "Internal Error"
    code = 11


class TeslaFleetMessageFaultWrongPersonalization(TeslaFleetMessageFault):
    """Wrong Personalization"""

    message = "Wrong Personalization"
    code = 12


class TeslaFleetMessageFaultBadParameter(TeslaFleetMessageFault):
    """Bad Parameter"""

    message = "Bad Parameter"
    code = 13


class TeslaFleetMessageFaultKeychainIsFull(TeslaFleetMessageFault):
    """Keychain is Full"""

    message = "Keychain is Full"
    code = 14


class TeslaFleetMessageFaultIncorrectEpoch(TeslaFleetMessageFault):
    """Incorrect Epoch"""

    message = "Incorrect Epoch"
    code = 15


class TeslaFleetMessageFaultIVIncorrectLength(TeslaFleetMessageFault):
    """IV Incorrect Length"""

    message = "IV Incorrect Length"
    code = 16


class TeslaFleetMessageFaultTimeExpired(TeslaFleetMessageFault):
    """Time Expired"""

    message = "Time Expired"
    code = 17


class TeslaFleetMessageFaultNotProvisionedWithIdentity(TeslaFleetMessageFault):
    """Not Provisioned with Identity"""

    message = "Not Provisioned with Identity"
    code = 18


class TeslaFleetMessageFaultCouldNotHashMetadata(TeslaFleetMessageFault):
    """Could not Hash Metadata"""

    message = "Could not Hash Metadata"
    code = 19


class TeslaFleetMessageFaultTimeToLiveTooLong(TeslaFleetMessageFault):
    """Time to Live Too Long"""

    message = "Time to Live Too Long"
    code = 20


class TeslaFleetMessageFaultRemoteAccessDisabled(TeslaFleetMessageFault):
    """Remote Access Disabled"""

    message = "Remote Access Disabled"
    code = 21


class TeslaFleetMessageFaultRemoteServiceAccessDisabled(TeslaFleetMessageFault):
    """Remote Service Access Disabled"""

    message = "Remote Service Access Disabled"
    code = 22


class TeslaFleetMessageFaultCommandRequiresAccountCredentials(TeslaFleetMessageFault):
    """Command Requires Account Credentials"""

    message = "Command Requires Account Credentials"
    code = 23


MESSAGE_FAULTS = [
    None,
    TeslaFleetMessageFaultBusy,
    TeslaFleetMessageFaultTimeout,
    TeslaFleetMessageFaultUnknownKeyId,
    TeslaFleetMessageFaultInactiveKey,
    TeslaFleetMessageFaultInvalidSignature,
    TeslaFleetMessageFaultInvalidTokenOrCounter,
    TeslaFleetMessageFaultInsufficientPrivileges,
    TeslaFleetMessageFaultInvalidDomains,
    TeslaFleetMessageFaultInvalidCommand,
    TeslaFleetMessageFaultDecoding,
    TeslaFleetMessageFaultInternal,
    TeslaFleetMessageFaultWrongPersonalization,
    TeslaFleetMessageFaultBadParameter,
    TeslaFleetMessageFaultKeychainIsFull,
    TeslaFleetMessageFaultIncorrectEpoch,
    TeslaFleetMessageFaultIVIncorrectLength,
    TeslaFleetMessageFaultTimeExpired,
    TeslaFleetMessageFaultNotProvisionedWithIdentity,
    TeslaFleetMessageFaultCouldNotHashMetadata,
    TeslaFleetMessageFaultTimeToLiveTooLong,
    TeslaFleetMessageFaultRemoteAccessDisabled,
    TeslaFleetMessageFaultRemoteServiceAccessDisabled,
    TeslaFleetMessageFaultCommandRequiresAccountCredentials,
]


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
            for exception in [
                OAuthExpired,
                MobileAccessDisabled,
                LoginRequired,
                MissingTeslemetryToken,
                MissingTessieToken,
                InvalidTeslemetryToken,
                InvalidTessieToken,
            ]:
                if error == exception.key:
                    raise exception(data)
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
        if error == InvalidMethod.key:
            raise InvalidMethod(data)
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
    elif resp.status == 424:
        raise InvalidResponse(data)
    elif resp.status == 429:
        raise RateLimited(
            {
                "reset": resp.headers.get("RateLimit-Reset"),
                "after": resp.headers.get("Retry-After"),
            }
        )
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
        raise ResponseError(status=resp.status, data=await resp.text())
    resp.raise_for_status()

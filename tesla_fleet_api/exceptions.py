import aiohttp
from tesla_fleet_api.const import LOGGER


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


class VehicleSubscriptionRequired(TeslaFleetError):  # Teslemetry specific
    """Subscription is required in order to use Teslemetry."""

    message = "Vehicle data subscription is required to make this request."
    status = 402
    key = "vehicle_subscription_required"


class InsufficientCredits(TeslaFleetError):
    """Account has insufficient credits to make this request."""

    message = "Account has insufficient command credits to make this request."
    status = 402
    key = "insufficient_credits"


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
    """Required vehicle subsystem is busy. Try again"""

    message = "Required vehicle subsystem is busy. Try again"
    code = 1


class TeslaFleetMessageFaultTimeout(TeslaFleetMessageFault):
    """Vehicle subsystem did not respond. Try again"""

    message = "Vehicle subsystem did not respond. Try again"
    code = 2


class TeslaFleetMessageFaultUnknownKeyId(TeslaFleetMessageFault):
    """Vehicle did not recognize the key used to authorize command. Make sure your key is paired with the vehicle"""

    message = "Vehicle did not recognize the key used to authorize command. Make sure your key is paired with the vehicle"
    code = 3


class TeslaFleetMessageFaultInactiveKey(TeslaFleetMessageFault):
    """Key used to authorize command has been disabled"""

    message = "Key used to authorize command has been disabled"
    code = 4


class TeslaFleetMessageFaultInvalidSignature(TeslaFleetMessageFault):
    """Command signature/MAC is incorrect. Use included session info to update session and try again"""

    message = "Command signature/MAC is incorrect. Use included session info to update session and try again"
    code = 5


class TeslaFleetMessageFaultInvalidTokenOrCounter(TeslaFleetMessageFault):
    """Command anti-replay counter has been used before. Use included session info to update session and try again"""

    message = "Command anti-replay counter has been used before. Use included session info to update session and try again"
    code = 6


class TeslaFleetMessageFaultInsufficientPrivileges(TeslaFleetMessageFault):
    """User is not authorized to execute command. This can be because of the role or because of vehicle state"""

    message = "User is not authorized to execute command. This can be because of the role or because of vehicle state"
    code = 7


class TeslaFleetMessageFaultInvalidDomains(TeslaFleetMessageFault):
    """Command was malformed or addressed to an unrecognized vehicle system. May indicate client error or older vehicle firmware"""

    message = "Command was malformed or addressed to an unrecognized vehicle system. May indicate client error or older vehicle firmware"
    code = 8


class TeslaFleetMessageFaultInvalidCommand(TeslaFleetMessageFault):
    """Unrecognized command. May indicate client error or unsupported vehicle firmware"""

    message = "Unrecognized command. May indicate client error or unsupported vehicle firmware"
    code = 9


class TeslaFleetMessageFaultDecoding(TeslaFleetMessageFault):
    """Could not parse command. Indicates client error"""

    message = "Could not parse command. Indicates client error"
    code = 10


class TeslaFleetMessageFaultInternal(TeslaFleetMessageFault):
    """Internal vehicle error. Try again. Most commonly encountered when the vehicle has not finished booting"""

    message = "Internal vehicle error. Try again. Most commonly encountered when the vehicle has not finished booting"
    code = 11


class TeslaFleetMessageFaultWrongPersonalization(TeslaFleetMessageFault):
    """Command sent to wrong VIN"""

    message = "Command sent to wrong VIN"
    code = 12


class TeslaFleetMessageFaultBadParameter(TeslaFleetMessageFault):
    """Command was malformed or used a deprecated parameter"""

    message = "Command was malformed or used a deprecated parameter"
    code = 13


class TeslaFleetMessageFaultKeychainIsFull(TeslaFleetMessageFault):
    """Vehicle's keychain is full. You must delete a key before you can add another"""

    message = (
        "Vehicle's keychain is full. You must delete a key before you can add another"
    )
    code = 14


class TeslaFleetMessageFaultIncorrectEpoch(TeslaFleetMessageFault):
    """Session ID mismatch. Use included session info to update session and try again"""

    message = (
        "Session ID mismatch. Use included session info to update session and try again"
    )
    code = 15


class TeslaFleetMessageFaultIVIncorrectLength(TeslaFleetMessageFault):
    """Initialization Value length is incorrect (AES-GCM must use 12-byte IVs). Indicates a client programming error"""

    message = "Initialization Value length is incorrect (AES-GCM must use 12-byte IVs). Indicates a client programming error"
    code = 16


class TeslaFleetMessageFaultTimeExpired(TeslaFleetMessageFault):
    """Command expired. Use included session info to determine if clocks have desynchronized and try again"""

    message = "Command expired. Use included session info to determine if clocks have desynchronized and try again"
    code = 17


class TeslaFleetMessageFaultNotProvisionedWithIdentity(TeslaFleetMessageFault):
    """Vehicle has not been provisioned with a VIN and may require service"""

    message = "Vehicle has not been provisioned with a VIN and may require service"
    code = 18


class TeslaFleetMessageFaultCouldNotHashMetadata(TeslaFleetMessageFault):
    """Internal vehicle error"""

    message = "Internal vehicle error"
    code = 19


class TeslaFleetMessageFaultTimeToLiveTooLong(TeslaFleetMessageFault):
    """Vehicle rejected command because its expiration time was too far in the future. This is a security precaution"""

    message = "Vehicle rejected command because its expiration time was too far in the future. This is a security precaution"
    code = 20


class TeslaFleetMessageFaultRemoteAccessDisabled(TeslaFleetMessageFault):
    """The vehicle owner has disabled Mobile access"""

    message = "The vehicle owner has disabled Mobile access"
    code = 21


class TeslaFleetMessageFaultRemoteServiceAccessDisabled(TeslaFleetMessageFault):
    """The command was authorized with a Service key, but the vehicle has not been configured to permit remote service commands"""

    message = "The command was authorized with a Service key, but the vehicle has not been configured to permit remote service commands"
    code = 22


class TeslaFleetMessageFaultCommandRequiresAccountCredentials(TeslaFleetMessageFault):
    """The command requires proof of Tesla account credentials but was not sent over a channel that provides this proof. Resend the command using Fleet API"""

    message = "The command requires proof of Tesla account credentials but was not sent over a channel that provides this proof. Resend the command using Fleet API"
    code = 23


class TeslaFleetMessageFaultFieldExceedsMTU(TeslaFleetMessageFault):
    """Client sent a request with a field that exceeds MTU"""

    message = "Client sent a request with a field that exceeds MTU"
    code = 24


class TeslaFleetMessageFaultResponseSizeExceedsMTU(TeslaFleetMessageFault):
    """Client's request was received, but response size exceeded MTU"""

    message = "Client's request was received, but response size exceeded MTU"
    code = 25

class TeslaFleetMessageFaultRepeatedCounter(TeslaFleetMessageFault):
    """The vehicle has seen this counter value before. Reset the counter and try again"""

    message = "The vehicle has seen this counter value before. Reset the counter and try again"
    code = 26


class TeslaFleetMessageFaultInvalidKeyHandle(TeslaFleetMessageFault):
    """The key handle is not valid. The key may have been revoked or expired"""

    message = "The key handle is not valid. The key may have been revoked or expired"
    code = 27


class TeslaFleetMessageFaultRequiresResponseEncryption(TeslaFleetMessageFault):
    """The response requires encryption but encryption was not requested"""

    message = "The response requires encryption but encryption was not requested"
    code = 28


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
    TeslaFleetMessageFaultFieldExceedsMTU,
    TeslaFleetMessageFaultResponseSizeExceedsMTU,
    TeslaFleetMessageFaultRepeatedCounter,
    TeslaFleetMessageFaultInvalidKeyHandle,
    TeslaFleetMessageFaultRequiresResponseEncryption,
]

class SignedMessageInformationFault(TeslaFleetError):
    """Vehicle has responded with an error when sending a signed command"""

    message = "Vehicle has responded with an error when sending a signed command"


class SignedMessageInformationFaultUnknown(SignedMessageInformationFault):
    """Unknown fault on signed command."""

    message = "Unknown fault on signed command."
    code = 1


class SignedMessageInformationFaultNotOnWhitelist(SignedMessageInformationFault):
    """Not on whitelist fault on signed command."""

    message = "Not on whitelist fault on signed command."
    code = 2


class SignedMessageInformationFaultIVSmallerThanExpected(SignedMessageInformationFault):
    """IV smaller than expected fault on signed command."""

    message = "IV smaller than expected fault on signed command."
    code = 3


class SignedMessageInformationFaultInvalidToken(SignedMessageInformationFault):
    """Invalid token fault on signed command."""

    message = "Invalid token fault on signed command."
    code = 4


class SignedMessageInformationFaultTokenAndCounterInvalid(SignedMessageInformationFault):
    """Token and counter invalid fault on signed command."""

    message = "Token and counter invalid fault on signed command."
    code = 5


class SignedMessageInformationFaultAESDecryptAuth(SignedMessageInformationFault):
    """AES decrypt auth fault on signed command."""

    message = "AES decrypt auth fault on signed command."
    code = 6


class SignedMessageInformationFaultECDSAInput(SignedMessageInformationFault):
    """ECDSA input fault on signed command."""

    message = "ECDSA input fault on signed command."
    code = 7


class SignedMessageInformationFaultECDSASignature(SignedMessageInformationFault):
    """ECDSA signature fault on signed command."""

    message = "ECDSA signature fault on signed command."
    code = 8


class SignedMessageInformationFaultLocalEntityStart(SignedMessageInformationFault):
    """Local entity start fault on signed command."""

    message = "Local entity start fault on signed command."
    code = 9


class SignedMessageInformationFaultLocalEntityResult(SignedMessageInformationFault):
    """Local entity result fault on signed command."""

    message = "Local entity result fault on signed command."
    code = 10


class SignedMessageInformationFaultCouldNotRetrieveKey(SignedMessageInformationFault):
    """Could not retrieve key fault on signed command."""

    message = "Could not retrieve key fault on signed command."
    code = 11


class SignedMessageInformationFaultCouldNotRetrieveToken(SignedMessageInformationFault):
    """Could not retrieve token fault on signed command."""

    message = "Could not retrieve token fault on signed command."
    code = 12


class SignedMessageInformationFaultSignatureTooShort(SignedMessageInformationFault):
    """Signature too short fault on signed command."""

    message = "Signature too short fault on signed command."
    code = 13


class SignedMessageInformationFaultTokenIsIncorrectLength(SignedMessageInformationFault):
    """Token is incorrect length fault on signed command."""

    message = "Token is incorrect length fault on signed command."
    code = 14


class SignedMessageInformationFaultIncorrectEpoch(SignedMessageInformationFault):
    """Incorrect epoch fault on signed command."""

    message = "Incorrect epoch fault on signed command."
    code = 15


class SignedMessageInformationFaultIVIncorrectLength(SignedMessageInformationFault):
    """IV incorrect length fault on signed command."""

    message = "IV incorrect length fault on signed command."
    code = 16


class SignedMessageInformationFaultTimeExpired(SignedMessageInformationFault):
    """Time expired fault on signed command."""

    message = "Time expired fault on signed command."
    code = 17


class SignedMessageInformationFaultNotProvisionedWithIdentity(
    SignedMessageInformationFault
):
    """Not provisioned with identity fault on signed command."""

    message = "Not provisioned with identity fault on signed command."
    code = 18


class SignedMessageInformationFaultCouldNotHashMetadata(SignedMessageInformationFault):
    """Could not hash metadata fault on signed command."""

    message = "Could not hash metadata fault on signed command."
    code = 19


SIGNED_MESSAGE_INFORMATION_FAULTS = [
    None,
    SignedMessageInformationFaultUnknown,
    SignedMessageInformationFaultNotOnWhitelist,
    SignedMessageInformationFaultIVSmallerThanExpected,
    SignedMessageInformationFaultInvalidToken,
    SignedMessageInformationFaultTokenAndCounterInvalid,
    SignedMessageInformationFaultAESDecryptAuth,
    SignedMessageInformationFaultECDSAInput,
    SignedMessageInformationFaultECDSASignature,
    SignedMessageInformationFaultLocalEntityStart,
    SignedMessageInformationFaultLocalEntityResult,
    SignedMessageInformationFaultCouldNotRetrieveKey,
    SignedMessageInformationFaultCouldNotRetrieveToken,
    SignedMessageInformationFaultSignatureTooShort,
    SignedMessageInformationFaultTokenIsIncorrectLength,
    SignedMessageInformationFaultIncorrectEpoch,
    SignedMessageInformationFaultIVIncorrectLength,
    SignedMessageInformationFaultTimeExpired,
    SignedMessageInformationFaultNotProvisionedWithIdentity,
    SignedMessageInformationFaultCouldNotHashMetadata,
]

class WhitelistOperationStatus(TeslaFleetError):
    message = "Whitelist operation failed"

class WhitelistOperationUndocumentedError(WhitelistOperationStatus):
    message = "Undocumented whitelist operation error"
    code = 1

class WhitelistOperationNoPermissionToRemoveOneself(WhitelistOperationStatus):
    message = "No permission to remove oneself from whitelist"
    code = 2

class WhitelistOperationKeyfobSlotsFull(WhitelistOperationStatus):
    message = "Keyfob slots are full"
    code = 3

class WhitelistOperationWhitelistFull(WhitelistOperationStatus):
    message = "Whitelist is full"
    code = 4

class WhitelistOperationNoPermissionToAdd(WhitelistOperationStatus):
    message = "No permission to add to whitelist"
    code = 5

class WhitelistOperationInvalidPublicKey(WhitelistOperationStatus):
    message = "Invalid public key"
    code = 6

class WhitelistOperationNoPermissionToRemove(WhitelistOperationStatus):
    message = "No permission to remove from whitelist"
    code = 7

class WhitelistOperationNoPermissionToChangePermissions(WhitelistOperationStatus):
    message = "No permission to change permissions"
    code = 8

class WhitelistOperationAttemptingToElevateOthersAboveOneself(WhitelistOperationStatus):
    message = "Attempting to elevate others above oneself"
    code = 9

class WhitelistOperationAttemptingToDemoteSuperiorToOneself(WhitelistOperationStatus):
    message = "Attempting to demote superior to oneself"
    code = 10

class WhitelistOperationAttemptingToRemoveOwnPermissions(WhitelistOperationStatus):
    message = "Attempting to remove own permissions"
    code = 11

class WhitelistOperationPublicKeyNotOnWhitelist(WhitelistOperationStatus):
    message = "Public key not on whitelist"
    code = 12

class WhitelistOperationAttemptingToAddExistingKey(WhitelistOperationStatus):
    message = "Attempting to add key that is already on the whitelist"
    code = 13

class WhitelistOperationNotAllowedToAddUnlessOnReader(WhitelistOperationStatus):
    message = "Not allowed to add unless on reader"
    code = 14

class WhitelistOperationFMModifyingOutsideOfFMode(WhitelistOperationStatus):
    message = "FM modifying outside of F mode"
    code = 15

class WhitelistOperationFMAttemptingToAddPermanentKey(WhitelistOperationStatus):
    message = "FM attempting to add permanent key"
    code = 16

class WhitelistOperationFMAttemptingToRemovePermanentKey(WhitelistOperationStatus):
    message = "FM attempting to remove permanent key"
    code = 17

class WhitelistOperationKeychainWhileFSFull(WhitelistOperationStatus):
    message = "Keychain while FS full"
    code = 18

class WhitelistOperationAttemptingToAddKeyWithoutRole(WhitelistOperationStatus):
    message = "Attempting to add key without role"
    code = 19

class WhitelistOperationAttemptingToAddKeyWithServiceRole(WhitelistOperationStatus):
    message = "Attempting to add key with service role"
    code = 20

class WhitelistOperationNonServiceKeyAttemptingToAddServiceTech(WhitelistOperationStatus):
    message = "Non-service key attempting to add service tech"
    code = 21

class WhitelistOperationServiceKeyAttemptingToAddServiceTechOutsideServiceMode(WhitelistOperationStatus):
    message = "Service key attempting to add service tech outside service mode"
    code = 22

# No idea what 23 & 24 are

class WhitelistOperationServiceAuthorizationRequestTimedOut(WhitelistOperationStatus):
    # This is observed but not documented
    message = "Authorization request timed out"
    code = 25


WHITELIST_OPERATION_STATUS = [
    None,
    WhitelistOperationUndocumentedError,
    WhitelistOperationNoPermissionToRemoveOneself,
    WhitelistOperationKeyfobSlotsFull,
    WhitelistOperationWhitelistFull,
    WhitelistOperationNoPermissionToAdd,
    WhitelistOperationInvalidPublicKey,
    WhitelistOperationNoPermissionToRemove,
    WhitelistOperationNoPermissionToChangePermissions,
    WhitelistOperationAttemptingToElevateOthersAboveOneself,
    WhitelistOperationAttemptingToDemoteSuperiorToOneself,
    WhitelistOperationAttemptingToRemoveOwnPermissions,
    WhitelistOperationPublicKeyNotOnWhitelist,
    WhitelistOperationAttemptingToAddExistingKey,
    WhitelistOperationNotAllowedToAddUnlessOnReader,
    WhitelistOperationFMModifyingOutsideOfFMode,
    WhitelistOperationFMAttemptingToAddPermanentKey,
    WhitelistOperationFMAttemptingToRemovePermanentKey,
    WhitelistOperationKeychainWhileFSFull,
    WhitelistOperationAttemptingToAddKeyWithoutRole,
    WhitelistOperationAttemptingToAddKeyWithServiceRole,
    WhitelistOperationNonServiceKeyAttemptingToAddServiceTech,
    WhitelistOperationServiceKeyAttemptingToAddServiceTechOutsideServiceMode,
    WhitelistOperationStatus,
    WhitelistOperationStatus,
    WhitelistOperationServiceAuthorizationRequestTimedOut
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
        for exception in [
            SubscriptionRequired,
            VehicleSubscriptionRequired,
            InsufficientCredits,
        ]:
            if error == exception.key:
                raise exception(data)
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

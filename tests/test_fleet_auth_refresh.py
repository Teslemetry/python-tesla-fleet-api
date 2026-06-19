"""Unit tests for TeslaFleetApi auth refresh retry behavior."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import (
    InvalidRegion,
    InvalidToken,
    LibraryError,
    LoginRequired,
    OAuthExpired,
)
from tesla_fleet_api.tesla.fleet import TeslaFleetApi


class TestTeslaFleetApi(TeslaFleetApi):
    """Test helper exposing a public wrapper for the protected request method."""

    async def request(self, method: Method, path: str) -> dict[str, object]:
        """Call the protected request path under test."""

        return await self._request(method, path)


class TeslaFleetApiAuthRefreshTests(IsolatedAsyncioTestCase):
    """Verify auth refresh retry behavior in TeslaFleetApi."""

    def create_api(
        self, force_token_refresh: AsyncMock | None = None
    ) -> TestTeslaFleetApi:
        """Create an API instance with a mocked session."""

        return TestTeslaFleetApi(
            session=MagicMock(),
            access_token="access-token",
            force_token_refresh=force_token_refresh,
            server="https://fleet.example.com",
        )

    async def test_constructor_is_backward_compatible(self) -> None:
        """The new refresh callback remains optional."""

        api = TeslaFleetApi(
            session=MagicMock(),
            access_token="access-token",
            server="https://fleet.example.com",
        )

        self.assertIsNone(api._force_token_refresh)  # pyright: ignore[reportPrivateUsage]

    async def test_request_retries_once_after_auth_failure_then_succeeds(self) -> None:
        """A recoverable auth failure should refresh and retry once."""

        for error_type in (InvalidToken, OAuthExpired, LoginRequired):
            with self.subTest(error_type=error_type.__name__):
                refresh = AsyncMock()
                api = self.create_api(force_token_refresh=refresh)
                request_once = AsyncMock(side_effect=[error_type(), {"response": "ok"}])
                api._request_once = request_once  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage]

                response = await api.request(Method.GET, "api/1/products")

                self.assertEqual(response, {"response": "ok"})
                self.assertEqual(request_once.await_count, 2)
                refresh.assert_awaited_once()

    async def test_request_raises_auth_error_when_retry_also_auth_fails(self) -> None:
        """A second auth failure should stop retrying and bubble up."""

        for error_type in (InvalidToken, OAuthExpired, LoginRequired):
            with self.subTest(error_type=error_type.__name__):
                refresh = AsyncMock()
                api = self.create_api(force_token_refresh=refresh)
                request_once = AsyncMock(side_effect=[error_type(), LoginRequired()])
                api._request_once = request_once  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage]

                with self.assertRaises(LoginRequired):
                    await api.request(Method.GET, "api/1/products")

                self.assertEqual(request_once.await_count, 2)
                refresh.assert_awaited_once()

    async def test_request_raises_auth_error_when_refresh_requires_reauth(self) -> None:
        """Refresh failures that require reauth should surface as LoginRequired."""

        for error_type in (InvalidToken, OAuthExpired, LoginRequired):
            with self.subTest(error_type=error_type.__name__):
                refresh = AsyncMock(side_effect=error_type())
                api = self.create_api(force_token_refresh=refresh)
                request_once = AsyncMock(side_effect=[InvalidToken()])
                api._request_once = request_once  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage]

                with self.assertRaises(LoginRequired):
                    await api.request(Method.GET, "api/1/products")

                self.assertEqual(request_once.await_count, 1)
                refresh.assert_awaited_once()

    async def test_request_raises_library_error_when_refresh_fails_transiently(self) -> None:
        """Transient callback failures should not be treated as success."""

        refresh = AsyncMock(side_effect=LibraryError("temporary refresh failure"))
        api = self.create_api(force_token_refresh=refresh)
        request_once = AsyncMock(side_effect=[InvalidToken()])
        api._request_once = request_once  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage]

        with self.assertRaises(LibraryError):
            await api.request(Method.GET, "api/1/products")

        self.assertEqual(request_once.await_count, 1)
        refresh.assert_awaited_once()

    async def test_request_re_raises_auth_error_without_refresh_callback(self) -> None:
        """Existing callers without a callback should see the original auth error."""

        api = self.create_api()
        request_once = AsyncMock(side_effect=[OAuthExpired()])
        api._request_once = request_once  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage]

        with self.assertRaises(OAuthExpired):
            await api.request(Method.GET, "api/1/products")

        self.assertEqual(request_once.await_count, 1)

    async def test_request_preserves_non_auth_tesla_error_from_refresh_callback(self) -> None:
        """Non-auth TeslaFleetError refresh failures should propagate unchanged."""

        refresh = AsyncMock(side_effect=InvalidRegion())
        api = self.create_api(force_token_refresh=refresh)
        request_once = AsyncMock(side_effect=[InvalidToken()])
        api._request_once = request_once  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage]

        with self.assertRaises(InvalidRegion):
            await api.request(Method.GET, "api/1/products")

        self.assertEqual(request_once.await_count, 1)
        refresh.assert_awaited_once()

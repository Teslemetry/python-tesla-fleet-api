# OSS Scanner build (https://github.com/anthropics/oss-scanner). The network is
# available only while this image builds; the scan and the tests run offline,
# so everything pytest needs is installed here.
FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.12.0 /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/src/.venv \
    PATH=/src/.venv/bin:$PATH

# scanner contract: the checkout lives inside the image, at /src
COPY . /src
WORKDIR /src

# Install the library and the dev group (pytest, pyright, ruff) from uv.lock.
RUN uv sync --locked

# Offline from here: `pytest` and `uv run --offline pytest` use the installed
# environment. Run the suite once so the build log shows it works, but do not
# fail the image on a test failure.
ENV UV_OFFLINE=1
RUN pytest -q || echo "WARNING: pytest reported failures"

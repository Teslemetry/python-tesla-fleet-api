---
name: release
description: Use when cutting a tesla-fleet-api release to PyPI - version bump, uv lock, vX.Y.Z tag and watching release.yml.
---

# Release tesla-fleet-api

There is no release automation. `.github/workflows/release.yml` runs on a
pushed `v*.*.*` tag: it reruns the full gate, publishes to PyPI by OIDC trusted
publishing in the `pypi` environment, then creates the GitHub Release.

The `pypi` environment has **no required reviewers**. Merging the version-bump
PR is the publish approval, so get that approval before you push the tag.

## Steps

1. Pick the new `X.Y.Z` (semver against the commits since the last `v*` tag).
2. Set the same version in both places:
   - `version` in `pyproject.toml`
   - `__version__` in `tesla_fleet_api/__init__.py`
3. Run `uv lock`. CI and the release gate run `uv sync --locked`, so a bump
   without the `uv.lock` change fails before merge.
4. Run the gate locally (the same steps as `release.yml`):
   ```bash
   uv sync --locked
   uv run ruff check tesla_fleet_api tests
   uv run pyright tesla_fleet_api
   uv run pytest tests -q
   uv build && uvx twine check dist/*
   ```
5. Commit only those three files as `Bump version to X.Y.Z`, open the PR and
   get it merged to `main`.
6. Tag the merge commit on `main` and push the tag:
   ```bash
   git fetch origin main
   git tag vX.Y.Z origin/main
   git push origin vX.Y.Z
   ```
   The tag must match the version in `pyproject.toml` exactly.
7. Watch the `Release gate & publish` run until the `gate`,
   `publish-to-pypi` and `github-release` jobs all pass. Then confirm the new
   version on https://pypi.org/p/tesla_fleet_api.

## Do not

- Do not convert `release.yml` to a reusable `workflow_call` workflow or rename
  it or the `pypi` environment. The PyPI trusted publisher is bound to workflow
  `release.yml` + environment `pypi`; a caller's signing identity would not
  match.
- Do not re-push a moved tag for a version PyPI already has. PyPI rejects a
  re-upload of the same version; bump to a new patch version instead.

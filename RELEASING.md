# Releasing

python-dotenv follows [Semantic Versioning](https://semver.org/). Bug fixes are
patch releases, backward-compatible features are minor releases, and breaking
changes are major releases.

Publishing is automated: creating a GitHub **Release** triggers
[`.github/workflows/release.yml`](.github/workflows/release.yml), which builds
the package, publishes it to PyPI via Trusted Publishing (OIDC, no tokens), and
deploys the docs to GitHub Pages. You never run `twine` by hand.

## Prerequisites

- Push access to `main` and permission to create releases.
- A clean local checkout: `git switch main && git pull --ff-only`.
- Dev tools installed: `uv pip install -r requirements.txt && uv pip install -e .`.

## Steps

1. **Write the changelog.** In `CHANGELOG.md`, rename the `## [Unreleased]`
   section to `## [X.Y.Z] - YYYY-MM-DD`, and add a fresh empty `## [Unreleased]`
   above it. Every entry credits the author and links the PR, for example:

   ```
   - Short description of the change by [@handle] in [#123]
   ```

   Add the matching link definitions at the bottom of the file (`[#123]: ...`
   and, for a first-time contributor, `[@handle]: https://github.com/handle`).

   Every version header is a reference link, so also maintain the compare links
   at the bottom: point `[Unreleased]` at the new tag and add the new version:

   ```
   [Unreleased]: https://github.com/theskumar/python-dotenv/compare/vX.Y.Z...HEAD
   [X.Y.Z]: https://github.com/theskumar/python-dotenv/compare/vPREV...vX.Y.Z
   ```

2. **Commit the notes** on `main`:

   ```
   git commit -am "docs: add X.Y.Z release notes"
   ```

3. **Bump the version.** This runs the checks, updates `src/dotenv/version.py`
   and `.bumpversion.cfg`, commits `Bump version: ... → X.Y.Z`, and tags
   `vX.Y.Z`:

   ```
   make release            # patch  (default)
   make release part=minor
   make release part=major
   ```

4. **Push** the release commit and tag:

   ```
   git push origin main --follow-tags
   ```

5. **Publish.** Create the GitHub Release from the new tag. This starts the
   PyPI upload and docs deploy:

   ```
   VERSION=$(uv run python -c "import dotenv.version as v; print(v.__version__)")
   gh release create "v$VERSION" --title "v$VERSION" \
     --notes "$(awk "/^## \\[$VERSION\\]/{f=1;next} /^## \\[/{f=0} f" CHANGELOG.md)"
   ```

6. **Verify.** Watch the workflow (`gh run watch`), then confirm the new version
   on [PyPI](https://pypi.org/project/python-dotenv/) and that the
   [docs](https://saurabh-kumar.com/python-dotenv/) rebuilt.

## Rollback

The version bump is a normal commit plus tag. Before you push, undo with
`git reset --hard HEAD~1 && git tag -d vX.Y.Z`. After a bad publish, yank the
release on PyPI and ship a follow-up patch; PyPI versions cannot be reused.

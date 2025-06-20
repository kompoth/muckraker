# Developer notes

## Version bumping

Currently project version is tracked in two locations: `pyproject.toml` and `muckraker/__init__.py`.
Those two MUST be synchronised.

## Linting

Currently project uses Ruff to perform static checks. To make sure that your commits will be accepted:

- Install `ruff` and `pre-commit` tools.
- Run `pre-commit install` to install our preconfigured hook in your local repo.
- Run `pre-commit run --all-files` to check the whole repo.

Now each time you commit your changes will be checked against the Ruff rules.

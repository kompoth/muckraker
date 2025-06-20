FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

# Muckraker dependencies
RUN apt-get update && apt-get install -y libpango-1.0-0 libpangoft2-1.0-0

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "uvicorn", "muckraker.main:app", "--host", "0.0.0.0", "--port", "80"]

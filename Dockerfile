FROM python:3.12-slim AS builder

RUN apt-get update 
RUN apt-get install -y libpango-1.0-0 libpangoft2-1.0-0

WORKDIR /build
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /build/


FROM builder AS runner

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry install --no-interaction --no-ansi --without dev

COPY ./muckraker /app/muckraker

CMD ["poetry", "run", "uvicorn", "muckraker.main:app", "--host", "0.0.0.0", "--port", "80"]

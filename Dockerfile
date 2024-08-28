FROM python:3.12-slim AS builder

WORKDIR /build

COPY ./pyproject.toml ./poetry.lock /build

RUN pip install poetry==1.8.3
RUN poetry export --without-hashes --only=main --format=requirements.txt > requirements.txt


FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update 
RUN apt-get install -y libpango-1.0-0 libpangoft2-1.0-0

COPY --from=builder /build/requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./muckraker /app/muckraker

CMD ["uvicorn", "muckraker.main:app", "--host", "0.0.0.0", "--port", "80"]

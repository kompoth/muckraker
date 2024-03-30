FROM python:3.11-slim

WORKDIR /app

RUN apt-get update 
RUN apt-get install -y libpango-1.0-0 libpangoft2-1.0-0

COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./muckraker /app/muckraker

CMD ["uvicorn", "muckraker.main:app", "--host", "0.0.0.0", "--port", "80"]

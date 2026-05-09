FROM python:3.12-slim

RUN apt-get update && apt-get install  -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=secret,id=netrc,target=/root/.netrc \
    cat /root/.netrc

COPY . .

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "src.main:app", "fastapi" ]

CMD [ "--host", "0.0.0.0", "--port", "8000", "--reload" ]
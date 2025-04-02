FROM python:3.13-slim AS python-base

ENV PATH="/root/.local/bin/:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

RUN mkdir /app
WORKDIR /app
COPY uv.lock pyproject.toml ./

RUN uv sync --frozen

COPY . /app/
WORKDIR /app
CMD ["uv", "run", "-m", "jumpradius_updater"]

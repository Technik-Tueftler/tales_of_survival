FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

ENV WORKING_DIR /user/app/tales_of_survival
WORKDIR $WORKING_DIR

COPY files/ ./files/
COPY src/ ./src/
COPY main.py default.env ./
COPY pyproject.toml uv.lock ./

RUN uv sync --locked

CMD ["uv", "run", "main.py"]
FROM python:3.10


WORKDIR /usr/app

RUN pip install poetry

COPY poetry.lock pyproject.toml /usr/app/
COPY src /usr/app/
COPY config.toml /usr/app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi


CMD ["poetry", "run", "discoboltalka"]

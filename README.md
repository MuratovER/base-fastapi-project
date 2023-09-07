# Base FastAPI project

Base FastAPI Project

![alt text](https://img.shields.io/badge/python-3.11.2-orange)

## Technology stack

1. FastAPI
2. SQLAlchemy + Alembic
3. PostgreSQL
4. Docker, docker compose

## Run

#### Run local environment stack
```shell
docker-compose up -d --build
```

#### Export local envs
```shell
cat .env.example > .env.local

export $(grep -v "^#" .env.local | xargs)
```

#### Install poetry
```shell
pip install poetry
```

#### Install the project dependencies
```shell
cd src && poetry install
```

#### Spawn a shell within the virtual environment
```shell
poetry shell
```

#### Run the server
```shell
uvicorn main:app --reload
```

## Migrations

#### Generate new migration
```shell
alembic revision --autogenerate -m "Migration Name"
```

#### Run migrations
```shell
alembic upgrade head
```

#### Downgrade last migration
```shell
alembic downgrade -1
```

## Development

#### Make lint, tests
```shell
cd src && make lint
cd src && make test
```

#### Branch naming
```
feature/{feature-name-in-kebab-case}  # branch with new functionality, code
fix/{fix-name-in-kebab-case}  # branch with fix changes
```

#### Commit messages
```
+ {message}  # adding new functionality, code
- {message}  # removing functionality, code
! {message}  # changing functionality, code
```

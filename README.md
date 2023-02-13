# Flicks
A django project, a social media for films.

Films are fetching from https://imdb-api.com/.

## Running tests
First install dependencies:
```shell
pip3 install -r requirements.txt
```
Then run tests via `pytest`:
```shell
pytest
```

## Setup
First clone the project:
```shell
git clone git@github.com:aminiun/traefik-validator.git
```
#### With django server:
1- Make a venv:
```shell
python3 -m venv venv
source venv/bin/activate
```
2- Run server:
```shell
python3 manage.py runserver <DESIRED_PORT>
```

#### With Docker:
```shell
docker-compose up -d
```

## Library management system on Django and Vue.js

[![CI/CD](https://github.com/peacefulseeker/django-libraryms/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/peacefulseeker/django-libraryms/actions/workflows/main.yml)
[![pytest-cov](./coverage.svg)](https://github.com/peacefulseeker/django-libraryms/actions/workflows/main.yml)

### MVP Goal & Requirements
Check out the [MVP Goal & Requirements](../../wiki/MVP-Goal-&-Requirements)

## Demo
#### Member orders a book
![Member orders a book](demo/demo-member-ui.gif)
#### Librarian processes the order
![Librarian processes the order](demo/demo-librarian-admin.gif)

## Project setup

#### Tool versions
Check [tool-versions](./.tool-versions)

#### Clone locally with frontend submodule(separate repo)
```shell
git clone --recurse-submodules git@github.com:peacefulseeker/django-libraryms.git ./local-project-dir

cd ./local-project-dir
cp src/core/.env.ci src/core/.env
```
Set `DEBUG=true` and other env variables such as `DATABASE_URL` in `src/core/.env`
to match your local environment needs.


#### Build backend
```shell
# Installs poetry, collects static assets, runs migrations
./scripts/build-backend.sh

# create superuser
poetry run python src/manage.py createsuperuser

# build frontend, in case you want to see working UI when visiting homepage
make build_frontend
```

#### Run server in development mode
```shell
make server
```

#### Run server in production mode
```shell
# builds frontend assets & collects static
make build_static
# runs gunicorn server against localhost:7070 in non-debug mode
make prodserver
```

### Further plans
Check out the [TODO](../../wiki/TODO)


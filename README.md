## Library management system on Django and Vue.js

### MVP Goal & Requirements
Check out the [MVP Goal & Requirements](../../wiki/MVP-Goal-&-Requirements)

## Project setup

#### Tool versions
Check [tool-versions](./.tool-versions)

#### Clone locally with frontend submodule(separate repo)
```shell
git clone --recurse-submodules git@github.com:peacefulseeker/django-libraryms.git ./local-project-dir

cd ./local-project-dir
cp src/core/.env.ci src/core/.env
```

Add extra environment variables to copied `src/core/.env`.
ADMIN_* ones needed for creating the superuser while executing
backend build script locally.

```shell
DEBUG=true
ADMIN_USERNAME=admin # change to whatever you like
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=admin
```

```shell
# install poetry, collects static, runs migrations, creates superuser(admin env vars required)
./scripts/build-backend.sh
```

#### Run server in development mode
```shell
make server
# same as
make s
# aliased to
poetry run python src/manage.py runserver 7070
```

#### Simulate production server
```shell
# builds both backend and frontend
./scripts/build.sh

# runs gunicorn server, serving frontend static assets(check aliases in Makefile)
make prod
```

### Further plans
Check out the [TODO](../../wiki/TODO)


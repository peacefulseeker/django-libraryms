## Poetry
```python
# is used to install Python CLI applications globally while still isolating them in virtual environments
pipx install poetry
# ~/.local/pipx/venvs/poetry

# enters local venv automatically
poetry shell

# gets info about current virtual environment
# would not need to create venv at all, but needed for vscode
poetry env info

# deleting the in-project environment seems only possible via command below
# or manually deleting the .venv
# https://github.com/python-poetry/poetry/issues/2124
poetry env remove --all

poetry config --list
# https://python-poetry.org/docs/configuration/#virtualenvsin-project
# virtualenvs.in-project = true is responsible for creating .venv within project root(needed for vscode)

petry add --group dev # add to dev deps
poetry install --no-dev # skip installing dev deps

```


## Dependencies
Caret requirements allow SemVer compatible updates to a specified version.
An update is allowed if the new version number does not modify the
left-most non-zero digit in the major, minor, patch grouping
```shell
python = "^3.11" # >=3.11.0 <4.0.0

Tilde requirements specify a minimal version with some ability to update
python = "~3.11" # >=3.11.0 <3.12
```


## Django
```python
# without password given, create_user will still save the user
# with ability to add password later
# https://stackoverflow.com/a/62579906
l = Librarian.objects.create_user(username="librarian")
m = Member.objects.create_user(username="member")
l.has_usable_password() # False

```


```python
# get installled app models
from django.apps import apps
models = apps.get_models()
```


### Can register same models leveraging proxy models
```python
class OrderProxy(Order):
    class Meta:
        proxy = True
        verbose_name = "proxied order"

admin.site.register(Order, ModelAdmin)
admin.site.register(OrderProxy, ModelAdmin)
```

### Unique fields don't need db_index
https://docs.djangoproject.com/en/5.0/ref/models/fields/#unique
Note that when unique is True, you don’t need to specify db_index,
because unique implies the creation of an index.

```shell
# Prints the SQL statements that would be executed for the flush command.
src/manage.py sqlflush
# Removes all data from the database and re-executes any post-synchronization handlers
src/manage.py flush
```
### Data dumpa & load
``` shell
src/manage.py dumpdata books users > db.json
docker-compose cp db.json web:/app
src/manage.py loaddata db.json
```

### Lint

```shell
# would report conflicts + potentially formatted files
poetry run ruff format --check src/core/conf/installed_apps.py
# would report potential rule violations
poetry run ruff check src/core/conf/installed_apps.py

# fmt: off
this_code_won_t_be_formatted =    "foo"
# fmt: on
```


## Python
```python
# and operator works lazily by default, meaning second won't be evaluated if first returns False
Rule1 and Rule2
# & bitwise operator works eagerly by default, meaning second will be evaluated even if first returns False
Rule1 & Rule2 # now clear why such syntax used in DRF permissions
```
In the first expression, the and operator works lazily, as expected. It evaluates the first function, and since the result is false, it doesn’t evaluate the second function. In the second expression, however, the bitwise AND operator (&) calls both functions eagerly even though the first function returns False. Note that in both cases, the final result is False.



### Relations
# OneToOne
When creating associated models outside, need to remember to save both of the models
```python
Reservation(member=self.member, book=self.book).save()
self.book.save()  # without that one, reservation relation won't be created on book instance
```

# Disable backward relation
Tthis will ensure that the User model won’t have a backwards relation to Order
```python
class Order
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="+",
    )
```


### Pytest
```shell
# it's a built-in pytest fixture and it could be used to dynamically access test data during execution of the test
request
# https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.FixtureRequest.getfixturevalue

def test_book_from_request(request):
    book = request.getfixturevalue("book")

    assert book.id == 1
```


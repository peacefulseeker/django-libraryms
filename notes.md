### Poetry
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
```


### Dependencies
Caret requirements allow SemVer compatible updates to a specified version.
An update is allowed if the new version number does not modify the
left-most non-zero digit in the major, minor, patch grouping
```shell
python = "^3.11" # >=3.11.0 <4.0.0

Tilde requirements specify a minimal version with some ability to update
python = "~3.11" # >=3.11.0 <3.12
```


### Django
```python
# without password given, create_user will still save the user
# with ability to add password later
# https://stackoverflow.com/a/62579906
l = Librarian.objects.create_user(username="librarian")
m = Member.objects.create_user(username="member")
l.has_usable_password() # False

```


```shell
# Prints the SQL statements that would be executed for the flush command.
src/manage.py sqlflush
# Removes all data from the database and re-executes any post-synchronization handlers
src/manage.py flush
```

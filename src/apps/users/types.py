from typing import TypedDict

# fmt: off
UserName = str
Email = str
# https://peps.python.org/pep-0589/#totality
class AuthAttrs(TypedDict, total=False):
    username: UserName | Email
    password: str
# fmt: on

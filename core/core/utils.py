import os
from typing import Optional


DEFAULT_AUTH_TOKEN_PATH = os.path.join(os.getcwd(), "..", "auth_token.secret")


def read_auth_token_file(path: Optional[str] = None) -> str:
    """Returns the value of the auth token stored in the auth_token.secret file located
    in the root dir. of this project.
    """
    if not path:
        path = DEFAULT_AUTH_TOKEN_PATH
    token_file_path = os.path.abspath(path)

    with open(token_file_path, "r") as f:
        return f.readline().strip()



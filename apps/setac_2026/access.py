"""Password verifier for the SETAC presentation; override through the environment."""

from __future__ import annotations

import os

# The plaintext password is not stored in the repository.
DEFAULT_PASSWORD_HASH = "scrypt:32768:8:1$55xXC03c461hfySp$3bfe47d93976f97869ec013ecf5076709529c358f034fd56b942dec26ab0dfe3c3e2039930d007d50f08aa2ef68f24bb28d1ee4ca6c1f8ccfac35a60e07c9b91"


def password_hash():
    return os.environ.get("SETAC_2026_PASSWORD_HASH", DEFAULT_PASSWORD_HASH)

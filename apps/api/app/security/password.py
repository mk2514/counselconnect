"""
Password hashing using Argon2id.

Per project rules (Tech Stack Lock):
- Argon2id is the mandated password hashing algorithm.
- Do not use bcrypt, scrypt, or PBKDF2.
"""

from argon2 import PasswordHasher
from argon2.exceptions import HashingError, VerificationError, VerifyMismatchError

_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MiB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2id. Returns the encoded hash string."""
    return _ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a stored hash.

    Returns True if the password matches, False otherwise.
    Does not raise on mismatch.
    """
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, VerificationError, HashingError):
        return False


def needs_rehash(hashed: str) -> bool:
    """Check if a hash needs to be rehashed due to parameter changes."""
    return _ph.check_needs_rehash(hashed)

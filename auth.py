# ============================================================
# SEVAGAN — Authentication Layer
# ============================================================

import hashlib
import hmac
import secrets
import re

from database import (
    create_user,
    get_user_by_username,
    get_user_by_id,
)


# ------------------------------------------------------------
# Password security
# ------------------------------------------------------------

PBKDF2_ITERATIONS = 210_000


def hash_password(password: str) -> str:
    """
    Create a salted PBKDF2 password hash.
    The original password is never stored.
    """

    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against its stored salted hash.
    """

    try:
        salt_hex, digest_hex = stored_hash.split(":", 1)

        salt = bytes.fromhex(salt_hex)

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )

        return hmac.compare_digest(
            calculated.hex(),
            digest_hex,
        )

    except (ValueError, TypeError):
        return False


# ------------------------------------------------------------
# Username validation
# ------------------------------------------------------------

def validate_username(username: str):
    username = username.strip().lower()

    if not username:
        return False, "Please enter a username."

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."

    if len(username) > 30:
        return False, "Username must be 30 characters or fewer."

    if not re.fullmatch(r"[a-z0-9_]+", username):
        return (
            False,
            "Username can contain only letters, numbers and underscores.",
        )

    return True, ""


# ------------------------------------------------------------
# Password validation
# ------------------------------------------------------------

def validate_password(password: str):
    if not password:
        return False, "Please enter a password."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    if len(password) > 128:
        return False, "Password is too long."

    return True, ""


# ------------------------------------------------------------
# Account creation
# ------------------------------------------------------------

def register_user(
    username,
    password,
    display_name="",
    board="CBSE",
    class_name="",
):
    """
    Create a new student account.

    Returns:
        (success, message, user_id)
    """

    username = username.strip().lower()
    display_name = display_name.strip()
    board = board.strip()
    class_name = class_name.strip()

    valid, message = validate_username(username)

    if not valid:
        return False, message, None

    valid, message = validate_password(password)

    if not valid:
        return False, message, None

    if get_user_by_username(username):
        return (
            False,
            "That username already exists. Please choose another.",
            None,
        )

    password_hash = hash_password(password)

    user_id = create_user(
        username=username,
        password_hash=password_hash,
        display_name=display_name,
        board=board,
        class_name=class_name,
    )

    if user_id is None:
        return (
            False,
            "Unable to create the account. Please try again.",
            None,
        )

    return (
        True,
        "Account created successfully.",
        user_id,
    )


# ------------------------------------------------------------
# Login
# ------------------------------------------------------------

def login_user(username, password):
    """
    Authenticate an existing user.

    Returns:
        (success, message, user)
    """

    username = username.strip().lower()

    if not username or not password:
        return (
            False,
            "Please enter your username and password.",
            None,
        )

    user = get_user_by_username(username)

    if user is None:
        return (
            False,
            "Incorrect username or password.",
            None,
        )

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return (
            False,
            "Incorrect username or password.",
            None,
        )

    return (
        True,
        "Login successful.",
        user,
    )


# ------------------------------------------------------------
# Get currently stored user
# ------------------------------------------------------------

def get_authenticated_user(user_id):
    """
    Retrieve the persistent user record using its database ID.
    """

    if not user_id:
        return None

    return get_user_by_id(user_id)

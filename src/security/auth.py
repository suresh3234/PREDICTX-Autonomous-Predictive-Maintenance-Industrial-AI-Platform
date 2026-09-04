import base64
import hashlib
import hmac
import json
import time
from datetime import timedelta
from typing import Any

# Secret key for JWT signing (configured via env in production)
JWT_SECRET_KEY = "predictx-industrial-ai-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str, salt: str | None = None) -> str:
    """
    PBKDF2-HMAC-SHA256 password hashing.
    """
    if not salt:
        salt = hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()[:16]
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored salt$hash string.
    """
    if "$" not in hashed_password:
        return False
    salt, expected_hash = hashed_password.split("$", 1)
    computed_hash = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return hmac.compare_digest(computed_hash, expected_hash)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data_str: str) -> bytes:
    padding = 4 - (len(data_str) % 4)
    if padding != 4:
        data_str += "=" * padding
    return base64.urlsafe_b64decode(data_str.encode("utf-8"))


def create_access_token(
    subject: str,
    role: str = "VIEWER",
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Creates a cryptographically signed HMAC-SHA256 JWT access token.
    """
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    now = int(time.time())
    expire = now + int((expires_delta or timedelta(minutes=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)).total_seconds())

    payload = {
        "sub": subject,
        "role": role.upper(),
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256
    ).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{signing_input}.{sig_b64}"


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Validates signature and expiration of a JWT access token.
    Raises ValueError if invalid or expired.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Malformed JWT token string.")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}"

    # Verify signature
    expected_sig = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256
    ).digest()
    actual_sig = _base64url_decode(sig_b64)

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Invalid JWT token signature.")

    # Decode and parse payload
    payload_bytes = _base64url_decode(payload_b64)
    payload = json.loads(payload_bytes.decode("utf-8"))

    # Check expiration
    if time.time() > payload.get("exp", 0):
        raise ValueError("JWT token has expired.")

    return payload

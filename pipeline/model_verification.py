"""Model file integrity verification using SHA-256 hashing.

Protects against pickle deserialization attacks by verifying file integrity
before loading. Hash files are generated during training and verified during scoring.
"""

import hashlib
import hmac
import pickle
from pathlib import Path


def load_verified_pickle(model_path: Path, hash_path: Path | None = None) -> dict:
    """Load pickle file with SHA-256 integrity verification.

    Args:
        model_path: Path to the pickle file
        hash_path: Path to the .sha256 hash file (defaults to model_path.with_suffix('.sha256'))

    Returns:
        Deserialized pickle data

    Raises:
        FileNotFoundError: If hash file doesn't exist
        ValueError: If hash verification fails
    """
    if hash_path is None:
        hash_path = model_path.with_suffix(".sha256")

    if not hash_path.exists():
        raise FileNotFoundError(
            f"Hash file not found: {hash_path}\n"
            f"Models must be saved with save_verified_pickle() to generate hash files"
        )

    expected_hash = hash_path.read_text().strip()
    data = model_path.read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()

    if not hmac.compare_digest(actual_hash, expected_hash):
        raise ValueError(
            f"Model integrity check failed: {model_path}\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual_hash}"
        )

    return pickle.loads(data)


def save_verified_pickle(obj: dict, model_path: Path) -> None:
    """Save pickle file with SHA-256 hash for integrity verification.

    Args:
        obj: Object to pickle
        model_path: Path where pickle will be saved

    Side effects:
        Creates model_path.pkl and model_path.sha256
    """
    model_path.parent.mkdir(parents=True, exist_ok=True)

    data = pickle.dumps(obj)
    model_path.write_bytes(data)

    hash_val = hashlib.sha256(data).hexdigest()
    hash_path = model_path.with_suffix(".sha256")
    hash_path.write_text(hash_val)

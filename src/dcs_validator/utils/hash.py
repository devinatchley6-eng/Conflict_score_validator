import hashlib
from pathlib import Path


def sha256_stream(path: str | Path, chunk_size: int = 8192) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()

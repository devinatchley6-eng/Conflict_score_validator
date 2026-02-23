from typing import Any


def compute_persistence(points) -> Any:
    """Wrapper stub for Gudhi persistent homology."""
    try:
        import gudhi  # noqa: F401
    except Exception:
        return {"status": "gudhi-not-available"}
    return {"status": "ok", "n_points": len(points)}

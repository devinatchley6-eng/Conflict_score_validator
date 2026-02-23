import platform


def platform_info() -> dict:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "python": platform.python_version(),
    }

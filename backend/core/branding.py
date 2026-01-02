from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = CORE_DIR / "assets"

DEFAULT_LOGO = ASSETS_DIR / "logo.png"
CUSTOM_LOGO = ASSETS_DIR / "branding" / "logo.png"


def get_logo_path() -> Path:
    """
    Returns custom logo if present, otherwise default logo.
    Works in dev and inside the container.
    """
    if CUSTOM_LOGO.exists():
        return CUSTOM_LOGO
    return DEFAULT_LOGO

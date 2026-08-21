"""Helpers for safely rendering stored image paths and external image URLs."""

from urllib.parse import urlparse


def normalize_static_path(value: object) -> str:
    """Return a relative static path for a local stored image."""
    path = str(value or "").strip()
    if path.startswith("/static/"):
        path = path[len("/static/"):]
    elif path.startswith("static/"):
        path = path[len("static/"):]

    if path and not path.startswith(("uploads/", "images/")):
        path = f"uploads/products/{path}"
    return path


def is_external_image_url(value: object) -> bool:
    """Return True only for absolute HTTP(S) URLs."""
    try:
        parsed = urlparse(str(value or "").strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except (TypeError, ValueError):
        return False


def product_image_src(value: object, static_url_builder) -> str:
    """
    Convert a database thumbnail value into a browser-ready src.

    External URLs remain external. Local filenames and static paths are
    normalized under /static/uploads/products/ (or /static/images/).
    """
    raw = str(value or "").strip()
    if not raw or raw == "None":
        return ""
    if is_external_image_url(raw):
        return raw
    return static_url_builder(filename=normalize_static_path(raw))
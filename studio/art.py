"""Which concept art a character uses: an AI-drawn variant, or the designer's own upload."""
import base64

from .portrait import data_uri, portrait_svg

MAX_UPLOAD_BYTES = 3 * 1024 * 1024


def chosen_art(item):
    """Return (kind, payload) for the character's selected art."""
    art = item["extras"].get("art", {"type": "ai", "variant": 0})
    c = item["versions"][-1]["character"]
    if art.get("type") == "upload":
        return "upload", art
    return "ai", portrait_svg(c, art.get("variant", 0))


def art_uri(item):
    kind, payload = chosen_art(item)
    if kind == "upload":
        return f"data:{payload['mime']};base64,{payload['data']}"
    return data_uri(payload)


def art_bytes(item):
    """Bytes + extension suitable for PDF embedding / download."""
    kind, payload = chosen_art(item)
    if kind == "upload":
        ext = "png" if "png" in payload["mime"] else "jpg"
        return base64.b64decode(payload["data"]), ext
    return payload.encode("utf-8"), "svg"


def upload_payload(file_bytes, mime, filename):
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Image is larger than 3 MB.")
    return {"type": "upload", "mime": mime, "filename": filename,
            "data": base64.b64encode(file_bytes).decode()}

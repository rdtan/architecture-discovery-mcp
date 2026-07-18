import re


def camel_to_words(name: str) -> str:
    words = re.sub(r"([A-Z])", r" \1", name).strip()
    return " ".join(w.capitalize() for w in words.split())


def generate_encoding(prefix: str, index: int) -> str:
    return f"{prefix}-{index:03d}"


def method_to_display_name(method_name: str) -> str:
    words = re.sub(r"([A-Z])", r" \1", method_name).strip().lower()
    return words


def class_to_module_name(class_name: str) -> str:
    name = class_name.replace("Controller", "").replace("Service", "").replace("Repository", "")
    parts = re.findall(r"[A-Z][a-z]*", name)
    return "-".join(p.lower() for p in parts) if parts else name.lower()

"""Normalizacion de nombres de juegos para matching de portadas."""
import re

def normalizar_nombre(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\s*[\(\[].*?[\)\]]", "", s)
    s = re.sub(r"\b(the|a|an|el|la|los|las|de|del|of|and|y)\b", " ", s)
    s = re.sub(r"[^\w\s\-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def nombre_archivo_seguro(nom: str, max_len: int = 80) -> str:
    s = re.sub(r"[^\w\s\-\.]", "", nom.strip())
    s = re.sub(r"\s+", " ", s).strip()
    return (s[:max_len] if s else "portada")

def score_similitud(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.85
    ta = set(a.split())
    tb = set(b.split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0

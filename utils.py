import pandas as pd
from datetime import date
import re

# Reference constants
ANNEE_REF = 2026
DATE_REF = date(ANNEE_REF, 12, 31)

FRANCHISES_ENFANT = [0, 200, 300, 400, 500, 600]
FRANCHISES_ADULTE = [300, 600, 1000, 1500, 2000, 2500]


def norm_str(s):
    """Retourne une chaîne normalisée : vide si manquante, trim, NBSP -> espace, majuscules."""
    if pd.isna(s) or s is None:
        return ""
    text = str(s)
    text = text.strip()
    text = text.replace("\u00A0", " ").replace("\xa0", " ")
    return text.upper()


def normalise_codepostal(x):
    if pd.isna(x) or x is None:
        return ""
    code_postal = str(x).strip()
    code_postal = code_postal.replace(" ", "")
    if code_postal.endswith('.0'):
        code_postal = code_postal[:-2]
    return code_postal


def franchise_label(fr):
    try:
        fr_int = int(float(fr))
    except Exception:
        return None
    return f"FRA-{fr_int}"


def fr_to_int_label(fr):
    if pd.isna(fr) or fr is None:
        return None
    s = str(fr).strip()
    if s.upper().startswith("FRA-"):
        try:
            return int(s.split("-")[1])
        except Exception:
            pass
    try:
        return int(float(s))
    except Exception:
        return None


def age_from_birth_year(year_str):
    try:
        year = int(str(year_str).strip())
    except Exception:
        return None
    if year < 1900 or year > ANNEE_REF:
        return None
    return ANNEE_REF - year


def classe_age_from_age(age):
    if age is None:
        return None
    if age <= 18:
        return "0 - 18"
    if age <= 25:
        return "19 - 25"
    return "26 - 130"

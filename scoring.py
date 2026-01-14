"""
Scoring avancé pour recommandations de films.

Objectif:
- Partir de la similarité sémantique SBERT
- Ajouter une pondération selon préférences de genres (sliders 1-5)
- Ajouter bonus si réalisateurs/acteurs mentionnés matchent les champs du film
- Ajouter (si dispo dans le référentiel) filtres période/langue via clés optionnelles:
    - film["Annee"] ou film["Year"]
    - film["Langue"] ou film["Language"]
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import re


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def normalize_cosine(cos: float) -> float:
    """
    SentenceTransformer cos_sim est généralement dans [-1, 1].
    On convertit vers [0, 1] pour un scoring plus lisible.
    """
    return clamp((cos + 1.0) / 2.0)


def _clean_text(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _contains_any(haystack: str, needles_csv: str) -> Tuple[int, int]:
    """
    Retourne (match_count, total_items) en cherchant chaque item (séparé par virgule)
    dans haystack.
    """
    needles_csv = (needles_csv or "").strip()
    if not needles_csv:
        return (0, 0)

    items = [x.strip() for x in needles_csv.split(",") if x.strip()]
    if not items:
        return (0, 0)

    h = _clean_text(haystack)
    matches = 0
    for it in items:
        it_clean = _clean_text(it)
        if it_clean and (it_clean in h):
            matches += 1
    return (matches, len(items))


def genre_preference_score(film_category: str, user_preferences: Dict[str, int]) -> float:
    """
    Map slider 1-5 vers [0,1]. Si genre absent: neutre 0.55.
    """
    if not user_preferences:
        return 0.55

    val = user_preferences.get(film_category)
    if val is None:
        return 0.55

    return clamp((val - 1) / 4.0)


def period_match_score(user_period: str, film: Dict[str, Any]) -> float:
    """
    Si le référentiel contient une année, on score selon la période choisie.
    Sinon on retourne neutre.
    """
    if not user_period or user_period == "Peu importe":
        return 0.60

    year = film.get("Annee", film.get("Year"))
    if year is None:
        return 0.60

    try:
        y = int(year)
    except Exception:
        return 0.60

    if user_period == "Classiques (avant 1980)":
        return 1.0 if y < 1980 else 0.0
    if user_period == "Années 80-90":
        return 1.0 if 1980 <= y <= 1999 else 0.0
    if user_period == "Années 2000-2010":
        return 1.0 if 2000 <= y <= 2010 else 0.0
    if user_period == "Récents (2010+)":
        return 1.0 if y >= 2010 else 0.0

    return 0.60


def language_match_score(user_lang: str, film: Dict[str, Any]) -> float:
    """
    Si le référentiel contient une langue, on score selon la langue choisie.
    Sinon neutre.
    """
    if not user_lang or user_lang == "Peu importe":
        return 0.60

    lang = film.get("Langue", film.get("Language"))
    if not lang:
        return 0.60

    lang_clean = _clean_text(str(lang))

    if user_lang == "Anglais":
        return 1.0 if ("en" in lang_clean or "anglais" in lang_clean or "english" in lang_clean) else 0.0
    if user_lang == "Français":
        return 1.0 if ("fr" in lang_clean or "français" in lang_clean or "french" in lang_clean) else 0.0
    if user_lang == "Japonais (Animation)":
        return 1.0 if ("ja" in lang_clean or "japonais" in lang_clean or "japanese" in lang_clean) else 0.0
    if user_lang == "Autres":
        if ("en" in lang_clean or "anglais" in lang_clean or "english" in lang_clean):
            return 0.0
        if ("fr" in lang_clean or "français" in lang_clean or "french" in lang_clean):
            return 0.0
        if ("ja" in lang_clean or "japonais" in lang_clean or "japanese" in lang_clean):
            return 0.0
        return 1.0

    return 0.60


def people_bonus_score(user_realisateurs: str, user_acteurs: str, film: Dict[str, Any]) -> float:
    """
    Bonus si réalisateurs/acteurs donnés par l'utilisateur apparaissent dans:
    - film["Keywords"]
    - film["Description"]
    - film["Film"] (titre)
    - (optionnel) film["Realisateur"], film["Acteurs"]
    """
    haystack = " ".join([
        str(film.get("Film", "")),
        str(film.get("Description", "")),
        str(film.get("Keywords", "")),
        str(film.get("Realisateur", "")),
        str(film.get("Acteurs", "")),
    ])

    r_matches, r_total = _contains_any(haystack, user_realisateurs)
    a_matches, a_total = _contains_any(haystack, user_acteurs)

    bonus = 0.0
    if r_total > 0:
        bonus += (r_matches / r_total) * 0.20
    if a_total > 0:
        bonus += (a_matches / a_total) * 0.20

    return clamp(bonus, 0.0, 0.35)


@dataclass
class ScoreBreakdown:
    semantic: float
    genre: float
    period: float
    language: float
    people_bonus: float
    final: float


def compute_final_score(
    cosine_similarity_raw: float,
    film: Dict[str, Any],
    user_answers: Dict[str, Any],
    weights: Dict[str, float] | None = None
) -> ScoreBreakdown:
    """
    Combine tout en un score final [0,1].

    weights (par défaut):
      - semantic: 0.62
      - genre:    0.23
      - period:   0.07
      - language: 0.06
      - people:   0.02  (bonus ajouté séparément)

    NB: people_bonus est un petit "add-on" (jusqu'à +0.35 max, mais en pratique souvent < 0.15).
    """
    w = weights or {
        "semantic": 0.62,
        "genre": 0.23,
        "period": 0.07,
        "language": 0.06,
        "people": 0.02,
    }

    sem = normalize_cosine(float(cosine_similarity_raw))
    prefs = user_answers.get("preferences", {}) or {}
    gen = genre_preference_score(str(film.get("Categorie", "")), prefs)

    per = period_match_score(str(user_answers.get("periode", "Peu importe")), film)
    lan = language_match_score(str(user_answers.get("langue", "Peu importe")), film)

    pb = people_bonus_score(
        str(user_answers.get("realisateurs", "")),
        str(user_answers.get("acteurs", "")),
        film
    )

    base = (w["semantic"] * sem) + (w["genre"] * gen) + (w["period"] * per) + (w["language"] * lan)
    final = clamp(base + pb)

    return ScoreBreakdown(
        semantic=sem,
        genre=gen,
        period=per,
        language=lan,
        people_bonus=pb,
        final=final
    )

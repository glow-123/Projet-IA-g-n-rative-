"""
Module GenAI (Gemini) :
- Génère une explication personnalisée "Pourquoi ce film" + pitch court
- Fallback automatique si pas de clé API (ne casse pas l'app)

Nécessite une variable d'env:
- GOOGLE_API_KEY (recommandé) ou GEMINI_API_KEY
"""

from __future__ import annotations
import os
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except Exception:
    genai = None


def _get_api_key() -> Optional[str]:
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


def gemini_available() -> bool:
    return genai is not None and bool(_get_api_key())


def generate_explanation(
    user_answers: Dict[str, Any],
    film: Dict[str, Any],
    score_final: float,
    max_chars: int = 420
) -> str:
    """
    Retourne une explication en FR.
    Si Gemini indisponible => fallback deterministe.
    """
    if not gemini_available():
        return (
            f"Ce film correspond à tes envies (score {score_final:.0%}). "
            f"Il partage des thèmes proches de ta description et de l’ambiance recherchée, "
            f"et il est aligné avec tes préférences de genre."
        )

    try:
        genai.configure(api_key=_get_api_key())
        model = genai.GenerativeModel("gemini-1.5-flash")

        description = (user_answers.get("description") or "").strip()
        ambiance = (user_answers.get("ambiance") or "").strip()
        realisateurs = (user_answers.get("realisateurs") or "").strip()
        acteurs = (user_answers.get("acteurs") or "").strip()
        periode = (user_answers.get("periode") or "Peu importe").strip()
        langue = (user_answers.get("langue") or "Peu importe").strip()
        prefs = user_answers.get("preferences") or {}

        film_title = film.get("Film", "")
        film_cat = film.get("Categorie", "")
        film_desc = film.get("Description", "")
        film_kw = film.get("Keywords", "")

        prompt = f"""
Tu es un assistant cinéma. Ta tâche: expliquer brièvement (en français) pourquoi un film est recommandé.

Contraintes:
- 2 à 4 phrases max
- Ton naturel, pas scolaire
- Pas de spoilers
- Mentionne 1 ou 2 éléments précis (ambiance, thème, genre) qui relient le film aux réponses
- Longueur max ~{max_chars} caractères

Réponses utilisateur:
- Type recherché: {description}
- Ambiance: {ambiance}
- Réalisateurs aimés: {realisateurs}
- Acteurs aimés: {acteurs}
- Période: {periode}
- Langue: {langue}
- Préférences de genres (1-5): {prefs}

Film recommandé:
- Titre: {film_title}
- Genre: {film_cat}
- Description: {film_desc}
- Mots-clés: {film_kw}

Score final: {score_final:.2f}
"""

        resp = model.generate_content(prompt)
        txt = (resp.text or "").strip()
        if not txt:
            raise RuntimeError("Empty response")

        txt = txt.replace("\n", " ").strip()
        if len(txt) > max_chars:
            txt = txt[: max_chars - 3].rstrip() + "..."
        return txt

    except Exception:
        return (
            f"Ce film colle bien à tes goûts (score {score_final:.0%}). "
            f"Son genre et son ambiance sont proches de ce que tu as décrit."
        )

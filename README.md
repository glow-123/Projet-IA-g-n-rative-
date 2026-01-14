# Système de Recommandation Cinématographique

> Moteur de recommandation IA sémantique basé sur SBERT et assisté par GenAI via RAG

**Projet IA Générative** • EFREI Paris M1 Data Engineering & IA • 2025-2026

## Auteurs

- **Gloria AMINI**
- **Mohamad KHOBAIZ**

---

## Description

Application web de recommandation de films personnalisée utilisant l'analyse sémantique des préférences utilisateur exprimées en langage naturel.

### Fonctionnalités

- **Analyse sémantique** des descriptions utilisateur avec SBERT
- **Scoring pondéré** multi-critères (sémantique, genre, période, langue)
- **Explications IA** générées par Gemini API (architecture RAG)
- **Visualisations interactives** avec Plotly
- **Interface intuitive** Streamlit

---

## Stack Technique

| Composant | Technologies |
|-----------|-------------|
| **Frontend** | Streamlit, Plotly |
| **NLP** | SBERT (sentence-transformers), Similarité Cosinus |
| **IA Générative** | Google Gemini API, Architecture RAG |
| **Data** | JSON, Pandas, NumPy |

### Modèle SBERT
- `all-MiniLM-L6-v2` : modèle léger (~80 Mo), support FR/EN

---

## Structure du Projet

```
Recommandation-Film/
├── 📄 app.py                    # Application principale Streamlit
├── 📄 nlp_engine.py             # Moteur NLP (SBERT + similarité)
├── 📄 scoring.py                # Scoring pondéré multi-critères
├── 📄 genai_module.py           # Module Gemini (explications IA)
├── 📄 visualisations.py         # Graphiques Plotly
├── 📄 referentiel_films.json    # Base de données films (55 films)
├── 📄 requirements.txt          # Dépendances Python
└── 📄 README.md                 # Documentation
```

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/glow-123/Projet-IA-generative-.git
cd Projet-IA-generative-
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer Gemini (optionnel)

Pour activer les explications IA personnalisées :

1. Obtenir une clé API sur [Google AI Studio](https://aistudio.google.com/apikey)
2. Créer un fichier `.env` à la racine :

```env
GOOGLE_API_KEY=votre_clé_ici
```

> ⚠️ Sans clé API, l'application fonctionne avec des explications génériques.

---

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

### Mode Debug

Pour voir le statut de connexion Gemini :
```
http://localhost:8501/?debug=1
```

---

## Pipeline IA

```
1. Input → 2. Préproc → 3. SBERT → 4. Cosine → 5. Scoring → 6. Top-N → 7. RAG
```

### Pondérations du Score Final

| Critère | Poids |
|---------|-------|
| Sémantique (SBERT) | 62% |
| Genre | 23% |
| Période | 7% |
| Langue | 6% |
| Bonus (réalisateur/acteur) | +2% |

---

## Référentiel de Données

- **55 films** couvrant 12 genres
- **Sources** : TMDB, IMDb, AlloCiné
- **Format** : JSON

### Attributs par film

```json
{
  "FilmID": 1,
  "Film": "Inception",
  "Categorie": "Science-Fiction",
  "Description": "...",
  "Keywords": "...",
  "Annee": 2010,
  "Langue": "en"
}
```

---

## Tests

### Profil A : Suspense
- **Input** : "Film captivant avec du suspense"
- **Output** : Inception, Interstellar, Shutter Island

### Profil B : Détente
- **Input** : "Comédie légère pour décompresser"
- **Output** : Intouchables, Le Dîner de cons

---

## Améliorations Futures

- [ ] Fine-tuning SBERT sur corpus cinéma
- [ ] Base vectorielle (Pinecone, ChromaDB)
- [ ] Chatbot conversationnel
- [ ] Enrichissement via TMDB API

---

## Licence

Projet académique - EFREI Paris 2025-2026

---

## Remerciements

- EFREI Paris - M1 Data Engineering & IA
- Google AI (Gemini API)

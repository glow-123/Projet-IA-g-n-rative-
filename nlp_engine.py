"""
NLP Engine - Moteur d'analyse sémantique pour la recommandation de films
Utilise SBERT (Sentence-BERT) pour encoder les textes et la similarité cosinus pour comparer
"""

from sentence_transformers import SentenceTransformer, util
import json
import numpy as np

# ========== CHARGEMENT DU MODÈLE SBERT ==========
# all-MiniLM-L6-v2 : modèle léger et performant pour le français et l'anglais
MODEL_NAME = "all-MiniLM-L6-v2"

def charger_modele():
    """
    Charge le modèle SBERT.
    Le premier chargement télécharge le modèle (~80 Mo), ensuite il est en cache.
    """
    print(f"📦 Chargement du modèle SBERT ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)
    print("✅ Modèle chargé avec succès !")
    return model


# ========== CHARGEMENT DU RÉFÉRENTIEL ==========
def charger_referentiel(chemin="referentiel_films.json"):
    """
    Charge le référentiel de films depuis le fichier JSON.
    
    Returns:
        dict: Données du référentiel (blocs et films)
    """
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Référentiel chargé : {len(data['films'])} films, {len(data['blocs'])} catégories")
        return data
    except FileNotFoundError:
        print(f"❌ Fichier {chemin} non trouvé")
        return None
    except json.JSONDecodeError:
        print(f"❌ Erreur de format JSON dans {chemin}")
        return None


# ========== ENCODAGE DES FILMS ==========
def encoder_films(model, films):
    """
    Encode les descriptions de tous les films du référentiel.
    
    Args:
        model: Modèle SBERT chargé
        films: Liste des films du référentiel
        
    Returns:
        dict: {FilmID: embedding}
    """
    print("Encodage des descriptions de films...")
    
    embeddings_films = {}
    
    for film in films:
        # Combine description + keywords pour un embedding plus riche
        texte_complet = f"{film['Description']} {film['Keywords']}"
        embedding = model.encode(texte_complet, convert_to_tensor=True)
        embeddings_films[film['FilmID']] = {
            'embedding': embedding,
            'film': film
        }
    
    print(f"✅ {len(embeddings_films)} films encodés")
    return embeddings_films


# ========== ENCODAGE DE LA REQUÊTE UTILISATEUR ==========
def encoder_requete_utilisateur(model, reponses):
    """
    Encode les réponses textuelles de l'utilisateur en un seul embedding.
    
    Args:
        model: Modèle SBERT chargé
        reponses: Dictionnaire des réponses utilisateur
        
    Returns:
        tensor: Embedding de la requête utilisateur
    """
    # Construire un texte combiné à partir des réponses
    texte_utilisateur = f"{reponses.get('description', '')} {reponses.get('ambiance', '')}"
    
    # Ajouter réalisateurs/acteurs si présents
    if reponses.get('realisateurs'):
        texte_utilisateur += f" {reponses['realisateurs']}"
    if reponses.get('acteurs'):
        texte_utilisateur += f" {reponses['acteurs']}"
    
    print(f"Encodage de la requête utilisateur...")
    embedding = model.encode(texte_utilisateur, convert_to_tensor=True)
    print("✅ Requête encodée")
    
    return embedding


# ========== CALCUL DE SIMILARITÉ ==========
def calculer_similarites(embedding_utilisateur, embeddings_films):
    """
    Calcule la similarité cosinus entre la requête utilisateur et chaque film.
    
    Args:
        embedding_utilisateur: Embedding de la requête
        embeddings_films: Dict des embeddings de films
        
    Returns:
        list: Liste de tuples (film, score_similarite) triée par score décroissant
    """
    print("Calcul des similarités cosinus...")
    
    resultats = []
    
    for film_id, data in embeddings_films.items():
        # Calcul de la similarité cosinus avec sentence-transformers
        similarite = util.cos_sim(embedding_utilisateur, data['embedding']).item()
        
        resultats.append({
            'film': data['film'],
            'score_semantique': similarite
        })
    
    # Trier par score décroissant
    resultats.sort(key=lambda x: x['score_semantique'], reverse=True)
    
    print(f"✅ Similarités calculées pour {len(resultats)} films")
    return resultats


# ========== FONCTION PRINCIPALE DE RECOMMANDATION ==========
def obtenir_recommandations(reponses_utilisateur, top_n=10):
    """
    Fonction principale qui orchestre tout le processus de recommandation.
    
    Args:
        reponses_utilisateur: Dict des réponses du questionnaire
        top_n: Nombre de recommandations à retourner
        
    Returns:
        list: Top N films recommandés avec leurs scores
    """
    # 1. Charger le modèle
    model = charger_modele()
    
    # 2. Charger le référentiel
    referentiel = charger_referentiel()
    if not referentiel:
        return []
    
    # 3. Encoder les films
    embeddings_films = encoder_films(model, referentiel['films'])
    
    # 4. Encoder la requête utilisateur
    embedding_utilisateur = encoder_requete_utilisateur(model, reponses_utilisateur)
    
    # 5. Calculer les similarités
    resultats = calculer_similarites(embedding_utilisateur, embeddings_films)
    
    # 6. Retourner le top N
    return resultats[:top_n]


# ========== FONCTION AVEC PONDÉRATION PAR GENRE ==========
def obtenir_recommandations_ponderees(reponses_utilisateur, top_n=10):
    """
    Version avancée qui combine similarité sémantique ET préférences de genre.
    
    Args:
        reponses_utilisateur: Dict des réponses (incluant 'preferences' pour les genres)
        top_n: Nombre de recommandations
        
    Returns:
        list: Top N films avec scores combinés
    """
    # Obtenir les recommandations de base
    resultats = obtenir_recommandations(reponses_utilisateur, top_n=len(obtenir_recommandations(reponses_utilisateur, 100)))
    
    # Si pas de préférences de genre, retourner les résultats bruts
    preferences = reponses_utilisateur.get('preferences', {})
    if not preferences:
        return resultats[:top_n]
    
    # Mapping catégorie -> préférence utilisateur (normalisé entre 0 et 1)
    poids_genres = {}
    for genre, score in preferences.items():
        poids_genres[genre] = score / 5.0  # Normaliser de 1-5 à 0.2-1.0
    
    # Appliquer la pondération
    for resultat in resultats:
        categorie = resultat['film']['Categorie']
        poids = poids_genres.get(categorie, 0.6)  # 0.6 par défaut si genre non trouvé
        
        # Score combiné : 70% sémantique + 30% préférence genre
        score_semantique = resultat['score_semantique']
        score_combine = (0.7 * score_semantique) + (0.3 * poids)
        
        resultat['score_genre'] = poids
        resultat['score_final'] = score_combine
    
    # Re-trier par score final
    resultats.sort(key=lambda x: x.get('score_final', x['score_semantique']), reverse=True)
    
    return resultats[:top_n]


# ========== TEST STANDALONE ==========
if __name__ == "__main__":
    # Test du module
    print("=" * 50)
    print("Test du moteur NLP")
    print("=" * 50)
    
    # Exemple de réponses utilisateur
    test_reponses = {
        "description": "Je veux un film avec beaucoup de suspense et des rebondissements inattendus",
        "ambiance": "Sombre et mystérieux, quelque chose qui fait réfléchir",
        "realisateurs": "Christopher Nolan",
        "acteurs": "",
        "preferences": {
            "Thriller": 5,
            "Romance": 2,
            "Comédie": 3,
            "Science-Fiction": 4,
            "Drame": 4,
            "Action": 3,
            "Horreur": 2,
            "Animation": 2
        }
    }
    
    print("\nRequête test:")
    print(f"   Description: {test_reponses['description']}")
    print(f"   Ambiance: {test_reponses['ambiance']}")
    
    print("\nRecherche des recommandations...\n")
    
    # Obtenir les recommandations
    recommandations = obtenir_recommandations(test_reponses, top_n=5)
    
    print("\n" + "=" * 50)
    print("🎬 TOP 5 RECOMMANDATIONS (similarité sémantique)")
    print("=" * 50)
    
    for i, rec in enumerate(recommandations, 1):
        film = rec['film']
        score = rec['score_semantique']
        print(f"\n{i}. {film['Film']} ({film['Categorie']})")
        print(f"   Score: {score:.4f}")
        print(f"   {film['Description'][:100]}...")

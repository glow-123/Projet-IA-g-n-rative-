from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import json
from nlp_engine import obtenir_recommandations  # CONNEXION AU MOTEUR NLP
from scoring import compute_final_score, ScoreBreakdown  # Phase 4: Scoring avancé
from genai_module import generate_explanation, gemini_available  # Phase 5: Gemini
from visualisations import (  # Phase 6: Visualisations
    creer_graphique_scores_recommandations,
    creer_radar_preferences,
    creer_camembert_categories
)

# ========== CONFIGURATION DE LA PAGE ==========
st.set_page_config(
    page_title="🎬 Recommandation Films",
    page_icon="🎬",
    layout="wide"
)

# ========== TITRE ET INTRODUCTION ==========
st.title("Système de Recommandation Cinématographique")
st.markdown("""
*Découvrez des films personnalisés grâce à l'analyse sémantique de vos préférences.*

Remplissez le questionnaire ci-dessous pour recevoir des recommandations adaptées à vos goûts !
""")

st.divider()

# ========== QUESTIONNAIRE ==========
st.header("Questionnaire")

# Deux colonnes pour organiser le formulaire
col1, col2 = st.columns(2)

# ===== COLONNE 1 : Questions texte libre =====
with col1:
    st.subheader("Décrivez vos envies")
    
    q1_description = st.text_area(
        "Quel type de film recherchez-vous ?",
        placeholder="Ex: Je veux un film captivant avec des rebondissements inattendus, une ambiance sombre et mystérieuse...",
        height=120,
        help="Décrivez librement le type de film que vous aimeriez voir"
    )
    
    q2_ambiance = st.text_area(
        "Quelle ambiance/mood recherchez-vous ?",
        placeholder="Ex: Quelque chose d'émouvant qui fait réfléchir, ou plutôt léger et divertissant...",
        height=120,
        help="Décrivez l'atmosphère ou l'émotion que vous recherchez"
    )
    
    # Questions guidées
    st.subheader("Précisions optionnelles")
    
    realisateurs = st.text_input(
        "Réalisateurs appréciés (optionnel)",
        placeholder="Ex: Christopher Nolan, Denis Villeneuve, Greta Gerwig...",
        help="Mentionnez des réalisateurs dont vous aimez le style"
    )
    
    acteurs = st.text_input(
        "Acteurs préférés (optionnel)",
        placeholder="Ex: Leonardo DiCaprio, Margot Robbie...",
        help="Mentionnez des acteurs que vous appréciez"
    )

# ===== COLONNE 2 : Questions Likert (1-5) =====
with col2:
    st.subheader("Vos préférences par genre")
    st.markdown("*Notez votre intérêt de 1 (pas du tout) à 5 (adore)*")
    
    pref_thriller = st.slider(
        "Thriller / Suspense",
        min_value=1,
        max_value=5,
        value=3,
        help="Films à suspense, tension psychologique"
    )
    
    pref_romance = st.slider(
        "Romance",
        min_value=1,
        max_value=5,
        value=3,
        help="Films centrés sur les relations amoureuses"
    )
    
    pref_comedie = st.slider(
        "Comédie",
        min_value=1,
        max_value=5,
        value=3,
        help="Films humoristiques et divertissants"
    )
    
    pref_sf = st.slider(
        "Science-Fiction",
        min_value=1,
        max_value=5,
        value=3,
        help="Films explorant technologies et futurs possibles"
    )
    
    pref_drame = st.slider(
        "Drame",
        min_value=1,
        max_value=5,
        value=3,
        help="Films émotionnels traitant de sujets profonds"
    )
    
    pref_action = st.slider(
        "Action",
        min_value=1,
        max_value=5,
        value=3,
        help="Films dynamiques avec scènes spectaculaires"
    )
    
    pref_horreur = st.slider(
        "Horreur",
        min_value=1,
        max_value=5,
        value=3,
        help="Films conçus pour effrayer"
    )
    
    pref_animation = st.slider(
        "Animation",
        min_value=1,
        max_value=5,
        value=3,
        help="Films d'animation pour tous publics"
    )

# ===== Questions supplémentaires =====
st.divider()
st.subheader("Paramètres supplémentaires")

col3, col4 = st.columns(2)

with col3:
    periode = st.selectbox(
        "Période préférée",
        options=[
            "Peu importe",
            "Classiques (avant 1980)",
            "Années 80-90",
            "Années 2000-2010",
            "Récents (2010+)"
        ],
        help="Préférez-vous des films d'une époque particulière ?"
    )

with col4:
    langue = st.selectbox(
        "Langue originale préférée",
        options=[
            "Peu importe",
            "Anglais",
            "Français",
            "Japonais (Animation)",
            "Autres"
        ],
        help="Avez-vous une préférence pour la langue originale ?"
    )

st.divider()

# ========== BOUTON D'ANALYSE ==========
if st.button("Analyser et Recommander", type="primary", use_container_width=True):
    
    # Vérification des champs obligatoires
    if not q1_description.strip() or not q2_ambiance.strip():
        st.error("Veuillez remplir les deux descriptions textuelles (type de film et ambiance recherchée).")
    else:
        # Stocker les réponses dans un dictionnaire
        reponses_utilisateur = {
            "description": q1_description.strip(),
            "ambiance": q2_ambiance.strip(),
            "realisateurs": realisateurs.strip(),
            "acteurs": acteurs.strip(),
            "periode": periode,
            "langue": langue,
            "preferences": {
                "Thriller": pref_thriller,
                "Romance": pref_romance,
                "Comédie": pref_comedie,
                "Science-Fiction": pref_sf,
                "Drame": pref_drame,
                "Action": pref_action,
                "Horreur": pref_horreur,
                "Animation": pref_animation
            }
        }
        
        # Sauvegarder temporairement dans session_state
        st.session_state['reponses'] = reponses_utilisateur
        
        # Afficher un message de succès
        st.success("✅ Réponses enregistrées ! Analyse en cours...")
        
        # Afficher un récapitulatif
        with st.expander("Récapitulatif de vos réponses", expanded=False):
            st.write("**Description souhaitée :**", q1_description)
            st.write("**Ambiance recherchée :**", q2_ambiance)
            if realisateurs:
                st.write("**Réalisateurs :**", realisateurs)
            if acteurs:
                st.write("**Acteurs :**", acteurs)
            st.write("**Période :**", periode)
            st.write("**Langue :**", langue)
            st.write("**Préférences par genre :**")
            for genre, score in reponses_utilisateur["preferences"].items():
                st.write(f"  - {genre}: {'⭐' * score}")
        
        # ========== PHASE 3 : APPEL DU MOTEUR NLP ==========
        with st.spinner("Analyse sémantique en cours..."):
            recommandations_brutes = obtenir_recommandations(reponses_utilisateur, top_n=10)
        
        # ========== PHASE 4 : SCORING AVANCÉ ==========
        with st.spinner("Calcul des scores pondérés..."):
            recommandations_enrichies = []
            
            for rec in recommandations_brutes:
                film = rec['film']
                score_semantique = rec['score_semantique']
                
                # Calcul du score final avec pondération
                breakdown = compute_final_score(
                    cosine_similarity_raw=score_semantique,
                    film=film,
                    user_answers=reponses_utilisateur
                )
                
                recommandations_enrichies.append({
                    'film': film,
                    'score_semantique': score_semantique,
                    'breakdown': breakdown,
                    'score_final': breakdown.final
                })
            
            # Trier par score final
            recommandations_enrichies.sort(key=lambda x: x['score_final'], reverse=True)
            
            # Garder le top 5
            top_recommandations = recommandations_enrichies[:5]
        
        # ========== PHASE 5 : GÉNÉRATION DES EXPLICATIONS (Gemini) ==========
        with st.spinner("Génération des explications personnalisées..."):
            for rec in top_recommandations:
                explanation = generate_explanation(
                    user_answers=reponses_utilisateur,
                    film=rec['film'],
                    score_final=rec['score_final']
                )
                rec['explanation'] = explanation
        
        # ========== AFFICHAGE DES RÉSULTATS ==========
        st.header("Vos Recommandations Personnalisées")
        
        # Indicateur Gemini
        if gemini_available():
            st.success("Explications générées par Gemini AI")
        else:
            st.info("Ajoutez GOOGLE_API_KEY pour des explications personnalisées par IA")
        
        # TOP 3 en colonnes
        st.subheader("Top 3 Films pour vous")
        cols = st.columns(3)
        
        medailles = ["🥇", "🥈", "🥉"]
        
        for i, rec in enumerate(top_recommandations[:3]):
            film = rec['film']
            score_final = rec['score_final']
            breakdown = rec['breakdown']
            explanation = rec.get('explanation', '')
            
            with cols[i]:
                st.markdown(f"### {medailles[i]} {film['Film']}")
                st.write(f"**Genre:** {film['Categorie']}")
                st.write(f"**Score:** {score_final:.0%}")
                st.progress(score_final)
                
                # Détail des scores
                with st.expander("Détail du score"):
                    st.write(f"- Sémantique: {breakdown.semantic:.0%}")
                    st.write(f"- Genre: {breakdown.genre:.0%}")
                    st.write(f"- Période: {breakdown.period:.0%}")
                    st.write(f"- Langue: {breakdown.language:.0%}")
                    if breakdown.people_bonus > 0:
                        st.write(f"- Bonus: +{breakdown.people_bonus:.0%}")
                
                # Explication Gemini
                st.info(f"{explanation}")
        
        st.divider()
        
        # ========== PHASE 6 : VISUALISATIONS ==========
        st.subheader("Visualisations")
        
        # Préparer les données pour les visualisations (format tuple)
        recommandations_viz = [
            (rec['film'], rec['score_final']) 
            for rec in top_recommandations
        ]
        
        # Ligne 1 : Radar + Camembert
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            fig_radar = creer_radar_preferences(reponses_utilisateur["preferences"])
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col_viz2:
            fig_camembert = creer_camembert_categories(recommandations_viz)
            st.plotly_chart(fig_camembert, use_container_width=True)
        
        # Ligne 2 : Barres horizontales des scores
        fig_scores = creer_graphique_scores_recommandations(recommandations_viz)
        st.plotly_chart(fig_scores, use_container_width=True)
        
        st.divider()
        
        # Détails des 5 recommandations
        with st.expander("Voir les 5 recommandations détaillées"):
            for i, rec in enumerate(top_recommandations, 1):
                film = rec['film']
                score_final = rec['score_final']
                breakdown = rec['breakdown']
                explanation = rec.get('explanation', '')
                
                st.markdown(f"### {i}. {film['Film']} ({film['Categorie']})")
                
                col_detail1, col_detail2 = st.columns([2, 1])
                
                with col_detail1:
                    st.write(f"**Description:** {film['Description']}")
                    st.write(f"**Mots-clés:** {film.get('Keywords', 'N/A')}")
                    st.info(f"**Pourquoi ce film ?** {explanation}")
                
                with col_detail2:
                    st.metric("Score Final", f"{score_final:.0%}")
                    st.write(f"Sémantique: {breakdown.semantic:.0%}")
                    st.write(f"Genre: {breakdown.genre:.0%}")
                    st.write(f"Période: {breakdown.period:.0%}")
                    st.write(f"Langue: {breakdown.language:.0%}")
                
                st.divider()

# ========== SIDEBAR : INFORMATIONS ==========
with st.sidebar:
    st.header("À propos")
    st.markdown("""
    Ce système utilise l'**analyse sémantique** pour comprendre vos préférences 
    et vous recommander des films personnalisés.
    """)
    
    st.divider()
    
    # Status Gemini (visible uniquement avec ?debug=1 dans l'URL)
    if st.query_params.get("debug") == "1":
        st.header("Status")
        if gemini_available():
            st.success("✅ Gemini connecté")
        else:
            st.warning("⚠️ Gemini non configuré")
            st.caption("Ajoutez GOOGLE_API_KEY")
    st.divider()
    
    st.header("Statistiques")
    try:
        with open("referentiel_films.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            st.metric("Nombre de films", len(data.get("films", [])))
            st.metric("Catégories", len(data.get("blocs", [])))
    except FileNotFoundError:
        st.warning("Référentiel non trouvé")


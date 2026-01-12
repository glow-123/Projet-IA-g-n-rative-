import streamlit as st
import json

# ========== CONFIGURATION DE LA PAGE ==========
st.set_page_config(
    page_title="🎬 Recommandation Films",
    page_icon="🎬",
    layout="wide"
)

# ========== TITRE ET INTRODUCTION ==========
st.title("🎬 Système de Recommandation Cinématographique")
st.markdown("""
*Découvrez des films personnalisés grâce à l'analyse sémantique de vos préférences.*

Remplissez le questionnaire ci-dessous pour recevoir des recommandations adaptées à vos goûts !
""")

st.divider()

# ========== QUESTIONNAIRE ==========
st.header(" Questionnaire")

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
        " Thriller / Suspense",
        min_value=1,
        max_value=5,
        value=3,
        help="Films à suspense, tension psychologique"
    )
    
    pref_romance = st.slider(
        " Romance",
        min_value=1,
        max_value=5,
        value=3,
        help="Films centrés sur les relations amoureuses"
    )
    
    pref_comedie = st.slider(
        " Comédie",
        min_value=1,
        max_value=5,
        value=3,
        help="Films humoristiques et divertissants"
    )
    
    pref_sf = st.slider(
        " Science-Fiction",
        min_value=1,
        max_value=5,
        value=3,
        help="Films explorant technologies et futurs possibles"
    )
    
    pref_drame = st.slider(
        " Drame",
        min_value=1,
        max_value=5,
        value=3,
        help="Films émotionnels traitant de sujets profonds"
    )
    
    pref_action = st.slider(
        " Action",
        min_value=1,
        max_value=5,
        value=3,
        help="Films dynamiques avec scènes spectaculaires"
    )
    
    pref_horreur = st.slider(
        " Horreur",
        min_value=1,
        max_value=5,
        value=3,
        help="Films conçus pour effrayer"
    )
    
    pref_animation = st.slider(
        " Animation",
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
        st.error("⚠️ Veuillez remplir les deux descriptions textuelles (type de film et ambiance recherchée).")
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
        
        # Afficher un récapitulatif (temporaire, sera remplacé par les résultats)
        with st.expander("📋 Récapitulatif de vos réponses", expanded=True):
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
        
        # Placeholder pour les résultats (sera complété dans les phases suivantes)
        st.info("Les recommandations seront affichées ici après l'intégration du moteur NLP (Phase 3).")

# ========== SIDEBAR : INFORMATIONS ==========
with st.sidebar:
    st.header("À propos")
    st.markdown("""
    Ce système utilise l'**analyse sémantique** pour comprendre vos préférences 
    et vous recommander des films personnalisés.
    
    **Technologies utilisées :**
    - SBERT (Sentence-BERT)
    - Similarité cosinus
    - IA Générative (Gemini)
    
    **Projet IA Générative**
    - Gloria AMINI
    - Mohamad Khobaiz
    """)
    
    st.divider()
    
    st.header("Statistiques du référentiel")
    try:
        with open("referentiel_films.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            st.metric("Nombre de films", len(data.get("films", [])))
            st.metric("Catégories", len(data.get("blocs", [])))
    except FileNotFoundError:
        st.warning("Référentiel non trouvé")


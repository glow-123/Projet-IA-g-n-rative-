"""
Phase 6 : Module de Visualisations
===================================
Ce module contient les fonctions de visualisation pour le système de recommandation.
Utilise Plotly pour des graphiques interactifs.

Projet IA Générative
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def creer_graphique_scores_recommandations(recommandations: list) -> go.Figure:
    """
    Visualisation 1 : Barres horizontales des scores de recommandation
    
    Affiche les films recommandés avec leurs scores sous forme de barres horizontales.
    
    Args:
        recommandations: Liste de tuples (film_dict, score)
    
    Returns:
        Figure Plotly
    """
    # Préparer les données
    films = [rec[0]["Film"] for rec in recommandations]
    scores = [rec[1] * 100 for rec in recommandations]  # Convertir en pourcentage
    categories = [rec[0]["Categorie"] for rec in recommandations]
    
    # Créer un DataFrame
    df = pd.DataFrame({
        "Film": films,
        "Score (%)": scores,
        "Catégorie": categories
    })
    
    # Inverser l'ordre pour avoir le meilleur en haut
    df = df.iloc[::-1]
    
    # Palette de couleurs par catégorie
    couleurs_categories = {
        "Thriller": "#e91e63",
        "Romance": "#f44336",
        "Comédie": "#ff9800",
        "Science-Fiction": "#2196f3",
        "Drame": "#9c27b0",
        "Action": "#4caf50",
        "Horreur": "#607d8b",
        "Animation": "#00bcd4"
    }
    
    # Créer le graphique
    fig = go.Figure()
    
    for categorie in df["Catégorie"].unique():
        df_cat = df[df["Catégorie"] == categorie]
        fig.add_trace(go.Bar(
            y=df_cat["Film"],
            x=df_cat["Score (%)"],
            orientation='h',
            name=categorie,
            marker_color=couleurs_categories.get(categorie, "#4fc3f7"),
            text=[f"{s:.1f}%" for s in df_cat["Score (%)"]],
            textposition='auto',
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}%<extra></extra>"
        ))
    
    fig.update_layout(
        title={
            'text': "🎯 Scores de Similarité des Films Recommandés",
            'font': {'size': 18}
        },
        xaxis_title="Score de similarité (%)",
        yaxis_title="",
        barmode='stack',
        showlegend=True,
        legend_title="Catégorie",
        height=400,
        template="plotly_dark",
        paper_bgcolor='rgba(26,26,46,1)',
        plot_bgcolor='rgba(22,33,62,1)',
        font=dict(color='white')
    )
    
    return fig


def creer_radar_preferences(preferences: dict) -> go.Figure:
    """
    Visualisation 2 : Radar des préférences utilisateur par genre
    
    Affiche les préférences Likert (1-5) sous forme de radar.
    
    Args:
        preferences: Dictionnaire {genre: score_likert}
    
    Returns:
        Figure Plotly
    """
    # Préparer les données
    genres = list(preferences.keys())
    scores = list(preferences.values())
    
    # Fermer le radar (répéter le premier point)
    genres_radar = genres + [genres[0]]
    scores_radar = scores + [scores[0]]
    
    # Créer le graphique radar
    fig = go.Figure()
    
    # Aire remplie
    fig.add_trace(go.Scatterpolar(
        r=scores_radar,
        theta=genres_radar,
        fill='toself',
        fillcolor='rgba(79, 195, 247, 0.3)',
        line=dict(color='#4fc3f7', width=2),
        name='Vos préférences',
        hovertemplate="<b>%{theta}</b><br>Score: %{r}/5<extra></extra>"
    ))
    
    # Points
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=genres,
        mode='markers',
        marker=dict(size=10, color='#4fc3f7'),
        showlegend=False,
        hovertemplate="<b>%{theta}</b><br>Score: %{r}/5<extra></extra>"
    ))
    
    fig.update_layout(
        title={
            'text': "Vos Préférences par Genre",
            'font': {'size': 18}
        },
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickmode='linear',
                tick0=0,
                dtick=1,
                gridcolor='rgba(255,255,255,0.2)',
                linecolor='rgba(255,255,255,0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',
                linecolor='rgba(255,255,255,0.2)'
            ),
            bgcolor='rgba(22,33,62,1)'
        ),
        showlegend=True,
        height=450,
        template="plotly_dark",
        paper_bgcolor='rgba(26,26,46,1)',
        font=dict(color='white')
    )
    
    return fig


def creer_camembert_categories(recommandations: list) -> go.Figure:
    """
    Visualisation 3 : Camembert de répartition par catégorie
    
    Affiche la distribution des films recommandés par catégorie.
    
    Args:
        recommandations: Liste de tuples (film_dict, score)
    
    Returns:
        Figure Plotly
    """
    # Compter les catégories
    categories = [rec[0]["Categorie"] for rec in recommandations]
    df_cat = pd.DataFrame({"Catégorie": categories})
    counts = df_cat["Catégorie"].value_counts().reset_index()
    counts.columns = ["Catégorie", "Nombre"]
    
    # Couleurs personnalisées
    couleurs = {
        "Thriller": "#e91e63",
        "Romance": "#f44336",
        "Comédie": "#ff9800",
        "Science-Fiction": "#2196f3",
        "Drame": "#9c27b0",
        "Action": "#4caf50",
        "Horreur": "#607d8b",
        "Animation": "#00bcd4"
    }
    
    colors = [couleurs.get(cat, "#4fc3f7") for cat in counts["Catégorie"]]
    
    # Créer le camembert
    fig = go.Figure(data=[go.Pie(
        labels=counts["Catégorie"],
        values=counts["Nombre"],
        hole=0.4,  # Donut chart
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate="<b>%{label}</b><br>%{value} film(s)<br>%{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title={
            'text': "Répartition par Catégorie",
            'font': {'size': 18}
        },
        showlegend=True,
        legend_title="Catégories",
        height=400,
        template="plotly_dark",
        paper_bgcolor='rgba(26,26,46,1)',
        font=dict(color='white'),
        annotations=[dict(
            text='Top Films',
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False,
            font_color='white'
        )]
    )
    
    return fig


def creer_comparaison_scores(recommandations: list, tous_les_films: list = None) -> go.Figure:
    """
    Visualisation 4 (bonus) : Distribution des scores
    
    Affiche un histogramme de la distribution des scores pour comprendre
    la qualité des recommandations.
    
    Args:
        recommandations: Liste de tuples (film_dict, score) - Top recommandations
        tous_les_films: Liste optionnelle de tous les films avec leurs scores
    
    Returns:
        Figure Plotly
    """
    # Scores des recommandations
    scores_top = [rec[1] * 100 for rec in recommandations]
    noms_top = [rec[0]["Film"] for rec in recommandations]
    
    # Créer le graphique
    fig = go.Figure()
    
    # Barres pour le top des recommandations
    fig.add_trace(go.Bar(
        x=noms_top,
        y=scores_top,
        marker=dict(
            color=scores_top,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Score (%)")
        ),
        text=[f"{s:.1f}%" for s in scores_top],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}%<extra></extra>"
    ))
    
    # Ligne de référence (seuil de bonne recommandation)
    fig.add_hline(
        y=40, 
        line_dash="dash", 
        line_color="#ff9800",
        annotation_text="Seuil recommandé (40%)",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title={
            'text': "Comparaison des Scores",
            'font': {'size': 18}
        },
        xaxis_title="Film",
        yaxis_title="Score de similarité (%)",
        height=400,
        template="plotly_dark",
        paper_bgcolor='rgba(26,26,46,1)',
        plot_bgcolor='rgba(22,33,62,1)',
        font=dict(color='white'),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def afficher_toutes_visualisations(recommandations: list, preferences: dict):
    """
    Fonction utilitaire pour afficher toutes les visualisations dans Streamlit.
    
    Args:
        recommandations: Liste de tuples (film_dict, score)
        preferences: Dictionnaire des préférences Likert
    
    Returns:
        Tuple de figures (scores, radar, camembert, comparaison)
    """
    fig_scores = creer_graphique_scores_recommandations(recommandations)
    fig_radar = creer_radar_preferences(preferences)
    fig_camembert = creer_camembert_categories(recommandations)
    fig_comparaison = creer_comparaison_scores(recommandations)
    
    return fig_scores, fig_radar, fig_camembert, fig_comparaison


# ============================================================
# Test du module
# ============================================================
if __name__ == "__main__":
    # Données de test
    recommandations_test = [
        ({"Film": "Inception", "Categorie": "Science-Fiction"}, 0.52),
        ({"Film": "The Dark Knight", "Categorie": "Action"}, 0.48),
        ({"Film": "Interstellar", "Categorie": "Science-Fiction"}, 0.45),
        ({"Film": "Parasite", "Categorie": "Thriller"}, 0.42),
        ({"Film": "Le Fabuleux Destin d'Amélie Poulain", "Categorie": "Comédie"}, 0.38),
    ]
    
    preferences_test = {
        "Thriller": 4,
        "Romance": 2,
        "Comédie": 3,
        "Science-Fiction": 5,
        "Drame": 3,
        "Action": 4,
        "Horreur": 1,
        "Animation": 3
    }
    
    print("✅ Module de visualisation chargé avec succès!")
    print("Fonctions disponibles:")
    print("  - creer_graphique_scores_recommandations(recommandations)")
    print("  - creer_radar_preferences(preferences)")
    print("  - creer_camembert_categories(recommandations)")
    print("  - creer_comparaison_scores(recommandations)")
    print("  - afficher_toutes_visualisations(recommandations, preferences)")
    
    # Test des visualisations
    fig1 = creer_graphique_scores_recommandations(recommandations_test)
    fig2 = creer_radar_preferences(preferences_test)
    fig3 = creer_camembert_categories(recommandations_test)
    fig4 = creer_comparaison_scores(recommandations_test)
    
    print("\n✅ Toutes les visualisations générées avec succès!")

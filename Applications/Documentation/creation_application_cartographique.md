# Guide de Création d'Applications Cartographiques avec Streamlit et Pydeck

## Table des Matières
1. [Prérequis et Configuration](#1-prérequis-et-configuration)
2. [Choix Technologique](#2-choix-technologique)
3. [Bonnes Pratiques](#3-bonnes-pratiques)
4. [Optimisations de Performance](#4-optimisations-de-performance)
5. [Leçons Apprises](#5-leçons-apprises)

## 1. Prérequis et Configuration

### 1.1 Dépendances Principales
```python
streamlit==1.32.0
pandas==2.2.0
geopandas==0.14.3
pydeck==0.8.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### 1.2 Structure du Projet
```
Applications/
├── carte_fibre/
│   ├── app.py
│   ├── .env
│   └── requirements.txt
└── Documentation/
    └── creation_application_cartographique.md
```

## 2. Choix Technologique

### 2.1 Pourquoi Pydeck ?
- Intégration native avec Streamlit via `st.pydeck_chart`
- Performance optimale grâce au rendu WebGL
- Gestion efficace des grandes quantités de données géospatiales
- Pas besoin de clé d'API ou de token
- Contrôle précis des propriétés visuelles

### 2.2 Configuration de Base
```python
import pydeck as pdk

# Configuration de la couche GeoJSON
layer = pdk.Layer(
    "GeoJsonLayer",
    data=geojson_data,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    extruded=False,
    get_fill_color="properties.color",
    get_line_color=[255, 255, 255],
    get_line_width=2,
)

# Configuration de la vue
view_state = pdk.ViewState(
    latitude=46.603354,
    longitude=1.888334,
    zoom=5,
    pitch=0,
    bearing=0
)

# Création de la carte
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="light",
    tooltip={
        "html": "<b>{nom}</b><br/>Donnée : {valeur}",
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }
)

# Affichage dans Streamlit
st.pydeck_chart(r)
```

## 3. Bonnes Pratiques

### 3.1 Gestion des Données
```python
@st.cache_data
def load_data():
    # Chargement des données avec mise en cache
    return data

@st.cache_data
def optimize_geojson(gdf, tolerance=0.001):
    # Optimisation des géométries
    return optimized_data
```

### 3.2 Gestion des Couleurs
```python
def get_color(value):
    # Définition des couleurs selon les seuils
    if pd.isna(value):
        return [200, 200, 200]  # Gris pour données manquantes
    elif value >= 100:
        return [222, 45, 38]    # Rouge foncé
    # ... autres seuils
```

### 3.3 Gestion des Erreurs et Feedback
```python
try:
    with st.spinner("Chargement de la carte..."):
        # Opérations de création de la carte
except Exception as e:
    st.error(f"Erreur lors de la création de la carte : {str(e)}")
```

## 4. Optimisations de Performance

### 4.1 Données Géographiques
- Simplification des géométries avec `gdf.simplify()`
- Réduction de la précision des coordonnées
- Sélection minimale des propriétés nécessaires
- Mise en cache des données avec `@st.cache_data`

### 4.2 Rendu de la Carte
```python
# Configuration optimale pour la performance
layer = pdk.Layer(
    "GeoJsonLayer",
    # ...
    pickable=True,  # Activer seulement si nécessaire
    auto_highlight=False,  # Désactiver si non utilisé
)
```

### 4.3 Tooltips et Interactions
- Limitation des informations dans les tooltips
- Utilisation de styles CSS simples
- Éviter les calculs complexes dans les tooltips

## 5. Leçons Apprises

### 5.1 Tooltips dans PyDeck
- Les tooltips dans PyDeck GeoJSON Layer accèdent directement aux propriétés du feature
- La syntaxe {nom} fonctionne pour les propriétés de premier niveau
- Éviter les syntaxes comme {object.properties.nom} ou {properties.nom}
- Pour formater les nombres, il faut le faire avant d'ajouter les données au GeoJSON

### 5.2 Contours des Polygones
- L'épaisseur des contours (get_line_width) doit être significative (>15) pour être visible
- Une valeur de 30 est recommandée pour une bonne visibilité à l'échelle départementale
- La couleur des contours doit contraster avec le remplissage (get_line_color)
- L'opacité (opacity) affecte à la fois le remplissage et les contours

## Conclusion

L'utilisation de Pydeck pour les applications cartographiques offre :
1. Une meilleure performance grâce au rendu WebGL
2. Une intégration native avec Streamlit
3. Un contrôle précis des propriétés visuelles
4. Une gestion efficace des grandes quantités de données

Recommandations principales :
- Optimiser les données géographiques en amont
- Utiliser le cache de manière appropriée
- Limiter les interactions complexes
- Tester la performance avec différents volumes de données 
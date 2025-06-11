# Guide de Gestion des Données Géographiques dans Streamlit

## Table des Matières
1. [Sources de Données](#1-sources-de-données)
2. [Optimisation des Géométries](#2-optimisation-des-géométries)
3. [Visualisation avec Folium](#3-visualisation-avec-folium)
4. [Bonnes Pratiques](#4-bonnes-pratiques)

## 1. Sources de Données

### 1.1 Formats Courants
- GeoJSON
- Shapefile
- PostGIS
- GeoPackage

### 1.2 Chargement des Données
```python
import geopandas as gpd

# Depuis un fichier GeoJSON
gdf = gpd.read_file("communes.geojson")

# Depuis PostGIS
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:password@localhost:5432/db')
gdf = gpd.read_postgis("SELECT * FROM communes", engine)
```

## 2. Optimisation des Géométries

### 2.1 Simplification
```python
def optimize_geometries(gdf, tolerance=0.001):
    """
    Simplifie les géométries tout en préservant la topologie.
    
    Args:
        gdf (GeoDataFrame): Les données géographiques
        tolerance (float): Niveau de simplification
    """
    # Copie pour éviter la modification en place
    gdf = gdf.copy()
    
    # Simplification avec préservation de la topologie
    gdf.geometry = gdf.geometry.simplify(
        tolerance=tolerance,
        preserve_topology=True
    )
    
    return gdf
```

### 2.2 Réduction de la Précision
```python
def reduce_precision(gdf, precision=3):
    """
    Réduit la précision des coordonnées.
    
    Args:
        gdf (GeoDataFrame): Les données géographiques
        precision (int): Nombre de décimales à conserver
    """
    def round_coordinates(geom):
        return geom.round_coords(precision)
    
    gdf.geometry = gdf.geometry.apply(round_coordinates)
    return gdf
```

## 3. Visualisation avec Folium

### 3.1 Configuration de Base
```python
def create_base_map(center=[46.603354, 1.888334], zoom=6):
    """
    Crée une carte de base optimisée.
    """
    return folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='CartoDB positron',
        prefer_canvas=True,
        disable_3d=True
    )
```

### 3.2 Couche Choroplèthe
```python
def add_choropleth_layer(m, gdf, value_column, legend_name):
    """
    Ajoute une couche choroplèthe optimisée.
    """
    return folium.Choropleth(
        geo_data=gdf.__geo_interface__,
        data=gdf,
        columns=['id', value_column],
        key_on='feature.properties.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        line_weight=0.5,
        legend_name=legend_name,
        smooth_factor=3
    ).add_to(m)
```

### 3.3 Tooltips Optimisés
```python
def add_tooltips(m, gdf, fields, aliases):
    """
    Ajoute des tooltips optimisés.
    """
    folium.GeoJson(
        gdf.__geo_interface__,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'transparent'
        },
        tooltip=folium.GeoJsonTooltip(
            fields=fields,
            aliases=aliases,
            sticky=False,
            labels=True
        )
    ).add_to(m)
```

## 4. Bonnes Pratiques

### 4.1 Gestion de la Mémoire
```python
# Nettoyer les colonnes inutiles
gdf = gdf[['geometry', 'id', 'name', 'value']]

# Convertir en types appropriés
gdf['id'] = gdf['id'].astype('category')
```

### 4.2 Mise en Cache
```python
@st.cache_data
def load_and_prepare_data(url, tolerance=0.001):
    # Téléchargement
    gdf = gpd.read_file(url)
    
    # Optimisation
    gdf = optimize_geometries(gdf, tolerance)
    gdf = reduce_precision(gdf)
    
    return gdf
```

### 4.3 Gestion des Erreurs
```python
def safe_load_geodata(url):
    try:
        with st.spinner('Chargement des données...'):
            gdf = gpd.read_file(url)
        return gdf
    except Exception as e:
        st.error(f"Erreur de chargement : {str(e)}")
        return None
```

## Problèmes Courants et Solutions

### 1. Données Volumineuses
- Problème : Temps de chargement et de rendu excessifs
- Solution : 
  - Simplification des géométries
  - Mise en cache des données
  - Chargement progressif

### 2. Précision vs Performance
- Problème : Équilibre entre qualité visuelle et performance
- Solution :
  - Ajuster la tolérance selon le niveau de zoom
  - Utiliser différents niveaux de détail

### 3. Mémoire
- Problème : Consommation excessive de mémoire
- Solution :
  - Nettoyage des données non utilisées
  - Optimisation des types de données
  - Streaming pour les grands ensembles

## Conclusion

La gestion efficace des données géographiques nécessite :
1. Une stratégie d'optimisation claire
2. Un équilibre entre performance et précision
3. Une bonne compréhension des outils disponibles
4. Une approche itérative du développement 
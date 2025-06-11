# Guide d'Optimisation des Performances pour Applications Streamlit

## Table des Matières
1. [Mise en Cache](#1-mise-en-cache)
2. [Optimisation des Données](#2-optimisation-des-données)
3. [Gestion de la Mémoire](#3-gestion-de-la-mémoire)
4. [Optimisation du Rendu](#4-optimisation-du-rendu)

## 1. Mise en Cache

### 1.1 Types de Cache Streamlit
```python
# Cache de données (pour les DataFrames, fichiers, etc.)
@st.cache_data
def load_data():
    return pd.read_csv("large_file.csv")

# Cache de ressources (pour les connexions DB, modèles ML, etc.)
@st.cache_resource
def get_database_connection():
    return create_connection()
```

### 1.2 Bonnes Pratiques de Cache
- Utiliser `show_spinner=False` pour réduire le bruit visuel
- Éviter de mettre en cache des objets mutables
- Gérer les paramètres non-hachables avec le préfixe `_`

## 2. Optimisation des Données

### 2.1 Chargement de Données
```python
# Charger uniquement les colonnes nécessaires
df = pd.read_csv("data.csv", usecols=['col1', 'col2'])

# Utiliser les types de données appropriés
df['category'] = df['category'].astype('category')
```

### 2.2 Données Géographiques
```python
def optimize_geodata(gdf, tolerance=0.001):
    # Simplifier les géométries
    gdf.geometry = gdf.geometry.simplify(tolerance)
    
    # Réduire la précision des coordonnées
    gdf = gdf.round(3)
    
    return gdf
```

## 3. Gestion de la Mémoire

### 3.1 Nettoyage des Données
```python
# Supprimer les colonnes inutiles
df = df.drop(columns=['unused_col'])

# Convertir en types plus efficaces
df['date'] = pd.to_datetime(df['date'])
df['id'] = df['id'].astype('int32')
```

### 3.2 Gestion des Sessions
```python
# Réinitialiser les variables de session si nécessaire
if st.button('Reset'):
    for key in st.session_state.keys():
        del st.session_state[key]
```

## 4. Optimisation du Rendu

### 4.1 Interface Utilisateur
```python
# Utiliser des conteneurs pour organiser le contenu
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        # Contenu léger
    with col2:
        # Contenu lourd
```

### 4.2 Cartes Interactives
```python
# Configuration optimisée pour Folium
m = folium.Map(
    prefer_canvas=True,
    disable_3d=True,
    zoom_control=False
)

# Réduire la complexité des tooltips
tooltip = folium.GeoJsonTooltip(
    fields=['name'],
    sticky=False
)
```

### 4.3 Graphiques et Visualisations
```python
# Limiter le nombre de points affichés
@st.cache_data
def downsample_data(df, n=1000):
    return df.sample(n=min(len(df), n))
```

## Bonnes Pratiques Générales

1. **Profilage et Monitoring**
   ```python
   import cProfile
   
   def profile_function():
       pr = cProfile.Profile()
       pr.enable()
       # Code à profiler
       pr.disable()
       pr.print_stats(sort='cumtime')
   ```

2. **Gestion des Ressources**
   ```python
   # Utiliser des gestionnaires de contexte
   with tempfile.TemporaryDirectory() as temp_dir:
       # Traitement temporaire
   ```

3. **Feedback Utilisateur**
   ```python
   with st.spinner('Opération en cours...'):
       # Opération longue
   st.success('Terminé!')
   ```

## Problèmes Courants et Solutions

### 1. Lenteur au Démarrage
- Problème : L'application met du temps à démarrer
- Solution : Différer le chargement des composants lourds

### 2. Consommation Mémoire Excessive
- Problème : L'application consomme trop de mémoire
- Solution : Nettoyer les données et utiliser le streaming

### 3. Latence d'Interaction
- Problème : Les interactions sont lentes
- Solution : Optimiser les callbacks et utiliser la mise en cache

## Conclusion

L'optimisation des performances est un processus itératif qui nécessite :
1. L'identification des goulots d'étranglement
2. La mesure des améliorations
3. L'équilibre entre fonctionnalités et performance
4. Une maintenance continue 
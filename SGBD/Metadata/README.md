# Métadonnées des Jeux de Données

## Vue d'ensemble

Ce dossier contient les métadonnées de tous les jeux de données importés dans le système, organisés par producteur et par thématique.

## Connexion à la Base Metadata

### Fichier de Connexion Principal

**`db_connection.py`** - Module unifié pour accéder à la base metadata sur neon.tech

#### Fonctions principales :

```python
from db_connection import analyze_table_metadata, get_table_metadata, list_all_tables

# Analyse complète d'une table (affichage formaté)
analyze_table_metadata('activite_residents_2016')

# Récupération des métadonnées sous forme de dictionnaire
metadata = get_table_metadata('activite_residents_2016')

# Liste de toutes les tables disponibles
tables = list_all_tables()
```

#### Usage en ligne de commande :

```bash
# Test de connexion + liste des tables
python db_connection.py

# Analyse rapide d'une table
python -c "from db_connection import analyze_table_metadata; analyze_table_metadata('nom_table')"
```

### ⚠️ Règles importantes :

1. **NE CRÉEZ PAS** de nouveaux scripts de connexion
2. **UTILISEZ TOUJOURS** `db_connection.py` pour accéder à la base metadata
3. **AJOUTEZ** de nouvelles fonctions au module existant si nécessaire
4. **DOCUMENTEZ** toute modification dans ce README

## Structure des Métadonnées

### Producteurs organisés :

- **INSEE/** : Données statistiques nationales (population, économie, logement)
- **Ministère de la Transition Écologique/** : Données énergétiques et environnementales  
- **Sit@del/** : Permis de construire (logements et locaux non-résidentiels)
- **Spallian/** : Données spécifiques (SCOD fréquentation)

### Exports :

- `Export/metadata_export_YYYYMMDD.csv` : Exports périodiques de la base metadata

## Maintenance

### Ajout de nouvelles métadonnées :
1. Utiliser l'interface Streamlit (Catalogue.py) pour la saisie
2. Vérifier la cohérence avec `analyze_table_metadata('nom_table')`
3. Exporter via `export_metadata.py` si nécessaire

### Dépannage :
```bash
# Test de connexion
python db_connection.py

# Vérification d'une table spécifique
python -c "from db_connection import get_table_metadata; print(get_table_metadata('nom_table'))"
```

## Structure des Fichiers

```
Metadata/
├── db_connection.py              # ⭐ FICHIER PRINCIPAL DE CONNEXION
├── export_metadata.py            # Export périodique des métadonnées
├── Export/                       # Exports CSV archivés
│   └── metadata_export_*.csv
├── INSEE/                        # Métadonnées INSEE organisées
│   ├── Economie/
│   ├── Population/
│   └── Logement/
└── README.md                     # Cette documentation
```

**Utilisez uniquement `db_connection.py` pour toute interaction avec la base metadata.**

## Structure des métadonnées

Pour chaque source de données, les métadonnées contiennent les informations suivantes :
- Description générale du jeu de données
- Schéma de la base de données
- Description des tables et champs
- Périodicité de mise à jour
- Source et date d'acquisition
- Format des données
- Clés de jointure avec d'autres jeux de données

## Sources de données

### 1. INSEE
- Données statistiques nationales
- Recensement de la population
- Indicateurs économiques
- Données démographiques

### 2. Spallian
- Données spécifiques à l'organisation
- Informations sectorielles
- Données géographiques

### 3. Sit@del (permis de construire)
- Données sur les permis de construire
- Informations urbanistiques
- Données de construction

### 4. Citepa (GES)
- Données sur les Gaz à Effet de Serre
- Inventaires d'émissions
- Indicateurs environnementaux

### 5. Ministère de la Transition Ecologique
- Données environnementales
- Politiques publiques
- Réglementations

### 6. Météo France
- Données météorologiques
- Historiques climatiques
- Prévisions

## Format des métadonnées

Les métadonnées sont stockées dans des fichiers au format suivant :
- JSON pour la structure des données
- Markdown pour la documentation
- SQL pour les schémas de base de données

## Mise à jour des métadonnées

Procédure à suivre lors de l'ajout ou de la modification d'un jeu de données :
1. Créer ou mettre à jour le fichier de métadonnées correspondant
2. Documenter les changements dans le fichier CHANGELOG.md
3. Vérifier la cohérence avec les autres jeux de données
4. Mettre à jour les requêtes SQL si nécessaire

## Bonnes pratiques

1. Documentation :
   - Maintenir à jour la description des champs
   - Documenter les transformations de données
   - Noter les limitations et contraintes

2. Organisation :
   - Utiliser des noms de fichiers explicites
   - Structurer les métadonnées de manière cohérente
   - Maintenir un historique des modifications

3. Qualité :
   - Vérifier la complétude des informations
   - S'assurer de la cohérence des formats
   - Documenter les anomalies connues 
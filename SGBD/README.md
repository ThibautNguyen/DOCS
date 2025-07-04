# Gestion des Bases de Données (SGBD)

## Vue d'ensemble

Ce dossier contient l'ensemble des éléments liés à la gestion des bases de données du système d'information, géré via DBeaver.

## Structure

Le dossier SGBD est organisé en deux composants principaux :

### 1. Metadata/
Contient les métadonnées des différents jeux de données importés, organisés par source :
- INSEE : Données statistiques nationales
- Spallian : Données spécifiques
- Sit@del : Données des permis de construire
- Citepa : Données sur les Gaz à Effet de Serre (GES)
- MTES : Données du Ministère de la Transition Écologique
- Météo France : Données météorologiques

#### Connexion à la base metadata
**Fichier principal :** `Metadata/db_connection.py`

Ce module fournit une interface unifiée pour se connecter à la base metadata sur neon.tech :

```python
from SGBD.Metadata.db_connection import analyze_table_metadata, get_table_metadata

# Analyse complète d'une table
analyze_table_metadata('activite_residents_2016')

# Récupération des métadonnées en dictionnaire
metadata = get_table_metadata('activite_residents_2016')
```

**Usage rapide en ligne de commande :**
```bash
python SGBD/Metadata/db_connection.py  # Test de connexion
python -c "from SGBD.Metadata.db_connection import analyze_table_metadata; analyze_table_metadata('nom_table')"
```

### 2. SQL Queries/
Regroupe les requêtes SQL organisées par thématique :
- Économie
- Environnement
- Énergie
- Logement
- Population

## Gestion des données

### Outils utilisés
- DBeaver : Interface de gestion des bases de données
- PostgreSQL : Système de gestion de base de données principal
- Neon.tech : Hébergement de la base metadata

### Bonnes pratiques
1. Documentation des métadonnées :
   - Description des champs
   - Sources des données
   - Périodicité de mise à jour
   - Format des données

2. Organisation des requêtes SQL :
   - Commentaires détaillés en en-tête
   - Documentation des paramètres
   - Explication des résultats attendus
   - Versioning des requêtes

3. Connexion aux bases :
   - **Utilisez toujours `db_connection.py`** pour accéder à la base metadata
   - Ne créez pas de nouveaux scripts de connexion redondants
   - Documentez les nouvelles fonctions dans le module principal

## Maintenance

Pour maintenir la cohérence des données :
1. Mettre à jour les métadonnées lors de l'import de nouveaux jeux de données
2. Documenter les modifications des schémas de base de données
3. Tester les requêtes SQL après chaque mise à jour de la structure
4. Utiliser le module `db_connection.py` pour toute analyse de métadonnées

## Liens utiles
- [Documentation DBeaver](https://dbeaver.io/docs/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Neon.tech Documentation](https://neon.tech/docs/) 
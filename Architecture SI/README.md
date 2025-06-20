# README TECHNIQUE : Architecture Hybride SGBD + BI

## 1. Vue d'ensemble

Ce document formalise une architecture hybride de système d'information combinant :
- ne interface open-source légère (Metabase Community ou Streamlit)
- une interface professionnelle pour la restitution haut de gamme (Power BI Pro / Service)

L'objectif est de développer un système mutualisé, modulaire, sûr et évolutif pour la diffusion d'indicateurs et de tableaux de bord à partir de données territoriales stockées dans un socle PostgreSQL/PostGIS.

---

## 2. Objectifs de l'architecture

- Centralisation des données dans PostgreSQL
- Maintien de deux canaux de diffusion distincts mais synchronisés :
  - Open source (Metabase, Streamlit)
  - Propriétaire (Power BI)
- Contrôle des accès par canal et par client
- Gouvernance documentaire unifiée
- Souveraineté des données et scalabilité progressive

---

## 3. Schéma global

```plaintext
                     +-----------------------------+
                     |       Données sources       |
                     |  Open data, Excel, API,     |
                     |  CSV, QGIS, Shapefile…      |
                     +-------------+---------------+
                                   |
                        (Python / dbt / ETL)
                                   |
                +------------------v------------------+
                |         PostgreSQL / PostGIS        |
                |   Schémas thématiques (economie,    |
                |   logement, sante, etc.)            |
                +--------+---------------+------------+
                         |               |
     +-------------------v--+         +--v--------------------+
     |  Architecture 1 :     |         |  Architecture 3 :     |
     |  Metabase Community   |         |  Power BI Pro / Svc   |
     |  ou Streamlit         |         |  + Cloud PostgreSQL   |
     |  (local/VPS)          |         |  (Neon, Scaleway)     |
     +----------+------------+         +----------+-----------+
                |                                 |
       Accès direct pour                       Partage à
      collectivités, TPE                     clients Premium
      ou livrables open                      avec sécurité AD,
             source                           export Excel/PDF

                +----------------------------------+
                |        GitHub + Docs MDC         |
                |  Catalogage, README, dictionnaires |
                +----------------------------------+
```

---

## 4. Composants techniques

### Stockage principal
- PostgreSQL/PostGIS
- Organisation en schémas thématiques : `economie`, `logement`, `population`, `sante`, etc.
- Vues dédiées par canal : `vw_powerbi_*`, `vw_metabase_*`

### Traitements et ETL
- Python + pandas + SQLAlchemy
- dbt pour versionner et documenter les transformations
- Option : Airflow si automatisation complexe

### Restitution

#### Canal open source
- Metabase Community (ou Streamlit)
- Idéal pour diagnostics territoriaux mutualisés, open data, tests

#### Canal professionnel
- Power BI Pro / Service
- Connexion directe à PostgreSQL ou à des exports
- Publication clients avec sécurité avancée

### Documentation & gouvernance
- GitHub pour le versionnement (scripts, vues, README)
- `.MDC` (Markdown) pour chaque dataset
- Table `datasets_catalog` dans PostgreSQL

---

## 5. Organisation des accès

### Côté PostgreSQL
- Rôles : `lecteur_metabase`, `lecteur_powerbi`, `admin_donnees`
- Permissions par schéma et vue

### Côté visualisation
- Power BI : via Microsoft 365, row-level security
- Metabase : via collections, ou Keycloak en option

---

## 6. Workflow opérationnel

1. **Ingestion** : via Python vers schéma staging
2. **Transformation** : via dbt vers vues exposées
3. **Documentation** : via `.MDC` + table `datasets_catalog`
4. **Restitution** :
   - Canal 1 : Metabase / Streamlit
   - Canal 2 : Power BI
5. **Export** : PDF, Excel, JSON

---

## 7. Recommandations

- Centraliser les calculs dans PostgreSQL
- Ne pas dupliquer les logiques de transformation
- Automatiser les contrôles de qualité des données
- Documenter dans GitHub ou via `dbt docs`

---

## 8. Évolutions possibles

| Extension                        | Objectif                                      |
|----------------------------------|-----------------------------------------------|
| Keycloak + Streamlit Panel       | Gestion centralisée des accès multi-clients   |
| API interne (FastAPI)            | Ouverture vers des outils tiers               |
| Intégration Superset             | Visualisation open source avancée             |
| Dashboard de monitoring          | Usage, sécurité, performance                  |

---

## 9. Conclusion

Cette architecture hybride :
- combine performance et flexibilité
- garantit la souveraineté et la gouvernance
- s'adapte à la diversité des projets clients
- permet une montée en puissance progressive et maîtrisée

Elle repose sur un socle PostgreSQL unique, exposé à travers deux canaux complémentaires, et documenté de façon structurée.


## 10. Gestion des secrets et sécurité

### Structure des variables d'environnement
```
.env
├── .env.development    # Variables de développement
├── .env.production     # Variables de production
└── .env.example       # Template sans valeurs sensibles
```

### Variables sensibles à gérer
- Identifiants PostgreSQL
- Clés API (INSEE, etc.)
- Secrets Power BI
- Tokens d'authentification

### Bonnes pratiques
- Utilisation de `python-dotenv` pour le chargement
- Exclusion des fichiers `.env` du versionnement
- Rotation régulière des secrets
- Différenciation des accès par environnement
- Utilisation de secrets managers en production


## 11. Plan de migration des données

### Phase 1 : Préparation
1. **Audit des données existantes**
   - Inventaire des tables et schémas
   - Volume de données
   - Dépendances entre tables
   - Contraintes et index

2. **Nettoyage pré-migration**
   - Suppression des données obsolètes
   - Standardisation des formats
   - Validation des intégrités

### Phase 2 : Migration
1. **Structure**
   - Création des schémas
   - Définition des tables
   - Mise en place des index
   - Configuration des contraintes

2. **Données**
   - Migration par lots
   - Vérification des intégrités
   - Tests de performance

### Phase 3 : Validation
1. **Tests**
   - Requêtes de référence
   - Performances
   - Intégrité des données
   - Accès utilisateurs

2. **Documentation**
   - Schéma de la base
   - Procédures de maintenance
   - Procédures de backup

### Scripts de migration
```python
# Exemple de script de migration par lots
import psycopg2
from dotenv import load_dotenv
import os

def migrate_data():
    load_dotenv()
    
    # Connexions source et destination
    source_conn = psycopg2.connect(
        host=os.getenv('SOURCE_POSTGRES_HOST'),
        database=os.getenv('SOURCE_POSTGRES_DB'),
        user=os.getenv('SOURCE_POSTGRES_USER'),
        password=os.getenv('SOURCE_POSTGRES_PASSWORD')
    )
    
    dest_conn = psycopg2.connect(
        host=os.getenv('DEST_POSTGRES_HOST'),
        database=os.getenv('DEST_POSTGRES_DB'),
        user=os.getenv('DEST_POSTGRES_USER'),
        password=os.getenv('DEST_POSTGRES_PASSWORD')
    )
    
    try:
        with source_conn.cursor() as source_cur:
            with dest_conn.cursor() as dest_cur:
                # Migration par lots de 1000 enregistrements
                source_cur.execute("SELECT * FROM ma_table")
                while True:
                    rows = source_cur.fetchmany(1000)
                    if not rows:
                        break
                    dest_cur.executemany(
                        "INSERT INTO ma_table VALUES (%s, %s, %s)",
                        rows
                    )
                    dest_conn.commit()
    finally:
        source_conn.close()
        dest_conn.close()
```

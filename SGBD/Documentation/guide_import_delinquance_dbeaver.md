# Guide d'Import des Données de Délinquance 2024 via DBeaver

## 📋 Vue d'ensemble

Ce guide détaille la procédure d'importation des données de délinquance départementale et régionale 2024 du Ministère de l'Intérieur dans une base PostgreSQL via DBeaver.

## 📊 Métadonnées des jeux de données

### **Base statistique départementale de la délinquance**
- **Nom du jeu** : `delinquance_2024_dep`
- **Table cible** : `securite.delinquance_2024_dep`
- **Producteur** : Ministère de l'Intérieur (SSMSI)
- **Granularité** : Département
- **Millésime** : 2024

### **Base statistique régionale de la délinquance**
- **Nom du jeu** : `delinquance_2024_reg`
- **Table cible** : `securite.delinquance_2024_reg`
- **Producteur** : Ministère de l'Intérieur (SSMSI)
- **Granularité** : Région
- **Millésime** : 2024

## 🔗 Source des données

**URL** : https://www.data.gouv.fr/fr/datasets/bases-statistiques-communale-departementale-et-regionale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales/

**Licence** : Licence Ouverte Etalab

## 📝 Structure des données

### Colonnes communes aux deux jeux de données :

| Colonne | Type | Description |
|---------|------|-------------|
| `code_departement`/`code_region` | VARCHAR | Code officiel géographique |
| `annee` | INTEGER | Année d'enregistrement de la délinquance |
| `indicateur` | TEXT | Indicateur des crimes et délits |
| `unite_de_compte` | TEXT | Unité de compte associée à l'indicateur |
| `nombre` | INTEGER | Nombre de faits de délinquance enregistrés |
| `taux_pour_mille` | DECIMAL(10,3) | Taux pour 1 000 habitants/logements |
| `est_diffuse` | BOOLEAN | Indicateur de secret statistique |
| `insee_pop` | INTEGER | Population municipale |
| `insee_pop_millesime` | INTEGER | Année de recensement population |
| `insee_log` | INTEGER | Nombre de logements |
| `insee_log_millesime` | INTEGER | Année de recensement logements |

## 🛠️ Procédure d'import step-by-step

### **Étape 1 : Préparation de la base de données**

1. **Ouvrir DBeaver** et se connecter à votre base PostgreSQL
2. **Exécuter le script de création** : `SGBD/SQL Queries/import_delinquance_2024.sql`
   - Ce script créera automatiquement :
     - Le schéma `securite`
     - Les tables `delinquance_2024_dep` et `delinquance_2024_reg`
     - Les index d'optimisation
     - Les commentaires explicatifs

### **Étape 2 : Téléchargement des données**

1. **Aller sur data.gouv.fr** : [Lien direct](https://www.data.gouv.fr/fr/datasets/bases-statistiques-communale-departementale-et-regionale-de-la-delinquance-enregistree-par-la-police-et-la-gendarmerie-nationales/)

2. **Télécharger les fichiers CSV** :
   - 📁 `bases-statistiques-departementale-delinquance-2024.csv`
   - 📁 `bases-statistiques-regionale-delinquance-2024.csv`

### **Étape 3 : Import des données départementales**

1. **Dans DBeaver**, naviguer vers `opendata` → `Schemas` → `securite` → `Tables`
2. **Clic droit** sur `delinquance_2024_dep` → **"Import Data"**
3. **Sélectionner "CSV"** comme source de données
4. **Choisir le fichier** `bases-statistiques-departementale-delinquance-2024.csv`

#### Configuration de l'import :

**Paramètres généraux :**
- ✅ **Separator** : `;` (point-virgule)
- ✅ **Encoding** : `UTF-8`
- ✅ **Header** : `First line contains column headers`
- ✅ **Quote Character** : `"` (guillemets doubles)

**Correspondance des colonnes :**

| Colonne CSV | Colonne Table | Type | Remarques |
|-------------|---------------|------|-----------|
| `Code departement` | `code_departement` | VARCHAR(3) | |
| `annee` | `annee` | INTEGER | |
| `indicateur` | `indicateur` | TEXT | |
| `unite de compte` | `unite_de_compte` | TEXT | |
| `nombre` | `nombre` | INTEGER | |
| `taux_pour_mille` | `taux_pour_mille` | DECIMAL | |
| `est_diffuse` | `est_diffuse` | BOOLEAN | Convertir `true`/`false` |
| `insee_pop` | `insee_pop` | INTEGER | |
| `insee_pop_millesime` | `insee_pop_millesime` | INTEGER | |
| `insee_log` | `insee_log` | INTEGER | |
| `insee_log_millesime` | `insee_log_millesime` | INTEGER | |

5. **Valider la configuration** et lancer l'import

### **Étape 4 : Import des données régionales**

1. **Clic droit** sur `delinquance_2024_reg` → **"Import Data"**
2. **Répéter la même procédure** avec le fichier régional
3. **Adapter la correspondance** : `Code region` → `code_region`

### **Étape 5 : Validation post-import**

Exécuter les requêtes de contrôle suivantes :

```sql
-- Vérification départementale
SELECT 
    COUNT(*) as total_lignes,
    COUNT(DISTINCT code_departement) as nb_departements,
    COUNT(DISTINCT indicateur) as nb_indicateurs,
    MIN(annee) as annee_min,
    MAX(annee) as annee_max
FROM securite.delinquance_2024_dep;

-- Vérification régionale
SELECT 
    COUNT(*) as total_lignes,
    COUNT(DISTINCT code_region) as nb_regions,
    COUNT(DISTINCT indicateur) as nb_indicateurs,
    MIN(annee) as annee_min,
    MAX(annee) as annee_max
FROM securite.delinquance_2024_reg;
```

**Résultats attendus :**
- **Départements** : ~101 départements français
- **Régions** : ~18 régions françaises
- **Années** : Multiple années disponibles
- **Indicateurs** : Plusieurs dizaines d'indicateurs de délinquance

## ⚠️ Points d'attention

### **Gestion des erreurs communes :**

1. **Erreur d'encodage** :
   - Vérifier que l'encodage est bien en `UTF-8`
   - Possible alternative : `ISO-8859-1` ou `Windows-1252`

2. **Erreur de séparateur** :
   - Confirmer que le séparateur est `;` (point-virgule)
   - Vérifier dans un éditeur de texte si nécessaire

3. **Erreur de type boolean** :
   - La colonne `est_diffuse` peut contenir `1`/`0` au lieu de `true`/`false`
   - Configurer la conversion dans DBeaver

4. **Valeurs nulles** :
   - Les colonnes `taux_pour_mille`, `insee_pop`, `insee_log` peuvent contenir des valeurs nulles
   - C'est normal pour certains indicateurs

### **Optimisations post-import :**

```sql
-- Mise à jour des statistiques
ANALYZE securite.delinquance_2024_dep;
ANALYZE securite.delinquance_2024_reg;

-- Vérification des index
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'securite';
```

## 📈 Utilisation des données

### **Exemples de requêtes d'analyse :**

```sql
-- Top 10 des départements avec le plus de vols
SELECT 
    code_departement,
    SUM(nombre) as total_vols
FROM securite.delinquance_2024_dep
WHERE indicateur ILIKE '%vol%'
  AND annee = 2024
GROUP BY code_departement
ORDER BY total_vols DESC
LIMIT 10;

-- Évolution par région d'un indicateur spécifique
SELECT 
    code_region,
    annee,
    SUM(nombre) as total_faits
FROM securite.delinquance_2024_reg
WHERE indicateur = 'Coups et blessures volontaires'
GROUP BY code_region, annee
ORDER BY code_region, annee;
```

## 🔄 Maintenance et mise à jour

- **Fréquence** : Annuelle (selon les métadonnées)
- **Source** : Surveillance de la page data.gouv.fr
- **Procédure** : Répéter les étapes d'import avec les nouvelles données

## 📞 Support

En cas de problème :
1. Vérifier les logs d'import dans DBeaver
2. Consulter la documentation data.gouv.fr
3. Valider la structure des fichiers CSV téléchargés

---
*Guide créé le 2025-06-25 - Basé sur les métadonnées du Ministère de l'Intérieur* 
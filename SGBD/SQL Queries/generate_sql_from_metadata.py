#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer automatiquement du SQL d'import basé sur les métadonnées.
Utilise l'infrastructure existante de metadata_app_clean.
"""

import sys
import os
from pathlib import Path
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# Ajout du répertoire metadata_app_clean au PYTHONPATH
metadata_app_path = Path(__file__).parent.parent.parent / "metadata_app_clean"
sys.path.append(str(metadata_app_path))

try:
    from utils.db_utils import get_db_connection
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous d'être dans le bon répertoire et que metadata_app_clean/utils/db_utils.py existe")
    sys.exit(1)

def infer_sql_type(column_name: str, sample_values: List, dict_info: Optional[Dict] = None) -> str:
    """
    Inférence intelligente du type SQL basée sur le nom de colonne, les valeurs d'exemple et le dictionnaire.
    """
    # Nettoyer les valeurs d'exemple (enlever les None et valeurs vides)
    clean_values = [str(v).strip() for v in sample_values if v is not None and str(v).strip()]
    
    # 1. Priorité au dictionnaire si disponible
    if dict_info and 'Type' in dict_info:
        type_desc = dict_info['Type'].lower()
        
        if 'texte' in type_desc:
            # Extraire la longueur si spécifiée (ex: "Texte (50)")
            import re
            match = re.search(r'\((\d+)\)', type_desc)
            if match:
                length = int(match.group(1))
                return f'VARCHAR({length})'
            else:
                return 'VARCHAR(255)'
        elif any(keyword in type_desc for keyword in ['entier', 'integer', 'nombre']):
            return 'INTEGER'
        elif any(keyword in type_desc for keyword in ['decimal', 'réel', 'float']):
            return 'DECIMAL(10,3)'
        elif any(keyword in type_desc for keyword in ['booléen', 'boolean']):
            return 'BOOLEAN'
        elif any(keyword in type_desc for keyword in ['date']):
            return 'DATE'
    
    # 2. Analyse du nom de colonne pour des patterns spécifiques
    col_lower = column_name.lower()
    
    # Codes géographiques
    if col_lower in ['codgeo', 'code_insee', 'insee']:
        return 'VARCHAR(5)'
    elif any(pattern in col_lower for pattern in ['code_dep', 'dep']):
        return 'VARCHAR(3)'
    elif any(pattern in col_lower for pattern in ['code_reg', 'reg']):
        return 'VARCHAR(2)'
    elif col_lower.startswith('code') or col_lower.endswith('_id'):
        return 'VARCHAR(20)'
    
    # Dates et années
    elif any(pattern in col_lower for pattern in ['annee', 'year']):
        return 'INTEGER'
    elif any(pattern in col_lower for pattern in ['date', 'timestamp']):
        return 'DATE'
    
    # Pourcentages et taux
    elif any(pattern in col_lower for pattern in ['taux', '%', 'pct', 'pourcentage', 'part']):
        return 'DECIMAL(5,2)'
    
    # Nombres et quantités
    elif any(pattern in col_lower for pattern in ['nombre', 'nb', 'count', 'total', 'pop', 'log']):
        return 'INTEGER'
    
    # Noms et libellés
    elif any(pattern in col_lower for pattern in ['nom', 'libelle', 'lib', 'designation', 'commune']):
        return 'VARCHAR(255)'
    
    # 3. Analyse des valeurs d'exemple
    if clean_values:
        # Test si toutes les valeurs sont des entiers
        try:
            all_integers = all(str(v).replace('-', '').isdigit() for v in clean_values)
            if all_integers:
                # Vérifier la taille des entiers
                max_val = max(abs(int(v)) for v in clean_values)
                if max_val < 32768:
                    return 'SMALLINT'
                elif max_val < 2147483648:
                    return 'INTEGER'
                else:
                    return 'BIGINT'
        except (ValueError, TypeError):
            pass
        
        # Test si toutes les valeurs sont des décimaux
        try:
            all_decimals = all(isinstance(float(str(v).replace(',', '.')), float) for v in clean_values)
            if all_decimals:
                return 'DECIMAL(10,3)'
        except (ValueError, TypeError):
            pass
        
        # Test pour les dates (format YYYY-MM-DD)
        try:
            if all(len(str(v)) == 10 and str(v).count('-') == 2 for v in clean_values):
                return 'DATE'
        except:
            pass
        
        # Test pour les booléens
        boolean_values = {'true', 'false', '1', '0', 'oui', 'non', 'yes', 'no'}
        if all(str(v).lower() in boolean_values for v in clean_values):
            return 'BOOLEAN'
        
        # Déterminer la longueur maximum pour VARCHAR
        max_length = max(len(str(v)) for v in clean_values) if clean_values else 50
        
        if max_length <= 10:
            return 'VARCHAR(20)'
        elif max_length <= 50:
            return 'VARCHAR(100)'
        elif max_length <= 255:
            return 'VARCHAR(255)'
        else:
            return 'TEXT'
    
    # 4. Par défaut
    return 'TEXT'

def generate_import_sql_from_metadata(table_name: str) -> str:
    """
    Génère une requête SQL d'import complète basée sur les métadonnées stockées.
    """
    try:
        # Connexion à la base de métadonnées
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupération des métadonnées
        cursor.execute("SELECT * FROM metadata WHERE nom_table = %s", (table_name,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError(f"Table '{table_name}' non trouvée dans la base de métadonnées")
        
        # Conversion en dictionnaire
        columns = [desc[0] for desc in cursor.description]
        metadata = dict(zip(columns, result))
        
        # Extraction des informations principales
        nom_table = metadata.get('nom_table', 'unknown_table')
        schema = metadata.get('schema', 'public')
        nom_base = metadata.get('nom_base', 'database')
        description = metadata.get('description', '')
        producteur = metadata.get('producteur', '')
        type_donnees = metadata.get('type_donnees', '')
        
        # Extraction du contenu CSV et du dictionnaire
        contenu_csv = metadata.get('contenu_csv', {})
        dictionnaire = metadata.get('dictionnaire', {})
        
        # Vérification de la présence des en-têtes CSV
        if not contenu_csv or 'header' not in contenu_csv:
            raise ValueError(f"Structure CSV non disponible pour la table '{table_name}'")
        
        colonnes = contenu_csv['header']
        separateur = contenu_csv.get('separator', ';')
        donnees_exemple = contenu_csv.get('data', [])
        
        # Création du dictionnaire des variables pour l'inférence de type
        dict_mapping = {}
        if dictionnaire and 'header' in dictionnaire and 'data' in dictionnaire:
            dict_headers = dictionnaire['header']
            dict_data = dictionnaire['data']
            
            # Pour chaque ligne du dictionnaire, créer un mapping nom_colonne -> infos
            for row in dict_data:
                if len(row) >= len(dict_headers):
                    # Créer un dict avec les infos de cette variable
                    var_info = dict(zip(dict_headers, row))
                    # La première colonne est généralement le nom de la variable
                    if dict_headers and row:
                        var_name = row[0]  # Nom de la variable
                        dict_mapping[var_name] = var_info
        
        # Génération du SQL
        sql_lines = []
        sql_lines.append("-- =====================================================================================")
        sql_lines.append(f"-- SCRIPT D'IMPORT POUR LA TABLE {nom_table}")
        sql_lines.append("-- =====================================================================================")
        sql_lines.append(f"-- Producteur: {producteur}")
        sql_lines.append(f"-- Type de données: {type_donnees}")
        sql_lines.append(f"-- Schéma: {schema}")
        sql_lines.append(f"-- Base de données: {nom_base}")
        sql_lines.append(f"-- Description: {description}")
        sql_lines.append(f"-- Généré automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sql_lines.append("-- =====================================================================================")
        sql_lines.append("")
        
        # 1. Création du schéma
        sql_lines.append("-- 1. Création du schéma (si nécessaire)")
        sql_lines.append(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')
        sql_lines.append("")
        
        # 2. Suppression de la table existante
        sql_lines.append("-- 2. Suppression de la table existante (si elle existe)")
        sql_lines.append(f'DROP TABLE IF EXISTS "{schema}"."{nom_table}";')
        sql_lines.append("")
        
        # 3. Création de la table avec inférence de types
        sql_lines.append("-- 3. Création de la table avec types optimisés")
        sql_lines.append(f'CREATE TABLE "{schema}"."{nom_table}" (')
        
        column_definitions = []
        for i, col in enumerate(colonnes):
            # Nettoyage du nom de colonne (conserver le nom original autant que possible)
            col_clean = col.strip()
            
            # Récupération des valeurs d'exemple pour cette colonne
            sample_values = [row[i] if len(row) > i else None for row in donnees_exemple]
            
            # Recherche des informations du dictionnaire
            dict_info = dict_mapping.get(col, {})
            
            # Inférence du type SQL
            sql_type = infer_sql_type(col_clean, sample_values, dict_info)
            
            # Ajout de contraintes spéciales
            constraints = []
            if col_clean.lower() in ['code_insee', 'codgeo']:
                constraints.append("NOT NULL")
            
            constraint_str = " " + " ".join(constraints) if constraints else ""
            
            column_definitions.append(f'    "{col_clean}" {sql_type}{constraint_str}')
        
        sql_lines.append(",\n".join(column_definitions))
        sql_lines.append(");")
        sql_lines.append("")
        
        # 4. Commentaires sur la table
        sql_lines.append("-- 4. Commentaires sur la table")
        safe_description = description.replace("'", "''")
        sql_lines.append(f'COMMENT ON TABLE "{schema}"."{nom_table}" IS \'{safe_description} (Producteur: {producteur})\';')
        sql_lines.append("")
        
        # 5. Import des données
        sql_lines.append("-- 5. Import des données")
        sql_lines.append("-- ATTENTION: Modifier le chemin vers votre fichier CSV")
        sql_lines.append(f'COPY "{schema}"."{nom_table}" FROM \'/chemin/vers/votre/{nom_table}.csv\'')
        sql_lines.append(f"WITH (FORMAT csv, HEADER true, DELIMITER '{separateur}', ENCODING 'UTF8');")
        sql_lines.append("")
        
        # 6. Index recommandés
        sql_lines.append("-- 6. Index recommandés")
        for col in colonnes:
            col_clean = col.strip()
            
            if any(pattern in col.lower() for pattern in ['code', 'id', 'insee', 'commune', 'geo', 'date']):
                index_name = f"idx_{nom_table}_{re.sub(r'[^a-zA-Z0-9_]', '_', col_clean.lower())}"
                sql_lines.append(f'CREATE INDEX IF NOT EXISTS {index_name} ON "{schema}"."{nom_table}" ("{col_clean}");')
        
        sql_lines.append("")
        
        # 7. Vérification de l'import
        sql_lines.append("-- 7. Vérification de l'import")
        sql_lines.append(f'SELECT COUNT(*) as nb_lignes_importees FROM "{schema}"."{nom_table}";')
        sql_lines.append("")
        sql_lines.append("-- 8. Aperçu des données importées")
        sql_lines.append(f'SELECT * FROM "{schema}"."{nom_table}" LIMIT 5;')
        
        conn.close()
        return "\n".join(sql_lines)
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du SQL : {str(e)}")
        raise

def main():
    """Fonction principale du script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Génère du SQL d\'import depuis les métadonnées')
    parser.add_argument('table_name', help='Nom de la table dans la base de métadonnées')
    parser.add_argument('-o', '--output', help='Fichier de sortie (optionnel)')
    
    args = parser.parse_args()
    
    try:
        print(f"🔍 Recherche des métadonnées pour '{args.table_name}'...")
        sql_generated = generate_import_sql_from_metadata(args.table_name)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(sql_generated)
            print(f"✅ SQL généré et sauvegardé dans {args.output}")
        else:
            print("\n" + "="*80)
            print(sql_generated)
            print("="*80)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
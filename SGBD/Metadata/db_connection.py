#!/usr/bin/env python3
"""
Module de connexion à la base de données metadata sur neon.tech

Ce module fournit une interface simple pour se connecter à la base metadata
et exécuter des requêtes d'analyse des métadonnées.

Usage:
    from db_connection import get_metadata_connection, analyze_table_metadata
    
    # Connexion simple
    conn = get_metadata_connection()
    
    # Analyse complète d'une table
    analyze_table_metadata('activite_residents_2016')
"""

import psycopg2
import json
from typing import Optional, Dict, Any

# Configuration de connexion à la base metadata sur neon.tech
METADATA_DB_CONFIG = {
    'host': 'ep-wispy-queen-abzi1lne-pooler.eu-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_XsA4wfvHy2Rn',
    'sslmode': 'require'
}

def get_metadata_connection():
    """
    Établit une connexion à la base metadata sur neon.tech
    
    Returns:
        psycopg2.connection: Connexion à la base metadata
    """
    return psycopg2.connect(**METADATA_DB_CONFIG)

def get_table_metadata(table_name: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les métadonnées complètes d'une table
    
    Args:
        table_name: Nom de la table à analyser
        
    Returns:
        Dict contenant toutes les métadonnées de la table ou None si introuvable
    """
    conn = get_metadata_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM metadata WHERE nom_table = %s', (table_name,))
        result = cursor.fetchone()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        return None
        
    finally:
        cursor.close()
        conn.close()

def analyze_table_metadata(table_name: str) -> None:
    """
    Affiche une analyse complète des métadonnées d'une table
    
    Args:
        table_name: Nom de la table à analyser
    """
    metadata = get_table_metadata(table_name)
    
    if not metadata:
        print(f"❌ Aucune métadonnée trouvée pour la table '{table_name}'")
        return
    
    print(f"=== MÉTADONNÉES DE LA TABLE {table_name} ===")
    print(f"ID: {metadata.get('id')}")
    print(f"Schema: {metadata.get('schema')}")
    print(f"Producteur: {metadata.get('producteur')}")
    print(f"Millésime: {metadata.get('millesime')}")
    print(f"Granularité géo: {metadata.get('granularite_geo')}")
    
    # Analyse du contenu CSV
    contenu_csv = metadata.get('contenu_csv')
    if contenu_csv:
        print(f"\n=== STRUCTURE CSV ===")
        if isinstance(contenu_csv, str):
            contenu_data = eval(contenu_csv)
        else:
            contenu_data = contenu_csv
            
        headers = contenu_data.get('header', [])
        print(f"Séparateur: {contenu_data.get('separator')}")
        print(f"Nombre de colonnes: {len(headers)}")
        
        # Identifier les colonnes critiques (identifiants)
        critical_cols = ['IRIS', 'TRIRIS', 'COM', 'DEP', 'REG', 'UU2010']
        print(f"\nColonnes identifiants trouvées:")
        for i, col in enumerate(headers):
            if any(crit in col.upper() for crit in critical_cols):
                print(f"  Position {i+1}: {col}")
    
    # Analyse du dictionnaire des variables
    dictionnaire = metadata.get('dictionnaire')
    if dictionnaire:
        print(f"\n=== DICTIONNAIRE DES VARIABLES ===")
        if isinstance(dictionnaire, str):
            dict_data = eval(dictionnaire)
        else:
            dict_data = dictionnaire
            
        variables = dict_data.get('data', [])
        print(f"Nombre de variables définies: {len(variables)}")
        
        # Analyse des types pour colonnes critiques
        print(f"\nTypes des colonnes critiques:")
        critical_cols = ['IRIS', 'TRIRIS', 'COM', 'DEP', 'REG', 'UU2010']
        
        for var_info in variables:
            if len(var_info) >= 3:
                var_name = var_info[0]
                var_desc = var_info[1] 
                var_type = var_info[2] if len(var_info) > 2 else 'MANQUANT'
                
                if any(crit in var_name.upper() for crit in critical_cols):
                    print(f"  📋 {var_name}: TYPE={var_type}")

def list_all_tables() -> list:
    """
    Liste toutes les tables disponibles dans metadata
    
    Returns:
        List des noms de tables
    """
    conn = get_metadata_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT nom_table FROM metadata ORDER BY nom_table')
        return [row[0] for row in cursor.fetchall()]
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Test de connexion
    print("🔍 Test de connexion à la base metadata...")
    try:
        tables = list_all_tables()
        print(f"✅ Connexion réussie ! {len(tables)} tables trouvées")
        
        # Exemple d'usage
        if tables:
            print(f"\nPremières tables: {tables[:5]}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}") 
#!/usr/bin/env python3
"""
Script de nettoyage des tables d'accidents
- Correction des codes départements (suppression du 0 final)
- [D'autres nettoyages pourront être ajoutés ici]
"""

import os
import pandas as pd
import glob
from pathlib import Path

def get_caract_filename(year):
    """
    Retourne le nom du fichier de caractéristiques pour une année donnée.
    Gère les différents formats de nommage selon les années.
    """
    year_str = str(year)
    patterns = [
        f"{year_str}/caracteristiques_{year_str}.csv",
        f"{year_str}/caracteristiques-{year_str}.csv",
        f"{year_str}/carcteristiques-{year_str}.csv",
        f"{year_str}/caract-{year_str}.csv"
    ]
    
    for pattern in patterns:
        if os.path.exists(pattern):
            return pattern
    return None

def clean_department_code(df):
    """
    Nettoie les codes départements en supprimant le 0 final si présent.
    Préserve les codes 2A0 et 2B0 qui doivent devenir 2A et 2B.
    """
    if 'dep' not in df.columns:
        print("⚠️  Colonne 'dep' non trouvée dans le fichier")
        return df
    
    # Convertir en string pour s'assurer que le traitement des caractères fonctionne
    df['dep'] = df['dep'].astype(str)
    
    # Traitement spécial pour la Corse
    df['dep'] = df['dep'].apply(lambda x: x[:-1] if x.endswith('0') and not x.startswith('2') else x)
    
    return df

def read_csv_file(filename):
    """
    Tente de lire un fichier CSV avec différents encodages et délimiteurs.
    Retourne le DataFrame en cas de succès, None en cas d'échec.
    """
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    separators = [',', ';']
    
    for encoding in encodings:
        for sep in separators:
            try:
                # Lecture avec pandas
                df = pd.read_csv(filename, encoding=encoding, sep=sep, dtype=str)
                print(f"✅ Lecture réussie avec encoding={encoding} et sep={sep}")
                return df
            except Exception as e:
                continue
    
    print(f"❌ Impossible de lire le fichier avec les encodages et séparateurs disponibles")
    return None

def process_year(year):
    """
    Traite les fichiers d'une année donnée.
    """
    filename = get_caract_filename(year)
    if not filename:
        print(f"❌ Aucun fichier de caractéristiques trouvé pour {year}")
        return False
    
    print(f"\n📅 Traitement de l'année {year}")
    print(f"📂 Fichier : {filename}")
    
    try:
        # Lecture du fichier avec gestion des différents formats
        df = read_csv_file(filename)
        if df is None:
            return False
        
        # Sauvegarde du nombre de lignes pour vérification
        initial_rows = len(df)
        
        # Nettoyage des codes départements
        df = clean_department_code(df)
        
        # Vérification que le nombre de lignes n'a pas changé
        if len(df) != initial_rows:
            print("⚠️  ATTENTION : Le nombre de lignes a changé pendant le traitement !")
            return False
        
        # Sauvegarde avec backup du fichier original
        backup_file = filename + '.bak'
        if not os.path.exists(backup_file):
            os.rename(filename, backup_file)
            print(f"✅ Backup créé : {backup_file}")
        
        # Sauvegarde du fichier nettoyé
        # Utiliser le même séparateur que le fichier d'origine
        sep = ',' if ',' in open(backup_file, 'r', encoding='latin1').readline() else ';'
        df.to_csv(filename, index=False, encoding='utf-8', sep=sep)
        print(f"✅ Fichier nettoyé sauvegardé : {filename}")
        
        # Afficher un exemple de modification
        sample = df['dep'].head()
        print("\nExemple de modifications (5 premières lignes) :")
        print(f"Codes départements : {', '.join(sample)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {filename}: {str(e)}")
        return False

def main():
    """
    Fonction principale qui traite toutes les années de 2005 à 2023
    """
    print("🧹 NETTOYAGE DES TABLES D'ACCIDENTS")
    print("=" * 50)
    print("Opérations de nettoyage :")
    print("1. Correction des codes départements")
    print("=" * 50)
    
    success_count = 0
    total_years = 0
    
    # Traitement de chaque année de 2005 à 2023
    for year in range(2005, 2024):
        if os.path.exists(str(year)):
            total_years += 1
            if process_year(year):
                success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Bilan : {success_count}/{total_years} années traitées avec succès")
    
    if success_count == total_years:
        print("🎉 Tous les fichiers ont été traités avec succès!")
    else:
        print("⚠️  Certains fichiers n'ont pas pu être traités")

if __name__ == "__main__":
    main() 
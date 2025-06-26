from utils.db_utils import get_db_connection
import json

def search_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Recherche de la table commune_techno_2025
    cursor.execute("SELECT * FROM metadata WHERE nom_table = %s", ('commune_techno_2025',))
    result = cursor.fetchone()
    
    if result:
        print("=== MÉTADONNÉES TROUVÉES POUR commune_techno_2025 ===")
        columns = [desc[0] for desc in cursor.description]
        metadata_dict = dict(zip(columns, result))
        
        # Affichage des informations principales
        print(f"ID: {metadata_dict['id']}")
        print(f"Type de données: {metadata_dict['type_donnees']}")
        print(f"Nom du jeu: {metadata_dict['nom_jeu_donnees']}")
        print(f"Producteur: {metadata_dict['producteur']}")
        print(f"Nom table: {metadata_dict['nom_table']}")
        print(f"Nom base: {metadata_dict['nom_base']}")
        print(f"Schéma: {metadata_dict['schema']}")
        print(f"Description: {metadata_dict['description']}")
        print(f"Granularité: {metadata_dict['granularite_geo']}")
        print(f"Millésime: {metadata_dict['millesime']}")
        
        # Affichage du contenu CSV
        if metadata_dict.get('contenu_csv'):
            print("\n=== STRUCTURE CSV ===")
            contenu_csv = metadata_dict['contenu_csv']
            if 'header' in contenu_csv:
                print("Colonnes:", contenu_csv['header'])
            if 'data' in contenu_csv and contenu_csv['data']:
                print("Première ligne:", contenu_csv['data'][0])
                print("Nombre de lignes:", len(contenu_csv['data']))
            if 'separator' in contenu_csv:
                print("Séparateur:", contenu_csv['separator'])
                
        # Affichage du dictionnaire
        if metadata_dict.get('dictionnaire'):
            print("\n=== DICTIONNAIRE DES VARIABLES ===")
            dictionnaire = metadata_dict['dictionnaire']
            if 'header' in dictionnaire:
                print("Colonnes du dictionnaire:", dictionnaire['header'])
            if 'data' in dictionnaire and dictionnaire['data']:
                print("Nombre de variables définies:", len(dictionnaire['data']))
                print("Premières variables:")
                for i, var in enumerate(dictionnaire['data'][:5]):
                    print(f"  {i+1}: {var}")
        
        return metadata_dict
    else:
        print("Aucune ligne trouvée avec nom_table = commune_techno_2025")
        
        # Recherche des tables similaires
        cursor.execute("SELECT nom_table FROM metadata WHERE nom_table ILIKE %s", ('%techno%',))
        similar = cursor.fetchall()
        if similar:
            print("Tables contenant 'techno':")
            for table in similar:
                print(f"  - {table[0]}")
        
        # Afficher toutes les tables disponibles
        cursor.execute("SELECT nom_table FROM metadata ORDER BY nom_table")
        all_tables = cursor.fetchall()
        print("\nToutes les tables disponibles:")
        for table in all_tables:
            print(f"  - {table[0]}")
        
        conn.close()
        return None

if __name__ == "__main__":
    search_table() 
from data_importer import DataImporter
import sys

def test_connection():
    # Configuration de la base de données
    db_config = {
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432',
        'database': 'postgres'
    }
    
    try:
        # Création d'une instance de DataImporter
        importer = DataImporter(db_config)
        
        # Test de la connexion en exécutant une requête simple
        with importer.engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.scalar()
            print(f"Connexion réussie ! Version de PostgreSQL : {version}")
            
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données : {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    # Configuration de l'encodage pour la sortie console
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    test_connection() 
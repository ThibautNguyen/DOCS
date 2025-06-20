import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging
from pathlib import Path
import time
import re
from typing import Dict, List, Optional, Union
import json
import pyarrow.parquet as pq
import os
from datetime import datetime
import io

class DataImporter:
    # Seuil en Mo pour basculer vers l'import par chunks
    CHUNK_THRESHOLD_MB = 100
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialise l'importeur de données.
        
        Args:
            db_config: Dictionnaire contenant les paramètres de connexion à la base de données
        """
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le système de logging."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'data_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def get_file_size_mb(self, file_path: Union[str, Path]) -> float:
        """
        Retourne la taille du fichier en Mo.
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            float: Taille du fichier en Mo
        """
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def standardize_table_name(self, name: str, year: Optional[str] = None, geo_level: Optional[str] = None) -> str:
        """
        Standardise le nom de la table selon les conventions.
        Les noms de colonnes ne sont pas modifiés pour préserver la compatibilité avec les métadonnées.
        
        Args:
            name: Nom original de la table
            year: Année des données (optionnel)
            geo_level: Niveau géographique (COM, EPCI, DEP, IRIS, REG)
            
        Returns:
            str: Nom de table standardisé
        """
        # Conversion en minuscules et remplacement des espaces par des underscores
        name = name.lower().replace(' ', '_')
        
        # Suppression des caractères spéciaux
        name = re.sub(r'[^a-z0-9_]', '', name)
        
        # Ajout de l'année et du niveau géographique si fournis
        if year:
            name = f"{name}_{year}"
        if geo_level:
            name = f"{name}_{geo_level}"
            
        return name
    
    def read_data(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Lit un fichier de données selon son extension.
        
        Args:
            file_path: Chemin vers le fichier
            **kwargs: Arguments supplémentaires pour pd.read_*
            
        Returns:
            pd.DataFrame: Données lues
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.csv':
                # Configuration par défaut pour les CSV
                kwargs.setdefault('encoding', 'utf-8')
                kwargs.setdefault('sep', ',')
                return pd.read_csv(file_path, **kwargs)
            elif extension in ['.xls', '.xlsx']:
                return pd.read_excel(file_path, **kwargs)
            elif extension == '.json':
                return pd.read_json(file_path, **kwargs)
            elif extension == '.parquet':
                return pd.read_parquet(file_path, **kwargs)
            else:
                raise ValueError(f"Format de fichier non supporté: {extension}")
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du fichier {file_path}: {str(e)}")
            raise
    
    def analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyse les valeurs manquantes dans le DataFrame.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dict[str, float]: Pourcentage de valeurs manquantes par colonne
        """
        missing = df.isnull().sum()
        total = len(df)
        return {col: (missing[col] / total) * 100 for col in df.columns}
    
    def import_with_copy(self, df: pd.DataFrame, table_name: str, schema: str) -> None:
        """
        Importe les données en utilisant COPY pour de meilleures performances.
        
        Args:
            df: DataFrame à importer
            table_name: Nom de la table
            schema: Schéma de la base de données
        """
        # Création d'un buffer pour les données
        output = io.StringIO()
        df.to_csv(output, index=False, header=False, na_rep='\\N')
        output.seek(0)
        
        # Connexion à la base de données
        conn = self.engine.raw_connection()
        cursor = conn.cursor()
        
        try:
            # Utilisation de COPY pour l'import
            cursor.copy_expert(
                f"COPY {schema}.{table_name} FROM STDIN WITH CSV NULL '\\N'",
                output
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def import_data(self, 
                   file_path: Union[str, Path],
                   table_name: str,
                   schema: str = 'public',
                   year: Optional[str] = None,
                   geo_level: Optional[str] = None,
                   force_chunks: Optional[bool] = None,
                   chunksize: int = 10000,
                   **kwargs) -> None:
        """
        Importe des données dans PostgreSQL.
        
        Args:
            file_path: Chemin vers le fichier à importer
            table_name: Nom de la table cible
            schema: Schéma de la base de données
            year: Année des données
            geo_level: Niveau géographique
            force_chunks: Forcer l'utilisation des chunks (None = auto)
            chunksize: Taille des chunks pour l'import
            **kwargs: Arguments supplémentaires pour la lecture des données
        """
        try:
            start_time = time.time()
            file_path = Path(file_path)
            table_name = self.standardize_table_name(table_name, year, geo_level)
            
            # Vérification de l'existence du fichier
            if not file_path.exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
            
            # Détection automatique du mode d'import
            file_size_mb = self.get_file_size_mb(file_path)
            use_chunks = force_chunks if force_chunks is not None else file_size_mb > self.CHUNK_THRESHOLD_MB
            
            logging.info(f"Début de l'import de {file_path} ({file_size_mb:.2f} Mo) vers {schema}.{table_name}")
            logging.info(f"Mode d'import: {'chunks' if use_chunks else 'direct'}")
            
            if use_chunks:
                # Import par chunks pour les très gros fichiers
                for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize, **kwargs)):
                    if i == 0:
                        # Création de la table avec le premier chunk
                        chunk.head(0).to_sql(
                            name=table_name,
                            schema=schema,
                            con=self.engine,
                            if_exists='replace',
                            index=False
                        )
                    
                    # Analyse des valeurs manquantes
                    missing_values = self.analyze_missing_values(chunk)
                    logging.info(f"Valeurs manquantes dans le chunk {i+1}:")
                    for col, pct in missing_values.items():
                        if pct > 0:
                            logging.info(f"  - {col}: {pct:.2f}%")
                    
                    # Import avec COPY pour de meilleures performances
                    self.import_with_copy(chunk, table_name, schema)
                    logging.info(f"Chunk {i+1} importé")
            else:
                # Import direct pour les fichiers de taille normale
                df = self.read_data(file_path, **kwargs)
                
                # Création de la table
                df.head(0).to_sql(
                    name=table_name,
                    schema=schema,
                    con=self.engine,
                    if_exists='replace',
                    index=False
                )
                
                # Analyse des valeurs manquantes
                missing_values = self.analyze_missing_values(df)
                logging.info("Valeurs manquantes:")
                for col, pct in missing_values.items():
                    if pct > 0:
                        logging.info(f"  - {col}: {pct:.2f}%")
                
                # Import avec COPY
                self.import_with_copy(df, table_name, schema)
            
            duration = time.time() - start_time
            logging.info(f"Import terminé en {duration:.2f} secondes")
            
        except Exception as e:
            logging.error(f"Erreur lors de l'import: {str(e)}")
            raise

# Exemple d'utilisation
if __name__ == "__main__":
    # Test de connexion à la base locale 'opendata'
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'opendata',
        'user': 'cursor_ai',
        'password': 'cursor_ai_is_quite_awesome'
    }
    try:
        importer = DataImporter(db_config)
        # Test simple : ouverture/fermeture de connexion
        conn = importer.engine.connect()
        logging.info("Connexion à la base 'opendata' réussie !")
        conn.close()
    except Exception as e:
        logging.error(f"Échec de la connexion à la base 'opendata' : {e}")
    
    # Configuration de la base de données
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'territoire',
        'user': 'votre_user',
        'password': 'votre_password'
    }
    
    # Création de l'importeur
    importer = DataImporter(db_config)
    
    # Exemple d'import (mode automatique)
    importer.import_data(
        file_path='chemin/vers/fichier.csv',
        table_name='population_communes',
        schema='population',
        year='2021',
        geo_level='COM'
    ) 
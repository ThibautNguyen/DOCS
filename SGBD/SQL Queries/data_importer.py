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

    def infer_sql_type(self, column_name: str, sample_values: List, dict_info: Optional[Dict] = None) -> str:
        """
        Inférence intelligente du type SQL basée sur le nom de colonne, les valeurs d'exemple et le dictionnaire.
        
        Args:
            column_name: Nom de la colonne
            sample_values: Liste des valeurs d'exemple
            dict_info: Informations du dictionnaire des variables (optionnel)
            
        Returns:
            str: Type SQL approprié
        """
        # Nettoyer les valeurs d'exemple (enlever les None et valeurs vides)
        clean_values = [str(v).strip() for v in sample_values if v is not None and str(v).strip()]
        
        # 1. Priorité au dictionnaire si disponible
        if dict_info:
            type_var = dict_info.get('TYPE_VAR', '').lower()
            lib_var = dict_info.get('LIB_VAR', '').lower()
            long_var = dict_info.get('LONG_VAR', '')
            
            if any(keyword in type_var for keyword in ['entier', 'numérique', 'integer']):
                return 'INTEGER'
            elif any(keyword in type_var for keyword in ['décimal', 'réel', 'float', 'double']):
                return 'DECIMAL(10,3)'
            elif any(keyword in type_var for keyword in ['booléen', 'boolean']):
                return 'BOOLEAN'
            elif any(keyword in type_var for keyword in ['date', 'timestamp']):
                return 'DATE'
            elif long_var and long_var.isdigit():
                max_length = int(long_var)
                if max_length <= 20:
                    return f'VARCHAR({max_length})'
                elif max_length <= 255:
                    return f'VARCHAR({max_length})'
                else:
                    return 'TEXT'
        
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

    def generate_import_sql_from_metadata(self, table_name: str, metadata_db_config: Optional[Dict] = None) -> str:
        """
        Génère une requête SQL d'import complète basée sur les métadonnées stockées.
        
        Args:
            table_name: Nom de la table dans la base de métadonnées
            metadata_db_config: Configuration de connexion à la base metadata (optionnel)
            
        Returns:
            str: Requête SQL d'import complète
        """
        
        # Configuration par défaut pour la base de métadonnées
        if metadata_db_config is None:
            # Les métadonnées sont dans la même base que celle configurée pour l'importer
            # ou dans une base spécialisée pour les métadonnées
            try:
                # Essai d'abord avec la base actuelle
                with self.engine.connect() as test_conn:
                    test_conn.execute(text("SELECT 1 FROM metadata LIMIT 1"))
                    metadata_db_config = None  # Utiliser la même base
            except:
                # Sinon, utiliser la base par défaut des métadonnées
                metadata_db_config = {
                    'host': 'localhost',
                    'port': '5432',
                    'database': 'opendata',
                    'user': 'cursor_ai',
                    'password': 'cursor_ai_is_quite_awesome'
                }
        
        try:
            # Connexion à la base de métadonnées
            if metadata_db_config is None:
                # Utiliser la même connexion que l'importer
                metadata_engine = self.engine
            else:
                metadata_engine = create_engine(
                    f"postgresql://{metadata_db_config['user']}:{metadata_db_config['password']}@{metadata_db_config['host']}:{metadata_db_config['port']}/{metadata_db_config['database']}"
                )
            
            with metadata_engine.connect() as conn:
                # Récupération des métadonnées
                query = "SELECT * FROM metadata WHERE nom_table = :nom_table"
                result = conn.execute(text(query), {'nom_table': table_name})
                metadata_row = result.fetchone()
                
                if not metadata_row:
                    raise ValueError(f"Table '{table_name}' non trouvée dans la base de métadonnées")
                
                # Conversion en dictionnaire
                metadata = dict(metadata_row._mapping)
                
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
                    
                    # Recherche des colonnes importantes dans le dictionnaire
                    cod_var_idx = None
                    type_var_idx = None
                    lib_var_idx = None
                    long_var_idx = None
                    
                    for i, header in enumerate(dict_headers):
                        header_lower = header.lower()
                        if 'cod_var' in header_lower or 'variable' in header_lower:
                            cod_var_idx = i
                        elif 'type' in header_lower:
                            type_var_idx = i
                        elif 'lib' in header_lower and 'long' not in header_lower:
                            lib_var_idx = i
                        elif 'long' in header_lower:
                            long_var_idx = i
                    
                    # Construction du mapping
                    for row in dict_data:
                        if cod_var_idx is not None and len(row) > cod_var_idx:
                            var_name = row[cod_var_idx]
                            dict_mapping[var_name] = {
                                'TYPE_VAR': row[type_var_idx] if type_var_idx is not None and len(row) > type_var_idx else '',
                                'LIB_VAR': row[lib_var_idx] if lib_var_idx is not None and len(row) > lib_var_idx else '',
                                'LONG_VAR': row[long_var_idx] if long_var_idx is not None and len(row) > long_var_idx else ''
                            }
                
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
                    # Nettoyage du nom de colonne
                    col_clean = col.strip().replace(' ', '_').replace('-', '_')
                    col_clean = re.sub(r'[^a-zA-Z0-9_]', '', col_clean)
                    if not col_clean or col_clean[0].isdigit():
                        col_clean = f"col_{i}"
                    
                    # Récupération des valeurs d'exemple pour cette colonne
                    sample_values = [row[i] if len(row) > i else None for row in donnees_exemple]
                    
                    # Recherche des informations du dictionnaire
                    dict_info = dict_mapping.get(col, {})
                    
                    # Inférence du type SQL
                    sql_type = self.infer_sql_type(col_clean, sample_values, dict_info)
                    
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
                sql_lines.append(f'COMMENT ON TABLE "{schema}"."{nom_table}" IS \'{description.replace("'", "''")} (Producteur: {producteur})\';')
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
                    col_clean = col.strip().replace(' ', '_').replace('-', '_')
                    col_clean = re.sub(r'[^a-zA-Z0-9_]', '', col_clean)
                    
                    if any(pattern in col.lower() for pattern in ['code', 'id', 'insee', 'commune', 'geo', 'date']):
                        index_name = f"idx_{nom_table}_{col_clean.lower()}"
                        sql_lines.append(f'CREATE INDEX IF NOT EXISTS {index_name} ON "{schema}"."{nom_table}" ("{col_clean}");')
                
                sql_lines.append("")
                
                # 7. Vérification de l'import
                sql_lines.append("-- 7. Vérification de l'import")
                sql_lines.append(f'SELECT COUNT(*) as nb_lignes_importees FROM "{schema}"."{nom_table}";')
                sql_lines.append("")
                sql_lines.append("-- 8. Aperçu des données importées")
                sql_lines.append(f'SELECT * FROM "{schema}"."{nom_table}" LIMIT 5;')
                
                return "\n".join(sql_lines)
                
        except Exception as e:
            logging.error(f"Erreur lors de la génération du SQL : {str(e)}")
            raise

# Fonction utilitaire pour tester depuis les métadonnées
def test_generate_sql(table_name: str = 'commune_techno_2025'):
    """
    Teste la génération SQL depuis les métadonnées.
    Utilise la bonne configuration de base de données avec les métadonnées.
    """
    # Configuration pour accéder à la base avec les métadonnées
    metadata_db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'opendata',
        'user': 'cursor_ai',
        'password': 'cursor_ai_is_quite_awesome'
    }
    
    # Configuration pour la base de destination (peut être la même)
    target_db_config = metadata_db_config.copy()
    
    try:
        importer = DataImporter(target_db_config)
        
        # Test de génération SQL depuis les métadonnées
        print("=== TEST DE GÉNÉRATION SQL ===")
        sql_generated = importer.generate_import_sql_from_metadata(table_name, metadata_db_config)
        print(sql_generated)
        
        return True
        
    except Exception as e:
        logging.error(f"Échec du test de génération SQL : {e}")
        return False

# Exemple d'utilisation
if __name__ == "__main__":
    # Test de la nouvelle fonctionnalité
    success = test_generate_sql('commune_techno_2025')
    
    if success:
        print("\n✅ Test de génération SQL réussi !")
    else:
        print("\n❌ Échec du test de génération SQL")
    
    # Exemple d'import manuel (décommenté si nécessaire)
    '''
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
    ''' 
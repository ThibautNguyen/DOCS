import psycopg2
import pandas as pd
from datetime import datetime
import os

# Paramètres de connexion
conn = psycopg2.connect(
    host='ep-wispy-queen-abzi1lne-pooler.eu-west-2.aws.neon.tech',
    database='neondb',
    user='neondb_owner',
    password='npg_XsA4wfvHy2Rn',
    sslmode='require'
)

# Lecture de la table metadata
df = pd.read_sql('SELECT * FROM metadata', conn)

# Création du dossier de destination si besoin
export_dir = os.path.dirname(__file__)

# Nom de fichier avec date pour archivage
date_str = datetime.now().strftime('%Y%m%d')
export_path = os.path.join(export_dir, f'metadata_export_{date_str}.csv')

# Export CSV
df.to_csv(export_path, index=False, encoding='utf-8')
print(f"Export réalisé : {export_path}")

conn.close()
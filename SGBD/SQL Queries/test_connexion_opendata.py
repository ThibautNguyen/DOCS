import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

conn_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'opendata',
    'user': 'cursor_ai',
    'password': 'cursor_ai_is_quite_awesome'
}

try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    # Lister les schémas
    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        ORDER BY schema_name;
    """)
    schemas = [row[0] for row in cur.fetchall()]
    logger.info(f"Schémas trouvés : {schemas}")
    # Lister les tables pour chaque schéma
    for schema in schemas:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name;
        """, (schema,))
        tables = [row[0] for row in cur.fetchall()]
        if tables:
            logger.info(f"Schéma '{schema}': {len(tables)} table(s)")
            for table in tables:
                print(f"  - {schema}.{table}")
        else:
            logger.info(f"Schéma '{schema}': aucune table")
except Exception as e:
    logger.error(f"Erreur de connexion ou de requête : {str(e)}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
        logger.info("Connexion fermée") 
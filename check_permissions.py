import psycopg2
from psycopg2.extras import RealDictCursor

def check_permissions():
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host='ep-wispy-queen-abzi1lne-pooler.eu-west-2.aws.neon.tech',
            database='neondb',
            user='neondb_owner',
            password='npg_XsA4wfvHy2Rn',
            sslmode='require'
        )
        
        # Création d'un curseur
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Vérification des schémas
        print("\n=== Schémas disponibles ===")
        cur.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schema_name;
        """)
        schemas = cur.fetchall()
        for schema in schemas:
            print(f"- {schema['schema_name']}")
        
        # Vérification des tables
        print("\n=== Tables dans le schéma public ===")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        for table in tables:
            print(f"- {table['table_name']}")
        
        # Vérification des permissions
        print("\n=== Permissions sur les tables ===")
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                tableowner,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'SELECT') as can_select,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'INSERT') as can_insert,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'UPDATE') as can_update
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        permissions = cur.fetchall()
        for perm in permissions:
            print(f"\nTable: {perm['schemaname']}.{perm['tablename']}")
            print(f"  Propriétaire: {perm['tableowner']}")
            print(f"  Permissions: SELECT={perm['can_select']}, INSERT={perm['can_insert']}, UPDATE={perm['can_update']}")
        
        # Fermeture de la connexion
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur : {str(e)}")

if __name__ == "__main__":
    check_permissions() 
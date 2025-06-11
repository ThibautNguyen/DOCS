# Guide de connexion à la base de données OpenData

## Paramètres de connexion locale
```python
conn_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'opendata',
    'user': 'cursor_ai',
    'password': 'cursor_ai_is_quite_awesome'
}
```

## Exemple de code de connexion
```python
import psycopg2
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    # Exécuter les requêtes ici
    
except Exception as e:
    logger.error(f"Erreur de connexion : {str(e)}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
        logger.info("Connexion fermée")
```

## Tables principales
- `reseau.techno_internet_com_2024` : Table source des données de couverture internet
- `reseau.techno_internet_com_2024_clean` : Table nettoyée (après transformation) 
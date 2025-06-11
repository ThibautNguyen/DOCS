import pandas as pd

# Chemin du fichier source
input_file = "C:/Users/thiba/OneDrive/Documents/Données/Sécurité/Délinquance - COM/2024/donnee-data.gouv-2024-geographie2024-produit-le2025-03-14.csv"

# Chemin du fichier nettoyé
output_file = "C:/Users/thiba/OneDrive/Documents/Données/Sécurité/Délinquance - COM/2024/donnee-data.gouv-2024-geographie2024-produit-le2025-03-14_nettoye.csv"

# Chargement du fichier CSV avec gestion d'erreur
try:
    df = pd.read_csv(input_file, sep=';', dtype=str)
except Exception as e:
    print(f"Erreur lors de la lecture du fichier source : {e}")
    exit(1)

# Remplacer toutes les chaînes "NA" par des valeurs vides (NaN pour Pandas, NULL pour PostgreSQL)
df.replace("NA", pd.NA, inplace=True)

# Exporter le fichier nettoyé
df.to_csv(output_file, sep=';', index=False, na_rep='')

# Afficher les premières lignes du DataFrame nettoyé
print(df.head())

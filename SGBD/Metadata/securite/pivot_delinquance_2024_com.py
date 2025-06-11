import pandas as pd

# 1. Charger le fichier source
fichier_source = r"C:\Users\thiba\OneDrive\Documents\Données\Sécurité\Délinquance - COM\2024\donnee-data.gouv-2024-geographie2024-produit-le2025-03-14_nettoye.csv"

df = pd.read_csv(fichier_source, sep=';', dtype=str)

# 2. Nettoyage des colonnes numériques
# Remplacer les virgules par des points pour la conversion correcte
if 'taux_pour_mille' in df.columns:
    df["taux_pour_mille"] = df["taux_pour_mille"].str.replace(",", ".")
    df["taux_pour_mille"] = pd.to_numeric(df["taux_pour_mille"], errors='coerce')
if 'annee' in df.columns:
    df["annee"] = pd.to_numeric(df["annee"], errors='coerce')

# 3. Nettoyage des libellés d'indicateur
df["indicateur"] = df["indicateur"].str.strip().str.lower()

# 4. Liste standardisée des types de délits à conserver
delits = [
    "autres coups et blessures volontaires",
    "coups et blessures volontaires",
    "destructions et dégradations volontaires",
    "trafic de stupéfiants",
    "vols avec armes",
    "vols d'accessoires sur véhicules",
    "vols dans les véhicules",
    "vols de véhicules",
    "vols sans violence contre des personnes",
    "vols violents sans arme"
]

# 5. Filtrage
df_filtre = df[df["indicateur"].isin(delits)]

# Filtrer la population sur df_filtre (communes > 1500 habitants)
if 'insee_pop' in df_filtre.columns:
    df_filtre = df_filtre[df_filtre['insee_pop'].astype(float) > 1500]

print("Valeurs uniques de la colonne 'indicateur' :", df['indicateur'].unique())
print("Nombre de lignes après filtrage :", len(df_filtre))

print(df_filtre.head(20))
print(df_filtre[["CODGEO_2024", "annee", "indicateur", "taux_pour_mille"]].isnull().sum())

# 6. Pivot vers un tableau au format large
if 'insee_pop' in df_filtre.columns:
    df_pivot = df_filtre.pivot_table(
        index=["CODGEO_2024", "insee_pop", "annee"],
        columns="indicateur",
        values="taux_pour_mille",
        aggfunc="first"
    ).reset_index()
else:
    df_pivot = df_filtre.pivot_table(
        index=["CODGEO_2024", "annee"],
        columns="indicateur",
        values="taux_pour_mille",
        aggfunc="first"
    ).reset_index()

# 7. Nettoyage des noms de colonnes
df_pivot.columns.name = None
df_pivot.rename(columns={"CODGEO_2024": "CODGEO"}, inplace=True)

# 8. Export du fichier CSV final
fichier_sortie = r"C:\Users\thiba\OneDrive\Documents\Données\Sécurité\Délinquance - COM\2024\donnee-delinquance_pivot.csv"
df_pivot.to_csv(fichier_sortie, sep=';', index=False)

# 9. Affichage d'un aperçu
print("✅ Export terminé. Aperçu du tableau :")
print(df_pivot.head())

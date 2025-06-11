-- Vérification des droits
SELECT has_schema_privilege('cursor_ai', 'reseau', 'CREATE') as has_create,
       has_schema_privilege('cursor_ai', 'reseau', 'USAGE') as has_usage,
       has_table_privilege('cursor_ai', 'reseau.techno_internet_com_2024', 'SELECT') as has_select;

-- Suppression des objets existants
DROP FUNCTION IF EXISTS reseau.clean_percentage(text);
DROP FUNCTION IF EXISTS reseau.clean_number(text);
DROP TABLE IF EXISTS reseau.techno_internet_com_2024_clean;

-- Création de la fonction clean_percentage
CREATE FUNCTION reseau.clean_percentage(text) RETURNS numeric AS 
$BODY$
BEGIN
    RETURN CASE 
        WHEN $1 IS NULL OR trim($1) = '-' THEN NULL
        ELSE NULLIF(regexp_replace(regexp_replace($1, '[%\s]', '', 'g'), ',', '.', 'g'), '')::numeric
    END;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Erreur lors du nettoyage du pourcentage : %', SQLERRM;
        RETURN NULL;
END;
$BODY$ LANGUAGE plpgsql;

-- Création de la fonction clean_number
CREATE FUNCTION reseau.clean_number(text) RETURNS integer AS 
$BODY$
BEGIN
    RETURN CASE 
        WHEN $1 IS NULL OR trim($1) = '-' THEN NULL
        ELSE NULLIF(regexp_replace($1, '\s', '', 'g'), '')::integer
    END;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Erreur lors du nettoyage du nombre : %', SQLERRM;
        RETURN NULL;
END;
$BODY$ LANGUAGE plpgsql;

-- Création de la table
CREATE TABLE reseau.techno_internet_com_2024_clean (
    code_insee char(5) PRIMARY KEY,
    commune varchar(100) NOT NULL,
    pct_fibre numeric(5,2),
    pct_cable numeric(5,2),
    pct_dsl numeric(5,2),
    pct_thd_radio numeric(5,2),
    pct_4g_fixe numeric(5,2),
    pct_hd_radio numeric(5,2),
    pct_satellite numeric(5,2),
    nb_locaux integer NOT NULL,
    nb_locaux_fibre integer,
    nb_locaux_cable integer,
    nb_locaux_dsl integer,
    nb_locaux_thd_radio integer,
    nb_locaux_4g_fixe integer,
    nb_locaux_hd_radio integer,
    nb_locaux_satellite integer,
    CONSTRAINT check_pct_fibre CHECK (pct_fibre BETWEEN 0 AND 100),
    CONSTRAINT check_pct_cable CHECK (pct_cable BETWEEN 0 AND 100),
    CONSTRAINT check_pct_dsl CHECK (pct_dsl BETWEEN 0 AND 100),
    CONSTRAINT check_pct_thd_radio CHECK (pct_thd_radio BETWEEN 0 AND 100),
    CONSTRAINT check_pct_4g_fixe CHECK (pct_4g_fixe BETWEEN 0 AND 100),
    CONSTRAINT check_pct_hd_radio CHECK (pct_hd_radio BETWEEN 0 AND 100),
    CONSTRAINT check_pct_satellite CHECK (pct_satellite BETWEEN 0 AND 100),
    CONSTRAINT check_nb_locaux_positive CHECK (nb_locaux > 0)
);

-- Insertion des données (en excluant les communes sans données de locaux)
WITH source_data AS (
    SELECT 
        trim("Code Insee") as code_insee,
        trim("Commune") as commune,
        reseau.clean_percentage("% Fibre") as pct_fibre,
        reseau.clean_percentage("% Câble") as pct_cable,
        reseau.clean_percentage("% DSL") as pct_dsl,
        reseau.clean_percentage("% THD Radio") as pct_thd_radio,
        reseau.clean_percentage("% 4G Fixe") as pct_4g_fixe,
        reseau.clean_percentage("% HD Radio") as pct_hd_radio,
        reseau.clean_percentage("% Satellite") as pct_satellite,
        reseau.clean_number(" Nombre total de locaux ") as nb_locaux,
        reseau.clean_number("Locaux Fibre") as nb_locaux_fibre,
        reseau.clean_number("Locaux Câble") as nb_locaux_cable,
        reseau.clean_number("Locaux DSL") as nb_locaux_dsl,
        reseau.clean_number("Locaux THD Radio") as nb_locaux_thd_radio,
        reseau.clean_number("Locaux 4G Fixe") as nb_locaux_4g_fixe,
        reseau.clean_number("Locaux HD Radio") as nb_locaux_hd_radio,
        reseau.clean_number("Locaux Satellite") as nb_locaux_satellite
    FROM reseau.techno_internet_com_2024
)
INSERT INTO reseau.techno_internet_com_2024_clean
SELECT *
FROM source_data
WHERE nb_locaux IS NOT NULL;

-- Création des index
CREATE INDEX idx_commune ON reseau.techno_internet_com_2024_clean(commune);
CREATE INDEX idx_pct_fibre ON reseau.techno_internet_com_2024_clean(pct_fibre);
CREATE INDEX idx_nb_locaux ON reseau.techno_internet_com_2024_clean(nb_locaux);

-- Ajout des commentaires
COMMENT ON TABLE reseau.techno_internet_com_2024_clean IS 'Version nettoyée de la table des technologies Internet par commune (2024)';
COMMENT ON COLUMN reseau.techno_internet_com_2024_clean.code_insee IS 'Code INSEE de la commune';
COMMENT ON COLUMN reseau.techno_internet_com_2024_clean.commune IS 'Nom de la commune';
COMMENT ON COLUMN reseau.techno_internet_com_2024_clean.pct_fibre IS 'Pourcentage de couverture fibre';
COMMENT ON COLUMN reseau.techno_internet_com_2024_clean.nb_locaux IS 'Nombre total de locaux dans la commune';

-- Vérification finale
SELECT COUNT(*) as total_communes,
       COUNT(CASE WHEN pct_fibre > 95 THEN 1 END) as communes_tres_fibrees,
       ROUND(AVG(pct_fibre)::numeric, 2) as moyenne_fibre,
       MIN(nb_locaux) as min_locaux,
       MAX(nb_locaux) as max_locaux
FROM reseau.techno_internet_com_2024_clean; 
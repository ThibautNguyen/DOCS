-- Création de la nouvelle table avec la structure propre
CREATE TABLE IF NOT EXISTS public.techno_internet_com_2024_clean (
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

-- Fonction pour convertir les pourcentages
CREATE OR REPLACE FUNCTION public.clean_percentage(text) RETURNS numeric AS $$
BEGIN
    -- Supprime les espaces, remplace la virgule par un point et enlève le %
    RETURN CASE 
        WHEN $1 IS NULL OR trim($1) = '-' THEN NULL
        ELSE NULLIF(regexp_replace(regexp_replace($1, '[%\s]', '', 'g'), ',', '.', 'g'), '')::numeric
    END;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour nettoyer les nombres
CREATE OR REPLACE FUNCTION public.clean_number(text) RETURNS integer AS $$
BEGIN
    -- Supprime les espaces et convertit en integer
    RETURN CASE 
        WHEN $1 IS NULL OR trim($1) = '-' THEN NULL
        ELSE NULLIF(regexp_replace($1, '\s', '', 'g'), '')::integer
    END;
END;
$$ LANGUAGE plpgsql;

-- Insertion des données nettoyées
INSERT INTO public.techno_internet_com_2024_clean
SELECT 
    trim(code_insee) as code_insee,
    trim(commune) as commune,
    public.clean_percentage("% Fibre") as pct_fibre,
    public.clean_percentage("% Câble") as pct_cable,
    public.clean_percentage("% DSL") as pct_dsl,
    public.clean_percentage("% THD Radio") as pct_thd_radio,
    public.clean_percentage("% 4G Fixe") as pct_4g_fixe,
    public.clean_percentage("% HD Radio") as pct_hd_radio,
    public.clean_percentage("% Satellite") as pct_satellite,
    public.clean_number(" Nombre total de locaux") as nb_locaux,
    public.clean_number("Locaux Fibre") as nb_locaux_fibre,
    public.clean_number("Locaux Câble") as nb_locaux_cable,
    public.clean_number("Locaux DSL") as nb_locaux_dsl,
    public.clean_number("Locaux THD Radio") as nb_locaux_thd_radio,
    public.clean_number("Locaux 4G Fixe") as nb_locaux_4g_fixe,
    public.clean_number("Locaux HD Radio") as nb_locaux_hd_radio,
    public.clean_number("Locaux Satellite") as nb_locaux_satellite
FROM reseau.techno_internet_com_2024;

-- Création d'index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_commune ON public.techno_internet_com_2024_clean(commune);
CREATE INDEX IF NOT EXISTS idx_pct_fibre ON public.techno_internet_com_2024_clean(pct_fibre);
CREATE INDEX IF NOT EXISTS idx_nb_locaux ON public.techno_internet_com_2024_clean(nb_locaux);

-- Ajout de commentaires sur la table et les colonnes
COMMENT ON TABLE public.techno_internet_com_2024_clean IS 'Version nettoyée de la table des technologies Internet par commune (2024)';
COMMENT ON COLUMN public.techno_internet_com_2024_clean.code_insee IS 'Code INSEE de la commune';
COMMENT ON COLUMN public.techno_internet_com_2024_clean.commune IS 'Nom de la commune';
COMMENT ON COLUMN public.techno_internet_com_2024_clean.pct_fibre IS 'Pourcentage de couverture fibre';
COMMENT ON COLUMN public.techno_internet_com_2024_clean.nb_locaux IS 'Nombre total de locaux dans la commune';

-- Vérification des données après insertion
SELECT COUNT(*) as total_communes,
       COUNT(CASE WHEN pct_fibre > 95 THEN 1 END) as communes_tres_fibrees,
       AVG(pct_fibre) as moyenne_fibre,
       MIN(nb_locaux) as min_locaux,
       MAX(nb_locaux) as max_locaux
FROM public.techno_internet_com_2024_clean; 
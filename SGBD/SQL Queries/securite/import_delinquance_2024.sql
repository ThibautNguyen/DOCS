-- =====================================================================================
-- SCRIPT D'IMPORT SIMPLIFIÉ - DONNÉES DE DÉLINQUANCE 2024
-- =====================================================================================

-- 1. CRÉATION DU SCHÉMA
-- =====================================================================================
CREATE SCHEMA IF NOT EXISTS "securite";

-- 2. SUPPRESSION DES TABLES SI ELLES EXISTENT
-- =====================================================================================
DROP TABLE IF EXISTS "securite"."delinquance_2024_dep";
DROP TABLE IF EXISTS "securite"."delinquance_2024_reg";

-- 3. CRÉATION DE LA TABLE DÉPARTEMENTALE (sans contrainte)
-- =====================================================================================
CREATE TABLE "securite"."delinquance_2024_dep" (
    "code_departement" VARCHAR(3) NOT NULL,
    "annee" INTEGER NOT NULL,
    "indicateur" TEXT NOT NULL,
    "unite_de_compte" TEXT,
    "nombre" INTEGER,
    "taux_pour_mille" DECIMAL(10,3),
    "est_diffuse" BOOLEAN,
    "insee_pop" INTEGER,
    "insee_pop_millesime" INTEGER,
    "insee_log" INTEGER,
    "insee_log_millesime" INTEGER,
    "date_import" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "source_fichier" TEXT DEFAULT 'data.gouv.fr - Ministère de l''Intérieur'
);

-- 4. CRÉATION DE LA TABLE RÉGIONALE (sans contrainte)
-- =====================================================================================
CREATE TABLE "securite"."delinquance_2024_reg" (
    "code_region" VARCHAR(2) NOT NULL,
    "annee" INTEGER NOT NULL,
    "indicateur" TEXT NOT NULL,
    "unite_de_compte" TEXT,
    "nombre" INTEGER,
    "taux_pour_mille" DECIMAL(10,3),
    "est_diffuse" BOOLEAN,
    "insee_pop" INTEGER,
    "insee_pop_millesime" INTEGER,
    "insee_log" INTEGER,
    "insee_log_millesime" INTEGER,
    "date_import" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "source_fichier" TEXT DEFAULT 'data.gouv.fr - Ministère de l''Intérieur'
);

-- 5. AJOUT DES CLÉS PRIMAIRES SÉPARÉMENT
-- =====================================================================================
ALTER TABLE "securite"."delinquance_2024_dep" 
ADD CONSTRAINT "pk_delinquance_dep" PRIMARY KEY ("code_departement", "annee", "indicateur");

ALTER TABLE "securite"."delinquance_2024_reg" 
ADD CONSTRAINT "pk_delinquance_reg" PRIMARY KEY ("code_region", "annee", "indicateur");

-- 6. CRÉATION D'INDEX POUR OPTIMISER LES PERFORMANCES
-- =====================================================================================
CREATE INDEX "idx_delinquance_dep_annee" ON "securite"."delinquance_2024_dep" ("annee");
CREATE INDEX "idx_delinquance_dep_indicateur" ON "securite"."delinquance_2024_dep" ("indicateur");
CREATE INDEX "idx_delinquance_dep_taux" ON "securite"."delinquance_2024_dep" ("taux_pour_mille") WHERE "taux_pour_mille" IS NOT NULL;

CREATE INDEX "idx_delinquance_reg_annee" ON "securite"."delinquance_2024_reg" ("annee");
CREATE INDEX "idx_delinquance_reg_indicateur" ON "securite"."delinquance_2024_reg" ("indicateur");
CREATE INDEX "idx_delinquance_reg_taux" ON "securite"."delinquance_2024_reg" ("taux_pour_mille") WHERE "taux_pour_mille" IS NOT NULL;

-- 7. COMMENTAIRES SUR LES TABLES
-- =====================================================================================
COMMENT ON TABLE "securite"."delinquance_2024_dep" IS 'Base statistique départementale de la délinquance 2024 - Source: Ministère de l''Intérieur (SSMSI)';
COMMENT ON TABLE "securite"."delinquance_2024_reg" IS 'Base statistique régionale de la délinquance 2024 - Source: Ministère de l''Intérieur (SSMSI)';

-- 8. DROITS D'ACCÈS
-- =====================================================================================
GRANT USAGE ON SCHEMA "securite" TO "cursor_ai";
GRANT SELECT ON "securite"."delinquance_2024_dep" TO "cursor_ai";
GRANT SELECT ON "securite"."delinquance_2024_reg" TO "cursor_ai";

-- 9. VÉRIFICATION DE LA CRÉATION
-- =====================================================================================
SELECT 
    table_schema, 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_schema = 'securite' 
  AND table_name IN ('delinquance_2024_dep', 'delinquance_2024_reg')
ORDER BY table_name, ordinal_position; 
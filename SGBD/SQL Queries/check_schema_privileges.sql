-- Vérification des droits sur les schémas
SELECT 
    n.nspname as schema_name,
    has_schema_privilege('cursor_ai', n.nspname, 'USAGE') as has_usage,
    has_schema_privilege('cursor_ai', n.nspname, 'CREATE') as has_create,
    -- Pour le droit SELECT, on vérifie si on peut lire au moins une table du schéma
    EXISTS (
        SELECT 1 
        FROM pg_class c
        WHERE c.relnamespace = n.oid 
        AND c.relkind = 'r'  -- tables normales uniquement
        AND has_table_privilege('cursor_ai', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'SELECT')
    ) as has_select_on_tables
FROM pg_namespace n
WHERE n.nspname NOT LIKE 'pg_%' 
    AND n.nspname != 'information_schema'
ORDER BY n.nspname; 
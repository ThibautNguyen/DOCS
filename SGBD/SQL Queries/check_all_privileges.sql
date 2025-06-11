-- Vérification des droits sur tous les schémas
SELECT 
    n.nspname as schema_name,
    CASE WHEN has_schema_privilege('cursor_ai', n.nspname, 'CREATE') THEN 'OUI' ELSE 'NON' END as droit_create,
    CASE WHEN has_schema_privilege('cursor_ai', n.nspname, 'USAGE') THEN 'OUI' ELSE 'NON' END as droit_usage
FROM pg_namespace n
WHERE n.nspname NOT LIKE 'pg_%' 
    AND n.nspname != 'information_schema'
ORDER BY n.nspname;

-- Vérification des droits sur toutes les tables par schéma
SELECT 
    n.nspname as schema_name,
    c.relname as table_name,
    CASE WHEN has_table_privilege('cursor_ai', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'SELECT') THEN 'OUI' ELSE 'NON' END as droit_select,
    CASE WHEN has_table_privilege('cursor_ai', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'INSERT') THEN 'OUI' ELSE 'NON' END as droit_insert,
    CASE WHEN has_table_privilege('cursor_ai', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'UPDATE') THEN 'OUI' ELSE 'NON' END as droit_update,
    CASE WHEN has_table_privilege('cursor_ai', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'DELETE') THEN 'OUI' ELSE 'NON' END as droit_delete
FROM pg_namespace n
JOIN pg_class c ON c.relnamespace = n.oid
WHERE n.nspname NOT LIKE 'pg_%' 
    AND n.nspname != 'information_schema'
    AND c.relkind = 'r'  -- uniquement les tables normales
ORDER BY n.nspname, c.relname;

-- Vérification des droits sur les fonctions par schéma
SELECT 
    n.nspname as schema_name,
    p.proname as function_name,
    CASE WHEN has_function_privilege('cursor_ai', p.oid, 'EXECUTE') THEN 'OUI' ELSE 'NON' END as droit_execute
FROM pg_namespace n
JOIN pg_proc p ON p.pronamespace = n.oid
WHERE n.nspname NOT LIKE 'pg_%' 
    AND n.nspname != 'information_schema'
ORDER BY n.nspname, p.proname;

-- Liste des rôles et appartenances
SELECT 
    r.rolname as role_name,
    r.rolsuper as est_superuser,
    r.rolinherit as herite_droits,
    r.rolcreaterole as peut_creer_roles,
    r.rolcreatedb as peut_creer_db,
    r.rolcanlogin as peut_se_connecter,
    r.rolreplication as peut_repliquer,
    r.rolbypassrls as bypass_rls
FROM pg_roles r
WHERE r.rolname = 'cursor_ai';

-- Afficher les membres des rôles
SELECT 
    pg_get_userbyid(m.roleid) as role_name,
    pg_get_userbyid(m.member) as membre,
    m.admin_option as est_admin
FROM pg_auth_members m
WHERE pg_get_userbyid(m.roleid) = 'cursor_ai' 
   OR pg_get_userbyid(m.member) = 'cursor_ai'; 
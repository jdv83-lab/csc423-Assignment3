SELECT 'DROP TABLE IF EXISTS "' || name || '";' 
FROM sqlite_master 
WHERE type = 'table' AND name NOT LIKE 'sqlite_%';


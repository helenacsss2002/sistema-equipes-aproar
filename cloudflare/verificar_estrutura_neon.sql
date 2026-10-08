-- Diagnóstico somente leitura. Não altera tabelas nem retorna dados pessoais.
-- Execute no SQL Editor do Neon e exporte o resultado em CSV.
SELECT c.table_schema,
       c.table_name,
       c.column_name,
       c.data_type,
       c.udt_name,
       c.is_nullable,
       c.column_default
FROM information_schema.columns AS c
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;

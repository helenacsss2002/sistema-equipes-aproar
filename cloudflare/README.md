# APROAR — preparação da Cloudflare

Etapa inicial: verificar a conexão e a estrutura do Neon. Não é ainda a plataforma completa e não altera registros. O Streamlit permanece independente.

## Configuração do projeto Worker conectado ao GitHub

- Diretório raiz: `cloudflare`
- Comando de build: `npm run check`
- Comando de deploy: `npm run deploy`
- Nome do Worker: `aproar-web`

A pasta precisa estar no repositório antes de criar o projeto. Não execute o schema.sql antigo na produção.

## Segredos (Settings → Variables and Secrets)

- `DATABASE_URL`: conexão do Neon; nunca inserir em código ou variável pública.
- `CONNECTION_CHECK_TOKEN`: token aleatório exclusivo para o diagnóstico (pelo menos 32 caracteres).

`GET /api/health` confirma apenas se a configuração existe, sem consultar o banco.
`POST /api/check-database`, com `Authorization: Bearer <CONNECTION_CHECK_TOKEN>`, testa o acesso e a presença das colunas necessárias. Não retorna registros pessoais, credenciais ou detalhes de erros de conexão.

Esta etapa não adiciona tabelas, migra dados nem implementa operações de escrita. O adaptador de dados, as permissões de cada perfil, a persistência e a interface de produção ainda precisam ser concluídos antes de liberar o uso.

## Adaptador de leitura

`src/neon-adapter.js` converte o esquema existente para a estrutura da interface. Testes cobrem presença padrão sem apontamento, múltiplos serviços, pagamentos, metadados legados e extras não padronizados. Ainda não está conectado ao HTML nem implementa gravação. Extras não padronizados e serviços sem correspondência são sinalizados para tratamento antes da produção.

`POST /api/preview-data` utiliza a mesma autenticação e lê os dados em uma transação somente leitura. Retorna uma prévia convertida para a interface; nenhuma operação de escrita é oferecida. Deve apontar para a branch `aproar-homologacao`, criada a partir de `production` com dados. Uma branch de testes não substitui um backup externo.

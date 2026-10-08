# APROAR HTML — ambiente de validação

Este arquivo identifica a branch de publicação de testes com uma cópia isolada dos dados de produção.

- Worker da Cloudflare: `sistema-equipes-aproar` (separado de `aproar-web`).
- Pasta raiz do build: `cloudflare`.
- Branch do GitHub: `aproar-html-validacao-cloudflare-20261008`.
- `APP_ENV=homologacao`.
- Gravações bloqueadas enquanto `WRITES_ENABLED` não for habilitado explicitamente.
- Sincronização automática do Trello bloqueada enquanto `TRELLO_AUTO_SYNC_ENABLED` não for habilitado explicitamente e sem Cron Trigger nesta configuração.
- Nunca conectar diretamente ao Neon `producao` antes dos testes de migração e autorização.

# Implantação de produção do APROAR (Cloudflare Worker)

Worker **existente**: `sistema-equipes-aproar` (não `aproar-web`).
Fonte do repositório: pasta `cloudflare/`; interface: `cloudflare/public/`.
A configuração `wrangler.producao.jsonc` é **separada** da configuração de homologação `wrangler.jsonc`.

## Pré-condição antes de publicar

**Não faça deploy sem comparar o pacote deste commit com a versão ativa do Worker.**
O Worker foi publicado manualmente por Wrangler e pode conter ajustes ainda não versionados no GitHub.
Verifique se as alterações de produção existentes (código e assets) foram preservadas.
A aplicação ativa deve estar ligada à branch de produção correta no Neon.

No painel do Cloudflare, confira (sem copiar os valores secretos):
- `APP_ENV=producao`
- `WRITES_ENABLED=true`
- `PRODUCTION_WRITE_APPROVED=true`
- `PRODUCTION_EXPECTED_HOST` corresponde exatamente ao host de `DATABASE_URL`
- `SESSION_SECRET`, `DATABASE_URL`, `ADMIN_PASSWORD`, `FINANCE_PASSWORD` e `DJOUNE_XAVIER_PASSWORD` são Secrets existentes

**Não coloque valores de senha ou banco de dados no GitHub, terminal compartilhado ou prints.**

## Comandos Windows PowerShell

Abra um terminal na raiz do repositório atualizado, a partir do commit aprovado:

```powershell
cd cloudflare
npm ci
npm run check
npm test
npx wrangler whoami
npx wrangler deploy --config wrangler.producao.jsonc --dry-run
```

O `--dry-run` apenas prepara o bundle, não publica nada.

**Somente após a comparação com o Worker ativo e o aceite dos testes:**

```powershell
npx wrangler deploy --config wrangler.producao.jsonc
```

Esse comando aponta para o Worker existente `sistema-equipes-aproar` e inclui a pasta `public` (ASSETS).
`keep_vars=true` preserva as demais variáveis de runtime definidas pelo painel.
O deploy não executa migrações SQL nem altera os dados do Neon.

## Conferência após publicação

1. Na aba Deployments do mesmo Worker, confira o novo deploy via Wrangler e registre a versão anterior para rollback.
2. Confira as telas de login, Controladoria, Financeiro e Supervisor.
3. No Portal do Supervisor, escolha `DJOUNE XAVIER`; o campo de senha deve aparecer.
4. Entre com a senha já salva em `DJOUNE_XAVIER_PASSWORD`.
5. Valide `CENTRO` e `MUSEU` em `aproar_web_settings.data.unitOwners`; não remova outras unidades.
6. Faça um salvamento controlado e confira que os dados persistem após atualização sem duplicações.
7. Em caso de erro, utilize o histórico do Cloudflare para restaurar a versão anterior e investigue antes de tentar novo deploy.

## Observações

O login de Djoune utiliza seu nome no seletor, com e-mail mostrado como identificação.
O e-mail não é uma conta de autenticação separada; a autenticação é via senha do Secret.
Não crie um Postgres role para supervisor (isso concederia acesso inadequado).

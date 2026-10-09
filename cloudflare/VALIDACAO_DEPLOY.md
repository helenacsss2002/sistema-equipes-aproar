# APROAR HTML — preparação do ambiente oficial

- Worker alvo: `sistema-equipes-aproar`, independente de `aproar-web` e do Streamlit.
- Branch de deploy: `aproar-html-validacao-cloudflare-20261008`.
- Pasta raiz do deploy: `cloudflare`.
- Esta proposta (`aproar-html-oficial-seguro-20261008`) prepara o código para ler Neon `producao`.
- Modo `APP_ENV=producao` identifica os dados reais, **sem autorizar gravação**.
- Gravações em produção exigem as três condições juntas:
  `WRITES_ENABLED=true`, `PRODUCTION_WRITE_APPROVED=true`
  e `PRODUCTION_EXPECTED_HOST` igual ao hostname da conexão de produção.
- `PRODUCTION_ALLOW_DELETE` deve permanecer ausente; exclusões são bloqueadas por padrão.
- Sincronização automática do Trello permanece desativada neste Worker até validação separada.
- O Streamlit continua operacional durante a transição.
- Builds de prévia no painel Cloudflare foram desligados após falhas de `wrangler preview`;
  a validação do PR depende dos testes automatizados do GitHub, sem deploy de preview.
- **Não fazer lançamento com gravações habilitadas antes de testar um registro seguro
  em banco isolado e aprovar o plano de transição.**

A presente alteração documental também força uma nova execução do CI do PR
depois da desativação dos builds de prévia no painel da Cloudflare.

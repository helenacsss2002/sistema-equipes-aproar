# APROAR — HTML original conectado ao Neon

Esta versão mantém os estilos, logo, telas, navegação e exportações do HTML original. A persistência local e os dados fictícios foram substituídos por consultas e gravações no servidor. É necessário enviar toda a pasta cloudflare, não apenas worker.js.

## Publicar no Worker existente

1. No Neon, selecione aproar-homologacao → neondb. Caso ainda não tenha executado migracao_homologacao.sql, execute todo o arquivo nesta branch. O script é aditivo e não apaga o histórico. Não execute schema.sql antigo nem altere production. Desative a expiração automática da branch.
2. Extraia o ZIP e envie a pasta cloudflare à raiz do repositório sistema-equipes-aproar, substituindo os arquivos correspondentes. Preserve app.py do Streamlit.
3. Em Cloudflare → aproar-web → Settings → Variables and Secrets, mantenha DATABASE_URL como Secret apontando à homologação e CONNECTION_CHECK_TOKEN como Secret. Acrescente os Secrets abaixo.
4. Após o deploy, confira os dados em Controladoria. Para liberar gravação nessa cópia de testes, defina a variável de runtime WRITES_ENABLED=true. APP_ENV deve continuar homologacao.

| Secret | Valor |
| --- | --- |
| ADMIN_PASSWORD | Senha da Controladoria; pode manter aproaradmin |
| FINANCE_PASSWORD | Senha do Financeiro; pode manter financeiro |
| VIEWER_PASSWORD | Senha escolhida para Somente visualizar |
| SUPERVISOR_PASSWORDS | JSON com nomes dos supervisores e senhas individuais |

Formato de SUPERVISOR_PASSWORDS (substitua as senhas):

```json
{"EDUARDO":"senha-eduardo","FELIPE":"senha-felipe","GABRIEL":"senha-gabriel","JOEL":"senha-joel","NETO":"senha-neto","SOARES":"senha-soares","VICTOR":"senha-victor"}
```

Cada perfil estará disponível quando seu Secret estiver configurado. O login passa a pedir a senha do perfil, sem expor tokens administrativos na página. Não publique os Secrets no GitHub nem os envie no chat. SESSION_SECRET pode ser configurado como Secret separado; se ausente, a assinatura das sessões utiliza CONNECTION_CHECK_TOKEN.

Comandos com a raiz do repositório como diretório de trabalho:

```text
Build: npm --prefix cloudflare install && npm --prefix cloudflare run check
Deploy: npm --prefix cloudflare run deploy
```

Mantenha Preview builds desativados nesta etapa. O nome do Worker continua aproar-web. Secrets e variáveis existentes são preservados no deploy.

## Conferir

Compare colaboradores, obras e apontamentos históricos. Crie uma convocação e um apontamento com vários serviços, atualize e confira a persistência. Teste conflitos de turnos, falta, atestado, retroativo, adicionais e os relatórios PDF/Excel. Supervisor grava sua própria equipe; Financeiro ajusta pagamentos; Somente visualizar não grava.

Não foi feita migração ou gravação remota por este pacote. O Streamlit permanece no banco atual. Novos registros do Streamlit não aparecem automaticamente na branch de homologação, que é uma cópia de testes. A passagem à produção exige uma etapa posterior; a gravação desta versão é limitada ao ambiente homologacao.

## Validação técnica

npm --prefix cloudflare test verifica transações PostgreSQL, desfazer integralmente uma operação que falhe, conflitos, serviços, permissões, ajustes financeiros e prevenção de duplicação em tentativas repetidas. Os testes usam um banco isolado, sem acessar o Neon do usuário.

As gravações são feitas em uma transação com auditoria e controle de versão. Alterações concorrentes exigem atualizar os dados, evitando sobrescrever silenciosamente o histórico. Não foi possível fazer conferência visual em navegador neste ambiente.

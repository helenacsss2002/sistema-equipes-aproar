# Trello — configuração de acesso

O quadro de referência é https://trello.com/b/TX8hGvmI.

Para a consulta pela API REST, configure os segredos `TRELLO_API_KEY` e `TRELLO_API_TOKEN` no Cloudflare Worker `sistema-equipes-aproar` (Settings > Variables and Secrets). Os valores ficam exclusivamente no servidor; não devem ser inseridos no front-end ou salvos no GitHub.

Para a sincronização agendada pelo GitHub Actions, adicione os mesmos nomes como Actions secrets no repositório, separadamente do Cloudflare. Preserve também o secret `DATABASE_URL` já existente.

Use um token gerado por uma conta corporativa com acesso ao quadro e escopo `read` (somente leitura). Não utilize a conta de alguém que está saindo da empresa. Nunca compartilhe tokens em chats ou commits.

A API exige chave + token mesmo quando o quadro é público. Configure as credenciais antes de validar a sincronização manual e o workflow de 12 horas.

Verificações: na Controladoria > Configurações, carregue listas do Trello, realize uma sincronização manual com poucas obras e confirme que registros históricos não foram apagados. Só depois confirme a sincronização automática.

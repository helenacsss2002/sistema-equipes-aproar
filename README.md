# Controle de Equipes e Medições — APROAR

Projeto separado da Torre de Controle Logístico.

## Arquitetura

GitHub → Streamlit Cloud → Supabase/PostgreSQL  
                     ↘ Trello

O Trello é a fonte das obras/cartões.  
O Supabase guarda colaboradores, convocações, apontamentos e histórico de medições.

## Arquivos fixos

- `app.py` — aplicação
- `requirements.txt` — dependências
- `schema.sql` — criação das tabelas

Não há arquivos v2/v3. Todas as mudanças futuras são feitas sobre esses arquivos.

## Secrets do Streamlit

```toml
[connections.postgresql]
dialect = "postgresql"
host = "HOST_TRANSACTION_POOLER"
port = "6543"
database = "postgres"
username = "USUARIO"
password = "SENHA"
sslmode = "require"

[trello]
key = "TRELLO_KEY"
token = "TRELLO_TOKEN"
board_id = "67503e37f48a3a5c8500025e"
```

Use o Transaction Pooler do Supabase para o app Streamlit.

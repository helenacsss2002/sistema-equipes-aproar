-- SISTEMA DE EQUIPES, APONTAMENTOS E MEDIÇÕES — APROAR
-- Execute uma única vez no SQL Editor do NOVO projeto Supabase.

CREATE TABLE IF NOT EXISTS colaboradores (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    funcao_base TEXT NOT NULL,
    frente_base TEXT NOT NULL,
    unidade_habitual TEXT,
    local_moradia TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS obras_trello (
    id BIGSERIAL PRIMARY KEY,
    trello_card_id TEXT NOT NULL UNIQUE,
    nome_original TEXT NOT NULL,
    numero_obra TEXT,
    titulo TEXT,
    unidade TEXT,
    pipe TEXT,
    lista_trello TEXT,
    origem TEXT,
    etiquetas TEXT,
    url_trello TEXT,
    data_atividade_trello TIMESTAMPTZ,
    sincronizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_obras_trello_lista ON obras_trello(lista_trello);
CREATE INDEX IF NOT EXISTS idx_obras_trello_numero ON obras_trello(numero_obra);

CREATE TABLE IF NOT EXISTS convocacoes (
    id BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL,
    trello_card_id TEXT,
    engenheiro TEXT NOT NULL,
    observacao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_convocacoes_data ON convocacoes(data);

CREATE TABLE IF NOT EXISTS convocacao_itens (
    id BIGSERIAL PRIMARY KEY,
    convocacao_id BIGINT NOT NULL REFERENCES convocacoes(id) ON DELETE CASCADE,
    colaborador_id BIGINT REFERENCES colaboradores(id),
    nome_exibicao TEXT NOT NULL,
    tipo_vinculo TEXT NOT NULL CHECK (tipo_vinculo IN ('FIXO','AVULSO')),
    funcao_executada TEXT NOT NULL,
    frente TEXT NOT NULL,
    observacao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS apontamentos (
    id BIGSERIAL PRIMARY KEY,
    convocacao_item_id BIGINT NOT NULL UNIQUE
        REFERENCES convocacao_itens(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'Pendente'
        CHECK (status IN ('Pendente','Presença','Falta','Atestado')),
    extra_valor NUMERIC(12,2) NOT NULL DEFAULT 0,
    observacao TEXT,
    atualizado_em TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS medicoes (
    id BIGSERIAL PRIMARY KEY,
    competencia DATE NOT NULL UNIQUE,
    nome_lista_trello TEXT NOT NULL,
    status_fechamento TEXT NOT NULL DEFAULT 'Aberta',
    ultima_sincronizacao TIMESTAMPTZ,
    fechado_em TIMESTAMPTZ,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS medicao_itens (
    id BIGSERIAL PRIMARY KEY,
    medicao_id BIGINT NOT NULL REFERENCES medicoes(id) ON DELETE CASCADE,
    trello_card_id TEXT NOT NULL,
    nome_original TEXT NOT NULL,
    numero_obra TEXT,
    titulo TEXT,
    unidade TEXT,
    pipe TEXT,
    origem TEXT NOT NULL DEFAULT 'OUTROS',
    etiquetas TEXT,
    url_trello TEXT,
    presente_na_lista BOOLEAN NOT NULL DEFAULT TRUE,
    status_medicao TEXT NOT NULL DEFAULT 'Pendente',
    valor_orcamento NUMERIC(14,2),
    valor_aprovado NUMERIC(14,2),
    resultado NUMERIC(14,2),
    percentual NUMERIC(10,4),
    observacao TEXT,
    sincronizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ,
    UNIQUE (medicao_id, trello_card_id)
);

CREATE INDEX IF NOT EXISTS idx_medicao_itens_medicao ON medicao_itens(medicao_id);
CREATE INDEX IF NOT EXISTS idx_medicao_itens_origem ON medicao_itens(origem);

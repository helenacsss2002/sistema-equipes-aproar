import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import json
from fpdf import FPDF
import unicodedata
import re
import os
import io
import time
import traceback
import uuid
import requests
import openpyxl
from zoneinfo import ZoneInfo
import hmac
import html as _html
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# --- APROAR | FASE 1 DE PRODUÇÃO (migração não destrutiva) ---
# --- CONFIGURAÇÕES DA PÁGINA & TEMA APROAR (CLARO / AZUL) ---
st.set_page_config(page_title="APROAR - Gestão de Equipes", page_icon="👷", layout="wide")


# Paleta principal. Se a identidade visual mudar, basta alterar o azul aqui e no CSS abaixo.
AZUL_APROAR = "#2563EB"
AZUL_APROAR_ESCURO = "#1D4ED8"

st.html("""
    <style>
    :root {
        --aproar-blue: #2563EB;
        --aproar-blue-dark: #1D4ED8;
        --aproar-blue-soft: #EFF6FF;
        --aproar-bg: #FFFFFF;
        --aproar-sidebar: #0F172A;
        --aproar-text: #0F172A;
        --aproar-muted: #64748B;
        --aproar-border: #E2E8F0;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp,
    [data-testid="stMain"], .main {
        background-color: var(--aproar-bg) !important;
        color: var(--aproar-text) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(255,255,255,0.96) !important;
        border-bottom: 1px solid #F1F5F9 !important;
    }

    h1, h2, h3, h4, h5, h6, p, label,
    .stMarkdown, .stText {
        color: var(--aproar-text) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Não sobrescreve a fonte dos ícones internos do Streamlit.
       Isso evita aparecer texto como _arrow_right no lugar das setas. */
    .material-symbols-rounded, .material-symbols-outlined,
    [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
    }

    small, .stCaption, [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: var(--aproar-muted) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
        width: 240px !important;
        min-width: 240px !important;
        padding-top: 15px;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-left: 15px;
        padding-right: 15px;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #334155 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stImage"] {
        margin-top: 4px;
        margin-bottom: 2px;
    }
    .aproar-sidebar-section {
        color: #94A3B8 !important;
        font-size: 10px !important;
        line-height: 1.2 !important;
        letter-spacing: 1.35px !important;
        font-weight: 800 !important;
        margin: 17px 2px 7px 2px !important;
        text-transform: uppercase;
    }

    /* Campos de formulário */
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    input, textarea, div[role="combobox"] {
        background-color: #FFFFFF !important;
        color: var(--aproar-text) !important;
        border-color: #CBD5E1 !important;
        border-radius: 8px !important;
    }
    input::placeholder, textarea::placeholder {
        color: #94A3B8 !important;
    }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        color: var(--aproar-text) !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: var(--aproar-text) !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: var(--aproar-blue-soft) !important;
        color: var(--aproar-blue-dark) !important;
    }

    /* Tags do multiselect */
    div[data-baseweb="tag"] {
        background-color: var(--aproar-blue) !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="tag"] * { color: #FFFFFF !important; }

    /* Botões */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stFileUploader"] button {
        background: var(--aproar-blue) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--aproar-blue) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transition: all 0.18s ease;
    }
    .stButton > button *, .stDownloadButton > button *,
    [data-testid="stFormSubmitButton"] > button *,
    [data-testid="stFileUploader"] button * {
        color: #FFFFFF !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    [data-testid="stFileUploader"] button:hover {
        background: var(--aproar-blue-dark) !important;
        border-color: var(--aproar-blue-dark) !important;
        transform: translateY(-1px);
    }

    /* Navegação lateral: azul Aproar sobre fundo escuro */
    section[data-testid="stSidebar"] .stButton > button {
        min-height: 40px !important;
        margin-bottom: 5px !important;
        justify-content: flex-start !important;
        padding-left: 14px !important;
        background: #2563EB !important;
        border-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #1D4ED8 !important;
        border-color: #1D4ED8 !important;
    }
    section[data-testid="stSidebar"] .stButton > button * {
        color: #FFFFFF !important;
    }

    /* Evita rolagem horizontal criada por componentes largos no modo wide */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow-x: hidden !important;
    }
    main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    @media (max-width: 900px) {
        main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Containers e métricas */
    div[data-testid="stVerticalBlock"] > div[style*="border"],
    [data-testid="stMetric"],
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-color: var(--aproar-border) !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    }
    [data-testid="stMetricLabel"] *, [data-testid="stMetricValue"] * {
        color: var(--aproar-text) !important;
    }

    /* Abas */
    [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid var(--aproar-border);
    }
    [data-baseweb="tab"] {
        color: #475569 !important;
        background: transparent !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--aproar-blue) !important;
        font-weight: 700 !important;
    }
    [data-baseweb="tab-highlight"] {
        background-color: var(--aproar-blue) !important;
    }

    /* Tabelas / editor */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        border: 1px solid var(--aproar-border) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }

    /* Upload */
    [data-testid="stFileUploaderDropzone"] {
        background: #F8FAFC !important;
        border-color: #CBD5E1 !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: var(--aproar-text) !important;
    }

    /* Alertas continuam coloridos, mas com texto legível */
    [data-testid="stAlert"] p, [data-testid="stAlert"] span {
        color: inherit !important;
    }

    hr { border-color: var(--aproar-border) !important; }
    </style>
""")


# --- UI APROAR | OPÇÃO 4 — MINIMALISTA, REALISTA E FUNCIONAL ---
st.html("""
<style>
/* Base */
:root {
    --ui-navy: #0B1B34;
    --ui-navy-2: #102442;
    --ui-blue: #2563EB;
    --ui-blue-hover: #1D4ED8;
    --ui-blue-soft: #EFF6FF;
    --ui-bg: #F8FAFC;
    --ui-card: #FFFFFF;
    --ui-text: #10213D;
    --ui-muted: #6B7C93;
    --ui-border: #DCE5F0;
    --ui-green: #10B981;
    --ui-orange: #F59E0B;
    --ui-red: #F43F5E;
    --ui-purple: #7C3AED;
}

html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {
    background: var(--ui-bg) !important;
    color: var(--ui-text) !important;
}
main .block-container {
    max-width: 1500px !important;
    padding-top: 4.25rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Tipografia mais próxima de um produto real */
html, body, p, label, input, textarea, button, .stMarkdown, .stCaption {
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif !important;
}
h1, h2, h3, h4, h5, h6 { letter-spacing: -0.02em !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--ui-navy) !important;
    border-right: 1px solid #18304F !important;
    width: 250px !important;
    min-width: 250px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 16px 14px 18px 14px !important;
}
section[data-testid="stSidebar"] [data-testid="stImage"] {
    max-width: 170px !important;
    margin: 0 auto 2px auto !important;
}
.aproar-sidebar-subtitle {
    text-align: center;
    color: #9FB0C7 !important;
    font-size: 11px;
    letter-spacing: .9px;
    margin: -3px 0 18px 0;
    font-weight: 600;
}
.aproar-sidebar-section {
    color: #7890AE !important;
    font-size: 9px !important;
    letter-spacing: 1.25px !important;
    font-weight: 700 !important;
    margin: 18px 8px 7px 8px !important;
    text-transform: uppercase;
}
section[data-testid="stSidebar"] .stButton { margin: 0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    min-height: 39px !important;
    width: 100% !important;
    justify-content: flex-start !important;
    padding: 0 12px !important;
    margin: 2px 0 !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #D7E1EE !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transform: none !important;
}
section[data-testid="stSidebar"] .stButton > button * { color: #D7E1EE !important; }
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #142A49 !important;
    border-color: #203A5C !important;
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--ui-blue) !important;
    border-color: var(--ui-blue) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] hr { border-color: #28415F !important; margin: 14px 0 !important; }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #8FA3BD !important;
    font-size: 11px !important;
}

/* Botões do conteúdo: secundário branco, primário azul */
main .stButton > button,
main .stDownloadButton > button {
    min-height: 40px !important;
    background: #FFFFFF !important;
    color: #24466F !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transform: none !important;
}
main .stButton > button:hover,
main .stDownloadButton > button:hover {
    background: #F7FAFE !important;
    border-color: #B8C8DD !important;
    color: #173A65 !important;
    transform: none !important;
}
main [data-testid="stBaseButton-primary"],
main .stButton > button[kind="primary"],
main [data-testid="stFormSubmitButton"] > button {
    background: var(--ui-blue) !important;
    color: #FFFFFF !important;
    border-color: var(--ui-blue) !important;
}
main [data-testid="stBaseButton-primary"] *,
main .stButton > button[kind="primary"] *,
main [data-testid="stFormSubmitButton"] > button * { color: #FFFFFF !important; }
main [data-testid="stBaseButton-primary"]:hover,
main .stButton > button[kind="primary"]:hover,
main [data-testid="stFormSubmitButton"] > button:hover {
    background: var(--ui-blue-hover) !important;
    border-color: var(--ui-blue-hover) !important;
}

/* Inputs */
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] > div,
div[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
div[role="combobox"] {
    min-height: 42px !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
}
[data-testid="stDateInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: var(--ui-text) !important;
}

/* Containers nativos */
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stExpander"] {
    border-color: var(--ui-border) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    background: #FFFFFF !important;
}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {
    border: 1px solid var(--ui-border) !important;
    border-radius: 9px !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

/* Cabeçalho da home */
.aproar-page-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin: 2px 0 18px 0;
}
.aproar-page-title-wrap { display: flex; align-items: center; gap: 14px; }
.aproar-page-icon {
    width: 48px; height: 48px;
    border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    background: #EEF5FF;
    color: var(--ui-blue);
    font-size: 24px;
    flex: 0 0 auto;
}
.aproar-page-title { font-size: 31px; line-height: 1.05; font-weight: 750; color: var(--ui-text); margin: 0; }
.aproar-page-subtitle { color: #7B8CA4; margin-top: 5px; font-size: 14px; }
.aproar-date-card {
    border: 1px solid #E4EAF2;
    background: #F7FAFF;
    border-radius: 10px;
    padding: 11px 15px;
    min-width: 280px;
    color: #24466F;
    font-size: 13px;
}
.aproar-date-card strong { color: #17385F; font-size: 13px; }
.aproar-date-card span { color: #7C8DA5; font-size: 12px; }

/* Métricas */
.aproar-metric-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
    margin: 16px 0 16px 0;
}
.aproar-metric {
    background: #FFFFFF;
    border: 1px solid var(--ui-border);
    border-radius: 10px;
    min-height: 116px;
    padding: 17px 17px;
    display: flex;
    align-items: flex-start;
    gap: 13px;
}
.aproar-metric-icon {
    width: 42px; height: 42px;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex: 0 0 auto;
}
.aproar-icon-blue { background:#EDF5FF; color:#1670F8; }
.aproar-icon-green { background:#EAF9F2; color:#10A76F; }
.aproar-icon-orange { background:#FFF5E3; color:#E78B00; }
.aproar-icon-red { background:#FFF0F3; color:#E62E50; }
.aproar-icon-purple { background:#F4EDFF; color:#7432D6; }
.aproar-metric-label { color:#40536D; font-size:11px; font-weight:700; text-transform:uppercase; margin-top:1px; }
.aproar-metric-value { color:#091A33; font-size:29px; line-height:1; font-weight:760; margin:6px 0 6px 0; }
.aproar-metric-note { color:#7D8EA5; font-size:11px; line-height:1.25; }
.aproar-note-green { color:#0E9F6E; font-weight:700; }
.aproar-note-orange { color:#D77B00; font-weight:700; }
.aproar-note-red { color:#DC3454; font-weight:700; }

/* Painéis centrais */
.aproar-panel {
    border: 1px solid var(--ui-border);
    border-radius: 10px;
    background: #FFFFFF;
    padding: 16px;
    min-height: 100%;
}
.aproar-panel.attention { background: #FFFCF5; border-color: #F1E6CB; }
.aproar-panel-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:12px; }
.aproar-panel-title { display:flex; gap:11px; align-items:center; }
.aproar-panel-title .iconbox {
    width: 40px; height: 40px; border-radius: 9px;
    display:flex; align-items:center; justify-content:center; font-size:19px;
}
.aproar-panel-title h3 { margin:0; color:#10213D; font-size:18px; font-weight:720; }
.aproar-panel-title p { margin:2px 0 0 0; color:#8090A7 !important; font-size:12px; }
.aproar-chip { border-radius:999px; padding:7px 12px; font-size:11px; font-weight:650; white-space:nowrap; }
.aproar-chip-orange { background:#FFF2D8; color:#C96D00; }
.aproar-chip-red { background:#FFE9EE; color:#D72B4C; }
.aproar-list-item {
    display:flex; align-items:center; justify-content:space-between; gap:12px;
    background:#FFFFFF; border:1px solid #E6EBF2; border-radius:9px;
    padding:12px 13px; margin-top:9px;
}
.aproar-list-left { display:flex; align-items:center; gap:11px; min-width:0; }
.aproar-mini-icon {
    width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; flex:0 0 auto;
    background:#F4F7FB; color:#56708F; font-size:15px;
}
.aproar-list-text strong { color:#142744; font-size:13px; font-weight:680; }
.aproar-list-text div { color:#71849D; font-size:11px; margin-top:2px; }
.aproar-chevron { color:#5E7898; font-size:18px; }
.aproar-conflict-item {
    background:#F9FBFE; border:1px solid #E5EBF3; border-radius:9px; padding:11px 12px; margin-top:8px;
    display:flex; justify-content:space-between; gap:10px; align-items:center;
}
.aproar-conflict-main { min-width:0; }
.aproar-conflict-type { color:#3D5574; font-size:10px; font-weight:750; text-transform:uppercase; }
.aproar-conflict-name { color:#1B3456; font-size:12px; font-weight:650; margin-top:2px; }
.aproar-conflict-detail { color:#7B8DA5; font-size:10px; margin-top:2px; }
.aproar-conflict-time { color:#E23B58; font-size:11px; font-weight:700; white-space:nowrap; }

.aproar-quick-title { display:flex; align-items:center; gap:11px; margin:15px 0 8px 0; }
.aproar-quick-icon { width:38px; height:38px; border-radius:9px; display:flex; align-items:center; justify-content:center; background:#EDF5FF; color:#2563EB; font-size:20px; }
.aproar-quick-title h3 { margin:0; font-size:18px; color:#142744; }
.aproar-quick-title p { margin:1px 0 0 0; color:#7E90A8 !important; font-size:11px; }

/* Alertas do sistema */
[data-testid="stAlert"] { border-radius:9px !important; box-shadow:none !important; }

@media (max-width: 1150px) {
    .aproar-metric-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
    .aproar-date-card { display:none; }
}
@media (max-width: 760px) {
    main .block-container { padding-top:3.6rem !important; padding-left:.85rem !important; padding-right:.85rem !important; }
    .aproar-page-title { font-size:25px; }
    .aproar-page-icon { width:42px; height:42px; }
    .aproar-metric-grid { grid-template-columns: 1fr; gap:8px; }
    .aproar-metric { min-height:94px; padding:13px; }
    .aproar-page-head { margin-bottom:12px; }
}
</style>
""")



# --- PATCH VISUAL V2: SIDEBAR + PÁGINAS ANALÍTICAS ---
st.html("""
<style>
section[data-testid="stSidebar"] .stButton > button {
    gap: 7px !important;
    min-height: 42px !important;
    font-size: 14px !important;
}
section[data-testid="stSidebar"] .stButton > button p {
    margin: 0 !important;
    font-size: 14px !important;
}

/* A sidebar não deve parecer um menu flutuante gigante em telas baixas */
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 12px !important;
}

/* Cabeçalho padrão das páginas internas */
.aproar-inner-head {
    display:flex;
    align-items:center;
    gap:12px;
    margin: 0 0 18px 0;
}
.aproar-inner-icon {
    width:44px;
    height:44px;
    border-radius:10px;
    background:#EEF5FF;
    color:#2563EB;
    display:flex;
    align-items:center;
    justify-content:center;
    flex:0 0 auto;
}
.aproar-inner-icon .material-symbols-rounded {
    font-family:"Material Symbols Rounded" !important;
    font-size:23px;
}
.aproar-inner-title { margin:0; font-size:28px; line-height:1.05; color:#10213D; font-weight:760; }
.aproar-inner-subtitle { margin-top:4px; font-size:13px; color:#8292A8; }

/* Métricas do dashboard no mesmo sistema visual da home */
.aproar-dash-metrics {
    display:grid;
    grid-template-columns:repeat(5,minmax(0,1fr));
    gap:12px;
    margin:14px 0 10px 0;
}
.aproar-dash-card {
    min-height:105px;
    padding:15px 16px;
    border:1px solid #DCE5F0;
    border-radius:10px;
    background:#FFFFFF;
}
.aproar-dash-label { font-size:10px; color:#53677F; font-weight:750; text-transform:uppercase; }
.aproar-dash-value { font-size:28px; line-height:1; color:#0C1C34; font-weight:760; margin:8px 0 5px; }
.aproar-dash-note { font-size:11px; color:#8393A8; }
.aproar-empty-card {
    border:1px solid #D9E6F5;
    background:#F4F8FE;
    border-radius:10px;
    padding:15px 17px;
    color:#35618F;
    font-size:13px;
    margin-top:12px;
}

/* O formulário analítico fica compacto e alinhado */
.aproar-filter-shell {
    border:1px solid #DCE5F0;
    background:#FFFFFF;
    border-radius:10px;
    padding:4px 10px 2px 10px;
    margin-bottom:12px;
}

@media (max-width: 1050px) {
    .aproar-dash-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width: 700px) {
    .aproar-dash-metrics { grid-template-columns:1fr; }
}
</style>
""")



# --- SIDEBAR V3: ÍCONES SVG CONSISTENTES (SEM MATERIAL ICONS) ---
st.html("""
<style>
/* Não dependemos mais da fonte de ícones do Streamlit para o menu. */
section[data-testid="stSidebar"] .stButton > button {
    position: relative !important;
    padding-left: 48px !important;
    justify-content: flex-start !important;
    gap: 0 !important;
}
section[data-testid="stSidebar"] .stButton > button::before {
    content: "";
    position: absolute;
    left: 17px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-color: currentColor;
    -webkit-mask-image: var(--nav-icon);
    mask-image: var(--nav-icon);
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    -webkit-mask-size: 20px 20px;
    mask-size: 20px 20px;
    opacity: .96;
}
section[data-testid="stSidebar"] .stButton > button p {
    margin: 0 !important;
}
/* O botão de bloquear edição não recebe ícone. */
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button {
    padding-left: 12px !important;
    justify-content: center !important;
}
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button::before { display:none !important; }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_inicio_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m3%2011%209-8%209%208%22%2F%3E%3Cpath%20d%3D%22M5%2010v10h14V10%22%2F%3E%3Cpath%20d%3D%22M9%2020v-6h6v6%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_conv_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M6%202h8l4%204v16H6z%22%2F%3E%3Cpath%20d%3D%22M14%202v5h5%22%2F%3E%3Cpath%20d%3D%22M9%2013h6%22%2F%3E%3Cpath%20d%3D%22M9%2017h6%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_conf_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%203%202.5%2020h19z%22%2F%3E%3Cpath%20d%3D%22M12%209v4%22%2F%3E%3Cpath%20d%3D%22M12%2017h.01%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_apon_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%2218%22%20height%3D%2218%22%20rx%3D%223%22%2F%3E%3Cpath%20d%3D%22m8%2012%203%203%205-6%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_wpp_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M21%2015a4%204%200%200%201-4%204H8l-5%203V7a4%204%200%200%201%204-4h10a4%204%200%200%201%204%204z%22%2F%3E%3Cpath%20d%3D%22M8%209h8%22%2F%3E%3Cpath%20d%3D%22M8%2013h5%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_disp_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M16%2021v-2a4%204%200%200%200-4-4H6a4%204%200%200%200-4%204v2%22%2F%3E%3Ccircle%20cx%3D%229%22%20cy%3D%227%22%20r%3D%224%22%2F%3E%3Cpath%20d%3D%22M22%2021v-2a4%204%200%200%200-3-3.87%22%2F%3E%3Cpath%20d%3D%22M16%203.13a4%204%200%200%201%200%207.75%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_indisp_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%229%22%2F%3E%3Cpath%20d%3D%22m5.6%205.6%2012.8%2012.8%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_dash_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221%22%2F%3E%3Crect%20x%3D%223%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_rel_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M4%2020V10%22%2F%3E%3Cpath%20d%3D%22M10%2020V4%22%2F%3E%3Cpath%20d%3D%22M16%2020v-7%22%2F%3E%3Cpath%20d%3D%22M22%2020H2%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_ind_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m3%2017%205-5%204%204%208-9%22%2F%3E%3Cpath%20d%3D%22M15%207h5v5%22%2F%3E%3C%2Fsvg%3E"); }
section[data-testid="stSidebar"] div[class*="st-key-btn_nav_cfg_ui4"] { --nav-icon: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%223%22%2F%3E%3Cpath%20d%3D%22M19.4%2015a1.65%201.65%200%200%200%20.33%201.82l.06.06-2.83%202.83-.06-.06A1.65%201.65%200%200%200%2015%2019.4a1.65%201.65%200%200%200-1%20.6%201.65%201.65%200%200%200-.4%201.08V21h-4v-.08A1.65%201.65%200%200%200%208.6%2019.4a1.65%201.65%200%200%200-1.82.33l-.06.06-2.83-2.83.06-.06A1.65%201.65%200%200%200%204.6%2015a1.65%201.65%200%200%200-.6-1%201.65%201.65%200%200%200-1.08-.4H3v-4h.08A1.65%201.65%200%200%200%204.6%208.6a1.65%201.65%200%200%200-.33-1.82l-.06-.06%202.83-2.83.06.06A1.65%201.65%200%200%200%209%204.6a1.65%201.65%200%200%200%201-.6%201.65%201.65%200%200%200%20.4-1.08V3h4v.08A1.65%201.65%200%200%200%2015.4%204.6a1.65%201.65%200%200%200%201.82-.33l.06-.06%202.83%202.83-.06.06A1.65%201.65%200%200%200%2019.4%209c.18.36.27.76.27%201.16s-.09.8-.27%201.16Z%22%2F%3E%3C%2Fsvg%3E"); }
</style>
""")



# --- APROAR REDESIGN V2 | BASE + SIDEBAR + HOME -------------------------------
st.html("""
<style>
:root{
    --r2-bg:#F5F7FA;
    --r2-surface:#FFFFFF;
    --r2-navy:#0A1830;
    --r2-navy-hover:#132947;
    --r2-blue:#245FE5;
    --r2-blue-hover:#1D4ED8;
    --r2-text:#142033;
    --r2-muted:#748197;
    --r2-border:#E4E9F0;
    --r2-border-strong:#D8DFE9;
    --r2-green:#15966B;
    --r2-amber:#C87A12;
    --r2-red:#D6455D;
}

/* Tira o máximo possível da aparência padrão do Streamlit. */
#MainMenu, footer { visibility:hidden !important; }
[data-testid="stToolbar"] { display:none !important; }
[data-testid="stDecoration"] { display:none !important; }
[data-testid="stHeader"]{
    background:rgba(245,247,250,.96) !important;
    border-bottom:0 !important;
    height:46px !important;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"]{
    background:var(--r2-bg) !important;
    color:var(--r2-text) !important;
}
main .block-container{
    max-width:1420px !important;
    padding:3.55rem 2.2rem 2.5rem !important;
}

/* Tipografia: menos "template", mais software interno real. */
html,body,p,label,input,textarea,button,.stMarkdown,.stCaption,
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{
    font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif !important;
}
h1,h2,h3,h4,h5,h6{ color:var(--r2-text) !important; letter-spacing:-.025em !important; }

/* SIDEBAR ------------------------------------------------------------------ */
section[data-testid="stSidebar"]{
    width:212px !important;
    min-width:212px !important;
    background:var(--r2-navy) !important;
    border-right:1px solid #142B4A !important;
}
section[data-testid="stSidebar"] > div:first-child{
    padding:16px 12px 14px !important;
}
section[data-testid="stSidebar"] [data-testid="stImage"]{
    max-width:146px !important;
    margin:7px auto 0 !important;
}
.aproar-sidebar-subtitle{
    color:#8093AD !important;
    font-size:9px !important;
    letter-spacing:1.5px !important;
    margin:4px 8px 16px !important;
    text-align:center !important;
    font-weight:700 !important;
}
.aproar-sidebar-section{
    color:#68809F !important;
    font-size:8px !important;
    letter-spacing:1.25px !important;
    margin:17px 9px 6px !important;
    font-weight:750 !important;
}
section[data-testid="stSidebar"] .stButton{ margin:0 !important; }
section[data-testid="stSidebar"] .stButton > button{
    min-height:38px !important;
    height:38px !important;
    margin:1px 0 !important;
    border-radius:7px !important;
    border:0 !important;
    background:transparent !important;
    color:#C9D4E2 !important;
    font-size:13px !important;
    font-weight:520 !important;
    padding-left:42px !important;
    box-shadow:none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover{
    background:var(--r2-navy-hover) !important;
    color:#FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] .stButton > button[kind="primary"]{
    background:var(--r2-blue) !important;
    color:#FFFFFF !important;
    font-weight:600 !important;
}
section[data-testid="stSidebar"] .stButton > button::before{
    left:14px !important;
    width:17px !important;
    height:17px !important;
    -webkit-mask-size:17px 17px !important;
    mask-size:17px 17px !important;
    opacity:.92 !important;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{
    color:#70839D !important;
    font-size:10px !important;
}
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button{
    min-height:31px !important;
    height:31px !important;
    padding-left:8px !important;
    color:#8295AE !important;
    font-size:11px !important;
    background:transparent !important;
}

/* HOME --------------------------------------------------------------------- */
.ap-home-head{
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:24px;
    margin:2px 0 19px;
}
.ap-home-title{font-size:30px;line-height:1.02;font-weight:750;color:var(--r2-text);}
.ap-home-sub{font-size:13px;color:var(--r2-muted);margin-top:6px;}
.ap-home-date{text-align:right;font-size:12px;color:#5F6F84;font-weight:600;}
.ap-home-date span{display:block;color:#97A3B3;font-size:11px;font-weight:450;margin-top:3px;}

/* Filtros compactos: uma barra, sem "caixa gigante". */
div[class*="st-key-ap2_filters"] [data-testid="stVerticalBlockBorderWrapper"] > div{
    background:var(--r2-surface) !important;
    border:1px solid var(--r2-border) !important;
    border-radius:9px !important;
    padding:10px 12px 8px !important;
}
div[class*="st-key-ap2_filters"] label p{
    font-size:10px !important;
    font-weight:650 !important;
    color:#66758A !important;
    margin-bottom:3px !important;
}
div[class*="st-key-ap2_filters"] div[data-baseweb="select"] > div,
div[class*="st-key-ap2_filters"] div[data-baseweb="base-input"] > div,
div[class*="st-key-ap2_filters"] div[data-baseweb="input"] > div{
    min-height:37px !important;
    height:37px !important;
    border:0 !important;
    border-radius:6px !important;
    background:#F7F9FC !important;
}
div[class*="st-key-ap2_filters"] .stButton > button{
    height:37px !important;
    min-height:37px !important;
    border-radius:6px !important;
    font-size:12px !important;
}

/* Linha de indicadores: discreta, branca, quase sem decoração. */
.ap-kpi-strip{
    display:grid;
    grid-template-columns:repeat(5,minmax(0,1fr));
    background:var(--r2-surface);
    border:1px solid var(--r2-border);
    border-radius:10px;
    margin:14px 0 16px;
    overflow:hidden;
}
.ap-kpi{
    position:relative;
    padding:16px 18px 15px;
    min-height:94px;
    border-right:1px solid var(--r2-border);
}
.ap-kpi:last-child{border-right:0;}
.ap-kpi-label{font-size:10px;text-transform:uppercase;letter-spacing:.35px;color:#69798F;font-weight:700;}
.ap-kpi-row{display:flex;align-items:baseline;gap:7px;margin-top:8px;}
.ap-kpi-value{font-size:27px;line-height:1;font-weight:730;color:#142033;}
.ap-kpi-badge{font-size:10px;font-weight:650;color:#76879D;}
.ap-kpi-note{font-size:10px;color:#9AA6B6;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ap-kpi.ok .ap-kpi-value{color:#177E61;}
.ap-kpi.warn .ap-kpi-value{color:#B66B13;}
.ap-kpi.danger .ap-kpi-value{color:#C44459;}

/* Conteúdo de ação: cards brancos e acentos laterais, sem fundos pastel grandes. */
.ap-action-grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(320px,.9fr);gap:14px;align-items:start;}
.ap-card{
    background:var(--r2-surface);
    border:1px solid var(--r2-border);
    border-radius:10px;
    padding:16px;
}
.ap-card-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px;}
.ap-card-title{font-size:15px;font-weight:700;color:#1A283B;}
.ap-card-sub{font-size:11px;color:#8A97A9;margin-top:3px;}
.ap-pill{font-size:10px;font-weight:650;color:#5E6B7B;background:#F2F4F7;border-radius:999px;padding:5px 9px;white-space:nowrap;}
.ap-pill.red{background:#FFF0F2;color:#C34458;}
.ap-pill.amber{background:#FFF6E9;color:#B66F15;}

.ap-task-list{display:flex;flex-direction:column;gap:7px;}
.ap-task{
    display:flex;align-items:center;justify-content:space-between;gap:14px;
    padding:11px 12px;
    border:1px solid #E9EDF3;
    border-left:3px solid #D6DEE8;
    border-radius:7px;
    background:#FFFFFF;
}
.ap-task.amber{border-left-color:#D4932F;}
.ap-task.red{border-left-color:#D45568;}
.ap-task.green{border-left-color:#37A17B;}
.ap-task strong{display:block;font-size:12px;color:#25354A;font-weight:650;}
.ap-task span{display:block;font-size:10px;color:#8A97A9;margin-top:2px;}
.ap-task-count{font-size:11px;font-weight:700;color:#5C6D83;white-space:nowrap;}

.ap-conflict-list{display:flex;flex-direction:column;gap:7px;}
.ap-conflict{
    padding:11px 12px;
    border:1px solid #E8EDF3;
    border-radius:7px;
    background:#FFFFFF;
}
.ap-conflict-top{display:flex;justify-content:space-between;gap:10px;align-items:center;}
.ap-conflict-name{font-size:12px;font-weight:670;color:#26364C;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ap-conflict-time{font-size:10px;color:#C34B5E;font-weight:650;}
.ap-conflict-detail{font-size:10px;color:#8B98AA;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

/* Ações rápidas pequenas, sem cards chamativos. */
.ap-quick-head{font-size:13px;font-weight:700;color:#314258;margin:17px 0 8px;}
div[class*="st-key-ap2_quick"] .stButton > button{
    min-height:36px !important;
    height:36px !important;
    font-size:11px !important;
    font-weight:600 !important;
    border:1px solid var(--r2-border) !important;
    background:#FFFFFF !important;
    color:#3E526C !important;
    border-radius:7px !important;
    box-shadow:none !important;
}
div[class*="st-key-ap2_quick"] .stButton > button:hover{
    border-color:#BFCBDC !important;
    background:#F9FAFC !important;
}
div[class*="st-key-ap2_quick"] [data-testid="stBaseButton-primary"]{
    background:var(--r2-blue) !important;
    color:#FFFFFF !important;
    border-color:var(--r2-blue) !important;
}

/* Componentes gerais mais secos. */
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stExpander"]{
    border-color:var(--r2-border) !important;
    box-shadow:none !important;
}
[data-testid="stAlert"]{border-radius:8px !important;box-shadow:none !important;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border-color:var(--r2-border) !important;box-shadow:none !important;}
main .stButton > button, main .stDownloadButton > button{
    box-shadow:none !important;
    border-radius:7px !important;
}

@media(max-width:1100px){
    .ap-kpi-strip{grid-template-columns:repeat(2,minmax(0,1fr));}
    .ap-kpi{border-bottom:1px solid var(--r2-border);}
    .ap-action-grid{grid-template-columns:1fr;}
}
@media(max-width:760px){
    section[data-testid="stSidebar"]{width:208px !important;min-width:208px !important;}
    main .block-container{padding:3.4rem .9rem 2rem !important;}
    .ap-home-title{font-size:25px;}
    .ap-home-date{display:none;}
    .ap-kpi-strip{grid-template-columns:1fr;}
    .ap-kpi{border-right:0;border-bottom:1px solid var(--r2-border);}
}
</style>
""")




# --- PATCH REDESIGN V2.1 | BOTÕES DE AÇÕES RÁPIDAS ---------------------------
st.html("""
<style>
/* Corrige texto invisível/colapsado dos botões de ações rápidas e dá acabamento consistente. */
div[class*="st-key-ap2_quick_conv"] button,
div[class*="st-key-ap2_quick_conv"] button,
div[class*="st-key-ap2_quick_apon"] button,
div[class*="st-key-ap2_quick_disp"] button,
div[class*="st-key-ap2_quick_ind"] button{
    position:relative !important;
    justify-content:flex-start !important;
    padding:0 12px 0 38px !important;
    gap:0 !important;
    overflow:visible !important;
}

div[class*="st-key-ap2_quick_conv"] button *,
div[class*="st-key-ap2_quick_conv"] button *,
div[class*="st-key-ap2_quick_apon"] button *,
div[class*="st-key-ap2_quick_disp"] button *,
div[class*="st-key-ap2_quick_ind"] button *{
    display:inline !important;
    visibility:visible !important;
    opacity:1 !important;
    font-size:12px !important;
    line-height:1 !important;
    white-space:nowrap !important;
}

div[class*="st-key-ap2_quick_conv"] button *{
    color:inherit !important;
}
div[class*="st-key-ap2_quick_apon"] button *,
div[class*="st-key-ap2_quick_disp"] button *,
div[class*="st-key-ap2_quick_ind"] button *{ color:#35485F !important; }

/* Ícones SVG pequenos no mesmo estilo da sidebar. */
div[class*="st-key-ap2_quick_conv"] button::before,
div[class*="st-key-ap2_quick_apon"] button::before,
div[class*="st-key-ap2_quick_disp"] button::before,
div[class*="st-key-ap2_quick_ind"] button::before{
    content:"";
    position:absolute;
    left:13px;
    top:50%;
    transform:translateY(-50%);
    width:15px;
    height:15px;
    background-color:currentColor;
    -webkit-mask-repeat:no-repeat;
    mask-repeat:no-repeat;
    -webkit-mask-position:center;
    mask-position:center;
    -webkit-mask-size:15px 15px;
    mask-size:15px 15px;
    opacity:.9;
}

div[class*="st-key-ap2_quick_conv"] button::before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M12 5v14M5 12h14'/%3E%3C/svg%3E");
    mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M12 5v14M5 12h14'/%3E%3C/svg%3E");
}
div[class*="st-key-ap2_quick_apon"] button::before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='3'/%3E%3Cpath d='m8 12 3 3 5-6'/%3E%3C/svg%3E");
    mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='3'/%3E%3Cpath d='m8 12 3 3 5-6'/%3E%3C/svg%3E");
}
div[class*="st-key-ap2_quick_disp"] button::before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='9' cy='7' r='4'/%3E%3Cpath d='M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'/%3E%3C/svg%3E");
    mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='9' cy='7' r='4'/%3E%3Cpath d='M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'/%3E%3C/svg%3E");
}
div[class*="st-key-ap2_quick_ind"] button::before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 17 5-5 4 4 8-9'/%3E%3Cpath d='M15 7h5v5'/%3E%3C/svg%3E");
    mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 17 5-5 4 4 8-9'/%3E%3Cpath d='M15 7h5v5'/%3E%3C/svg%3E");
}

/* Mais equilíbrio horizontal na faixa dos filtros e ações em telas grandes. */
@media(min-width:1200px){
    div[class*="st-key-ap2_quick"]{ max-width:980px; }
}
</style>
""")




# --- PATCH REDESIGN V2.2 | AÇÕES RÁPIDAS ADAPTATIVAS AO TEMA -----------------
# Usa as variáveis de tema do próprio Streamlit. Assim os botões acompanham
# tema claro, escuro e a opção "System" sem manter fundo branco fixo.
st.html("""
<style>
.ap-quick-head{
    color:var(--st-text-color, var(--text-color, #314258)) !important;
}

/* Todas as ações rápidas acompanham o tema atual. */
div[class*="st-key-ap2_quick_conv"] button,
div[class*="st-key-ap2_quick_apon"] button,
div[class*="st-key-ap2_quick_disp"] button,
div[class*="st-key-ap2_quick_ind"] button{
    background:var(
        --st-secondary-background-color,
        var(--secondary-background-color, #FFFFFF)
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color, #35485F)
    ) !important;
    border-color:var(
        --st-border-color,
        rgba(128, 140, 158, .28)
    ) !important;
}

/* O texto interno herda a cor real do botão. */
div[class*="st-key-ap2_quick_conv"] button *,
div[class*="st-key-ap2_quick_apon"] button *,
div[class*="st-key-ap2_quick_disp"] button *,
div[class*="st-key-ap2_quick_ind"] button *{
    color:inherit !important;
}

/* Hover também acompanha o tema, sem virar um retângulo branco no escuro. */
div[class*="st-key-ap2_quick_conv"] button:hover,
div[class*="st-key-ap2_quick_apon"] button:hover,
div[class*="st-key-ap2_quick_disp"] button:hover,
div[class*="st-key-ap2_quick_ind"] button:hover{
    background:color-mix(
        in srgb,
        var(--st-text-color, var(--text-color, #35485F)) 7%,
        var(--st-secondary-background-color, var(--secondary-background-color, #FFFFFF))
    ) !important;
    border-color:color-mix(
        in srgb,
        var(--st-text-color, var(--text-color, #35485F)) 24%,
        transparent
    ) !important;
}



/* Fallback para navegadores/versões que não exponham as variáveis do tema. */
@media (prefers-color-scheme: dark){
    div[class*="st-key-ap2_quick_conv"] button,
    div[class*="st-key-ap2_quick_apon"] button,
    div[class*="st-key-ap2_quick_disp"] button,
    div[class*="st-key-ap2_quick_ind"] button{
        background:var(
            --st-secondary-background-color,
            var(--secondary-background-color, #172033)
        ) !important;
        color:var(
            --st-text-color,
            var(--text-color, #E6ECF4)
        ) !important;
        border-color:var(
            --st-border-color,
            #2C3950
        ) !important;
    }
}
</style>
""")




# --- PATCH V2.4 | CORREÇÃO DEFINITIVA DO BOTÃO NOVA CONVOCAÇÃO --------------
st.html("""
<style>
div[class*="st-key-ap2_quick_conv"] button{
    background:var(
        --st-secondary-background-color,
        var(--secondary-background-color, #FFFFFF)
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color, #35485F)
    ) !important;
    border:1px solid var(
        --st-border-color,
        rgba(128,140,158,.28)
    ) !important;
    box-shadow:none !important;
}

div[class*="st-key-ap2_quick_conv"] button *,
div[class*="st-key-ap2_quick_conv"] button p,
div[class*="st-key-ap2_quick_conv"] button span{
    color:inherit !important;
    -webkit-text-fill-color:currentColor !important;
    opacity:1 !important;
}

div[class*="st-key-ap2_quick_conv"] button::before{
    background-color:currentColor !important;
}

div[class*="st-key-ap2_quick_conv"] button:hover{
    background:color-mix(
        in srgb,
        var(--st-text-color, var(--text-color, #35485F)) 7%,
        var(--st-secondary-background-color, var(--secondary-background-color, #FFFFFF))
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color, #35485F)
    ) !important;
}

@media (prefers-color-scheme: dark){
    div[class*="st-key-ap2_quick_conv"] button{
        background:var(
            --st-secondary-background-color,
            var(--secondary-background-color, #172033)
        ) !important;
        color:var(
            --st-text-color,
            var(--text-color, #E6ECF4)
        ) !important;
        border-color:var(--st-border-color, #2C3950) !important;
    }
}
</style>
""")




# --- APROAR DESIGN SYSTEM V3 | PÁGINAS INTERNAS + TABELAS -------------------
st.html("""
<style>
/* Variáveis com fallback: acompanham Light / Dark / System quando o Streamlit
   expõe o tema, mas continuam consistentes com a identidade APROAR. */
:root{
    --ap3-bg:var(--st-background-color, var(--background-color, #F5F7FA));
    --ap3-surface:var(--st-secondary-background-color, var(--secondary-background-color, #FFFFFF));
    --ap3-text:var(--st-text-color, var(--text-color, #172033));
    --ap3-primary:var(--st-primary-color, var(--primary-color, #245FE5));
    --ap3-muted:color-mix(in srgb, var(--ap3-text) 58%, transparent);
    --ap3-border:color-mix(in srgb, var(--ap3-text) 14%, transparent);
    --ap3-border-soft:color-mix(in srgb, var(--ap3-text) 9%, transparent);
}

/* Cabeçalho padrão das páginas internas */
.ap3-page-head{
    display:flex;
    justify-content:space-between;
    align-items:flex-end;
    gap:22px;
    margin:2px 0 20px;
    padding-bottom:15px;
    border-bottom:1px solid var(--ap3-border-soft);
}
.ap3-page-kicker{
    font-size:9px;
    text-transform:uppercase;
    letter-spacing:1.2px;
    font-weight:750;
    color:var(--ap3-primary);
    margin-bottom:6px;
}
.ap3-page-title{
    font-size:28px;
    line-height:1.05;
    font-weight:760;
    letter-spacing:-.025em;
    color:var(--ap3-text);
}
.ap3-page-sub{
    font-size:12px;
    line-height:1.45;
    color:var(--ap3-muted);
    margin-top:6px;
    max-width:760px;
}
.ap3-page-side{
    font-size:10px;
    color:var(--ap3-muted);
    white-space:nowrap;
}

/* Títulos de seção sem excesso de emoji/decoracão */
.ap3-section{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin:20px 0 9px;
}
.ap3-section-title{
    font-size:14px;
    font-weight:700;
    color:var(--ap3-text);
}
.ap3-section-sub{
    font-size:10px;
    color:var(--ap3-muted);
    margin-top:2px;
}

/* Tabs com aparência de software, não de formulário Streamlit */
[data-testid="stTabs"] [data-baseweb="tab-list"]{
    gap:22px !important;
    border-bottom:1px solid var(--ap3-border-soft) !important;
    margin-bottom:13px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]{
    height:39px !important;
    padding:0 2px !important;
    background:transparent !important;
    border-radius:0 !important;
    color:var(--ap3-muted) !important;
    font-size:12px !important;
    font-weight:600 !important;
}
[data-testid="stTabs"] [aria-selected="true"]{
    color:var(--ap3-primary) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{
    background:var(--ap3-primary) !important;
    height:2px !important;
}

/* Campos mais compactos e consistentes */
main label p{
    font-size:10px !important;
    font-weight:650 !important;
    color:var(--ap3-muted) !important;
}
main div[data-baseweb="select"] > div,
main div[data-baseweb="base-input"] > div,
main div[data-baseweb="input"] > div,
main [data-baseweb="textarea"] > div,
main div[role="combobox"]{
    min-height:39px !important;
    border-radius:7px !important;
    border:1px solid var(--ap3-border) !important;
    background:var(--ap3-surface) !important;
    box-shadow:none !important;
}
main input, main textarea{
    color:var(--ap3-text) !important;
}

/* Containers e expanders */
main [data-testid="stVerticalBlockBorderWrapper"] > div{
    border:1px solid var(--ap3-border-soft) !important;
    border-radius:9px !important;
    background:var(--ap3-surface) !important;
    box-shadow:none !important;
}
main [data-testid="stExpander"]{
    border:1px solid var(--ap3-border-soft) !important;
    border-radius:9px !important;
    background:var(--ap3-surface) !important;
    box-shadow:none !important;
}
main [data-testid="stExpander"] summary{
    font-size:12px !important;
    font-weight:650 !important;
}

/* Métricas nativas */
[data-testid="stMetric"]{
    background:var(--ap3-surface) !important;
    border:1px solid var(--ap3-border-soft) !important;
    border-radius:9px !important;
    padding:13px 15px !important;
}
[data-testid="stMetricLabel"] p{
    font-size:9px !important;
    text-transform:uppercase !important;
    letter-spacing:.45px !important;
    font-weight:700 !important;
    color:var(--ap3-muted) !important;
}
[data-testid="stMetricValue"]{
    font-size:24px !important;
    font-weight:720 !important;
    color:var(--ap3-text) !important;
}

/* -------------------- TABELAS BONITINHAS -------------------- */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"]{
    border:1px solid var(--ap3-border) !important;
    border-radius:10px !important;
    overflow:hidden !important;
    background:var(--ap3-surface) !important;
    box-shadow:0 1px 2px rgba(15,23,42,.035) !important;
}
[data-testid="stDataFrame"] > div,
[data-testid="stDataEditor"] > div{
    border-radius:10px !important;
    background:var(--ap3-surface) !important;
}

/* Cabeçalhos / células quando a versão do Glide expõe os roles no DOM */
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataEditor"] [role="columnheader"]{
    background:color-mix(in srgb, var(--ap3-text) 5%, var(--ap3-surface)) !important;
    color:var(--ap3-text) !important;
    font-size:10px !important;
    font-weight:700 !important;
    border-bottom:1px solid var(--ap3-border) !important;
}
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataEditor"] [role="gridcell"]{
    color:var(--ap3-text) !important;
    font-size:11px !important;
    border-color:var(--ap3-border-soft) !important;
}

/* Toolbar da tabela fica discreta */
[data-testid="stDataFrame"] button,
[data-testid="stDataEditor"] button{
    border-radius:6px !important;
    box-shadow:none !important;
}

/* Botões da área principal */
main .stButton > button,
main .stDownloadButton > button{
    min-height:38px !important;
    border-radius:7px !important;
    font-size:11px !important;
    font-weight:620 !important;
    box-shadow:none !important;
}
main [data-testid="stBaseButton-primary"],
main .stButton > button[kind="primary"],
main [data-testid="stFormSubmitButton"] > button{
    background:var(--ap3-primary) !important;
    border-color:var(--ap3-primary) !important;
    color:#FFF !important;
}

/* Alertas menos "cartazes" */
[data-testid="stAlert"]{
    border-radius:8px !important;
    box-shadow:none !important;
    font-size:11px !important;
}

/* Gráficos ficam dentro do mesmo ritmo visual */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"]{
    background:var(--ap3-surface) !important;
    border:1px solid var(--ap3-border-soft) !important;
    border-radius:9px !important;
    padding:8px !important;
}

@media(max-width:760px){
    .ap3-page-head{align-items:flex-start;flex-direction:column;gap:8px;}
    .ap3-page-title{font-size:24px;}
    .ap3-page-side{display:none;}
}
</style>
""")




# --- APROAR V3.1 | CORREÇÃO GLOBAL DE ESPAÇAMENTO ---------------------------
st.html("""
<style>
/* O conteúdo começa perto do topo, sem a faixa vazia que aparecia antes. */
[data-testid="stMainBlockContainer"],
main .block-container{
    padding-top:1.45rem !important;
    padding-bottom:1.6rem !important;
}

/* Sidebar também começa no topo de forma natural. */
[data-testid="stSidebarContent"]{
    padding-top:1.1rem !important;
    padding-bottom:1rem !important;
}
section[data-testid="stSidebar"]{
    padding-top:0 !important;
}
section[data-testid="stSidebar"] > div:first-child{
    padding-top:1rem !important;
}

/* Os elementos invisíveis de estilo não devem reservar altura em versões
   do Streamlit que ainda criem um container ao redor deles. */
[data-testid="stElementContainer"]:has(style),
.element-container:has(style){
    display:none !important;
    height:0 !important;
    min-height:0 !important;
    margin:0 !important;
    padding:0 !important;
}

/* Ritmo vertical geral: compacto, mas sem deixar formulário apertado. */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]{
    gap:.8rem !important;
}
main [data-testid="stForm"] [data-testid="stVerticalBlock"],
main [data-testid="stExpander"] [data-testid="stVerticalBlock"],
main [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]{
    gap:.65rem !important;
}
main [data-testid="stHorizontalBlock"]{
    gap:.75rem !important;
}

/* Sidebar: remove o ar excessivo entre logo, grupos e opções. */
[data-testid="stSidebarContent"] [data-testid="stVerticalBlock"]{
    gap:.34rem !important;
}
section[data-testid="stSidebar"] [data-testid="stImage"]{
    margin:0 auto .35rem !important;
}
.aproar-sidebar-subtitle{
    margin:4px 8px 14px !important;
}
.aproar-sidebar-section{
    margin:16px 10px 7px !important;
}
section[data-testid="stSidebar"] .stButton > button{
    margin:0 !important;
    min-height:40px !important;
    height:40px !important;
}

/* Home */
.ap-home-head{
    margin:0 0 12px !important;
}
.ap-home-sub{
    margin-top:4px !important;
}
div[class*="st-key-ap2_filters"] [data-testid="stVerticalBlockBorderWrapper"] > div{
    padding:8px 11px 7px !important;
}
.ap-kpi-strip{
    margin:10px 0 12px !important;
}
.ap-kpi{
    min-height:84px !important;
    padding:13px 16px 12px !important;
}
.ap-kpi-row{
    margin-top:6px !important;
}
.ap-kpi-note{
    margin-top:6px !important;
}
.ap-action-grid{
    gap:12px !important;
}
.ap-card{
    padding:14px !important;
}
.ap-card-head{
    margin-bottom:9px !important;
}
.ap-quick-head{
    margin:12px 0 6px !important;
}

/* Páginas internas */
.ap3-page-head{
    margin:0 0 12px !important;
    padding-bottom:10px !important;
}
.ap3-page-kicker{
    margin-bottom:4px !important;
}
.ap3-page-sub{
    margin-top:4px !important;
}
.ap3-section{
    margin:14px 0 7px !important;
}
[data-testid="stTabs"] [data-baseweb="tab-list"]{
    margin-bottom:8px !important;
}

/* Métricas e caixas ocupam menos altura sem perder legibilidade. */
[data-testid="stMetric"]{
    padding:11px 13px !important;
}
[data-testid="stMetricValue"]{
    font-size:22px !important;
}
main [data-testid="stVerticalBlockBorderWrapper"] > div{
    padding-top:.7rem;
    padding-bottom:.7rem;
}

/* Campos e botões ligeiramente mais baixos. */
main div[data-baseweb="select"] > div,
main div[data-baseweb="base-input"] > div,
main div[data-baseweb="input"] > div,
main div[role="combobox"]{
    min-height:37px !important;
}
main .stButton > button,
main .stDownloadButton > button{
    min-height:36px !important;
}

/* Espaços artificiais criados com divs vazias antigas. */
main div[style*="height:18px"],
main div[style*="height:20px"],
main div[style*="height:24px"]{
    height:8px !important;
}

@media(max-width:900px){
    [data-testid="stMainBlockContainer"],
    main .block-container{
        padding-top:1rem !important;
        padding-left:1rem !important;
        padding-right:1rem !important;
    }
}
</style>
""")




# --- APROAR V4 | ACABAMENTO CORPORATIVO -------------------------------------
st.html("""
<style>
/* ==========================================================================
   IDENTIDADE
   ========================================================================== */
:root{
    --corp-navy:#0B1B33;
    --corp-navy-2:#102746;
    --corp-blue:#245FD6;
    --corp-blue-hover:#1D51BE;
    --corp-bg:#F4F6F9;
    --corp-surface:#FFFFFF;
    --corp-text:#172235;
    --corp-muted:#718096;
    --corp-border:#E0E6EE;
    --corp-border-soft:#E9EDF3;
    --corp-shadow:0 1px 2px rgba(15,23,42,.035), 0 5px 16px rgba(15,23,42,.025);
}

/* Fundo e largura da aplicação */
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
    background:var(--st-background-color, var(--background-color, var(--corp-bg))) !important;
}
[data-testid="stMainBlockContainer"],
main .block-container{
    max-width:1480px !important;
    padding-left:2.4rem !important;
    padding-right:2.4rem !important;
    padding-top:1.75rem !important;
}

/* Tipografia */
html,body,p,label,input,textarea,button,.stMarkdown,.stCaption{
    font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif !important;
}
main h1,main h2,main h3,main h4{
    letter-spacing:-.025em !important;
}

/* ==========================================================================
   SIDEBAR — MAIS SÓLIDA E CORPORATIVA
   ========================================================================== */
section[data-testid="stSidebar"]{
    width:224px !important;
    min-width:224px !important;
    background:var(--corp-navy) !important;
    border-right:1px solid #173152 !important;
}
[data-testid="stSidebarContent"]{
    padding:1.15rem 14px 1.1rem !important;
}
section[data-testid="stSidebar"] > div:first-child{
    padding-top:1rem !important;
}

/* Logo */
section[data-testid="stSidebar"] [data-testid="stImage"]{
    max-width:150px !important;
    margin:0 auto .5rem !important;
}
.aproar-sidebar-subtitle{
    color:#8093AE !important;
    font-size:8px !important;
    font-weight:750 !important;
    letter-spacing:1.65px !important;
    margin:4px 8px 17px !important;
}

/* Grupos */
.aproar-sidebar-section{
    color:#6682A5 !important;
    font-size:7.5px !important;
    font-weight:800 !important;
    letter-spacing:1.45px !important;
    margin:18px 10px 7px !important;
}

/* Navegação */
[data-testid="stSidebarContent"] [data-testid="stVerticalBlock"]{
    gap:.3rem !important;
}
section[data-testid="stSidebar"] .stButton{
    margin:0 !important;
}
section[data-testid="stSidebar"] .stButton > button{
    height:40px !important;
    min-height:40px !important;
    border-radius:7px !important;
    border:1px solid transparent !important;
    padding-left:44px !important;
    padding-right:12px !important;
    background:transparent !important;
    color:#CED8E5 !important;
    font-size:12.5px !important;
    font-weight:530 !important;
    box-shadow:none !important;
    transition:background .15s ease,border-color .15s ease,color .15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover{
    background:#122C4D !important;
    border-color:#1A385D !important;
    color:#FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] .stButton > button[kind="primary"]{
    background:var(--corp-blue) !important;
    border-color:var(--corp-blue) !important;
    color:#FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover,
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{
    background:var(--corp-blue-hover) !important;
    border-color:var(--corp-blue-hover) !important;
}

/* Ícones */
section[data-testid="stSidebar"] .stButton > button::before{
    left:14px !important;
    width:17px !important;
    height:17px !important;
    -webkit-mask-size:17px 17px !important;
    mask-size:17px 17px !important;
    opacity:.88 !important;
}

/* Rodapé de edição */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{
    color:#657A96 !important;
    font-size:9.5px !important;
}
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button{
    height:31px !important;
    min-height:31px !important;
    padding:0 8px !important;
    color:#91A2B8 !important;
    font-size:10.5px !important;
    border:1px solid #203A5B !important;
    background:#0E213B !important;
}
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button:hover{
    background:#142A47 !important;
    color:#DCE5F0 !important;
}

/* ==========================================================================
   CABEÇALHOS
   ========================================================================== */
.ap-home-head{
    margin:0 0 14px !important;
}
.ap-home-title{
    font-size:30px !important;
    font-weight:760 !important;
    color:var(--st-text-color,var(--text-color,var(--corp-text))) !important;
}
.ap-home-sub{
    font-size:12px !important;
    color:color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 55%,transparent) !important;
}
.ap-home-date{
    font-size:11px !important;
    color:color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 68%,transparent) !important;
}
.ap-home-date span{
    font-size:10px !important;
    color:color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 45%,transparent) !important;
}

.ap3-page-head{
    margin:0 0 15px !important;
    padding-bottom:12px !important;
    border-bottom:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 10%,transparent) !important;
}
.ap3-page-kicker{
    font-size:8px !important;
    letter-spacing:1.35px !important;
    color:var(--st-primary-color,var(--primary-color,var(--corp-blue))) !important;
}
.ap3-page-title{
    font-size:27px !important;
    font-weight:755 !important;
}
.ap3-page-sub{
    font-size:11.5px !important;
    max-width:720px !important;
}
.ap3-section{
    margin:17px 0 8px !important;
}
.ap3-section-title{
    font-size:13.5px !important;
}

/* ==========================================================================
   FILTROS / FORMULÁRIOS
   ========================================================================== */
div[class*="st-key-ap2_filters"] [data-testid="stVerticalBlockBorderWrapper"] > div{
    background:var(--st-secondary-background-color,var(--secondary-background-color,#FFFFFF)) !important;
    border:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 13%,transparent) !important;
    border-radius:8px !important;
    padding:9px 12px 8px !important;
    box-shadow:var(--corp-shadow) !important;
}
main label p{
    font-size:9.5px !important;
    font-weight:680 !important;
    color:color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 58%,transparent) !important;
}
main div[data-baseweb="select"] > div,
main div[data-baseweb="base-input"] > div,
main div[data-baseweb="input"] > div,
main [data-baseweb="textarea"] > div,
main div[role="combobox"]{
    min-height:38px !important;
    border-radius:6px !important;
    border:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 13%,transparent) !important;
    background:var(--st-secondary-background-color,var(--secondary-background-color,#FFFFFF)) !important;
    box-shadow:none !important;
}
main div[data-baseweb="select"] > div:focus-within,
main div[data-baseweb="base-input"] > div:focus-within,
main div[data-baseweb="input"] > div:focus-within{
    border-color:color-mix(in srgb,var(--st-primary-color,var(--primary-color,#245FD6)) 65%,transparent) !important;
    box-shadow:0 0 0 2px color-mix(in srgb,var(--st-primary-color,var(--primary-color,#245FD6)) 10%,transparent) !important;
}

/* ==========================================================================
   CARDS / MÉTRICAS
   ========================================================================== */
.ap-kpi-strip{
    border:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 12%,transparent) !important;
    border-radius:9px !important;
    box-shadow:var(--corp-shadow) !important;
}
.ap-kpi{
    min-height:88px !important;
    padding:14px 17px 13px !important;
}
.ap-kpi-label{
    font-size:8.5px !important;
    letter-spacing:.45px !important;
}
.ap-kpi-value{
    font-size:26px !important;
    font-weight:745 !important;
}
.ap-kpi-note{
    font-size:9.5px !important;
}
.ap-card{
    border:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 11%,transparent) !important;
    border-radius:9px !important;
    box-shadow:var(--corp-shadow) !important;
}
.ap-card-title{
    font-size:14px !important;
}
.ap-card-sub{
    font-size:10px !important;
}
.ap-task,.ap-conflict{
    border-radius:6px !important;
}
.ap-task strong,.ap-conflict-name{
    font-size:11.5px !important;
}

[data-testid="stMetric"]{
    border:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 11%,transparent) !important;
    border-radius:8px !important;
    padding:12px 14px !important;
    box-shadow:var(--corp-shadow) !important;
}
[data-testid="stMetricValue"]{
    font-size:23px !important;
    font-weight:735 !important;
}

/* Containers internos */
main [data-testid="stVerticalBlockBorderWrapper"] > div,
main [data-testid="stExpander"]{
    border-radius:8px !important;
    border-color:color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 11%,transparent) !important;
    box-shadow:none !important;
}

/* ==========================================================================
   TABS
   ========================================================================== */
[data-testid="stTabs"] [data-baseweb="tab-list"]{
    gap:25px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]{
    font-size:11px !important;
    font-weight:620 !important;
}

/* ==========================================================================
   TABELAS
   ========================================================================== */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"]{
    border:1px solid color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 13%,transparent) !important;
    border-radius:8px !important;
    box-shadow:var(--corp-shadow) !important;
}
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataEditor"] [role="columnheader"]{
    background:color-mix(in srgb,var(--st-text-color,var(--text-color,#172235)) 4%,var(--st-secondary-background-color,var(--secondary-background-color,#FFFFFF))) !important;
    font-size:9.5px !important;
    font-weight:720 !important;
}
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataEditor"] [role="gridcell"]{
    font-size:10.5px !important;
}

/* ==========================================================================
   BOTÕES
   ========================================================================== */
main .stButton > button,
main .stDownloadButton > button{
    min-height:37px !important;
    height:auto !important;
    border-radius:6px !important;
    font-size:10.8px !important;
    font-weight:620 !important;
    box-shadow:none !important;
    transition:background .15s ease,border-color .15s ease,transform .08s ease !important;
}
main .stButton > button:active,
main .stDownloadButton > button:active{
    transform:translateY(1px);
}
main [data-testid="stBaseButton-primary"],
main .stButton > button[kind="primary"],
main [data-testid="stFormSubmitButton"] > button{
    background:var(--st-primary-color,var(--primary-color,var(--corp-blue))) !important;
    border-color:var(--st-primary-color,var(--primary-color,var(--corp-blue))) !important;
    color:#FFFFFF !important;
}

/* Ações rápidas: linguagem uniforme e sem exagero */
.ap-quick-head{
    font-size:12px !important;
    margin:14px 0 7px !important;
}
div[class*="st-key-ap2_quick"] .stButton > button{
    border-radius:6px !important;
}

/* ==========================================================================
   ALERTAS
   ========================================================================== */
[data-testid="stAlert"]{
    border-radius:7px !important;
    font-size:10.5px !important;
    border-width:1px !important;
}

/* ==========================================================================
   RESPONSIVO
   ========================================================================== */
@media(max-width:1100px){
    [data-testid="stMainBlockContainer"],
    main .block-container{
        padding-left:1.25rem !important;
        padding-right:1.25rem !important;
    }
}
@media(max-width:760px){
    section[data-testid="stSidebar"]{
        width:212px !important;
        min-width:212px !important;
    }
    [data-testid="stMainBlockContainer"],
    main .block-container{
        padding-left:.9rem !important;
        padding-right:.9rem !important;
    }
}
</style>
""")




# --- APROAR V4.2 | TOPO DAS PÁGINAS + AÇÕES DE RELATÓRIO --------------------
st.html("""
<style>
/*
O cabeçalho fixo do Streamlit mede cerca de 46 px.
Na V4 o conteúdo estava com apenas 1.75rem de padding, então títulos de
Dashboard, Relatórios, Indicadores etc. entravam por baixo dele.
*/
[data-testid="stMainBlockContainer"],
main .block-container{
    padding-top:4.15rem !important;
}

/* Garante que nenhum cabeçalho interno seja recortado. */
.ap3-page-head,
.ap-home-head{
    overflow:visible !important;
}
.ap3-page-title,
.ap-home-title{
    line-height:1.16 !important;
    padding-top:2px !important;
}

/* Relatórios: ações menos pesadas que dois blocos azuis gigantes. */
div[class*="st-key-rel_gerar_pdf_v42"] button,
div[class*="st-key-rel_gerar_excel_v42"] button{
    min-height:40px !important;
    background:var(
        --st-secondary-background-color,
        var(--secondary-background-color,#FFFFFF)
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color,#24364D)
    ) !important;
    border:1px solid color-mix(
        in srgb,
        var(--st-text-color,var(--text-color,#24364D)) 16%,
        transparent
    ) !important;
    border-radius:7px !important;
    box-shadow:none !important;
    font-size:11px !important;
    font-weight:620 !important;
}
div[class*="st-key-rel_gerar_pdf_v42"] button *,
div[class*="st-key-rel_gerar_excel_v42"] button *{
    color:inherit !important;
}
div[class*="st-key-rel_gerar_pdf_v42"] button:hover,
div[class*="st-key-rel_gerar_excel_v42"] button:hover{
    background:color-mix(
        in srgb,
        var(--st-text-color,var(--text-color,#24364D)) 5%,
        var(--st-secondary-background-color,var(--secondary-background-color,#FFFFFF))
    ) !important;
    border-color:color-mix(
        in srgb,
        var(--st-primary-color,var(--primary-color,#245FD6)) 42%,
        transparent
    ) !important;
}

/* Em telas menores também preserva o espaço do cabeçalho. */
@media(max-width:900px){
    [data-testid="stMainBlockContainer"],
    main .block-container{
        padding-top:3.9rem !important;
    }
}
</style>
""")




# --- APROAR V4.3 | BOTÕES + AÇÕES DE LIMPEZA -------------------------------
st.html("""
<style>
/* Item ativo da sidebar: azul mais sóbrio e borda discreta. */
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] .stButton > button[kind="primary"]{
    background:#235ED5 !important;
    border:1px solid #3470E6 !important;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.08) !important;
    border-radius:8px !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover,
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{
    background:#1E54C3 !important;
    border-color:#2F68D9 !important;
}

/* Bloquear edição vira uma ação de sistema mais discreta. */
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button{
    height:35px !important;
    min-height:35px !important;
    background:transparent !important;
    border:1px solid #294563 !important;
    color:#B9C7D8 !important;
    border-radius:7px !important;
    font-size:10.5px !important;
}
section[data-testid="stSidebar"] div[class*="st-key-bloquear_edicao_sidebar_ui4"] button:hover{
    background:#122944 !important;
    color:#FFFFFF !important;
}

/* Botão de limpeza por data = secundário. */
div[class*="st-key-btn_limpar_data_v43"] button{
    background:var(
        --st-secondary-background-color,
        var(--secondary-background-color,#FFFFFF)
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color,#29384D)
    ) !important;
    border:1px solid color-mix(
        in srgb,
        var(--st-text-color,var(--text-color,#29384D)) 17%,
        transparent
    ) !important;
}
div[class*="st-key-btn_limpar_data_v43"] button *{
    color:inherit !important;
}

/* Ação destrutiva só fica vermelha quando está realmente habilitada. */
div[class*="st-key-btn_limpar_todos_testes_v43"] button:not(:disabled){
    background:#C93D4F !important;
    border-color:#C93D4F !important;
    color:#FFFFFF !important;
    font-weight:680 !important;
}
div[class*="st-key-btn_limpar_todos_testes_v43"] button:not(:disabled) *{
    color:#FFFFFF !important;
}
div[class*="st-key-btn_limpar_todos_testes_v43"] button:not(:disabled):hover{
    background:#B83243 !important;
    border-color:#B83243 !important;
}
div[class*="st-key-btn_limpar_todos_testes_v43"] button:disabled{
    opacity:.46 !important;
    cursor:not-allowed !important;
}

/* Botões secundários da área principal acompanham Light / Dark / System. */
main .stButton > button[kind="secondary"]{
    background:var(
        --st-secondary-background-color,
        var(--secondary-background-color,#FFFFFF)
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color,#29384D)
    ) !important;
    border-color:color-mix(
        in srgb,
        var(--st-text-color,var(--text-color,#29384D)) 15%,
        transparent
    ) !important;
}
main .stButton > button[kind="secondary"] *{
    color:inherit !important;
}
main .stButton > button[kind="secondary"]:hover{
    border-color:color-mix(
        in srgb,
        var(--st-primary-color,var(--primary-color,#245FD6)) 40%,
        transparent
    ) !important;
}
</style>
""")




# --- APROAR PRODUÇÃO | AJUSTE DE AÇÃO DE LIMPEZA ----------------------------
st.html("""
<style>
div[class*="st-key-btn_limpar_data_prod_v1"] button{
    background:var(
        --st-secondary-background-color,
        var(--secondary-background-color,#FFFFFF)
    ) !important;
    color:var(
        --st-text-color,
        var(--text-color,#29384D)
    ) !important;
    border:1px solid color-mix(
        in srgb,
        var(--st-text-color,var(--text-color,#29384D)) 17%,
        transparent
    ) !important;
}
div[class*="st-key-btn_limpar_data_prod_v1"] button *{
    color:inherit !important;
}
div[class*="st-key-btn_limpar_data_prod_v1"] button:hover{
    border-color:#C93D4F !important;
    color:#B83243 !important;
}
</style>
""")



# --- APROAR V6.8 | LIMPEZA TOTAL ADMIN --------------------------------------
st.html("""
<style>
div[class*="st-key-btn_limpar_todos_dados_admin_v68"] button:not(:disabled){
    background:#C93D4F !important;
    border-color:#C93D4F !important;
    color:#FFFFFF !important;
    font-weight:700 !important;
}
div[class*="st-key-btn_limpar_todos_dados_admin_v68"] button:not(:disabled):hover{
    background:#B83243 !important;
    border-color:#B83243 !important;
}
div[class*="st-key-btn_limpar_todos_dados_admin_v68"] button:disabled{
    opacity:.45 !important;
}
</style>
""")


# --- MESES EM PORTUGUÊS ---
MESES_PT = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}

# --- BANCO DE DADOS: NEON (PREFERENCIAL) OU SUPABASE (FALLBACK) ---
#
# Se DATABASE_URL existir nos Secrets, o sistema usa PostgreSQL/Neon.
# Caso contrário, mantém compatibilidade com o Supabase antigo.
#
# O adaptador abaixo imita a pequena parte da API supabase.table(...)
# que este sistema utiliza. Assim o restante do app não precisa ser reescrito.

class _DBResponse:
    def __init__(self, data=None):
        self.data = data if data is not None else []


def _identificador_sql(nome):
    """Valida e protege nomes de tabela/coluna usados internamente pelo app."""
    nome = str(nome or "").strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        raise ValueError(f"Identificador SQL inválido: {nome}")
    return f'"{nome}"'


class _PostgresQuery:
    def __init__(self, db, tabela):
        self.db = db
        self.tabela = tabela
        self.operacao = None
        self.colunas = "*"
        self.payload = None
        self.filtros = []
        self.limite = None

    def select(self, colunas="*"):
        self.operacao = "select"
        self.colunas = colunas or "*"
        return self

    def insert(self, payload):
        self.operacao = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operacao = "update"
        self.payload = payload
        return self

    def delete(self):
        self.operacao = "delete"
        return self

    def eq(self, coluna, valor):
        self.filtros.append(("eq", coluna, valor))
        return self

    def gte(self, coluna, valor):
        self.filtros.append(("gte", coluna, valor))
        return self

    def lte(self, coluna, valor):
        self.filtros.append(("lte", coluna, valor))
        return self

    def in_(self, coluna, valores):
        self.filtros.append(("in", coluna, list(valores or [])))
        return self

    def limit(self, quantidade):
        self.limite = int(quantidade)
        return self

    def _where(self):
        partes = []
        params = []

        for operador, coluna, valor in self.filtros:
            col = _identificador_sql(coluna)

            if operador == "eq":
                if valor is None:
                    partes.append(f"{col} IS NULL")
                else:
                    partes.append(f"{col} = %s")
                    params.append(valor)

            elif operador == "gte":
                partes.append(f"{col} >= %s")
                params.append(valor)

            elif operador == "lte":
                partes.append(f"{col} <= %s")
                params.append(valor)

            elif operador == "in":
                valores = list(valor or [])
                if not valores:
                    partes.append("FALSE")
                else:
                    placeholders = ", ".join(["%s"] * len(valores))
                    partes.append(f"{col} IN ({placeholders})")
                    params.extend(valores)

        sql = (" WHERE " + " AND ".join(partes)) if partes else ""
        return sql, params

    def _colunas_select(self):
        if str(self.colunas).strip() == "*":
            return "*"
        nomes = [c.strip() for c in str(self.colunas).split(",") if c.strip()]
        return ", ".join(_identificador_sql(c) for c in nomes)

    def execute(self):
        tabela = _identificador_sql(self.tabela)
        where_sql, where_params = self._where()

        with self.db._connect() as conn:
            with conn.cursor() as cur:
                if self.operacao == "select":
                    sql = f"SELECT {self._colunas_select()} FROM {tabela}{where_sql}"
                    params = list(where_params)
                    if self.limite is not None:
                        sql += " LIMIT %s"
                        params.append(self.limite)

                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    return _DBResponse([dict(r) for r in rows])

                if self.operacao == "insert":
                    registros = self.payload if isinstance(self.payload, list) else [self.payload]
                    registros = [r for r in registros if isinstance(r, dict) and r]
                    if not registros:
                        return _DBResponse([])

                    resultado = []
                    for registro in registros:
                        colunas = list(registro.keys())
                        cols_sql = ", ".join(_identificador_sql(c) for c in colunas)
                        placeholders = ", ".join(["%s"] * len(colunas))
                        valores = [registro[c] for c in colunas]

                        cur.execute(
                            f"INSERT INTO {tabela} ({cols_sql}) "
                            f"VALUES ({placeholders}) RETURNING *",
                            valores,
                        )
                        row = cur.fetchone()
                        if row:
                            resultado.append(dict(row))

                    conn.commit()
                    return _DBResponse(resultado)

                if self.operacao == "update":
                    payload = dict(self.payload or {})
                    if not payload:
                        return _DBResponse([])

                    sets = []
                    params = []
                    for coluna, valor in payload.items():
                        sets.append(f"{_identificador_sql(coluna)} = %s")
                        params.append(valor)

                    sql = (
                        f"UPDATE {tabela} SET {', '.join(sets)}"
                        f"{where_sql} RETURNING *"
                    )
                    params.extend(where_params)
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    conn.commit()
                    return _DBResponse([dict(r) for r in rows])

                if self.operacao == "delete":
                    sql = f"DELETE FROM {tabela}{where_sql} RETURNING *"
                    cur.execute(sql, where_params)
                    rows = cur.fetchall()
                    conn.commit()
                    return _DBResponse([dict(r) for r in rows])

                raise RuntimeError("Nenhuma operação de banco foi definida.")


class _PostgresCompat:
    def __init__(self, database_url):
        self.database_url = str(database_url).strip()

    def _connect(self):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise RuntimeError(
                "O pacote psycopg não está instalado. "
                "Adicione psycopg[binary]>=3.2 ao requirements.txt."
            )

        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=12,
        )

    def table(self, tabela):
        tabelas_autorizadas = {
            "obras", "colaboradores", "convocacoes",
            "indisponibilidades", "conflitos_convocacao", "apontamentos",
            "servicos_apontamento", "auditoria", "erros_sistema",
        }
        if tabela not in tabelas_autorizadas:
            raise ValueError(f"Tabela não autorizada no adaptador: {tabela}")
        return _PostgresQuery(self, tabela)


def _secret_opcional(nome):
    try:
        valor = st.secrets.get(nome, "")
        return str(valor).strip() if valor else ""
    except Exception:
        return ""


DATABASE_URL = _secret_opcional("DATABASE_URL")
TEAMS_COBRANCA_WEBHOOK_URL = _secret_opcional(
    "TEAMS_COBRANCA_WEBHOOK_URL"
)
DB_BACKEND = "NEON" if DATABASE_URL else "SUPABASE"


@st.cache_resource
def init_connection():
    if DATABASE_URL:
        return _PostgresCompat(DATABASE_URL)

    url = _secret_opcional("SUPABASE_URL")
    key = _secret_opcional("SUPABASE_KEY") or _secret_opcional("SUPABASE_ANON_KEY")
    if not url or not key:
        try:
            bloco_supabase = st.secrets.get("supabase", {})
            url = url or str(bloco_supabase.get("url", "") or bloco_supabase.get("SUPABASE_URL", "")).strip()
            key = key or str(bloco_supabase.get("key", "") or bloco_supabase.get("anon_key", "") or bloco_supabase.get("SUPABASE_KEY", "")).strip()
        except Exception:
            pass
    if not url or not key:
        raise RuntimeError("Configure DATABASE_URL (Neon) ou SUPABASE_URL + SUPABASE_KEY/SUPABASE_ANON_KEY nos Secrets.")
    return create_client(url, key)


try:
    # Mantemos o nome "supabase" por compatibilidade com o restante do app.
    # Quando DATABASE_URL existe, este objeto na verdade aponta para o Neon/PostgreSQL.
    supabase = init_connection()
except Exception as e:
    st.error(f"Erro ao iniciar o banco de dados: {e}")
    st.stop()


# Valor disponível também durante as migrações iniciais do banco.
# A mesma constante é reafirmada mais abaixo junto às demais regras do SEBRAE.
VALOR_ADICIONAL_NOTURNO_SEBRAE = 90.00


@st.cache_resource
def _garantir_estrutura_cadastros_admin():
    """
    Pequena migração compatível com a base atual.

    - local_moradia passa a fazer parte do cadastro do colaborador;
    - ativo é garantido para permitir exclusão lógica sem destruir histórico;
    - obras deixam de ser únicas apenas pelo nome e passam a ser únicas por
      nome + unidade;
    - sequences são corrigidas caso uma importação antiga tenha avançado IDs
      manualmente e deixado o serial para trás.
    """
    if DB_BACKEND != "NEON" or not hasattr(supabase, "_connect"):
        return False

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    ALTER TABLE colaboradores
                    ADD COLUMN IF NOT EXISTS local_moradia TEXT
                    """
                )

                cur.execute(
                    """
                    ALTER TABLE colaboradores
                    ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE
                    """
                )

                cur.execute(
                    """
                    ALTER TABLE colaboradores
                    ADD COLUMN IF NOT EXISTS categoria_diaria TEXT
                    """
                )

                cur.execute(
                    """
                    UPDATE colaboradores
                       SET categoria_diaria =
                           CASE
                               WHEN UPPER(COALESCE(funcao, '')) LIKE ANY(
                                   ARRAY[
                                       '%AJUDANTE%',
                                       '%AUXILIAR%',
                                       '%SERVENTE%'
                                   ]
                               )
                                   THEN 'Ajudante'
                               WHEN COALESCE(valor_diaria, 0) > 0
                                AND COALESCE(valor_diaria, 0) < 220
                                   THEN 'Ajudante'
                               ELSE 'Profissional'
                           END
                     WHERE categoria_diaria IS NULL
                        OR TRIM(COALESCE(categoria_diaria, '')) = ''
                    """
                )

                # Campos financeiros do apontamento. Mantemos também em
                # convocacoes porque os relatórios operacionais já usam esta
                # tabela como leitura rápida/compatível.
                for _tabela_fin in ("convocacoes", "apontamentos"):
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS tipo_diaria TEXT
                        """
                    )
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS custo_pago NUMERIC(12,2)
                        """
                    )
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS valor_acordo NUMERIC(12,2) NOT NULL DEFAULT 0
                        """
                    )
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS valor_adicional_noturno NUMERIC(12,2) NOT NULL DEFAULT 0
                        """
                    )
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS custo_encargos_base NUMERIC(12,2)
                        """
                    )
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS custos_separados BOOLEAN NOT NULL DEFAULT FALSE
                        """
                    )
                    cur.execute(
                        f"""
                        ALTER TABLE IF EXISTS {_tabela_fin}
                        ADD COLUMN IF NOT EXISTS migracao_sebrae_noturno_v2 BOOLEAN NOT NULL DEFAULT FALSE
                        """
                    )

                # ------------------------------------------------------------
                # MIGRAÇÃO AUTOMÁTICA DOS APONTAMENTOS ANTIGOS
                # ------------------------------------------------------------
                # Os relatórios atuais leem "convocacoes" como fonte rápida.
                # Por isso migramos convocacoes E apontamentos.
                #
                # O antigo "valor_extra" continua sendo tratado como EXTRA.
                # Para o Financeiro acrescentamos a base líquida (120/60).
                # Para a Controladoria congelamos o custo cadastrado do
                # colaborador no momento desta migração.
                #
                # A migração é idempotente: só atua onde os campos novos
                # ainda estão NULL. Recarregar o app não duplica valores.
                _status_meia_sql = (
                    "'Presente (Só Manhã)', "
                    "'Presente (Só Tarde)', "
                    "'Saída Antecipada'"
                )

                _status_presenca_sql = (
                    "'Presente (Integral)', "
                    "'Presente (Só Manhã)', "
                    "'Presente (Só Tarde)', "
                    "'Saída Antecipada', "
                    "'Presente', "
                    "'Extra'"
                )

                # 1) CONVOCACOES — é a fonte usada pelos relatórios atuais.
                cur.execute(
                    f"""
                    UPDATE convocacoes AS v
                       SET tipo_diaria =
                               COALESCE(
                                   NULLIF(v.tipo_diaria, ''),
                                   CASE
                                       WHEN v.status IN ({_status_meia_sql})
                                           THEN 'Meia diária'
                                       ELSE 'Diária'
                                   END
                               ),

                           custo_pago =
                               CASE
                                   WHEN v.status IN ({_status_presenca_sql})
                                       THEN
                                           (
                                               CASE
                                                   WHEN v.status IN ({_status_meia_sql})
                                                       THEN 60.00
                                                   ELSE 120.00
                                               END
                                           )
                                           + GREATEST(
                                               COALESCE(v.valor_extra, 0),
                                               0
                                           )
                                   ELSE 0
                               END,

                           valor_acordo =
                               COALESCE(
                                   v.valor_acordo,
                                   0
                               ),

                           custo_encargos_base =
                               CASE
                                   WHEN v.status IN ({_status_presenca_sql})
                                       THEN
                                           ROUND(
                                               (
                                                   COALESCE(
                                                       NULLIF(c.valor_diaria, 0),
                                                       CASE
                                                           WHEN UPPER(
                                                               COALESCE(c.funcao, '')
                                                           ) LIKE ANY(
                                                               ARRAY[
                                                                   '%AJUDANTE%',
                                                                   '%AUXILIAR%',
                                                                   '%SERVENTE%'
                                                               ]
                                                           )
                                                               THEN 182.34
                                                           ELSE 241.74
                                                       END
                                                   )
                                                   *
                                                   CASE
                                                       WHEN v.status IN ({_status_meia_sql})
                                                           THEN 0.5
                                                       ELSE 1.0
                                                   END
                                               )::numeric,
                                               2
                                           )
                                   ELSE 0
                               END
                      FROM colaboradores AS c
                     WHERE c.id = v.colaborador_id
                       AND (
                           v.custo_pago IS NULL
                           OR v.custo_encargos_base IS NULL
                           OR v.tipo_diaria IS NULL
                           OR TRIM(COALESCE(v.tipo_diaria, '')) = ''
                       )
                    """
                )

                # 2) APONTAMENTOS — preserva a mesma regra na tabela estruturada.
                cur.execute(
                    f"""
                    UPDATE apontamentos AS a
                       SET tipo_diaria =
                               COALESCE(
                                   NULLIF(a.tipo_diaria, ''),
                                   CASE
                                       WHEN a.status IN ({_status_meia_sql})
                                           THEN 'Meia diária'
                                       ELSE 'Diária'
                                   END
                               ),

                           custo_pago =
                               CASE
                                   WHEN a.status IN ({_status_presenca_sql})
                                       THEN
                                           (
                                               CASE
                                                   WHEN a.status IN ({_status_meia_sql})
                                                       THEN 60.00
                                                   ELSE 120.00
                                               END
                                           )
                                           + GREATEST(
                                               COALESCE(a.valor_extra, 0),
                                               0
                                           )
                                   ELSE 0
                               END,

                           valor_acordo =
                               COALESCE(
                                   a.valor_acordo,
                                   0
                               ),

                           custo_encargos_base =
                               CASE
                                   WHEN a.status IN ({_status_presenca_sql})
                                       THEN
                                           ROUND(
                                               (
                                                   COALESCE(
                                                       NULLIF(c.valor_diaria, 0),
                                                       CASE
                                                           WHEN UPPER(
                                                               COALESCE(c.funcao, '')
                                                           ) LIKE ANY(
                                                               ARRAY[
                                                                   '%AJUDANTE%',
                                                                   '%AUXILIAR%',
                                                                   '%SERVENTE%'
                                                               ]
                                                           )
                                                               THEN 182.34
                                                           ELSE 241.74
                                                       END
                                                   )
                                                   *
                                                   CASE
                                                       WHEN a.status IN ({_status_meia_sql})
                                                           THEN 0.5
                                                       ELSE 1.0
                                                   END
                                               )::numeric,
                                               2
                                           )
                                   ELSE 0
                               END
                      FROM colaboradores AS c
                     WHERE c.id = a.colaborador_id
                       AND (
                           a.custo_pago IS NULL
                           OR a.custo_encargos_base IS NULL
                           OR a.tipo_diaria IS NULL
                           OR TRIM(COALESCE(a.tipo_diaria, '')) = ''
                       )
                    """
                )

                # ------------------------------------------------------------
                # MIGRAÇÃO ESPECIAL SEBRAE — adicional noturno legado
                # ------------------------------------------------------------
                # O SEBRAE trabalha no período 17h–02h e essa jornada continua
                # sendo uma diária integral.
                #
                # Antes da criação do campo próprio, o adicional noturno de
                # R$ 90,00 era lançado junto com "Extra". Por isso:
                #
                #   Extra  90,00 -> Extra   0,00 + Noturno 90,00
                #   Extra 137,56 -> Extra  47,56 + Noturno 90,00
                #   Extra 185,12 -> Extra  95,12 + Noturno 90,00
                #   Extra   0,00 -> Extra   0,00 + Noturno 90,00
                #
                # A condição valor_adicional_noturno = 0 deixa a migração
                # idempotente: ela não duplica os R$ 90 ao reiniciar o app.
                cur.execute(
                    f"""
                    UPDATE convocacoes AS v
                       SET valor_adicional_noturno =
                               {VALOR_ADICIONAL_NOTURNO_SEBRAE},

                           valor_extra =
                               CASE
                                   WHEN COALESCE(v.valor_extra, 0)
                                        >= {VALOR_ADICIONAL_NOTURNO_SEBRAE}
                                       THEN GREATEST(
                                           0,
                                           COALESCE(v.valor_extra, 0)
                                           - {VALOR_ADICIONAL_NOTURNO_SEBRAE}
                                       )
                                   ELSE COALESCE(v.valor_extra, 0)
                               END,

                           custo_pago =
                               CASE
                                   WHEN COALESCE(v.valor_extra, 0)
                                        >= {VALOR_ADICIONAL_NOTURNO_SEBRAE}
                                       THEN GREATEST(
                                           CASE
                                               WHEN COALESCE(
                                                   NULLIF(v.tipo_diaria, ''),
                                                   'Diária'
                                               ) = 'Meia diária'
                                                   THEN 60.00
                                               ELSE 120.00
                                           END,
                                           COALESCE(v.custo_pago, 0)
                                           - {VALOR_ADICIONAL_NOTURNO_SEBRAE}
                                       )
                                   ELSE COALESCE(
                                       v.custo_pago,
                                       120.00
                                   )
                               END,

                           tipo_diaria = 'Diária',

                           custo_encargos_base =
                               COALESCE(
                                   NULLIF(c.valor_diaria, 0),
                                   CASE
                                       WHEN UPPER(
                                           COALESCE(c.funcao, '')
                                       ) LIKE ANY(
                                           ARRAY[
                                               '%AJUDANTE%',
                                               '%AUXILIAR%',
                                               '%SERVENTE%'
                                           ]
                                       )
                                           THEN 182.34
                                       ELSE 241.74
                                   END
                               )

                      FROM obras AS o,
                           colaboradores AS c

                     WHERE o.id = v.obra_id
                       AND c.id = v.colaborador_id
                       AND UPPER(
                           TRIM(
                               COALESCE(o.unidade, '')
                           )
                       ) = 'SEBRAE'
                       AND COALESCE(
                           v.valor_adicional_noturno,
                           0
                       ) = 0
                       AND v.status IN (
                           'Presente (Integral)',
                           'Presente (Só Manhã)',
                           'Presente (Só Tarde)',
                           'Saída Antecipada',
                           'Presente',
                           'Extra'
                       )
                    """
                )

                # Espelha a reclassificação na tabela estruturada.
                cur.execute(
                    """
                    UPDATE apontamentos AS a
                       SET valor_adicional_noturno =
                               COALESCE(
                                   v.valor_adicional_noturno,
                                   0
                               ),
                           valor_extra =
                               COALESCE(
                                   v.valor_extra,
                                   0
                               ),
                           custo_pago =
                               COALESCE(
                                   v.custo_pago,
                                   0
                               ),
                           tipo_diaria =
                               COALESCE(
                                   v.tipo_diaria,
                                   'Diária'
                               ),
                           custo_encargos_base =
                               COALESCE(
                                   v.custo_encargos_base,
                                   0
                               )
                      FROM convocacoes AS v
                     WHERE CAST(
                               a.convocacao_id AS TEXT
                           ) = CAST(
                               v.id AS TEXT
                           )
                       AND COALESCE(
                           v.valor_adicional_noturno,
                           0
                       ) > 0
                       AND (
                           COALESCE(
                               a.valor_adicional_noturno,
                               0
                           ) = 0
                           OR ABS(
                               COALESCE(
                                   a.valor_extra,
                                   0
                               )
                               - COALESCE(
                                   v.valor_extra,
                                   0
                               )
                           ) > 0.005
                       )
                    """
                )

                # ------------------------------------------------------------
                # MIGRAÇÃO V2 — DIÁRIA E EXTRA EM CAMPOS SEPARADOS
                # ------------------------------------------------------------
                # A versão antiga gravava "custo_pago" como DIÁRIA + EXTRA.
                # Agora:
                #   custo_pago = diária efetivamente paga;
                #   valor_extra = extra real;
                #   valor_acordo = acordos/bonificações;
                #   valor_adicional_noturno = adicional noturno.
                #
                # Padrões reconhecidos das planilhas antigas:
                # Profissional: R$ 120 padrão, com diárias negociadas como 150/200.
                # Ajudante: R$ 80 padrão, com diárias negociadas como 100/120.
                # Meia diária = metade do valor cheio.
                cur.execute(
                    """
                    SELECT
                        v.id,
                        v.status,
                        v.tipo_diaria,
                        v.custo_pago,
                        v.valor_extra,
                        v.valor_adicional_noturno,
                        v.observacao,
                        v.colaborador_id,
                        o.unidade,
                        c.funcao,
                        c.categoria_diaria,
                        c.valor_diaria
                    FROM convocacoes v
                    LEFT JOIN obras o
                      ON o.id = v.obra_id
                    LEFT JOIN colaboradores c
                      ON c.id = v.colaborador_id
                    WHERE COALESCE(v.custos_separados, FALSE) = FALSE
                    """
                )

                _linhas_custo_legado = cur.fetchall() or []

                _status_presenca_v2 = {
                    "Presente (Integral)",
                    "Presente (Só Manhã)",
                    "Presente (Só Tarde)",
                    "Saída Antecipada",
                    "Presente",
                    "Extra",
                }

                _status_meia_v2 = {
                    "Presente (Só Manhã)",
                    "Presente (Só Tarde)",
                    "Saída Antecipada",
                }

                def _row_get_v2(row, chave, idx):
                    if isinstance(row, dict):
                        return row.get(chave)
                    try:
                        return row[idx]
                    except Exception:
                        return None

                def _float_v2(valor, padrao=0.0):
                    try:
                        return float(valor or 0.0)
                    except Exception:
                        return float(padrao)

                for _row_v2 in _linhas_custo_legado:
                    _id_v2 = _row_get_v2(_row_v2, "id", 0)
                    _status_v2 = str(
                        _row_get_v2(_row_v2, "status", 1)
                        or ""
                    ).strip()
                    _tipo_v2 = str(
                        _row_get_v2(_row_v2, "tipo_diaria", 2)
                        or ""
                    ).strip()
                    _custo_antigo_v2 = _float_v2(
                        _row_get_v2(_row_v2, "custo_pago", 3)
                    )
                    _extra_antigo_v2 = _float_v2(
                        _row_get_v2(_row_v2, "valor_extra", 4)
                    )
                    _noturno_v2 = _float_v2(
                        _row_get_v2(
                            _row_v2,
                            "valor_adicional_noturno",
                            5,
                        )
                    )
                    _obs_v2 = str(
                        _row_get_v2(_row_v2, "observacao", 6)
                        or ""
                    )
                    _unidade_v2 = str(
                        _row_get_v2(_row_v2, "unidade", 8)
                        or ""
                    ).strip()
                    _funcao_v2 = str(
                        _row_get_v2(_row_v2, "funcao", 9)
                        or ""
                    )
                    _categoria_v2 = str(
                        _row_get_v2(
                            _row_v2,
                            "categoria_diaria",
                            10,
                        )
                        or ""
                    ).upper()
                    _valor_planilha_v2 = _float_v2(
                        _row_get_v2(
                            _row_v2,
                            "valor_diaria",
                            11,
                        )
                    )

                    _presente_v2 = (
                        _status_v2
                        in _status_presenca_v2
                    )

                    if (
                        "AJUD" in _categoria_v2
                        or "SERVENT" in _categoria_v2
                        or "AUX" in _categoria_v2
                    ):
                        _eh_ajudante_v2 = True
                    elif any(
                        termo in _funcao_v2.upper()
                        for termo in (
                            "AJUDANTE",
                            "AUXILIAR",
                            "SERVENTE",
                        )
                    ):
                        _eh_ajudante_v2 = True
                    elif (
                        _valor_planilha_v2 > 0
                        and _valor_planilha_v2 < 220
                    ):
                        _eh_ajudante_v2 = True
                    else:
                        _eh_ajudante_v2 = False

                    _meia_v2 = (
                        "MEIA" in _tipo_v2.upper()
                        or _status_v2
                        in _status_meia_v2
                    )

                    # SEBRAE 17h–02h é sempre diária integral.
                    if _unidade_v2.upper() == "SEBRAE":
                        _meia_v2 = False

                        if (
                            _presente_v2
                            and _noturno_v2 <= 0.005
                        ):
                            # Caso ainda exista uma versão antiga com os R$ 90
                            # misturados no custo/extra, separa antes da leitura.
                            if (
                                _extra_antigo_v2 >= 89.995
                                and _custo_antigo_v2 >= 90.0
                            ):
                                _extra_antigo_v2 = max(
                                    0.0,
                                    _extra_antigo_v2 - 90.0,
                                )
                                _custo_antigo_v2 = max(
                                    0.0,
                                    _custo_antigo_v2 - 90.0,
                                )

                            _noturno_v2 = 90.0

                    _base_cheia_fin_v2 = (
                        80.0
                        if _eh_ajudante_v2
                        else 120.0
                    )
                    _base_fin_v2 = (
                        _base_cheia_fin_v2 / 2.0
                        if _meia_v2
                        else _base_cheia_fin_v2
                    )

                    _base_cheia_ctrl_v2 = (
                        182.34
                        if _eh_ajudante_v2
                        else 241.74
                    )
                    _base_ctrl_v2 = (
                        _base_cheia_ctrl_v2 / 2.0
                        if _meia_v2
                        else _base_cheia_ctrl_v2
                    )

                    if not _presente_v2:
                        _diaria_nova_v2 = 0.0
                        _extra_novo_v2 = 0.0

                    else:
                        _total_antigo_v2 = (
                            _custo_antigo_v2
                            if _custo_antigo_v2 > 0
                            else (
                                _base_fin_v2
                                + max(
                                    0.0,
                                    _extra_antigo_v2,
                                )
                            )
                        )

                        _obs_norm_v2 = (
                            unicodedata.normalize(
                                "NFKD",
                                _obs_v2,
                            )
                            .encode(
                                "ASCII",
                                "ignore",
                            )
                            .decode(
                                "utf-8"
                            )
                            .upper()
                        )

                        # "acrescido 30 para fechar a diária de R$150,00"
                        _alvo_diaria_v2 = None
                        _match_diaria_v2 = re.search(
                            r"(?:FECHAR|COMPLETAR).*?DIARIA.*?R\\$?\\s*([0-9]+(?:[\\.,][0-9]+)?)",
                            _obs_norm_v2,
                        )

                        if _match_diaria_v2:
                            try:
                                _numero_v2 = (
                                    _match_diaria_v2
                                    .group(1)
                                )

                                if (
                                    "," in _numero_v2
                                    and "." in _numero_v2
                                ):
                                    _numero_v2 = (
                                        _numero_v2
                                        .replace(".", "")
                                        .replace(",", ".")
                                    )
                                else:
                                    _numero_v2 = (
                                        _numero_v2
                                        .replace(",", ".")
                                    )

                                _alvo_diaria_v2 = float(
                                    _numero_v2
                                )

                                if _meia_v2:
                                    _alvo_diaria_v2 /= 2.0

                            except Exception:
                                _alvo_diaria_v2 = None

                        _tem_indicio_extra_v2 = any(
                            termo in _obs_norm_v2
                            for termo in (
                                "PRODUCAO",
                                "HORA EXTRA",
                                "HORAS EXTRA",
                                "SERVICO EXTRA",
                                "EXTRA ",
                            )
                        )

                        if (
                            _alvo_diaria_v2 is not None
                            and _alvo_diaria_v2 > 0
                        ):
                            _diaria_nova_v2 = min(
                                _total_antigo_v2,
                                _alvo_diaria_v2,
                            )
                            _extra_novo_v2 = max(
                                0.0,
                                _total_antigo_v2
                                - _diaria_nova_v2,
                            )

                        elif _tem_indicio_extra_v2:
                            _diaria_nova_v2 = _base_fin_v2
                            _extra_novo_v2 = max(
                                0.0,
                                _total_antigo_v2
                                - _diaria_nova_v2,
                            )

                        else:
                            if _eh_ajudante_v2:
                                _candidatos_cheios_v2 = [
                                    80.0,
                                    100.0,
                                    120.0,
                                ]
                            else:
                                _candidatos_cheios_v2 = [
                                    120.0,
                                    150.0,
                                    200.0,
                                ]

                            _candidatos_v2 = [
                                (
                                    valor / 2.0
                                    if _meia_v2
                                    else valor
                                )
                                for valor
                                in _candidatos_cheios_v2
                            ]

                            _candidato_exato_v2 = next(
                                (
                                    valor
                                    for valor
                                    in _candidatos_v2
                                    if abs(
                                        _total_antigo_v2
                                        - valor
                                    ) <= 0.005
                                ),
                                None,
                            )

                            if (
                                _candidato_exato_v2
                                is not None
                            ):
                                _diaria_nova_v2 = (
                                    _candidato_exato_v2
                                )
                                _extra_novo_v2 = 0.0

                            elif (
                                not _meia_v2
                                and _total_antigo_v2
                                >= _base_fin_v2
                                and abs(
                                    _total_antigo_v2 / 10.0
                                    - round(
                                        _total_antigo_v2 / 10.0
                                    )
                                ) <= 0.0005
                            ):
                                # Ex.: 150 no antigo Custo + Extra passa
                                # a significar Diária = 150.
                                _diaria_nova_v2 = (
                                    _total_antigo_v2
                                )
                                _extra_novo_v2 = 0.0

                            else:
                                _diaria_nova_v2 = (
                                    _base_fin_v2
                                )
                                _extra_novo_v2 = max(
                                    0.0,
                                    _total_antigo_v2
                                    - _diaria_nova_v2,
                                )

                    cur.execute(
                        """
                        UPDATE convocacoes
                           SET custo_pago = %s,
                               valor_extra = %s,
                               valor_adicional_noturno = %s,
                               custo_encargos_base = %s,
                               custos_separados = TRUE
                         WHERE id = %s
                        """,
                        (
                            round(
                                _diaria_nova_v2,
                                2,
                            ),
                            round(
                                _extra_novo_v2,
                                2,
                            ),
                            round(
                                _noturno_v2,
                                2,
                            ),
                            round(
                                (
                                    _base_ctrl_v2
                                    if _presente_v2
                                    else 0.0
                                ),
                                2,
                            ),
                            _id_v2,
                        ),
                    )

                # Espelha a nova leitura na tabela estruturada.
                cur.execute(
                    """
                    UPDATE apontamentos AS a
                       SET tipo_diaria = v.tipo_diaria,
                           custo_pago = v.custo_pago,
                           valor_extra = v.valor_extra,
                           valor_acordo = v.valor_acordo,
                           valor_adicional_noturno = v.valor_adicional_noturno,
                           custo_encargos_base = v.custo_encargos_base,
                           custos_separados = TRUE
                      FROM convocacoes AS v
                     WHERE CAST(a.convocacao_id AS TEXT)
                           = CAST(v.id AS TEXT)
                    """
                )

                # ------------------------------------------------------------
                # CORREÇÃO V2 SEBRAE — R$ 90 ANTIGO = ADICIONAL NOTURNO
                # ------------------------------------------------------------
                # Antes de existir o campo "Adicional noturno", os R$ 90 do
                # SEBRAE eram colocados no antigo "Custo + Extra".
                #
                # Exemplos corrigidos:
                #   diária 120 + extra 90 + noturno 90 -> diária 120 + extra 0 + noturno 90
                #   diária 210 + extra 0  + noturno 90 -> diária 120 + extra 0 + noturno 90
                #
                # Novos apontamentos já nascem marcados e não entram nesta
                # correção histórica.
                cur.execute(
                    """
                    SELECT
                        v.id,
                        v.status,
                        v.custo_pago,
                        v.valor_extra,
                        v.valor_adicional_noturno,
                        c.funcao,
                        c.categoria_diaria
                    FROM convocacoes v
                    JOIN obras o
                      ON o.id = v.obra_id
                    JOIN colaboradores c
                      ON c.id = v.colaborador_id
                    WHERE UPPER(TRIM(COALESCE(o.unidade, ''))) = 'SEBRAE'
                      AND COALESCE(v.migracao_sebrae_noturno_v2, FALSE) = FALSE
                    """
                )

                _rows_sb_v2 = cur.fetchall() or []

                for _row_sb in _rows_sb_v2:
                    def _sb_get(chave, idx):
                        if isinstance(_row_sb, dict):
                            return _row_sb.get(chave)
                        try:
                            return _row_sb[idx]
                        except Exception:
                            return None

                    _id_sb = _sb_get("id", 0)
                    _status_sb = str(
                        _sb_get("status", 1) or ""
                    ).strip()
                    _diaria_sb = float(
                        _sb_get("custo_pago", 2) or 0.0
                    )
                    _extra_sb = float(
                        _sb_get("valor_extra", 3) or 0.0
                    )
                    _noturno_sb = float(
                        _sb_get("valor_adicional_noturno", 4) or 0.0
                    )
                    _funcao_sb = str(
                        _sb_get("funcao", 5) or ""
                    ).upper()
                    _categoria_sb = str(
                        _sb_get("categoria_diaria", 6) or ""
                    ).upper()

                    _presente_sb = _status_sb in {
                        "Presente (Integral)",
                        "Presente (Só Manhã)",
                        "Presente (Só Tarde)",
                        "Saída Antecipada",
                        "Presente",
                        "Extra",
                    }

                    _ajudante_sb = (
                        "AJUD" in _categoria_sb
                        or "AUX" in _categoria_sb
                        or "SERVENT" in _categoria_sb
                        or any(
                            termo in _funcao_sb
                            for termo in (
                                "AJUDANTE",
                                "AUXILIAR",
                                "SERVENTE",
                            )
                        )
                    )

                    _base_fin_sb = 80.0 if _ajudante_sb else 120.0

                    if _presente_sb:
                        _noturno_novo_sb = max(
                            90.0,
                            _noturno_sb,
                        )

                        # O R$ 90 antigo do Soares não é Extra.
                        _extra_novo_sb = (
                            0.0
                            if abs(_extra_sb - 90.0) <= 0.01
                            else _extra_sb
                        )

                        # Se a diária ficou inflada exatamente em +R$ 90
                        # por causa do antigo campo combinado, volta à base.
                        _diaria_nova_sb = (
                            _base_fin_sb
                            if abs(
                                _diaria_sb - (_base_fin_sb + 90.0)
                            ) <= 0.01
                            else (
                                _diaria_sb
                                if _diaria_sb > 0
                                else _base_fin_sb
                            )
                        )
                    else:
                        _noturno_novo_sb = 0.0
                        _extra_novo_sb = 0.0
                        _diaria_nova_sb = 0.0

                    cur.execute(
                        """
                        UPDATE convocacoes
                           SET tipo_diaria = 'Diária',
                               custo_pago = %s,
                               valor_extra = %s,
                               valor_adicional_noturno = %s,
                               migracao_sebrae_noturno_v2 = TRUE
                         WHERE id = %s
                        """,
                        (
                            round(_diaria_nova_sb, 2),
                            round(_extra_novo_sb, 2),
                            round(_noturno_novo_sb, 2),
                            _id_sb,
                        ),
                    )

                cur.execute(
                    """
                    UPDATE apontamentos AS a
                       SET tipo_diaria = v.tipo_diaria,
                           custo_pago = v.custo_pago,
                           valor_extra = v.valor_extra,
                           valor_adicional_noturno = v.valor_adicional_noturno,
                           migracao_sebrae_noturno_v2 = TRUE
                      FROM convocacoes AS v
                     WHERE CAST(a.convocacao_id AS TEXT)
                           = CAST(v.id AS TEXT)
                       AND COALESCE(v.migracao_sebrae_noturno_v2, FALSE) = TRUE
                    """
                )

                # O índice antigo impedia, por exemplo, uma obra com o mesmo
                # nome em duas unidades diferentes.
                cur.execute("DROP INDEX IF EXISTS uq_obras_nome")
                cur.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_obras_nome_unidade
                    ON obras (nome, unidade)
                    """
                )

                # Corrige sequences somente quando estiverem atrás do maior ID.
                for tabela in ("obras", "colaboradores"):
                    cur.execute(
                        f"SELECT COALESCE(MAX(id), 0) AS max_id FROM {tabela}"
                    )
                    row_max = cur.fetchone()
                    max_id = int(
                        (
                            row_max.get("max_id")
                            if isinstance(row_max, dict)
                            else row_max[0]
                        )
                        or 0
                    )

                    cur.execute(
                        f"SELECT last_value FROM {tabela}_id_seq"
                    )
                    row_seq = cur.fetchone()
                    seq_last = int(
                        (
                            row_seq.get("last_value")
                            if isinstance(row_seq, dict)
                            else row_seq[0]
                        )
                        or 0
                    )

                    if seq_last < max_id:
                        cur.execute(
                            f"SELECT setval('{tabela}_id_seq', %s, true)",
                            (max_id,),
                        )

                conn.commit()

        return True

    except Exception:
        return False


_garantir_estrutura_cadastros_admin()


@st.cache_resource
def _garantir_estrutura_cobrancas_teams():
    """Cria apenas as tabelas de configuração/log das cobranças Teams."""
    if DB_BACKEND != "NEON" or not hasattr(supabase, "_connect"):
        return False

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS engenheiros_teams (
                        engenheiro TEXT PRIMARY KEY,
                        email_teams TEXT,
                        ativo BOOLEAN NOT NULL DEFAULT TRUE,
                        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cobrancas_teams (
                        id BIGSERIAL PRIMARY KEY,
                        data_execucao DATE NOT NULL,
                        horario TEXT NOT NULL,
                        engenheiro TEXT NOT NULL,
                        email_teams TEXT,
                        qtd_pendentes INTEGER NOT NULL DEFAULT 0,
                        mensagem TEXT,
                        status TEXT NOT NULL DEFAULT 'ENVIADA',
                        resposta_http INTEGER,
                        enviado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        UNIQUE (data_execucao, horario, engenheiro)
                    )
                    """
                )

                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_cobrancas_teams_enviado_em
                    ON cobrancas_teams (enviado_em DESC)
                    """
                )

                # Gustavo foi desligado: preservamos histórico,
                # mas ele deixa de receber novas cobranças.
                cur.execute(
                    """
                    UPDATE engenheiros_teams
                       SET ativo = FALSE,
                           atualizado_em = NOW()
                     WHERE UPPER(engenheiro) = 'GUSTAVO'
                    """
                )

                conn.commit()

        return True

    except Exception:
        return False


_garantir_estrutura_cobrancas_teams()


# --- LIMPEZA SELETIVA DE CACHE ---
def limpar_cache_operacional():
    """
    Atualiza os caches estruturais quando obras/colaboradores podem ter mudado.
    Não limpa o cache do Trello.
    """
    for nome_funcao in (
        "buscar_obras",
        "buscar_colaboradores",
        "buscar_colaboradores_todos",
        "_buscar_convocacoes_intervalo",
    ):
        funcao = globals().get(nome_funcao)
        if funcao is not None and hasattr(funcao, "clear"):
            try:
                funcao.clear()
            except Exception:
                pass


def limpar_cache_convocacoes():
    """
    Cache rápido para ações de campo.
    Convocar/apontar altera convocações, mas não a base de obras/colaboradores.
    Evita recarregar cadastros inteiros no rerun.
    """
    funcao = globals().get("_buscar_convocacoes_intervalo")
    if funcao is not None and hasattr(funcao, "clear"):
        try:
            funcao.clear()
        except Exception:
            pass


def limpar_cache_colaboradores():
    """Limpa somente a base de colaboradores, sem tocar em obras/convocações."""
    for nome_funcao in (
        "buscar_colaboradores",
        "buscar_colaboradores_todos",
    ):
        funcao = globals().get(nome_funcao)
        if funcao is not None and hasattr(funcao, "clear"):
            try:
                funcao.clear()
            except Exception:
                pass


def _get_conexao_admin_rapida():
    """
    Mantém uma conexão Neon reutilizável durante a sessão do usuário.

    Isso reduz principalmente o tempo de:
    - excluir funcionário;
    - trocar moradia;
    - editar cadastro.
    """
    if (
        DB_BACKEND != "NEON"
        or not hasattr(supabase, "_connect")
    ):
        return None

    chave = "_conn_admin_colaboradores"

    conn = st.session_state.get(chave)

    try:
        if conn is not None and not getattr(conn, "closed", True):
            return conn
    except Exception:
        pass

    try:
        conn = supabase._connect()
        st.session_state[chave] = conn
        return conn
    except Exception:
        st.session_state.pop(chave, None)
        return None


def _descartar_conexao_admin_rapida():
    chave = "_conn_admin_colaboradores"
    conn = st.session_state.pop(chave, None)

    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass


def _salvar_moradias_em_lote_admin(alteracoes):
    """
    Salva várias mudanças de moradia de uma vez.

    alteracoes:
        {
            colaborador_id: {
                "antes": <valor anterior>,
                "depois": <valor novo>,
                "nome": <nome>
            }
        }

    No Neon, todas as alterações + auditorias usam UMA única transação.
    """
    alteracoes = dict(alteracoes or {})

    if not alteracoes:
        return True, 0

    if DB_BACKEND == "NEON":
        for _tentativa in range(2):
            conn = _get_conexao_admin_rapida()

            if conn is None:
                break

            try:
                with conn.cursor() as cur:
                    for colaborador_id, info in alteracoes.items():
                        depois = info.get("depois")
                        antes = info.get("antes")

                        cur.execute(
                            """
                            UPDATE colaboradores
                               SET local_moradia = %s,
                                   atualizado_em = NOW()
                             WHERE id = %s
                            """,
                            (
                                depois,
                                colaborador_id,
                            ),
                        )

                        # Auditoria na mesma conexão/transação.
                        try:
                            cur.execute(
                                "SAVEPOINT audit_moradia_lote"
                            )

                            cur.execute(
                                """
                                INSERT INTO auditoria
                                    (
                                        entidade,
                                        entidade_id,
                                        acao,
                                        usuario,
                                        antes,
                                        depois,
                                        contexto
                                    )
                                VALUES
                                    (
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s::jsonb,
                                        %s::jsonb,
                                        %s::jsonb
                                    )
                                """,
                                (
                                    "colaboradores",
                                    str(colaborador_id),
                                    "EDITAR_MORADIA",
                                    "ADMIN",
                                    _json_db({
                                        "local_moradia": antes
                                    }),
                                    _json_db({
                                        "local_moradia": depois
                                    }),
                                    _json_db({
                                        "origem": (
                                            "banco_funcionarios_lote"
                                        )
                                    }),
                                ),
                            )

                            cur.execute(
                                "RELEASE SAVEPOINT audit_moradia_lote"
                            )

                        except Exception:
                            try:
                                cur.execute(
                                    "ROLLBACK TO SAVEPOINT audit_moradia_lote"
                                )
                                cur.execute(
                                    "RELEASE SAVEPOINT audit_moradia_lote"
                                )
                            except Exception:
                                pass

                conn.commit()
                limpar_cache_colaboradores()
                return True, len(alteracoes)

            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass

                _descartar_conexao_admin_rapida()

    # Fallback compatível com backend legado.
    salvos = 0

    try:
        for colaborador_id, info in alteracoes.items():
            (
                supabase.table("colaboradores")
                .update({
                    "local_moradia": info.get("depois")
                })
                .eq(
                    "id",
                    colaborador_id,
                )
                .execute()
            )

            salvos += 1

        limpar_cache_colaboradores()
        return True, salvos

    except Exception:
        return False, salvos


def _atualizar_colaborador_admin_rapido(
    colaborador_id,
    campos,
    acao,
    antes=None,
):
    """
    UPDATE administrativo otimizado.

    - reutiliza a conexão PostgreSQL da sessão;
    - UPDATE + auditoria na mesma transação;
    - limpa apenas o cache de colaboradores;
    - se a conexão estiver velha, reconecta automaticamente.
    """
    campos_permitidos = {
        "ativo",
        "local_moradia",
        "nome",
        "funcao",
        "valor_diaria",
        "categoria_diaria",
    }

    payload = {
        k: v
        for k, v in dict(campos or {}).items()
        if k in campos_permitidos
    }

    if not payload:
        return False

    if DB_BACKEND == "NEON":
        for _tentativa in range(2):
            conn = _get_conexao_admin_rapida()

            if conn is None:
                break

            try:
                with conn.cursor() as cur:
                    atribuicoes = ", ".join(
                        f"{campo} = %s"
                        for campo in payload.keys()
                    )

                    valores = list(payload.values())
                    valores.append(colaborador_id)

                    cur.execute(
                        f"""
                        UPDATE colaboradores
                           SET {atribuicoes},
                               atualizado_em = NOW()
                         WHERE id = %s
                        """,
                        tuple(valores),
                    )

                    # Auditoria na mesma conexão.
                    try:
                        cur.execute(
                            "SAVEPOINT audit_colab_inline"
                        )

                        cur.execute(
                            """
                            INSERT INTO auditoria
                                (
                                    entidade,
                                    entidade_id,
                                    acao,
                                    usuario,
                                    antes,
                                    depois,
                                    contexto
                                )
                            VALUES
                                (
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s::jsonb,
                                    %s::jsonb,
                                    %s::jsonb
                                )
                            """,
                            (
                                "colaboradores",
                                str(colaborador_id),
                                str(acao),
                                "ADMIN",
                                (
                                    _json_db(antes)
                                    if antes is not None
                                    else None
                                ),
                                _json_db(payload),
                                _json_db({
                                    "origem": (
                                        "banco_funcionarios_inline"
                                    )
                                }),
                            ),
                        )

                        cur.execute(
                            "RELEASE SAVEPOINT audit_colab_inline"
                        )

                    except Exception:
                        try:
                            cur.execute(
                                "ROLLBACK TO SAVEPOINT audit_colab_inline"
                            )
                            cur.execute(
                                "RELEASE SAVEPOINT audit_colab_inline"
                            )
                        except Exception:
                            pass

                conn.commit()
                limpar_cache_colaboradores()
                return True

            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass

                _descartar_conexao_admin_rapida()

    # Fallback compatível.
    try:
        (
            supabase.table("colaboradores")
            .update(payload)
            .eq("id", colaborador_id)
            .execute()
        )

        limpar_cache_colaboradores()

        registrar_auditoria_prod(
            "colaboradores",
            colaborador_id,
            acao,
            "ADMIN",
            antes=antes,
            depois=payload,
            contexto={
                "origem": "banco_funcionarios_inline"
            },
        )

        return True

    except Exception:
        return False


# --- FUNÇÕES DE LIMPEZA E PADRONIZAÇÃO ---
def identificar_unidade(nome_card):
    if not nome_card: return "GERAL"
    texto = unicodedata.normalize('NFKD', str(nome_card)).encode('ASCII', 'ignore').decode('utf-8').upper()
    
    if "APRL005" in texto or "MARACANAU" in texto: return "MARACANAÚ"
    if "SEBRAE" in texto: return "SEBRAE"
    if "UNIFOR" in texto: return "UNIFOR"
    if "IDALYA" in texto or "MATHEUS" in texto: return "IDALYA E MATHEUS"
    if "COLISEU" in texto: return "COLISEU"
    if "BARRA" in texto: return "BARRA DO CEARÁ"
    if "MUSEU" in texto: return "MUSEU"
    if "HORIZONTE" in texto: return "HORIZONTE"
    if "ESCRITORIO" in texto: return "ESCRITÓRIO"
    if "CASA DA INDUSTRIA" in texto or "FIEC" in texto or " DR " in texto or "| SESI DR |" in texto or "| SESI DR" in texto: return "FIEC"
    if "CENTRO" in texto: return "CENTRO"
    
    partes = str(nome_card).split('|')
    if len(partes) >= 2:
        return partes[1].strip().upper()
    return "GERAL"

def limpar_funcao(texto):
    if not texto or str(texto).upper() == 'NAN': return "INDEFINIDA"
    texto_limpo = str(texto).upper().strip()
    texto_limpo = re.sub(r'^\d+\s*-\s*', '', texto_limpo)
    texto_limpo = unicodedata.normalize('NFKD', texto_limpo).encode('ASCII', 'ignore').decode('utf-8')
    return texto_limpo

def normalizar(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛"]
    hash_num = sum(ord(c) for c in str(funcao))
    return cores[hash_num % len(cores)]

# ---------------------------------------------------------------------------
# REGRAS DE DIÁRIA POR CATEGORIA
# ---------------------------------------------------------------------------
# CONTROLADORIA — custo padrão com encargos.
VALOR_DIARIA_PROFISSIONAL = 241.74
VALOR_DIARIA_AJUDANTE = 182.34

# FINANCEIRO — valor líquido padrão pago ao colaborador.
VALOR_FIN_DIARIA_PROFISSIONAL = 120.00
VALOR_FIN_MEIA_PROFISSIONAL = 60.00
VALOR_FIN_DIARIA_AJUDANTE = 80.00
VALOR_FIN_MEIA_AJUDANTE = 40.00

# Compatibilidade com trechos antigos que assumiam Profissional.
VALOR_LIMPO_DIARIA = VALOR_FIN_DIARIA_PROFISSIONAL
VALOR_LIMPO_MEIA_DIARIA = VALOR_FIN_MEIA_PROFISSIONAL

TIPOS_DIARIA = ["Diária", "Meia diária"]

# Regras de prazo/cobrança:
# - Demais unidades: o apontamento do dia deve estar concluído até 16:00.
# - SEBRAE: jornada 17h–02h continua sendo DIÁRIA INTEGRAL;
#   o apontamento pode ser concluído até 09:29 do dia seguinte sem atraso.
# - Para o Teams, o SEBRAE recebe apenas UM lembrete automático às 21:00
#   do próprio dia do serviço. Depois disso continua visível para cobrança manual.
VALOR_ADICIONAL_NOTURNO_SEBRAE = 90.00
HORA_LIMITE_APONTAMENTO_GERAL = datetime.time(16, 0)
HORA_LIMITE_APONTAMENTO_SEBRAE = datetime.time(9, 30)
HORA_LEMBRETE_TEAMS_SEBRAE = datetime.time(21, 0)


def eh_unidade_sebrae(unidade):
    return normalizar(unidade or "") == "SEBRAE"


def apontamento_esta_atrasado(
    data_servico,
    unidade="",
    agora=None,
):
    """
    Regra operacional de atraso.

    DEMAIS UNIDADES
    ----------------
    O apontamento do serviço do dia D deve ser concluído até 16:00 de D.
    Portanto:
      - D antes de 16:00 -> ainda no prazo;
      - D a partir de 16:00 -> atrasado;
      - D+1 em diante -> atrasado.

    SEBRAE
    ------
    Como a jornada é 17h–02h, o apontamento de D pode ser concluído
    até 09:29 de D+1 sem ser marcado como atraso.
    O lembrete do Teams às 21:00 de D é apenas uma cobrança preventiva
    e não muda essa regra operacional.
    """
    agora = agora or agora_aproar()

    if not isinstance(
        data_servico,
        datetime.date,
    ):
        try:
            data_servico = (
                datetime.date.fromisoformat(
                    str(data_servico)
                )
            )
        except Exception:
            return False

    if agora.date() < data_servico:
        return False

    if eh_unidade_sebrae(unidade):
        if agora.date() == data_servico:
            return False

        dia_seguinte = (
            data_servico
            + datetime.timedelta(days=1)
        )

        if agora.date() == dia_seguinte:
            return (
                agora.time()
                >= HORA_LIMITE_APONTAMENTO_SEBRAE
            )

        return agora.date() > dia_seguinte

    # Demais unidades.
    if agora.date() == data_servico:
        return (
            agora.time()
            >= HORA_LIMITE_APONTAMENTO_GERAL
        )

    return agora.date() > data_servico


def pendencia_teams_esta_atrasada(
    data_servico,
    unidade="",
    agora=None,
):
    """
    Indica atraso operacional. A lista de Configurações não depende desta
    função: toda pendência de hoje ou de dias anteriores continua visível
    para conferência e cobrança manual.
    """
    return apontamento_esta_atrasado(
        data_servico,
        unidade=unidade,
        agora=agora or agora_aproar(),
    )


def proxima_cobranca_automatica_teams(
    data_servico,
    unidade="",
    agora=None,
):
    """
    Retorna a próxima janela automática prevista para uma pendência.

    Demais unidades:
      D 16:00
      D+1 09:30
      D+1 15:00
      depois: somente manual

    SEBRAE:
      D 21:00 (único automático)
      depois: somente manual
    """
    agora = agora or agora_aproar()

    if not isinstance(
        data_servico,
        datetime.date,
    ):
        try:
            data_servico = (
                datetime.date.fromisoformat(
                    str(data_servico)
                )
            )
        except Exception:
            return "Somente manual"

    hoje = agora.date()

    if data_servico > hoje:
        return "Ainda não iniciou"

    if eh_unidade_sebrae(unidade):
        if data_servico == hoje:
            if agora.time() < HORA_LEMBRETE_TEAMS_SEBRAE:
                return "Hoje · 21:00"
            return "Automático de 21:00 já passou"
        return "Somente manual"

    # Demais unidades.
    if data_servico == hoje:
        if agora.time() < datetime.time(16, 0):
            return "Hoje · 16:00"
        return "Amanhã · 09:30"

    dia_seguinte = (
        data_servico
        + datetime.timedelta(days=1)
    )

    if hoje == dia_seguinte:
        if agora.time() < datetime.time(9, 30):
            return "Hoje · 09:30"
        if agora.time() < datetime.time(15, 0):
            return "Hoje · 15:00"
        return "Último automático já passou"

    return "Somente manual"


def situacao_pendencia_teams(
    data_servico,
    unidade="",
    agora=None,
):
    """
    Texto curto para a prévia da Configuração.
    """
    agora = agora or agora_aproar()

    if apontamento_esta_atrasado(
        data_servico,
        unidade=unidade,
        agora=agora,
    ):
        return "ATRASADO"

    if eh_unidade_sebrae(unidade):
        return "PENDENTE · SEBRAE"

    return "PENDENTE"



def normalizar_tipo_diaria(valor):
    bruto = normalizar(valor or "")
    if "MEIA" in bruto:
        return "Meia diária"
    return "Diária"


def valor_limpo_por_tipo_diaria(tipo_diaria):
    """
    Compatibilidade: retorna o padrão de Profissional.
    Para cálculos reais, use valor_financeiro_padrao_colaborador().
    """
    return (
        VALOR_FIN_MEIA_PROFISSIONAL
        if normalizar_tipo_diaria(
            tipo_diaria
        ) == "Meia diária"
        else VALOR_FIN_DIARIA_PROFISSIONAL
    )


def categoria_diaria_colaborador(colab):
    colab = colab or {}

    categoria = normalizar(
        colab.get("categoria_diaria")
        or ""
    )

    if (
        "AJUD" in categoria
        or "SERVENT" in categoria
        or "AUX" in categoria
    ):
        return "Ajudante"

    if "PROF" in categoria:
        return "Profissional"

    funcao = normalizar(
        colab.get("funcao")
        or ""
    )

    if any(
        termo in funcao
        for termo in (
            "AJUDANTE",
            "AUXILIAR",
            "SERVENTE",
        )
    ):
        return "Ajudante"

    try:
        valor_ref = float(
            colab.get("valor_diaria")
            or 0.0
        )
    except Exception:
        valor_ref = 0.0

    if 0 < valor_ref < 220:
        return "Ajudante"

    return "Profissional"


def valor_financeiro_padrao_colaborador(
    colab,
    tipo_diaria,
):
    meia = (
        normalizar_tipo_diaria(
            tipo_diaria
        )
        == "Meia diária"
    )

    if (
        categoria_diaria_colaborador(
            colab
        )
        == "Ajudante"
    ):
        return (
            VALOR_FIN_MEIA_AJUDANTE
            if meia
            else VALOR_FIN_DIARIA_AJUDANTE
        )

    return (
        VALOR_FIN_MEIA_PROFISSIONAL
        if meia
        else VALOR_FIN_DIARIA_PROFISSIONAL
    )


def valor_controladoria_padrao_colaborador(
    colab,
    tipo_diaria,
):
    valor_cheio = (
        VALOR_DIARIA_AJUDANTE
        if categoria_diaria_colaborador(
            colab
        )
        == "Ajudante"
        else VALOR_DIARIA_PROFISSIONAL
    )

    return round(
        valor_cheio
        * (
            0.5
            if normalizar_tipo_diaria(
                tipo_diaria
            )
            == "Meia diária"
            else 1.0
        ),
        2,
    )


def fracao_encargos_por_tipo_diaria(tipo_diaria):
    return 0.5 if normalizar_tipo_diaria(tipo_diaria) == "Meia diária" else 1.0


def registro_tem_servico_sebrae(registro):
    """
    Identifica SEBRAE tanto pela obra principal quanto por serviços adicionais.

    Isso é importante porque um apontamento pode conter vários serviços/unidades.
    """
    registro = registro or {}

    # Alguns fluxos já carregam a unidade diretamente.
    if eh_unidade_sebrae(
        registro.get("unidade")
        or registro.get("Unidade")
        or ""
    ):
        return True

    # Obra principal.
    obra_id = registro.get("obra_id")
    obra = {}

    try:
        obra = dict_obras.get(obra_id, {})
        if not obra and obra_id is not None:
            obra = dict_obras.get(str(obra_id), {})
    except Exception:
        obra = {}

    if eh_unidade_sebrae(
        (obra or {}).get("unidade")
        or ""
    ):
        return True

    # Serviços adicionais guardados nos metadados da observação.
    try:
        func_meta = globals().get(
            "obter_metadata_operacional"
        )

        if callable(func_meta):
            meta = func_meta(
                registro.get("observacao")
                or ""
            ) or {}

            adicionais = (
                meta.get("servicos_adicionais")
                or []
            )

            for adicional in adicionais:
                if not isinstance(
                    adicional,
                    dict,
                ):
                    continue

                if eh_unidade_sebrae(
                    adicional.get("unidade")
                    or ""
                ):
                    return True

                obra_id_add = str(
                    adicional.get("obra_id")
                    or ""
                ).strip()

                if obra_id_add:
                    obra_add = {}

                    try:
                        obra_add = (
                            dict_obras.get(
                                obra_id_add,
                                {},
                            )
                            or dict_obras.get(
                                adicional.get(
                                    "obra_id"
                                ),
                                {},
                            )
                        )
                    except Exception:
                        obra_add = {}

                    if eh_unidade_sebrae(
                        (obra_add or {}).get(
                            "unidade"
                        )
                        or ""
                    ):
                        return True

                nome_add = normalizar(
                    adicional.get("servico")
                    or ""
                )

                if nome_add:
                    try:
                        for _obra in obras:
                            if (
                                normalizar(
                                    _obra.get("nome")
                                    or ""
                                )
                                == nome_add
                                and eh_unidade_sebrae(
                                    _obra.get("unidade")
                                    or ""
                                )
                            ):
                                return True
                    except Exception:
                        pass

    except Exception:
        pass

    return False


def _adicional_noturno_salvo_registro(
    registro,
):
    try:
        return max(
            0.0,
            float(
                (registro or {}).get(
                    "valor_adicional_noturno"
                )
                or 0.0
            ),
        )
    except Exception:
        return 0.0


def tipo_diaria_registro(registro):
    registro = registro or {}

    status = normalizar_status_operacional(
        registro.get("status")
        or ""
    )

    # Regra fixa do SEBRAE:
    # jornada 17h–02h = diária integral.
    if (
        status_eh_presenca(status)
        and registro_tem_servico_sebrae(
            registro
        )
    ):
        return "Diária"

    valor = str(
        registro.get("tipo_diaria")
        or ""
    ).strip()

    if valor:
        return normalizar_tipo_diaria(valor)

    # Compatibilidade com apontamentos antigos.
    if status in [
        "Presente (Só Manhã)",
        "Presente (Só Tarde)",
        "Saída Antecipada",
    ]:
        return "Meia diária"
    return "Diária"


def valor_diaria_financeiro_registro(
    registro,
    colab=None,
):
    """
    Diária efetivamente paga ao colaborador.

    custo_pago passa a guardar SOMENTE a diária.
    Extra fica em valor_extra.
    """
    registro = registro or {}

    if not status_eh_presenca(
        normalizar_status_operacional(
            registro.get("status")
            or ""
        )
    ):
        return 0.0

    if colab is None:
        try:
            colab = dict_colaboradores.get(
                registro.get(
                    "colaborador_id"
                ),
                {},
            )
        except Exception:
            colab = {}

    valor = registro.get(
        "custo_pago"
    )

    if valor not in (
        None,
        "",
    ):
        try:
            valor = max(
                0.0,
                float(valor),
            )
            if valor > 0:
                return round(
                    valor,
                    2,
                )
        except Exception:
            pass

    return round(
        valor_financeiro_padrao_colaborador(
            colab or {},
            tipo_diaria_registro(
                registro
            ),
        ),
        2,
    )


def custo_pago_total_registro(
    registro,
    colab=None,
):
    """Alias de compatibilidade: hoje representa apenas a diária."""
    return valor_diaria_financeiro_registro(
        registro,
        colab=colab,
    )


def valor_extra_registro(registro):
    """Extra real, separado da diária."""
    registro = registro or {}

    if not status_eh_presenca(
        normalizar_status_operacional(
            registro.get("status")
            or ""
        )
    ):
        return 0.0

    try:
        return round(
            max(
                0.0,
                float(
                    registro.get(
                        "valor_extra"
                    )
                    or 0.0
                ),
            ),
            2,
        )
    except Exception:
        return 0.0


def valor_adicional_noturno_registro(registro):
    """
    Regra definitiva:
    qualquer presença no SEBRAE recebe R$ 90,00 de adicional noturno.

    Se um valor maior tiver sido lançado manualmente no futuro, ele é
    preservado.
    """
    registro = registro or {}

    status = normalizar_status_operacional(
        registro.get("status")
        or ""
    )

    if not status_eh_presenca(
        status
    ):
        return 0.0

    salvo = (
        _adicional_noturno_salvo_registro(
            registro
        )
    )

    if registro_tem_servico_sebrae(
        registro
    ):
        return round(
            max(
                float(
                    VALOR_ADICIONAL_NOTURNO_SEBRAE
                ),
                salvo,
            ),
            2,
        )

    return round(
        salvo,
        2,
    )


def valor_acordo_registro(registro):
    registro = registro or {}
    if not status_eh_presenca(
        normalizar_status_operacional(registro.get("status") or "")
    ):
        return 0.0
    try:
        return max(0.0, float(registro.get("valor_acordo") or 0.0))
    except Exception:
        return 0.0


def custo_encargos_base_registro(
    registro,
    colab=None,
):
    """
    Custo-base da Controladoria por categoria.

    Profissional:
      diária R$ 241,74
      meia   R$ 120,87

    Ajudante:
      diária R$ 182,34
      meia   R$ 91,17
    """
    registro = registro or {}

    if not status_eh_presenca(
        normalizar_status_operacional(
            registro.get("status")
            or ""
        )
    ):
        return 0.0

    if colab is None:
        try:
            colab = dict_colaboradores.get(
                registro.get(
                    "colaborador_id"
                ),
                {},
            )
        except Exception:
            colab = {}

    return valor_controladoria_padrao_colaborador(
        colab or {},
        tipo_diaria_registro(
            registro
        ),
    )


def inferir_tipo_colaborador(
    funcao,
    valor_referencia=None,
):
    f = normalizar(funcao or "")

    if any(
        termo in f
        for termo in (
            "AJUDANTE",
            "AUXILIAR",
            "AUX.",
            "AUX ",
            "SERVENTE",
        )
    ):
        return "Ajudante"

    try:
        valor_ref = float(
            valor_referencia
            or 0.0
        )
    except Exception:
        valor_ref = 0.0

    if 0 < valor_ref < 220:
        return "Ajudante"

    return "Profissional"

def valor_diaria_por_tipo(tipo):
    return VALOR_DIARIA_AJUDANTE if normalizar(tipo) == "AJUDANTE" else VALOR_DIARIA_PROFISSIONAL

def obter_valor_diaria_colaborador(colab):
    """Custo diário com encargos cadastrado/importado para o colaborador."""
    colab = colab or {}

    try:
        valor_cadastrado = float(
            colab.get("valor_diaria")
            or 0.0
        )
    except Exception:
        valor_cadastrado = 0.0

    return valor_cadastrado if valor_cadastrado > 0 else 0.0


def calcular_diaria_proporcional(status, valor_diaria_base):
    diaria = float(valor_diaria_base or VALOR_DIARIA_PROFISSIONAL)
    if status in ["Presente (Integral)", "Presente", "Extra"]:
        return diaria
    elif status in ["Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada"]:
        return diaria / 2.0
    return 0.0

def formatar_reais(valor):
    return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def to_latin(texto):
    if not texto: return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

def proximo_dia_util(data_base=None):
    """
    Retorna o dia seguinte à data informada.
    Convocações podem ocorrer em qualquer dia da semana,
    inclusive sábado, domingo e feriado.

    O nome da função foi mantido para compatibilidade
    com o restante do sistema.
    """
    data_ref = data_base or datetime.date.today()
    return data_ref + datetime.timedelta(days=1)

NOME_OBRA_PLACEHOLDER = "A DEFINIR NO APONTAMENTO"

def nome_obra_placeholder_unidade(unidade):
    """
    Gera um nome técnico único por Unidade.
    Isso evita conflito com o índice UNIQUE de nome da tabela obras no Neon.
    """
    unidade_limpa = " ".join(str(unidade or "").strip().split()).upper()
    return f"{NOME_OBRA_PLACEHOLDER} - {unidade_limpa}"


def eh_obra_placeholder(obra):
    """
    Identifica tanto o placeholder legado:
        A DEFINIR NO APONTAMENTO
    quanto os novos placeholders por Unidade:
        A DEFINIR NO APONTAMENTO - UNIFOR
        A DEFINIR NO APONTAMENTO - FIEC
        etc.
    """
    if not obra:
        return False

    nome_norm = normalizar(obra.get("nome", ""))
    prefixo_norm = normalizar(NOME_OBRA_PLACEHOLDER)

    return nome_norm == prefixo_norm or nome_norm.startswith(prefixo_norm + " - ")


def obter_obra_placeholder_unidade(unidade):
    """
    Retorna/cria a obra técnica da Unidade para convocações ainda sem
    Obra/Serviço definida.

    Cada Unidade recebe um nome técnico diferente no banco para não violar
    a restrição UNIQUE de obras.nome.
    """
    unidade_limpa = " ".join(str(unidade or "").strip().split()).upper()
    if not unidade_limpa:
        return None

    try:
        # 1) Se já existe qualquer placeholder nessa Unidade, reutiliza.
        existentes = (
            supabase.table("obras")
            .select("*")
            .eq("unidade", unidade_limpa)
            .execute().data or []
        )

        for obra in existentes:
            if eh_obra_placeholder(obra):
                return obra.get("id")

        # 2) Cria um placeholder exclusivo desta Unidade.
        nome_placeholder = nome_obra_placeholder_unidade(unidade_limpa)

        criado = (
            supabase.table("obras")
            .insert({
                "unidade": unidade_limpa,
                "nome": nome_placeholder
            })
            .execute().data or []
        )

        if criado:
            limpar_cache_operacional()
            return criado[0].get("id")

    except Exception as e:
        # Guarda o diagnóstico para o administrativo, mas não derruba o app.
        try:
            st.session_state["erro_placeholder_unidade"] = (
                f"{type(e).__name__}: {str(e)[:300]}"
            )
        except Exception:
            pass

        # 3) Última confirmação: o INSERT pode ter sido concluído e apenas a
        # resposta ter falhado. Consulta novamente antes de desistir.
        try:
            existentes = (
                supabase.table("obras")
                .select("*")
                .eq("unidade", unidade_limpa)
                .execute().data or []
            )
            for obra in existentes:
                if eh_obra_placeholder(obra):
                    return obra.get("id")
        except Exception:
            pass

    return None

def obras_reais_da_unidade(unidade):
    """Lista somente Obras/Serviços reais, ocultando o registro temporário."""
    return [o for o in obras if o.get("unidade") == unidade and not eh_obra_placeholder(o)]

OBS_META_MARKER = " ||APROAR_META|| "
try:
    TZ_APROAR = ZoneInfo("America/Fortaleza")
except Exception:
    TZ_APROAR = None


def agora_aproar():
    """Horário operacional da Aproar (Fortaleza), inclusive no Streamlit Cloud."""
    if TZ_APROAR is not None:
        return datetime.datetime.now(TZ_APROAR)
    return datetime.datetime.now()


# ============================================================
# FASE 1 DE PRODUÇÃO — ESTRUTURA NOVA EM PARALELO
# ============================================================
# As tabelas estruturadas são ativadas somente quando a migração SQL já foi
# aplicada no Neon. Enquanto isso, o app continua lendo/gravar pelo modelo
# legado, sem interromper a operação.
TABELAS_PRODUCAO = {
    "indisponibilidades",
    "conflitos_convocacao",
    "apontamentos",
    "servicos_apontamento",
    "auditoria",
}


@st.cache_data(ttl=60, show_spinner=False)
def schema_producao_disponivel():
    if DB_BACKEND != "NEON" or not hasattr(supabase, "_connect"):
        return False
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) FILTER (WHERE table_name IN (
                            'indisponibilidades','conflitos_convocacao','apontamentos',
                            'servicos_apontamento','auditoria'
                        )) AS qtd_tabelas,
                        EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_schema = 'public'
                              AND table_name = 'convocacoes'
                              AND column_name = 'turno'
                        ) AS tem_turno
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                row = cur.fetchone()
                if isinstance(row, dict):
                    return int(row.get("qtd_tabelas") or 0) >= 5 and bool(row.get("tem_turno"))
                return bool(row and int(row[0] or 0) >= 5 and row[1])
    except Exception:
        return False


def _json_db(valor):
    try:
        return json.dumps(valor, ensure_ascii=False, default=str)
    except Exception:
        return json.dumps(str(valor), ensure_ascii=False)


def registrar_auditoria_prod(entidade, entidade_id, acao, usuario=None, antes=None, depois=None, contexto=None):
    """Auditoria silenciosa: nunca derruba a operação principal."""
    if not schema_producao_disponivel():
        return False
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO auditoria
                        (entidade, entidade_id, acao, usuario, antes, depois, contexto)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
                    """,
                    (
                        str(entidade), str(entidade_id or ""), str(acao),
                        str(usuario or ""),
                        _json_db(antes) if antes is not None else None,
                        _json_db(depois) if depois is not None else None,
                        _json_db(contexto or {}),
                    ),
                )
                conn.commit()
        return True
    except Exception:
        return False


def _auditoria_texto_json(valor):
    if valor in (None, "", {}, []):
        return ""
    try:
        if isinstance(valor, str):
            try:
                valor = json.loads(valor)
            except Exception:
                return valor
        return json.dumps(valor, ensure_ascii=False, default=str)
    except Exception:
        return str(valor)


def render_historico_auditoria():
    """Consulta somente leitura do histórico operacional gravado no Neon."""
    st.markdown("### 🧾 Histórico de auditoria")
    st.caption("Mostra alterações operacionais importantes: quem executou, o que mudou e quando.")

    if DB_BACKEND != "NEON" or not schema_producao_disponivel() or not hasattr(supabase, "_connect"):
        st.info("Histórico estruturado disponível somente com a estrutura Neon ativa.")
        return

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, entidade, entidade_id, acao, usuario, ocorrido_em, antes, depois, contexto
                    FROM auditoria
                    ORDER BY ocorrido_em DESC
                    LIMIT 500
                    """
                )
                rows = cur.fetchall() or []
    except Exception as e:
        exibir_erro_amigavel("auditoria", "consultar", e, "Não foi possível consultar o histórico de auditoria.")
        return

    registros = [dict(r) if isinstance(r, dict) else {
        "id": r[0], "entidade": r[1], "entidade_id": r[2], "acao": r[3], "usuario": r[4],
        "ocorrido_em": r[5], "antes": r[6], "depois": r[7], "contexto": r[8]
    } for r in rows]

    if not registros:
        st.info("Nenhuma ação auditada registrada ainda.")
        return

    df = pd.DataFrame(registros)
    df["usuario"] = df["usuario"].fillna("").replace("", "NÃO INFORMADO")
    df["entidade"] = df["entidade"].fillna("").replace("", "NÃO INFORMADO")
    df["acao"] = df["acao"].fillna("").replace("", "NÃO INFORMADA")

    try:
        datas = pd.to_datetime(df["ocorrido_em"], utc=True, errors="coerce")
        df["data_local"] = datas.dt.tz_convert(TZ_APROAR).dt.date
        df["Data/Hora"] = datas.dt.tz_convert(TZ_APROAR).dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        df["data_local"] = None
        df["Data/Hora"] = df["ocorrido_em"].astype(str)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        usuarios = ["TODOS"] + sorted([x for x in df["usuario"].dropna().astype(str).unique().tolist() if x])
        usuario_sel = st.selectbox("Usuário", usuarios, key="audit_usuario")
    with f2:
        entidades = ["TODAS"] + sorted([x for x in df["entidade"].dropna().astype(str).unique().tolist() if x])
        entidade_sel = st.selectbox("Entidade", entidades, key="audit_entidade")
    with f3:
        acoes = ["TODAS"] + sorted([x for x in df["acao"].dropna().astype(str).unique().tolist() if x])
        acao_sel = st.selectbox("Ação", acoes, key="audit_acao")
    with f4:
        periodo_sel = st.selectbox("Período", ["Hoje", "7 dias", "30 dias", "Tudo"], index=1, key="audit_periodo")

    filtrado = df.copy()
    if usuario_sel != "TODOS":
        filtrado = filtrado[filtrado["usuario"].astype(str) == usuario_sel]
    if entidade_sel != "TODAS":
        filtrado = filtrado[filtrado["entidade"].astype(str) == entidade_sel]
    if acao_sel != "TODAS":
        filtrado = filtrado[filtrado["acao"].astype(str) == acao_sel]

    hoje_local = agora_aproar().date()
    dias = {"Hoje": 0, "7 dias": 6, "30 dias": 29}.get(periodo_sel)
    if dias is not None and "data_local" in filtrado.columns:
        inicio = hoje_local - datetime.timedelta(days=dias)
        filtrado = filtrado[filtrado["data_local"].apply(lambda d: bool(d and inicio <= d <= hoje_local))]

    st.caption(f"{len(filtrado)} registro(s) exibido(s) • últimos 500 eventos disponíveis nesta consulta")
    if filtrado.empty:
        st.info("Nenhum registro encontrado com esses filtros.")
        return

    exib = filtrado[["id", "Data/Hora", "usuario", "acao", "entidade", "entidade_id"]].copy()
    exib.columns = ["ID", "Data/Hora", "Usuário", "Ação", "Entidade", "ID do registro"]
    tabela_aproar(exib, key="tbl_auditoria")

    opcoes = []
    mapa = {}
    for _, row in filtrado.head(100).iterrows():
        label = f"#{row['id']} • {row['Data/Hora']} • {row['usuario']} • {row['acao']} • {row['entidade']}"
        opcoes.append(label)
        mapa[label] = row

    if opcoes:
        detalhe_sel = st.selectbox("Ver detalhes de um registro", opcoes, key="audit_detalhe")
        row = mapa[detalhe_sel]
        d1, d2, d3 = st.columns(3)
        d1.write(f"**Antes**\n\n{_auditoria_texto_json(row.get('antes')) or '—'}")
        d2.write(f"**Depois**\n\n{_auditoria_texto_json(row.get('depois')) or '—'}")
        d3.write(f"**Contexto**\n\n{_auditoria_texto_json(row.get('contexto')) or '—'}")


# ============================================================
# ESTABILIDADE / OBSERVABILIDADE
# ============================================================
AMBIENTE_APP = (_secret_opcional("AMBIENTE") or "producao").strip().lower()


def _tabela_erros_disponivel():
    if DB_BACKEND != "NEON" or not hasattr(supabase, "_connect"):
        return False
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass('public.erros_sistema') AS tabela")
                row = cur.fetchone()
                if isinstance(row, dict):
                    return bool(row.get("tabela"))
                return bool(row and row[0])
    except Exception:
        return False


def registrar_erro_sistema(modulo, acao, erro, usuario=None, contexto=None):
    """Registra erro técnico e devolve um código curto para suporte."""
    agora = agora_aproar() if "agora_aproar" in globals() else datetime.datetime.now()
    codigo = f"AP-{agora.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:5].upper()}"
    try:
        if _tabela_erros_disponivel():
            with supabase._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO erros_sistema
                            (codigo, ambiente, modulo, acao, tipo_erro, mensagem, detalhes, usuario, contexto)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                        """,
                        (
                            codigo, AMBIENTE_APP, str(modulo or ""), str(acao or ""),
                            type(erro).__name__, str(erro)[:1200],
                            traceback.format_exc()[-8000:], str(usuario or ""),
                            _json_db(contexto or {}),
                        ),
                    )
                    conn.commit()
    except Exception:
        pass
    return codigo


def exibir_erro_amigavel(modulo, acao, erro, mensagem="Não foi possível concluir esta operação.", usuario=None, contexto=None):
    codigo = registrar_erro_sistema(modulo, acao, erro, usuario=usuario, contexto=contexto)
    st.error(f"{mensagem} Nenhum dado adicional deve ser alterado. Código: {codigo}")
    return codigo


def render_diagnostico_sistema():
    st.markdown("### 🩺 Diagnóstico do sistema")
    d1, d2, d3 = st.columns(3)
    d1.metric("AMBIENTE", AMBIENTE_APP.upper())
    d2.metric("BANCO", DB_BACKEND)
    d3.metric("ESTRUTURA NOVA", "ATIVA" if schema_producao_disponivel() else "INCOMPLETA")

    banco_ok, banco_msg = _testar_banco_ativo() if "_testar_banco_ativo" in globals() else (True, "OK")
    if banco_ok:
        st.success(f"Banco acessível: {banco_msg}")
    else:
        st.error("Banco indisponível no momento.")

    if _tabela_erros_disponivel():
        try:
            with supabase._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT codigo, criado_em, modulo, acao, tipo_erro, usuario, resolvido
                        FROM erros_sistema
                        ORDER BY criado_em DESC
                        LIMIT 20
                        """
                    )
                    rows = cur.fetchall() or []
            if rows:
                st.caption("Últimos erros técnicos registrados")
                tabela_aproar(pd.DataFrame([dict(r) for r in rows]), key="tbl_erros")
            else:
                st.info("Nenhum erro técnico registrado ainda.")
        except Exception:
            st.info("A tabela de erros existe, mas não foi possível consultar o histórico agora.")
    else:
        st.warning("Execute a migração da etapa de estabilidade para ativar o registro de erros.")


def registrar_conflito_estruturado(registro_existente, engenheiro_tentativa, turno_tentativa, unidade_tentativa=""):
    if not schema_producao_disponivel():
        return False
    try:
        obra_original = dict_obras.get(registro_existente.get("obra_id"), {}) if "dict_obras" in globals() else {}
        colab = obter_colaborador_por_id(registro_existente.get("colaborador_id")) if "obter_colaborador_por_id" in globals() else {}
        turno_original = turno_da_convocacao(registro_existente) if "turno_da_convocacao" in globals() else "Integral"
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conflitos_convocacao (
                        colaborador_id, colaborador_nome_snapshot, data,
                        convocacao_existente_id, engenheiro_original, turno_original,
                        unidade_original, engenheiro_tentativa, turno_tentativa,
                        unidade_tentativa, contexto
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        str(registro_existente.get("colaborador_id") or ""),
                        str((colab or {}).get("nome") or ""),
                        str(registro_existente.get("data") or ""),
                        str(registro_existente.get("id") or ""),
                        str(registro_existente.get("engenheiro") or "N/A"),
                        str(turno_original),
                        str(obra_original.get("unidade") or ""),
                        str(engenheiro_tentativa or "N/A"),
                        str(turno_tentativa or "Integral"),
                        str(unidade_tentativa or ""),
                        _json_db({"origem": "app_streamlit"}),
                    ),
                )
                conn.commit()
        registrar_auditoria_prod(
            "convocacao", registro_existente.get("id"), "CONFLITO_CONVOCACAO",
            usuario=engenheiro_tentativa,
            contexto={
                "engenheiro_original": registro_existente.get("engenheiro"),
                "turno_original": turno_original,
                "turno_tentativa": turno_tentativa,
                "data": registro_existente.get("data"),
            },
        )
        return True
    except Exception:
        return False


def resolver_conflitos_estruturados(convocacao_id, resolvido_por="PAULO"):
    if not schema_producao_disponivel():
        return False
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE conflitos_convocacao
                    SET resolvido = TRUE, resolvido_em = NOW(), resolvido_por = %s
                    WHERE convocacao_existente_id = %s AND resolvido = FALSE
                    """,
                    (str(resolvido_por), str(convocacao_id or "")),
                )
                conn.commit()
        return True
    except Exception:
        return False


def listar_indisponibilidades_estruturadas():
    if not schema_producao_disponivel():
        return None
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, colaborador_id, colaborador_nome_snapshot, motivo,
                           inicio, fim, observacao, criado_em, criado_por
                    FROM indisponibilidades
                    WHERE ativo = TRUE
                    ORDER BY inicio DESC, fim DESC
                """)
                rows = cur.fetchall() or []
        saida = []
        for row in rows:
            r = dict(row) if isinstance(row, dict) else {
                "id": row[0], "colaborador_id": row[1], "colaborador_nome_snapshot": row[2],
                "motivo": row[3], "inicio": row[4], "fim": row[5], "observacao": row[6],
                "criado_em": row[7], "criado_por": row[8],
            }
            saida.append({
                "id": r.get("id"),
                "colaborador_id": str(r.get("colaborador_id") or ""),
                "colaborador_nome": str(r.get("colaborador_nome_snapshot") or ""),
                "motivo": r.get("motivo"),
                "inicio": r.get("inicio").isoformat() if hasattr(r.get("inicio"), "isoformat") else str(r.get("inicio") or ""),
                "fim": r.get("fim").isoformat() if hasattr(r.get("fim"), "isoformat") else str(r.get("fim") or ""),
                "observacao": r.get("observacao") or "",
                "criado_em": str(r.get("criado_em") or ""),
                "_origem": "producao",
            })
        return saida
    except Exception:
        return None


def migrar_indisponibilidades_legadas_para_producao():
    """Copia uma vez os registros técnicos antigos sem apagar a origem."""
    if not schema_producao_disponivel() or "obras_todas" not in globals():
        return 0
    migradas = 0
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                for obra in obras_todas:
                    if not eh_registro_indisponibilidade(obra):
                        continue
                    dados = decodificar_indisponibilidade(obra)
                    if not dados:
                        continue
                    cur.execute(
                        """
                        INSERT INTO indisponibilidades (
                            colaborador_id, colaborador_nome_snapshot, motivo, inicio, fim,
                            observacao, criado_em, legacy_origem_id
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (legacy_origem_id) DO NOTHING
                        """,
                        (
                            str(dados.get("colaborador_id") or ""),
                            str(dados.get("colaborador_nome") or ""),
                            str(dados.get("motivo") or "Outro"),
                            str(dados.get("inicio") or ""),
                            str(dados.get("fim") or ""),
                            str(dados.get("observacao") or ""),
                            dados.get("criado_em") or agora_aproar().isoformat(),
                            str(obra.get("id") or ""),
                        ),
                    )
                    migradas += max(0, cur.rowcount or 0)
                conn.commit()
    except Exception:
        return 0
    return migradas


def salvar_indisponibilidade_estruturada(colaborador_id, motivo, inicio, fim, observacao="", criado_por="PAULO"):
    if not schema_producao_disponivel():
        return None
    colab = obter_colaborador_por_id(colaborador_id) if "obter_colaborador_por_id" in globals() else {}
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO indisponibilidades
                        (colaborador_id, colaborador_nome_snapshot, motivo, inicio, fim,
                         observacao, criado_por)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                    """,
                    (
                        str(colaborador_id), str((colab or {}).get("nome") or ""),
                        str(motivo), inicio, fim, str(observacao or ""), str(criado_por),
                    ),
                )
                row = cur.fetchone()
                conn.commit()
        novo_id = row.get("id") if isinstance(row, dict) else (row[0] if row else None)
        registrar_auditoria_prod(
            "indisponibilidade", novo_id, "CRIAR", criado_por,
            depois={"colaborador_id": str(colaborador_id), "motivo": motivo, "inicio": inicio, "fim": fim},
        )
        return True
    except Exception:
        return False


def excluir_indisponibilidade_estruturada(registro_id, usuario="PAULO"):
    if not schema_producao_disponivel():
        return None
    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE indisponibilidades SET ativo = FALSE WHERE id = %s RETURNING *", (registro_id,))
                row = cur.fetchone()
                conn.commit()
        registrar_auditoria_prod("indisponibilidade", registro_id, "DESATIVAR", usuario, antes=dict(row) if isinstance(row, dict) else None)
        return True
    except Exception:
        return False


def salvar_apontamento_estruturado(
    convocacao, data_servico, engenheiro, status, valor_extra, observacao_livre,
    obra_principal_id, periodo_principal, servicos_adicionais=None,
    tipo_diaria=None, custo_pago=None, valor_acordo=0.0,
    valor_adicional_noturno=0.0,
    custo_encargos_base=None,
):
    """Dual-write do apontamento estruturado + dados Financeiro/Controladoria."""
    if not schema_producao_disponivel():
        return False
    try:
        conv_id = str(convocacao.get("id") or "")
        colab_id = str(convocacao.get("colaborador_id") or "")
        obra_principal = dict_obras.get(obra_principal_id, {}) if "dict_obras" in globals() else {}
        unidade_principal = str(obra_principal.get("unidade") or "")
        retroativo = apontamento_esta_atrasado(
            data_servico,
            unidade=unidade_principal,
            agora=agora_aproar(),
        )
        tipo_diaria = normalizar_tipo_diaria(tipo_diaria or tipo_diaria_registro(convocacao))
        if eh_unidade_sebrae(unidade_principal):
            tipo_diaria = "Diária"
        custo_pago = float(custo_pago or 0.0)
        valor_acordo = float(valor_acordo or 0.0)
        valor_adicional_noturno = float(valor_adicional_noturno or 0.0)
        custo_encargos_base = float(custo_encargos_base or 0.0)

        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO apontamentos (
                        convocacao_id, data_servico, colaborador_id, engenheiro, status,
                        valor_extra, observacao, apontado_em, apontado_por, retroativo, atualizado_em,
                        tipo_diaria, custo_pago, valor_acordo, valor_adicional_noturno,
                        custo_encargos_base, custos_separados,
                        migracao_sebrae_noturno_v2
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s,%s,NOW(),%s,%s,%s,%s,%s,TRUE,TRUE)
                    ON CONFLICT (convocacao_id) DO UPDATE SET
                        data_servico = EXCLUDED.data_servico,
                        colaborador_id = EXCLUDED.colaborador_id,
                        engenheiro = EXCLUDED.engenheiro,
                        status = EXCLUDED.status,
                        valor_extra = EXCLUDED.valor_extra,
                        observacao = EXCLUDED.observacao,
                        apontado_por = EXCLUDED.apontado_por,
                        retroativo = EXCLUDED.retroativo,
                        tipo_diaria = EXCLUDED.tipo_diaria,
                        custo_pago = EXCLUDED.custo_pago,
                        valor_acordo = EXCLUDED.valor_acordo,
                        valor_adicional_noturno = EXCLUDED.valor_adicional_noturno,
                        custo_encargos_base = EXCLUDED.custo_encargos_base,
                        custos_separados = TRUE,
                        migracao_sebrae_noturno_v2 = TRUE,
                        atualizado_em = NOW()
                    """,
                    (
                        conv_id, data_servico, colab_id, str(engenheiro), str(status),
                        float(valor_extra or 0), str(observacao_livre or ""), str(engenheiro), retroativo,
                        tipo_diaria, custo_pago, valor_acordo, valor_adicional_noturno,
                        custo_encargos_base,
                    ),
                )

                cur.execute("DELETE FROM servicos_apontamento WHERE convocacao_id = %s", (conv_id,))
                cur.execute(
                    """
                    INSERT INTO servicos_apontamento
                        (convocacao_id, obra_id, obra_nome_snapshot, unidade_snapshot, periodo, principal)
                    VALUES (%s,%s,%s,%s,%s,TRUE)
                    """,
                    (
                        conv_id, str(obra_principal_id or ""), str(obra_principal.get("nome") or ""),
                        str(obra_principal.get("unidade") or ""), str(periodo_principal or ""),
                    ),
                )
                for item in servicos_adicionais or []:
                    nome = str(item.get("servico") or "").strip() if isinstance(item, dict) else str(item or "").strip()
                    if not nome:
                        continue
                    periodo = str(item.get("periodo") or "") if isinstance(item, dict) else ""
                    obra = next((o for o in (obras if "obras" in globals() else []) if normalizar(o.get("nome")) == normalizar(nome)), {})
                    cur.execute(
                        """
                        INSERT INTO servicos_apontamento
                            (convocacao_id, obra_id, obra_nome_snapshot, unidade_snapshot, periodo, principal)
                        VALUES (%s,%s,%s,%s,%s,FALSE)
                        """,
                        (
                            conv_id, str(obra.get("id") or ""), nome,
                            str(obra.get("unidade") or obra_principal.get("unidade") or ""), periodo,
                        ),
                    )
                conn.commit()

        registrar_auditoria_prod(
            "apontamento", conv_id, "SALVAR", engenheiro,
            depois={
                "data_servico": data_servico,
                "status": status,
                "tipo_diaria": tipo_diaria,
                "custo_pago": custo_pago,
                "valor_extra": valor_extra,
                "valor_acordo": valor_acordo,
                "valor_adicional_noturno": valor_adicional_noturno,
                "custo_encargos_base": custo_encargos_base,
                "obra_principal_id": str(obra_principal_id),
                "periodo_principal": periodo_principal,
                "servicos_adicionais": servicos_adicionais or [],
                "retroativo": retroativo,
            },
        )
        return True
    except Exception:
        return False


def separar_observacao_metadata(observacao):
    texto = str(observacao or "")
    if OBS_META_MARKER not in texto:
        return texto.strip(), {}
    base, bruto = texto.split(OBS_META_MARKER, 1)
    try:
        meta = json.loads(bruto.strip()) if bruto.strip() else {}
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        meta = {}
    return base.strip(), meta


def obter_metadata_operacional(observacao):
    return separar_observacao_metadata(observacao)[1]


def decompor_observacao_operacional(observacao):
    """Lê turno/observação livre escondendo os metadados internos de auditoria."""
    texto, _ = separar_observacao_metadata(observacao)
    turno = "Integral"

    m_turno = re.search(r"Turno:\s*(Integral|Manhã|Tarde|Noite)", texto, flags=re.IGNORECASE)
    if m_turno:
        turno_encontrado = m_turno.group(1).lower()
        mapa_turnos = {"integral": "Integral", "manhã": "Manhã", "tarde": "Tarde", "noite": "Noite"}
        turno = mapa_turnos.get(turno_encontrado, "Integral")

    livre = re.sub(r"Turno:\s*(Integral|Manhã|Tarde|Noite)\s*(?:\|\s*)?", "", texto, flags=re.IGNORECASE)
    livre = re.sub(r"HE:\s*[0-9]+(?:[\.,][0-9]+)?\s*h\s*(?:\|\s*)?", "", livre, flags=re.IGNORECASE)
    livre = re.sub(r"^Obs:\s*", "", livre, flags=re.IGNORECASE).strip(" |")
    return turno, livre


def montar_observacao_operacional(turno, observacao_livre="", metadata=None):
    partes = [f"Turno: {turno}"]
    if str(observacao_livre or "").strip():
        partes.append(f"Obs: {str(observacao_livre).strip()}")
    texto = " | ".join(partes)
    if metadata:
        try:
            meta_limpa = {k: v for k, v in dict(metadata).items() if v not in (None, "", [], {})}
            if meta_limpa:
                texto += OBS_META_MARKER + json.dumps(meta_limpa, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            pass
    return texto


def atualizar_metadata_observacao(observacao, **alteracoes):
    turno, livre = decompor_observacao_operacional(observacao)
    meta = obter_metadata_operacional(observacao)
    for chave, valor in alteracoes.items():
        if valor is None:
            meta.pop(chave, None)
        else:
            meta[chave] = valor
    return montar_observacao_operacional(turno, livre, meta)


def normalizar_status_operacional(status):
    """Compatibilidade: registros antigos com status Extra passam a ser presença integral."""
    return "Presente (Integral)" if str(status or "") == "Extra" else str(status or "Presente (Integral)")


def status_eh_presenca(status):
    s = normalizar_status_operacional(status)
    return s in ["Presente (Integral)", "Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada", "Presente"]


def _normalizar_servicos_adicionais(meta):
    """Compatibilidade entre versões, preservando obra, unidade e período."""
    meta = meta or {}
    saida = []
    vistos = set()

    for item in meta.get("servicos_adicionais", []) or []:
        if isinstance(item, dict):
            nome = str(item.get("servico") or "").strip()
            periodo = str(item.get("periodo") or "").strip() or "Não informado"
            obra_id = str(item.get("obra_id") or "").strip()
            unidade = str(item.get("unidade") or "").strip()
        else:
            nome = str(item or "").strip()
            periodo = "Não informado"
            obra_id = ""
            unidade = ""

        chave = obra_id or normalizar(nome)
        if nome and chave not in vistos:
            saida.append({
                "servico": nome,
                "periodo": periodo,
                "obra_id": obra_id,
                "unidade": unidade,
            })
            vistos.add(chave)

    # Registros das versões anteriores continuam válidos.
    for nome in meta.get("servicos_extras", []) or []:
        nome = str(nome or "").strip()
        chave = normalizar(nome)
        if nome and chave not in vistos:
            saida.append({
                "servico": nome,
                "periodo": "Não informado",
                "obra_id": "",
                "unidade": "",
            })
            vistos.add(chave)

    return saida


def descricao_servicos_convocacao(convocacao, obra_primaria=None):
    obra_primaria = obra_primaria or dict_obras.get(convocacao.get("obra_id"), {})
    meta = obter_metadata_operacional(convocacao.get("observacao") or "")
    partes = []

    nome_principal = str(obra_primaria.get("nome") or "").strip()
    periodo_principal = str(meta.get("periodo_servico_principal") or "").strip()
    if nome_principal and not eh_obra_placeholder(obra_primaria):
        partes.append(f"{nome_principal} ({periodo_principal})" if periodo_principal else nome_principal)

    for item in _normalizar_servicos_adicionais(meta):
        nome = item["servico"]
        periodo = item.get("periodo") or ""
        rotulo = f"{nome} ({periodo})" if periodo and periodo != "Não informado" else nome
        if normalizar(nome) != normalizar(nome_principal):
            partes.append(rotulo)

    return " + ".join(partes) if partes else NOME_OBRA_PLACEHOLDER


def registrar_metadata_apontamento(
    convocacao,
    data_servico,
    servicos_extras=None,
    apontado_por=None,
    periodo_principal=None,
    servicos_adicionais=None,
    unidade_servico=None,
):
    meta = obter_metadata_operacional(convocacao.get("observacao") or "")
    agora = agora_aproar()
    if not meta.get("apontado_em"):
        meta["apontado_em"] = agora.isoformat()
    meta["ultimo_apontamento_em"] = agora.isoformat()

    if unidade_servico is None:
        obra_meta = dict_obras.get(
            convocacao.get("obra_id"),
            {},
        )
        unidade_servico = obra_meta.get("unidade") or ""

    meta["apontamento_atrasado"] = apontamento_esta_atrasado(
        data_servico,
        unidade=unidade_servico,
        agora=agora,
    )
    if apontado_por:
        meta["apontado_por"] = str(apontado_por)
    if periodo_principal:
        meta["periodo_servico_principal"] = str(periodo_principal)

    adicionais = []
    for item in servicos_adicionais or []:
        if not isinstance(item, dict):
            continue

        nome = str(item.get("servico") or "").strip()
        periodo = str(item.get("periodo") or "Não informado").strip()
        obra_id = str(item.get("obra_id") or "").strip()
        unidade = str(item.get("unidade") or "").strip()

        if nome:
            adicionais.append({
                "servico": nome,
                "periodo": periodo,
                "obra_id": obra_id,
                "unidade": unidade,
            })

    # Compatibilidade com chamadas antigas.
    if not adicionais and servicos_extras:
        adicionais = [{"servico": str(nome), "periodo": "Não informado"} for nome in servicos_extras if str(nome).strip()]

    meta["servicos_adicionais"] = adicionais
    meta["servicos_extras"] = [x["servico"] for x in adicionais]
    return meta


def rotulo_atraso_apontamento(convocacao):
    meta = obter_metadata_operacional(convocacao.get("observacao") or "")
    if meta.get("apontamento_atrasado"):
        return "🟧 APONTAMENTO RETROATIVO"
    return ""

def formatar_nome_whatsapp(nome):
    """Deixa nomes em formato legível para a mensagem, preservando partículas comuns."""
    nome_fmt = " ".join(str(nome or "").strip().split()).title()
    if not nome_fmt:
        return "Colaborador não identificado"
    minusculas = {"Da", "Das", "De", "Do", "Dos", "E"}
    partes = nome_fmt.split()
    return " ".join(p.lower() if i > 0 and p in minusculas else p for i, p in enumerate(partes))


def formatar_unidade_whatsapp(unidade):
    """Formata a Unidade para o cabeçalho da mensagem do WhatsApp."""
    texto = " ".join(str(unidade or "").strip().split())
    if not texto:
        return "Unidade não identificada"
    siglas = {"FIEC", "SEBRAE", "UNIFOR"}
    if normalizar(texto) in siglas:
        return normalizar(texto)
    titulo = texto.title()
    minusculas = {"Da", "Das", "De", "Do", "Dos", "E"}
    partes = titulo.split()
    return " ".join(p.lower() if i > 0 and p in minusculas else p for i, p in enumerate(partes))


def rotulo_data_whatsapp(data_alvo):
    hoje = datetime.date.today()
    if data_alvo == hoje:
        return f"hoje {data_alvo.strftime('%d/%m')}"
    if data_alvo == hoje + datetime.timedelta(days=1):
        return f"amanhã {data_alvo.strftime('%d/%m')}"
    return f"o dia {data_alvo.strftime('%d/%m')}"


def organizar_convocacoes_whatsapp(convocacoes, mostrar_funcao=False):
    """Agrupa convocações por Unidade e Turno para montar a mensagem pronta para copiar."""
    ordem_turnos = ["Integral", "Manhã", "Tarde", "Noite"]
    agrupado = {}

    for conv in convocacoes or []:
        obra = dict_obras.get(conv.get("obra_id"), {})
        unidade = obra.get("unidade") or "NÃO IDENTIFICADA"
        colab = dict_colaboradores.get(conv.get("colaborador_id"), {})
        nome = formatar_nome_whatsapp(colab.get("nome", ""))
        funcao = str(colab.get("funcao", "") or "").strip()
        turno, _ = decompor_observacao_operacional(conv.get("observacao", ""))

        if mostrar_funcao and funcao:
            funcao_fmt = funcao.replace("AVULSO - ", "").strip().title()
            nome = f"{nome} ({funcao_fmt})"

        agrupado.setdefault(unidade, {}).setdefault(turno, [])
        if nome not in agrupado[unidade][turno]:
            agrupado[unidade][turno].append(nome)

    # Ordena colaboradores alfabeticamente e turnos na sequência operacional.
    saida = {}
    for unidade in sorted(agrupado.keys(), key=lambda x: normalizar(x)):
        saida[unidade] = {}
        for turno in ordem_turnos:
            nomes = agrupado[unidade].get(turno, [])
            if nomes:
                saida[unidade][turno] = sorted(nomes, key=lambda x: normalizar(x))
        # Compatibilidade para algum turno antigo/não previsto.
        for turno, nomes in agrupado[unidade].items():
            if turno not in saida[unidade] and nomes:
                saida[unidade][turno] = sorted(nomes, key=lambda x: normalizar(x))
    return saida


def montar_mensagem_whatsapp(data_alvo, convocacoes, mostrar_funcao=False, aviso_pendentes=False, somente_unidade=None):
    agrupado = organizar_convocacoes_whatsapp(convocacoes, mostrar_funcao=mostrar_funcao)
    if somente_unidade is not None:
        agrupado = {somente_unidade: agrupado.get(somente_unidade, {})} if somente_unidade in agrupado else {}

    linhas = [f"Segue divisão de Equipes para {rotulo_data_whatsapp(data_alvo)}", ""]

    for unidade, turnos in agrupado.items():
        linhas.append(f"*{formatar_unidade_whatsapp(unidade)}*")
        linhas.append("")

        turnos_com_pessoas = [(turno, nomes) for turno, nomes in turnos.items() if nomes]
        exibir_turnos = len(turnos_com_pessoas) > 1 or any(turno != "Integral" for turno, _ in turnos_com_pessoas)

        contador = 1
        for turno, nomes in turnos_com_pessoas:
            if exibir_turnos:
                linhas.append(f"_{turno}_")
            for nome in nomes:
                linhas.append(f"{contador}. {nome}")
                contador += 1
            if exibir_turnos:
                linhas.append("")
        linhas.append("")

    if aviso_pendentes:
        if agrupado:
            linhas.append("As demais demandas serão enviadas pelos respectivos responsáveis.")
        else:
            linhas.append("As demandas serão enviadas pelos respectivos responsáveis.")

    # Remove excesso de linhas vazias no fim sem mexer na separação interna.
    while linhas and not str(linhas[-1]).strip():
        linhas.pop()
    return "\n".join(linhas)

def criar_ou_obter_colaborador_manual(nome, tipo, funcao_livre="", avulso=False):
    """Cria um colaborador digitado pelo engenheiro sem exigir novas colunas no Supabase."""
    nome_limpo = " ".join(str(nome or "").strip().split())
    if not nome_limpo:
        return None, None, "Informe o nome do colaborador."

    try:
        atuais = supabase.table("colaboradores").select("*").execute().data or []
        existente = next(
            (
                c for c in atuais
                if normalizar(c.get("nome", ""))
                == normalizar(nome_limpo)
            ),
            None,
        )

        if existente:
            if existente.get("ativo", True) is False:
                atualizado = (
                    supabase.table("colaboradores")
                    .update({"ativo": True})
                    .eq("id", existente.get("id"))
                    .execute()
                    .data
                    or []
                )
                limpar_cache_operacional()
                if atualizado:
                    existente = atualizado[0]

            return (
                existente.get("id"),
                existente,
                "Cadastro existente localizado e reutilizado.",
            )

        funcao_texto = str(funcao_livre or "").strip()
        if avulso:
            funcao_salva = f"AVULSO - {funcao_texto}" if funcao_texto else f"AVULSO - {str(tipo).upper()}"
        else:
            funcao_salva = funcao_texto if funcao_texto else str(tipo).upper()

        valor = valor_diaria_por_tipo(tipo)
        criado = supabase.table("colaboradores").insert({
            "nome": nome_limpo.upper(),
            "funcao": limpar_funcao(funcao_salva),
            "valor_diaria": valor,
            "categoria_diaria": str(tipo)
        }).execute().data or []

        if criado:
            limpar_cache_operacional()
            return criado[0].get("id"), criado[0], "Novo colaborador cadastrado."
        return None, None, "O cadastro não retornou um identificador."
    except Exception:
        return None, None, "Não foi possível cadastrar o nome informado."

def gerar_excel_colaboradores(lista_colaboradores):
    """Gera uma planilha Excel com a base atual de colaboradores do Supabase."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Colaboradores"

    # Título e metadados
    ws.merge_cells("A1:F1")
    ws["A1"] = "APROAR ENGENHARIA - BASE ATUALIZADA DE COLABORADORES"
    ws["A1"].font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 24

    ws.merge_cells("A2:F2")
    ws["A2"] = f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | Total de colaboradores: {len(lista_colaboradores)}"
    ws["A2"].font = Font(name="Arial", size=9, italic=True, color="64748B")
    ws["A2"].alignment = Alignment(horizontal="left")

    headers = [
        "Nome",
        "Função",
        "Categoria",
        "Valor / Custo Diário (R$)",
        "Local de Moradia",
        "Avulso",
    ]
    linha_header = 4
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=linha_header, column=col_idx, value=header)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    borda = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    ordenados = sorted(lista_colaboradores, key=lambda c: normalizar(c.get("nome", "")))
    for row_idx, colab in enumerate(ordenados, linha_header + 1):
        funcao = str(colab.get("funcao") or "").strip()
        valor_diaria = obter_valor_diaria_colaborador(colab)
        categoria = inferir_tipo_colaborador(funcao)
        avulso = (
            "SIM"
            if normalizar(funcao).startswith("AVULSO -")
            else "NÃO"
        )

        valores = [
            str(colab.get("nome") or "").strip(),
            funcao,
            categoria,
            valor_diaria,
            str(colab.get("local_moradia") or "Não informado"),
            avulso,
        ]
        for col_idx, valor in enumerate(valores, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=valor)
            cell.font = Font(name="Arial", size=9)
            cell.border = borda
            cell.alignment = Alignment(vertical="center", horizontal="left" if col_idx in [1, 2, 5] else "center")
            if col_idx == 4:
                cell.number_format = 'R$ #,##0.00'
                cell.alignment = Alignment(horizontal="right", vertical="center")

    fim = linha_header + len(ordenados)
    if fim >= linha_header:
        ws.auto_filter.ref = f"A{linha_header}:F{fim}"
    ws.freeze_panes = "A5"

    larguras = {"A": 38, "B": 30, "C": 16, "D": 24, "E": 20, "F": 12}
    for coluna, largura in larguras.items():
        ws.column_dimensions[coluna].width = largura

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()

def buscar_convocacao_existente(colaborador_id, data_convocacao):
    """Retorna todas as alocações do colaborador naquela data."""
    try:
        return (
            supabase.table("convocacoes")
            .select("*")
            .eq("colaborador_id", colaborador_id)
            .eq("data", data_convocacao.isoformat())
            .execute().data or []
        )
    except Exception:
        return []


def normalizar_turno_convocacao(turno):
    """Padroniza os turnos usados na regra de conflito."""
    t = normalizar(turno or "Integral")
    mapa = {
        "INTEGRAL": "Integral",
        "MANHA": "Manhã",
        "TARDE": "Tarde",
        "NOITE": "Noite",
    }
    return mapa.get(t, "Integral")


def turno_da_convocacao(registro):
    """Prefere a coluna de produção e mantém compatibilidade com a observação legada."""
    turno_coluna = str((registro or {}).get("turno") or "").strip()
    if turno_coluna:
        return normalizar_turno_convocacao(turno_coluna)
    try:
        turno, _ = decompor_observacao_operacional((registro or {}).get("observacao") or "")
    except Exception:
        turno = "Integral"
    return normalizar_turno_convocacao(turno)


def turnos_se_sobrepoem(turno_a, turno_b):
    """
    Regra operacional:
    - Integral ocupa o dia inteiro e conflita com qualquer turno.
    - Manhã conflita com Manhã/Integral.
    - Tarde conflita com Tarde/Integral.
    - Noite conflita com Noite/Integral.
    - Turnos específicos diferentes podem coexistir no mesmo dia.
    """
    a = normalizar_turno_convocacao(turno_a)
    b = normalizar_turno_convocacao(turno_b)
    if "Integral" in (a, b):
        return True
    return a == b


def _garantir_multiturno_neon():
    """
    No Neon, remove uma eventual restrição UNIQUE antiga em
    (colaborador_id, data), pois agora o mesmo colaborador pode ter
    duas alocações na mesma data desde que os turnos não se sobreponham.

    A validação de sobreposição continua sendo feita pela aplicação.
    """
    if DB_BACKEND != "NEON" or not hasattr(supabase, "_connect"):
        return True

    if st.session_state.get("_schema_multiturno_ok"):
        return True

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                # Remove constraints UNIQUE exatamente em colaborador_id + data.
                cur.execute("""
                    SELECT con.conname,
                           array_agg(att.attname ORDER BY u.ord) AS cols
                    FROM pg_constraint con
                    JOIN unnest(con.conkey) WITH ORDINALITY AS u(attnum, ord) ON TRUE
                    JOIN pg_attribute att
                      ON att.attrelid = con.conrelid
                     AND att.attnum = u.attnum
                    WHERE con.conrelid = 'convocacoes'::regclass
                      AND con.contype = 'u'
                    GROUP BY con.conname
                """)
                for row in cur.fetchall() or []:
                    if isinstance(row, dict):
                        nome_constraint = row.get("conname")
                        cols = list(row.get("cols") or [])
                    else:
                        nome_constraint, cols = row
                        cols = list(cols or [])
                    if len(cols) == 2 and set(cols) == {"colaborador_id", "data"}:
                        cur.execute(f'ALTER TABLE convocacoes DROP CONSTRAINT IF EXISTS "{nome_constraint}"')

                # Remove índice UNIQUE direto equivalente, mas somente quando
                # ele NÃO pertence a uma constraint (as constraints já foram tratadas acima).
                cur.execute("""
                    SELECT i.relname AS indexname,
                           pg_get_indexdef(i.oid) AS indexdef
                    FROM pg_class t
                    JOIN pg_index ix ON t.oid = ix.indrelid
                    JOIN pg_class i ON i.oid = ix.indexrelid
                    LEFT JOIN pg_constraint con ON con.conindid = i.oid
                    WHERE t.relname = 'convocacoes'
                      AND ix.indisunique = TRUE
                      AND con.oid IS NULL
                """)
                for row in cur.fetchall() or []:
                    if isinstance(row, dict):
                        idx_name = str(row.get("indexname") or "")
                        idx_def = str(row.get("indexdef") or "")
                    else:
                        idx_name, idx_def = str(row[0] or ""), str(row[1] or "")
                    idx_upper = idx_def.upper()
                    if (
                        "COLABORADOR_ID" in idx_upper
                        and "DATA" in idx_upper
                        and "OBSERVACAO" not in idx_upper
                        and not idx_name.endswith("_pkey")
                    ):
                        cur.execute(f'DROP INDEX IF EXISTS "{idx_name}"')

                conn.commit()

        st.session_state["_schema_multiturno_ok"] = True
        return True
    except Exception as e:
        st.session_state["_schema_multiturno_erro"] = f"{type(e).__name__}: {str(e)[:250]}"
        return False


def registrar_conflito_convocacao(
    registro_existente,
    engenheiro_tentativa,
    turno_tentativa=None,
    unidade_tentativa=None,
):
    """Persiste somente conflitos de turnos sobrepostos para o Paulo/Admin."""
    try:
        obs_atual = registro_existente.get("observacao") or ""
        meta = obter_metadata_operacional(obs_atual)
        conflitos = list(meta.get("conflitos_convocacao") or [])
        colab_id = registro_existente.get("colaborador_id")
        colab = obter_colaborador_por_id(colab_id) if "obter_colaborador_por_id" in globals() else {}
        turno_original = turno_da_convocacao(registro_existente)
        conflitos.append({
            "tentativa_por": str(engenheiro_tentativa or "N/A"),
            "engenheiro_original": str(registro_existente.get("engenheiro") or "N/A"),
            "colaborador_id": str(colab_id or ""),
            "colaborador_nome": str((colab or {}).get("nome") or ""),
            "data_convocacao": str(registro_existente.get("data") or ""),
            "turno_original": turno_original,
            "turno_tentativa": normalizar_turno_convocacao(turno_tentativa),
            "unidade_tentativa": str(unidade_tentativa or ""),
            "em": agora_aproar().isoformat(),
            "resolvido": False,
            "paulo_pendente": True,
        })
        meta["conflitos_convocacao"] = conflitos[-30:]
        meta["tem_conflito_pendente"] = True
        # Fase 1: também grava em tabela própria quando a estrutura nova está ativa.
        registrar_conflito_estruturado(
            registro_existente,
            engenheiro_tentativa,
            normalizar_turno_convocacao(turno_tentativa),
            unidade_tentativa or "",
        )
        turno, livre = decompor_observacao_operacional(obs_atual)
        nova_obs = montar_observacao_operacional(turno, livre, meta)
        supabase.table("convocacoes").update({"observacao": nova_obs}).eq("id", registro_existente.get("id")).execute()
        limpar_cache_operacional()
        return True
    except Exception:
        return False


def resolver_conflitos_convocacao(registro):
    try:
        obs_atual = registro.get("observacao") or ""
        meta = obter_metadata_operacional(obs_atual)
        conflitos = list(meta.get("conflitos_convocacao") or [])
        for conflito in conflitos:
            if not conflito.get("resolvido"):
                conflito["resolvido"] = True
                conflito["paulo_pendente"] = False
                conflito["resolvido_em"] = agora_aproar().isoformat()
        meta["conflitos_convocacao"] = conflitos
        meta["tem_conflito_pendente"] = any(not c.get("resolvido") for c in conflitos)
        turno, livre = decompor_observacao_operacional(obs_atual)
        supabase.table("convocacoes").update({
            "observacao": montar_observacao_operacional(turno, livre, meta)
        }).eq("id", registro.get("id")).execute()
        resolver_conflitos_estruturados(registro.get("id"), "PAULO")
        registrar_auditoria_prod("convocacao", registro.get("id"), "RESOLVER_CONFLITO", "PAULO")
        limpar_cache_operacional()
        return True
    except Exception:
        return False


def listar_conflitos_convocacao_pendentes(dias=90):
    """Retorna a fila de conflitos ainda não tratados pelo Paulo/Admin."""
    try:
        inicio = (datetime.date.today() - datetime.timedelta(days=int(dias))).isoformat()
        registros = supabase.table("convocacoes").select("*").gte("data", inicio).execute().data or []
    except Exception:
        registros = []

    saida = []
    for reg in registros:
        meta = obter_metadata_operacional(reg.get("observacao") or "")
        pendentes = [c for c in (meta.get("conflitos_convocacao") or []) if not c.get("resolvido")]
        if pendentes:
            saida.append((reg, pendentes))
    return saida


def inserir_convocacao_segura(obra_id, colaborador_id, data_convocacao, engenheiro, turno):
    """
    Bloqueia apenas indisponibilidade ou sobreposição real de turno.

    Exemplos:
    - Neto / Manhã + Gustavo / Tarde -> permitido.
    - Neto / Manhã + Gustavo / Manhã -> conflito.
    - Neto / Manhã + Gustavo / Integral -> conflito.
    - Neto / Integral + Gustavo / Tarde -> conflito.
    """
    indisp = (
        obter_indisponibilidade_colaborador(colaborador_id, data_convocacao)
        if "obter_indisponibilidade_colaborador" in globals()
        else None
    )
    if indisp:
        return False, (
            f"está indisponível ({indisp.get('motivo', 'Indisponível')}) de "
            f"{indisp.get('inicio', '')} a {indisp.get('fim', '')}"
        )

    turno_tentativa = normalizar_turno_convocacao(turno)
    existentes = buscar_convocacao_existente(colaborador_id, data_convocacao)

    conflitos_outro_eng = []
    duplicidades_mesmo_eng = []

    for reg in existentes:
        turno_existente = turno_da_convocacao(reg)
        if not turnos_se_sobrepoem(turno_existente, turno_tentativa):
            # Ex.: já está de manhã, mas a nova convocação é à tarde.
            continue

        eng_atual = str(reg.get("engenheiro") or "N/A")
        if normalizar(eng_atual) == normalizar(engenheiro):
            duplicidades_mesmo_eng.append((reg, turno_existente))
        else:
            conflitos_outro_eng.append((reg, turno_existente, eng_atual))

    # Se houver conflito com outro supervisor, bloqueia e manda para o Paulo.
    if conflitos_outro_eng:
        mensagens = []
        obra_tentativa = dict_obras.get(obra_id, {}) if "dict_obras" in globals() else {}
        unidade_tentativa = obra_tentativa.get("unidade", "")

        for reg, turno_existente, eng_atual in conflitos_outro_eng:
            registrado = registrar_conflito_convocacao(
                reg,
                engenheiro,
                turno_tentativa=turno_tentativa,
                unidade_tentativa=unidade_tentativa,
            )
            complemento = " O conflito foi registrado para conferência do Paulo." if registrado else ""
            mensagens.append(
                f"já foi convocado(a) por {eng_atual} no turno {turno_existente}; "
                f"a tentativa em {turno_tentativa} se sobrepõe.{complemento}"
            )

        return False, " ".join(mensagens)

    # Mesmo engenheiro também não deve duplicar um turno que se sobrepõe.
    if duplicidades_mesmo_eng:
        turnos_existentes = ", ".join(sorted({t for _, t in duplicidades_mesmo_eng}))
        return False, (
            f"já estava convocado(a) por você em turno que se sobrepõe "
            f"({turnos_existentes})"
        )

    # Se chegou aqui, pode haver outro registro na mesma data, mas em turno compatível.
    # No Neon removemos a restrição antiga por data, caso ela exista.
    _garantir_multiturno_neon()

    agora = agora_aproar()
    meta = {
        "convocado_em": agora.isoformat(),
        "convocado_por": str(engenheiro),
        "convocacao_atrasada": bool(
            agora.hour >= 16 and data_convocacao == proximo_dia_util(agora.date())
        ),
    }

    try:
        payload_conv = {
            "obra_id": obra_id,
            "colaborador_id": colaborador_id,
            "data": data_convocacao.isoformat(),
            "engenheiro": engenheiro,
            "status": "Presente (Integral)",
            "valor_extra": 0,
            "observacao": montar_observacao_operacional(turno_tentativa, "", meta)
        }
        if schema_producao_disponivel():
            payload_conv.update({
                "turno": turno_tentativa,
                "criado_em": agora.isoformat(),
                "criado_por": str(engenheiro),
            })
        retorno_conv = supabase.table("convocacoes").insert(payload_conv).execute().data or []
        novo_id = (retorno_conv[0].get("id") if retorno_conv else "")
        registrar_auditoria_prod(
            "convocacao", novo_id, "CRIAR", engenheiro,
            depois={
                "colaborador_id": str(colaborador_id), "data": data_convocacao,
                "turno": turno_tentativa, "obra_id": str(obra_id),
            },
        )
        limpar_cache_operacional()
        return True, f"convocado(a) com sucesso no turno {turno_tentativa}"

    except Exception as e:
        detalhe = str(e)
        if DB_BACKEND == "NEON" and "unique" in detalhe.lower():
            erro_schema = st.session_state.get("_schema_multiturno_erro", "")
            complemento = f" Diagnóstico: {erro_schema}" if erro_schema else ""
            return False, (
                "o turno é compatível, mas o banco ainda está restringindo duas alocações "
                f"na mesma data.{complemento}"
            )
        return False, "não pôde ser convocado(a); verifique os dados e tente novamente"



def inserir_convocacoes_lote_mobile(
    obra_id,
    pessoas,
    data_convocacao,
    engenheiro,
    turno,
    existentes_data=None,
    indisponiveis_map=None,
):
    """
    Versão otimizada para o portal ?eng.

    - Reaproveita convocações/indisponibilidades já carregadas na tela.
    - Valida conflito em memória.
    - Insere todos os colaboradores aptos em uma única operação de banco.
    - Mantém o registro de conflito para o Paulo.
    """
    turno_tentativa = normalizar_turno_convocacao(turno)
    existentes_data = list(existentes_data or [])
    indisponiveis_map = dict(indisponiveis_map or {})

    existentes_por_colab = {}
    for reg in existentes_data:
        cid_reg = str(reg.get("colaborador_id") or "").strip()
        if cid_reg:
            existentes_por_colab.setdefault(cid_reg, []).append(reg)

    aptos = []
    avisos = []

    obra_tentativa = dict_obras.get(obra_id, {}) if "dict_obras" in globals() else {}
    unidade_tentativa = str(obra_tentativa.get("unidade") or "")

    for colaborador_id, nome_pessoa in pessoas:
        cid = str(colaborador_id or "").strip()
        if not cid:
            avisos.append(f"{nome_pessoa}: colaborador inválido.")
            continue

        indisp = indisponiveis_map.get(cid)
        if indisp:
            avisos.append(
                f"{nome_pessoa}: indisponível "
                f"({indisp.get('motivo','Indisponível')}) de "
                f"{indisp.get('inicio','')} a {indisp.get('fim','')}."
            )
            continue

        conflitos_outro_eng = []
        duplicidades_mesmo_eng = []

        for reg in existentes_por_colab.get(cid, []):
            turno_existente = turno_da_convocacao(reg)
            if not turnos_se_sobrepoem(turno_existente, turno_tentativa):
                continue

            eng_atual = str(reg.get("engenheiro") or "N/A")
            if normalizar(eng_atual) == normalizar(engenheiro):
                duplicidades_mesmo_eng.append((reg, turno_existente))
            else:
                conflitos_outro_eng.append((reg, turno_existente, eng_atual))

        if conflitos_outro_eng:
            mensagens = []
            for reg, turno_existente, eng_atual in conflitos_outro_eng:
                registrado = registrar_conflito_convocacao(
                    reg,
                    engenheiro,
                    turno_tentativa=turno_tentativa,
                    unidade_tentativa=unidade_tentativa,
                )
                complemento = (
                    " O conflito foi registrado para conferência do Paulo."
                    if registrado else ""
                )
                mensagens.append(
                    f"já está com {eng_atual} no turno {turno_existente}; "
                    f"{turno_tentativa} se sobrepõe.{complemento}"
                )

            avisos.append(f"{nome_pessoa}: " + " ".join(mensagens))
            continue

        if duplicidades_mesmo_eng:
            turnos_existentes = ", ".join(
                sorted({t for _, t in duplicidades_mesmo_eng})
            )
            avisos.append(
                f"{nome_pessoa}: já está na sua equipe em turno que se sobrepõe "
                f"({turnos_existentes})."
            )
            continue

        aptos.append((colaborador_id, nome_pessoa))

    if not aptos:
        return 0, avisos

    _garantir_multiturno_neon()

    agora = agora_aproar()
    payloads = []
    for colaborador_id, _nome_pessoa in aptos:
        meta = {
            "convocado_em": agora.isoformat(),
            "convocado_por": str(engenheiro),
            "convocacao_atrasada": bool(
                agora.hour >= 16
                and data_convocacao == proximo_dia_util(agora.date())
            ),
        }

        payload = {
            "obra_id": obra_id,
            "colaborador_id": colaborador_id,
            "data": data_convocacao.isoformat(),
            "engenheiro": engenheiro,
            "status": "Presente (Integral)",
            "valor_extra": 0,
            "observacao": montar_observacao_operacional(
                turno_tentativa, "", meta
            ),
        }

        if schema_producao_disponivel():
            payload.update({
                "turno": turno_tentativa,
                "criado_em": agora.isoformat(),
                "criado_por": str(engenheiro),
            })

        payloads.append(payload)

    try:
        # _PostgresCompat trata uma lista inteira dentro da mesma conexão.
        retorno = (
            supabase.table("convocacoes")
            .insert(payloads)
            .execute()
            .data
            or []
        )

        quantidade = len(retorno) if retorno else len(payloads)

        # Auditoria em uma única conexão para não transformar 10 pessoas
        # em 10 novas conexões só para o histórico.
        if (
            retorno
            and DB_BACKEND == "NEON"
            and schema_producao_disponivel()
            and hasattr(supabase, "_connect")
        ):
            try:
                with supabase._connect() as conn:
                    with conn.cursor() as cur:
                        for reg in retorno:
                            cur.execute(
                                """
                                INSERT INTO auditoria
                                    (entidade, entidade_id, acao, usuario, antes, depois, contexto)
                                VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
                                """,
                                (
                                    "convocacao",
                                    str(reg.get("id") or ""),
                                    "CRIAR",
                                    str(engenheiro),
                                    None,
                                    _json_db({
                                        "colaborador_id": str(reg.get("colaborador_id") or ""),
                                        "data": data_convocacao,
                                        "turno": turno_tentativa,
                                        "obra_id": str(obra_id),
                                    }),
                                    _json_db({"origem": "portal_engenheiro_lote"}),
                                ),
                            )
                        conn.commit()
            except Exception:
                pass

        limpar_cache_convocacoes()
        return quantidade, avisos

    except Exception:
        # Fallback seguro: se o banco recusar o lote por alguma condição
        # concorrente, volta para a validação individual já existente.
        sucessos = 0
        avisos_fallback = list(avisos)

        for colaborador_id, nome_pessoa in aptos:
            ok, motivo = inserir_convocacao_segura(
                obra_id,
                colaborador_id,
                data_convocacao,
                engenheiro,
                turno_tentativa,
            )
            if ok:
                sucessos += 1
            else:
                avisos_fallback.append(f"{nome_pessoa}: {motivo}")

        return sucessos, avisos_fallback


# --- ACESSO RESILIENTE AO BANCO ---
def _cliente_supabase_para_tentativa(tentativa=0):
    """
    Retorna um cliente novo para retry.
    O nome da função foi preservado para compatibilidade interna.
    """
    if DB_BACKEND == "NEON":
        return _PostgresCompat(DATABASE_URL)

    if tentativa == 0:
        return supabase

    url = _secret_opcional("SUPABASE_URL")
    key = _secret_opcional("SUPABASE_KEY") or _secret_opcional("SUPABASE_ANON_KEY")
    if not url or not key:
        try:
            bloco_supabase = st.secrets.get("supabase", {})
            url = url or str(bloco_supabase.get("url", "") or bloco_supabase.get("SUPABASE_URL", "")).strip()
            key = key or str(bloco_supabase.get("key", "") or bloco_supabase.get("anon_key", "") or bloco_supabase.get("SUPABASE_KEY", "")).strip()
        except Exception:
            pass
    return create_client(url, key)


def _executar_supabase_com_retry(operacao, tentativas=3):
    ultimo_erro = None

    for tentativa in range(tentativas):
        try:
            cliente = _cliente_supabase_para_tentativa(tentativa)
            return operacao(cliente)
        except Exception as e:
            ultimo_erro = e
            try:
                st.cache_resource.clear()
            except Exception:
                pass

            if tentativa < tentativas - 1:
                time.sleep(1.0 * (tentativa + 1))

    raise ultimo_erro


def _listar_obras_resiliente():
    resposta = _executar_supabase_com_retry(
        lambda db: db.table("obras").select("id,nome,unidade").execute(),
        tentativas=3
    )
    return resposta.data or [], DB_BACKEND.lower()


def _obra_existe_no_supabase(nome_obra, tentativas=2):
    resposta = _executar_supabase_com_retry(
        lambda db: (
            db.table("obras")
            .select("id,nome")
            .eq("nome", nome_obra)
            .limit(1)
            .execute()
        ),
        tentativas=tentativas
    )
    return bool(resposta.data or [])


def _inserir_obra_resiliente(nome_obra, unidade, tentativas=3):
    ultimo_erro = None

    for tentativa in range(tentativas):
        try:
            if _obra_existe_no_supabase(nome_obra, tentativas=1):
                return True, "existente"
        except Exception as e:
            ultimo_erro = e

        try:
            cliente = _cliente_supabase_para_tentativa(tentativa)
            (
                cliente.table("obras")
                .insert({
                    "unidade": unidade,
                    "nome": nome_obra
                })
                .execute()
            )
            return True, "inserida"

        except Exception as e:
            ultimo_erro = e

            try:
                if _obra_existe_no_supabase(nome_obra, tentativas=1):
                    return True, "inserida"
            except Exception:
                pass

            if tentativa < tentativas - 1:
                time.sleep(1.2 * (tentativa + 1))

    try:
        st.session_state["banco_ultimo_erro_sync"] = (
            f"{type(ultimo_erro).__name__}: {str(ultimo_erro)[:220]}"
        )
    except Exception:
        pass

    return False, "erro"


def _testar_banco_ativo():
    try:
        resposta = _executar_supabase_com_retry(
            lambda db: db.table("obras").select("id").limit(1).execute(),
            tentativas=2
        )
        return True, f"{DB_BACKEND} OK"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:220]}"


# --- SINCRONIZAÇÃO COM TRELLO (MÊS VIGENTE OU SELEÇÃO MANUAL) ---
TRELLO_JSON_URL = "https://trello.com/b/TX8hGvmI.json"


def _garantir_tabela_snapshot_trello():
    """
    Cria uma tabela minúscula no Neon para guardar a última leitura válida
    do quadro público. Isso permite o sistema continuar sincronizando mesmo
    se o Trello estiver temporariamente lento/fora do ar.
    """
    if DB_BACKEND != "NEON" or not hasattr(supabase, "_connect"):
        return False

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trello_snapshot (
                        snapshot_id INTEGER PRIMARY KEY,
                        listas JSONB NOT NULL,
                        cards JSONB NOT NULL,
                        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                conn.commit()
        return True
    except Exception:
        return False


def _salvar_snapshot_trello(listas, cards):
    if not _garantir_tabela_snapshot_trello():
        return

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO trello_snapshot
                        (snapshot_id, listas, cards, atualizado_em)
                    VALUES
                        (1, %s::jsonb, %s::jsonb, NOW())
                    ON CONFLICT (snapshot_id)
                    DO UPDATE SET
                        listas = EXCLUDED.listas,
                        cards = EXCLUDED.cards,
                        atualizado_em = NOW()
                    """,
                    (
                        json.dumps(listas, ensure_ascii=False),
                        json.dumps(cards, ensure_ascii=False),
                    )
                )
                conn.commit()
    except Exception:
        pass


def _carregar_snapshot_trello():
    if not _garantir_tabela_snapshot_trello():
        return [], [], None

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT listas, cards, atualizado_em
                    FROM trello_snapshot
                    WHERE snapshot_id = 1
                    LIMIT 1
                    """
                )
                linha = cur.fetchone()

        if not linha:
            return [], [], None

        if isinstance(linha, dict):
            listas = linha.get("listas") or []
            cards = linha.get("cards") or []
            atualizado_em = linha.get("atualizado_em")
        else:
            listas, cards, atualizado_em = linha

        if isinstance(listas, list) and isinstance(cards, list):
            return listas, cards, atualizado_em

    except Exception:
        pass

    return [], [], None


@st.cache_data(ttl=300, show_spinner=False)
def _baixar_trello_publico():
    """
    Leitura pública do mesmo .json usado pela Torre de Controle.
    Sem API Key, Token ou autenticação.
    Faz uma segunda tentativa somente quando necessário.
    """
    ultimo_erro = None

    for tentativa in range(2):
        try:
            # Timeout separado: conexão rápida, mas tolerância maior para leitura
            # do JSON completo quando o Trello estiver mais lento.
            timeout_leitura = 35 if tentativa == 0 else 65

            resposta = requests.get(
                TRELLO_JSON_URL,
                timeout=(8, timeout_leitura)
            )
            resposta.raise_for_status()

            dados = resposta.json()

            if (
                not isinstance(dados, dict)
                or not isinstance(dados.get("cards"), list)
                or not isinstance(dados.get("lists"), list)
            ):
                raise ValueError(
                    "O JSON público respondeu sem as listas/cards esperados."
                )

            return dados.get("lists", []), dados.get("cards", [])

        except Exception as e:
            ultimo_erro = e

            if tentativa == 0:
                time.sleep(1.2)

    raise ultimo_erro


def obter_listas_trello():
    """
    Ordem de prioridade:
      1. Trello público ao vivo / cache de 5 minutos;
      2. última leitura válida da sessão;
      3. último snapshot persistido no Neon.

    O sistema não fica inutilizável por um timeout momentâneo do Trello.
    """
    try:
        listas, cards = _baixar_trello_publico()

        if isinstance(listas, list) and isinstance(cards, list):
            st.session_state["trello_snapshot_sessao"] = {
                "listas": listas,
                "cards": cards,
            }
            st.session_state["trello_ultimo_erro"] = ""
            st.session_state["trello_fonte"] = "Trello público"
            st.session_state["trello_usando_snapshot"] = False

            # Persistência de contingência; falha silenciosa não afeta o app.
            _salvar_snapshot_trello(listas, cards)

            return listas, cards

    except Exception as e:
        st.session_state["trello_ultimo_erro"] = (
            f"{type(e).__name__}: {str(e)[:300]}"
        )

    # Fallback 1: última leitura desta sessão
    snapshot_sessao = st.session_state.get("trello_snapshot_sessao") or {}
    listas_sessao = snapshot_sessao.get("listas") or []
    cards_sessao = snapshot_sessao.get("cards") or []

    if listas_sessao or cards_sessao:
        st.session_state["trello_fonte"] = "Última leitura válida"
        st.session_state["trello_usando_snapshot"] = True
        return listas_sessao, cards_sessao

    # Fallback 2: snapshot persistente do Neon
    listas_db, cards_db, atualizado_em = _carregar_snapshot_trello()

    if listas_db or cards_db:
        st.session_state["trello_snapshot_sessao"] = {
            "listas": listas_db,
            "cards": cards_db,
        }
        st.session_state["trello_fonte"] = "Última leitura salva"
        st.session_state["trello_usando_snapshot"] = True
        st.session_state["trello_snapshot_data"] = atualizado_em
        return listas_db, cards_db

    st.session_state["trello_fonte"] = ""
    st.session_state["trello_usando_snapshot"] = False
    return [], []


def executar_sincronizacao_trello(id_lista_target=None, id_card_target=None, listas_precarregadas=None, cards_precarregados=None):
    """
    Sincroniza cards/listas do Trello com a tabela 'obras'.

    Sincroniza o Trello público com o banco ativo (Neon/PostgreSQL).
    A leitura do Trello é sempre renovada ao executar uma sincronização.
    """
    try:
        # A tela de Configurações já leu o Trello para montar os dropdowns.
        # Reutilizamos exatamente esse payload no clique do botão, evitando
        # uma segunda requisição que era a causa do ReadTimeout.
        if listas_precarregadas is not None and cards_precarregados is not None:
            lists = list(listas_precarregadas)
            cards = list(cards_precarregados)
        else:
            lists, cards = obter_listas_trello()
        if not lists and not cards:
            detalhe = ""
            try:
                detalhe = st.session_state.get("trello_ultimo_erro", "")
            except Exception:
                pass

            msg = (
                "Não foi possível obter uma leitura válida do quadro ORÇAMENTOS agora. "
                "O restante do sistema continua funcionando normalmente."
            )
            return False, msg

        nome_alvo = ""
        cards_execucao = []

        # Busca manual de um card específico (útil para medições retroativas)
        if id_card_target:
            card_alvo = next((c for c in cards if c.get("id") == id_card_target), None)
            if not card_alvo:
                return False, "Card selecionado não foi encontrado no Trello."

            cards_execucao = [card_alvo]
            nome_alvo = f"Card: {card_alvo.get('name', 'Sem nome')}"

        else:
            id_lista_execucao = id_lista_target
            nome_lista_alvo = ""

            # Sem seleção manual: procura primeiro a medição do mês vigente.
            if not id_lista_execucao:
                hoje = datetime.date.today()
                mes_vigente = MESES_PT.get(hoje.month, "")
                ano_vigente = str(hoje.year)
                termo_busca = f"MEDICAO {mes_vigente} {ano_vigente}"

                lista_mes = next(
                    (lst for lst in lists if termo_busca in normalizar(lst.get("name", ""))),
                    None
                )
                lista_fallback = next(
                    (lst for lst in lists if "EM EXECUCAO" in normalizar(lst.get("name", ""))),
                    None
                )
                lista_alvo = lista_mes or lista_fallback

                if lista_alvo:
                    id_lista_execucao = lista_alvo.get("id")
                    nome_lista_alvo = lista_alvo.get("name", "")
            else:
                lista_alvo = next(
                    (lst for lst in lists if lst.get("id") == id_lista_execucao),
                    None
                )
                if lista_alvo:
                    nome_lista_alvo = lista_alvo.get("name", "")

            if not id_lista_execucao:
                return False, "Nenhuma lista do mês vigente ou de execução foi encontrada no Trello."

            cards_execucao = [
                c for c in cards
                if c.get("idList") == id_lista_execucao and not c.get("closed", False)
            ]
            nome_alvo = f"Lista: {nome_lista_alvo}"

        # IMPORTANTE:
        # Não usamos buscar_obras() aqui, pois essa função geral retorna [] quando há
        # falha de conexão. Durante uma sincronização isso poderia parecer "banco vazio"
        # e fazer o sistema tentar reinserir todas as obras.
        try:
            resposta_obras = _executar_supabase_com_retry(
                lambda sb: sb.table("obras").select("id,nome,unidade").execute(),
                tentativas=3
            )
            obras_atuais = resposta_obras.data or []
        except Exception as e:
            try:
                st.session_state["supabase_ultimo_erro_sync"] = (
                    f"{type(e).__name__}: {str(e)[:220]}"
                )
            except Exception:
                pass

            return False, (
                "Não foi possível conectar ao banco de dados agora. "
                "Nenhuma obra foi alterada. Aguarde alguns segundos e tente sincronizar novamente."
            )

        nomes_cadastrados = {
            normalizar(o.get("nome", ""))
            for o in obras_atuais
            if o.get("nome")
        }

        novas_inseridas = 0
        ja_existentes = 0
        falhas = []

        for card in cards_execucao:
            nome_card = str(card.get("name", "") or "").strip()
            if not nome_card:
                continue

            nome_norm = normalizar(nome_card)
            unidade_card = identificar_unidade(nome_card)

            if nome_norm in nomes_cadastrados:
                ja_existentes += 1
                continue

            ok, situacao = _inserir_obra_resiliente(
                nome_obra=nome_card,
                unidade=unidade_card,
                tentativas=3
            )

            if not ok:
                falhas.append(nome_card)
                continue

            nomes_cadastrados.add(nome_norm)

            if situacao == "inserida":
                novas_inseridas += 1
            else:
                # Pode ter sido criada em uma tentativa anterior cuja resposta se perdeu,
                # ou já existir no banco apesar do snapshot inicial.
                ja_existentes += 1

        limpar_cache_operacional()

        if falhas:
            return False, (
                f"Sincronização de {nome_alvo} concluída parcialmente: "
                f"{novas_inseridas} nova(s) obra(s) adicionada(s), "
                f"{ja_existentes} já existente(s) e "
                f"{len(falhas)} item(ns) não puderam ser confirmados no banco. "
                "Tente sincronizar novamente em alguns segundos."
            )

        return True, (
            f"Sincronização de {nome_alvo} concluída: "
            f"{novas_inseridas} nova(s) obra(s) adicionada(s) e "
            f"{ja_existentes} já existente(s)."
        )

    except Exception as e:
        # Última barreira: nenhum erro da sincronização deve abrir o traceback vermelho.
        try:
            st.session_state["supabase_ultimo_erro_sync"] = (
                f"{type(e).__name__}: {str(e)[:220]}"
            )
        except Exception:
            pass

        return False, (
            "Não foi possível concluir a sincronização agora. "
            "O sistema continua funcionando com os dados já cadastrados. "
            "Aguarde alguns segundos e tente novamente."
        )


# --- BUSCA DE DADOS COM CACHE ---
@st.cache_data(ttl=180, show_spinner=False)
def buscar_obras():
    try: return supabase.table("obras").select("*").execute().data
    except Exception: return []

@st.cache_data(ttl=180, show_spinner=False)
def buscar_colaboradores_todos():
    try:
        res = (
            supabase.table("colaboradores")
            .select("*")
            .execute()
            .data
        )
        return res if res else []
    except Exception:
        return []


@st.cache_data(ttl=180, show_spinner=False)
def buscar_colaboradores():
    """Base operacional: somente colaboradores ativos."""
    try:
        res = (
            supabase.table("colaboradores")
            .select("*")
            .eq("ativo", True)
            .execute()
            .data
        )
        return res if res else []
    except Exception:
        # Compatibilidade caso o backend legado ainda não possua a coluna.
        try:
            res = (
                supabase.table("colaboradores")
                .select("*")
                .execute()
                .data
            )
            return res if res else []
        except Exception:
            return []

# --- INDISPONIBILIDADES / FÉRIAS / ATESTADOS ---
INDISP_UNIDADE = "__APROAR_INDISPONIBILIDADE__"
INDISP_PREFIX = "APROAR_INDISP|"


def eh_registro_indisponibilidade(obra):
    return bool(obra) and (
        str(obra.get("unidade") or "") == INDISP_UNIDADE
        or str(obra.get("nome") or "").startswith(INDISP_PREFIX)
    )


def decodificar_indisponibilidade(obra):
    if not eh_registro_indisponibilidade(obra):
        return None
    try:
        bruto = str(obra.get("nome") or "")[len(INDISP_PREFIX):]
        dados = json.loads(bruto)
        if not isinstance(dados, dict):
            return None
        dados["id"] = obra.get("id")
        return dados
    except Exception:
        return None


def listar_indisponibilidades():
    if schema_producao_disponivel():
        migrar_indisponibilidades_legadas_para_producao()
        estruturadas = listar_indisponibilidades_estruturadas()
        if estruturadas is not None:
            return estruturadas

    saida = []
    for item in obras_todas:
        dados = decodificar_indisponibilidade(item)
        if dados:
            dados["_origem"] = "legado"
            saida.append(dados)
    return saida


def obter_colaborador_por_id(colaborador_id):
    """Localiza o colaborador mesmo quando o Neon devolve UUID e o JSON guarda string."""
    alvo = str(colaborador_id or "").strip()
    if not alvo:
        return {}

    direto = dict_colaboradores.get(colaborador_id) if "dict_colaboradores" in globals() else None
    if direto:
        return direto

    for colab in colaboradores if "colaboradores" in globals() else []:
        if str(colab.get("id") or "").strip() == alvo:
            return colab
    return {}


def obter_indisponibilidade_colaborador(colaborador_id, data_ref):
    if isinstance(data_ref, datetime.datetime):
        data_ref = data_ref.date()
    alvo = str(colaborador_id or "").strip()
    for item in listar_indisponibilidades():
        if str(item.get("colaborador_id") or "").strip() != alvo:
            continue
        try:
            ini = datetime.date.fromisoformat(str(item.get("inicio")))
            fim = datetime.date.fromisoformat(str(item.get("fim")))
        except Exception:
            continue
        if ini <= data_ref <= fim:
            return item
    return None


def salvar_indisponibilidade(colaborador_id, motivo, inicio, fim, observacao=""):
    if fim < inicio:
        return False, "A data final não pode ser anterior à data inicial."

    if schema_producao_disponivel():
        ok = salvar_indisponibilidade_estruturada(
            colaborador_id, motivo, inicio, fim, observacao, criado_por="PAULO"
        )
        if ok:
            limpar_cache_operacional()
            return True, "Indisponibilidade registrada."
        if ok is False:
            return False, "Não foi possível registrar a indisponibilidade na estrutura de produção."

    colab_ref = obter_colaborador_por_id(colaborador_id)
    dados = {
        "colaborador_id": str(colaborador_id),
        "colaborador_nome": str(colab_ref.get("nome") or "").strip(),
        "motivo": str(motivo),
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "observacao": str(observacao or "").strip(),
        "criado_em": agora_aproar().isoformat(),
    }
    try:
        supabase.table("obras").insert({
            "unidade": INDISP_UNIDADE,
            "nome": INDISP_PREFIX + json.dumps(dados, ensure_ascii=False, separators=(",", ":")),
        }).execute()
        limpar_cache_operacional()
        return True, "Indisponibilidade registrada."
    except Exception as e:
        return False, f"Não foi possível registrar a indisponibilidade: {e}"


def excluir_indisponibilidade(registro_id):
    if schema_producao_disponivel():
        ok = excluir_indisponibilidade_estruturada(registro_id, "PAULO")
        if ok is not None:
            limpar_cache_operacional()
            return bool(ok)
    try:
        supabase.table("obras").delete().eq("id", registro_id).execute()
        limpar_cache_operacional()
        return True
    except Exception:
        return False


obras_todas = buscar_obras() or []
obras = [
    o
    for o in obras_todas
    if not eh_registro_indisponibilidade(o)
]

colaboradores_todos = buscar_colaboradores_todos() or []
colaboradores = [
    c
    for c in colaboradores_todos
    if c.get("ativo", True) is not False
]

dict_colaboradores = (
    {
        c["id"]: c
        for c in colaboradores_todos
    }
    if colaboradores_todos
    else {}
)
dict_obras = (
    {
        o["id"]: o
        for o in obras
    }
    if obras
    else {}
)

ENGENHEIROS = [
    "EDUARDO",
    "GABRIEL",
    "JOEL",
    "NETO",
    "PAULO",
    "SOARES",
    "VICTOR",
]

UNIDADES_APROAR = [
    "BARRA DO CEARÁ",
    "MARACANAÚ",
    "COLISEU",
    "HORIZONTE",
    "ESCRITÓRIO",
    "CENTRO",
    "MUSEU",
    "FIEC",
    "UNIFOR",
    "SEBRAE",
    "PARANGABA",
    "APARTAMENTO 701",
]

# Responsáveis oficiais usados nas cobranças automáticas e manuais.
RESPONSAVEIS_UNIDADES_TEAMS = {
    "EDUARDO": [
        "BARRA DO CEARÁ",
    ],
    "SOARES": [
        "HORIZONTE",
        "SEBRAE",
    ],
    "JOEL": [
        "COLISEU",
        "UNIFOR",
    ],
    "GABRIEL": [
        "FIEC",
        "PARANGABA",
        "APARTAMENTO 701",
    ],
    "VICTOR": [
        "CENTRO",
        "MUSEU",
    ],
    "NETO": [
        "MARACANAÚ",
    ],
}

OBSERVADORES_TEAMS = [
    "PAULO",
    "HELENA",
]

SUPERVISORES_TEAMS = (
    list(RESPONSAVEIS_UNIDADES_TEAMS.keys())
    + OBSERVADORES_TEAMS
)


def _responsavel_por_unidade_teams(unidade):
    alvo = normalizar(unidade or "")

    for supervisor, unidades in (
        RESPONSAVEIS_UNIDADES_TEAMS.items()
    ):
        if any(
            normalizar(u) == alvo
            for u in unidades
        ):
            return supervisor

    return "SEM RESPONSÁVEL"


def _todas_unidades_responsaveis_teams():
    unidades = []

    for lista in RESPONSAVEIS_UNIDADES_TEAMS.values():
        for unidade in lista:
            if normalizar(unidade) not in {
                normalizar(u)
                for u in unidades
            }:
                unidades.append(unidade)

    return unidades

def _carregar_pendentes_responsavel_teams(
    cur,
    supervisor,
    hoje_ref,
    agora_ref=None,
):
    """
    Carrega TODAS as pendências visíveis no painel.

    A prévia e o botão manual independem dos horários automáticos:
    - pendência do próprio dia já aparece;
    - uma cobrança automática não remove a linha;
    - a linha só desaparece quando o apontamento é regularizado.
    """
    supervisor = str(
        supervisor or ""
    ).strip().upper()

    where_unidade = ""
    params_unidade = []

    if supervisor not in OBSERVADORES_TEAMS:
        unidades = RESPONSAVEIS_UNIDADES_TEAMS.get(
            supervisor,
            [],
        )

        if not unidades:
            return []

        where_unidade = """
          AND UPPER(TRIM(COALESCE(o.unidade, ''))) = ANY(%s)
        """
        params_unidade = [[
            str(u).strip().upper()
            for u in unidades
        ]]

    cur.execute(
        f"""
        SELECT
            c.id,
            c.data,
            c.turno,
            c.engenheiro,
            col.nome AS colaborador,
            o.unidade,
            o.nome AS obra_atual
        FROM convocacoes c
        JOIN colaboradores col
          ON col.id = c.colaborador_id
        JOIN obras o
          ON o.id = c.obra_id
        WHERE c.data <= %s
          AND UPPER(COALESCE(o.nome, '')) LIKE UPPER(%s)
          {where_unidade}
        ORDER BY
            c.data ASC,
            o.unidade ASC,
            col.nome ASC
        """,
        (
            hoje_ref,
            "A DEFINIR NO APONTAMENTO%",
            *params_unidade,
        ),
    )

    return cur.fetchall() or []


def _situacao_pendencia_teams(
    data_servico,
    unidade,
    agora_ref=None,
):
    """
    Compatibilidade com a UI atual: devolve Situação + Próxima automática
    usando exatamente as mesmas regras operacionais e de cobrança.
    """
    agora_ref = agora_ref or datetime.datetime.now(
        ZoneInfo("America/Fortaleza")
    )

    situacao_base = situacao_pendencia_teams(
        data_servico,
        unidade=unidade,
        agora=agora_ref,
    )
    automatico = proxima_cobranca_automatica_teams(
        data_servico,
        unidade=unidade,
        agora=agora_ref,
    )

    if situacao_base == "ATRASADO":
        situacao = "Atrasado"
    else:
        try:
            mesma_data = data_servico == agora_ref.date()
        except Exception:
            mesma_data = False

        if mesma_data:
            situacao = "Pendente hoje"
        else:
            situacao = "Pendente"

    return situacao, automatico


def _montar_mensagem_cobranca_manual_teams(
    supervisor,
    pendentes,
):
    grupos = {}

    for item in pendentes:
        if isinstance(item, dict):
            data_ref = item.get("data")
            unidade = item.get("unidade") or "SEM UNIDADE"
        else:
            data_ref = item[1]
            unidade = item[5] or "SEM UNIDADE"

        chave = (data_ref, unidade)
        grupos[chave] = grupos.get(chave, 0) + 1

    linhas = []

    for (data_ref, unidade), qtd in sorted(
        grupos.items(),
        key=lambda x: (
            str(x[0][0]),
            str(x[0][1]),
        ),
    ):
        data_txt = (
            data_ref.strftime("%d/%m")
            if hasattr(data_ref, "strftime")
            else str(data_ref)
        )

        termo = (
            "colaborador"
            if qtd == 1
            else "colaboradores"
        )

        linhas.append(
            f"• {data_txt} · "
            f"{_html.escape(str(unidade))} · "
            f"{qtd} {termo}"
        )

    if len(linhas) > 8:
        restante = len(linhas) - 8
        linhas = (
            linhas[:8]
            + [f"• + {restante} grupo(s) pendente(s)"]
        )

    total = len(pendentes)
    termo_total = (
        "apontamento pendente"
        if total == 1
        else "apontamentos pendentes"
    )

    portal_url = (
        "https://apontamentos-aproar.streamlit.app/?eng"
    )

    return (
        "<b>APROAR · Apontamentos pendentes</b><br><br>"
        f"{_html.escape(supervisor.title())}, existem "
        f"<b>{total} {termo_total}</b> que ainda precisam "
        "ser regularizados.<br>"
        "<span style='color:#6b7280'>Cobrança manual</span>"
        "<br><br>"
        + "<br>".join(linhas)
        + "<br><br>"
        "Favor regularizar no <b>Portal do Supervisor</b>: "
        f"<a href='{portal_url}'>abrir apontamentos</a>."
    )


def _cobrar_supervisor_teams_agora(
    supervisor,
    email_teams,
):
    """
    Envia uma cobrança manual sem interferir nas execuções automáticas
    das 09:30 e 15:00.
    """
    supervisor = str(
        supervisor or ""
    ).strip().upper()

    email_teams = str(
        email_teams or ""
    ).strip()

    if not email_teams:
        return False, "Informe o e-mail Teams deste supervisor."

    if not TEAMS_COBRANCA_WEBHOOK_URL:
        return (
            False,
            "O webhook do Teams ainda não está configurado "
            "nos Secrets do Streamlit.",
        )

    if DB_BACKEND != "NEON":
        return (
            False,
            "A cobrança manual está disponível com Neon/PostgreSQL.",
        )

    agora = datetime.datetime.now(
        ZoneInfo("America/Fortaleza")
    )
    hoje_ref = agora.date()

    try:
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                pendentes = (
                    _carregar_pendentes_responsavel_teams(
                        cur,
                        supervisor,
                        hoje_ref,
                        agora_ref=agora,
                    )
                )

                if not pendentes:
                    return (
                        True,
                        f"{supervisor}: não há apontamentos pendentes "
                        "nas unidades sob sua responsabilidade.",
                    )

                mensagem = (
                    _montar_mensagem_cobranca_manual_teams(
                        supervisor,
                        pendentes,
                    )
                )

                payload = {
                    "recipient": email_teams,
                    "engineer": supervisor,
                    "slot": "MANUAL",
                    "pendingCount": len(pendentes),
                    "message": mensagem,
                    "portalUrl": (
                        "https://apontamentos-aproar.streamlit.app/?eng"
                    ),
                }

                resposta = requests.post(
                    TEAMS_COBRANCA_WEBHOOK_URL,
                    json=payload,
                    timeout=20,
                )

                sucesso = (
                    200
                    <= resposta.status_code
                    < 300
                )

                horario_log = (
                    "MANUAL "
                    + agora.strftime("%H:%M:%S")
                )

                cur.execute(
                    """
                    INSERT INTO cobrancas_teams (
                        data_execucao,
                        horario,
                        engenheiro,
                        email_teams,
                        qtd_pendentes,
                        mensagem,
                        status,
                        resposta_http,
                        enviado_em
                    )
                    VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,NOW()
                    )
                    ON CONFLICT (
                        data_execucao,
                        horario,
                        engenheiro
                    )
                    DO UPDATE SET
                        email_teams = EXCLUDED.email_teams,
                        qtd_pendentes = EXCLUDED.qtd_pendentes,
                        mensagem = EXCLUDED.mensagem,
                        status = EXCLUDED.status,
                        resposta_http = EXCLUDED.resposta_http,
                        enviado_em = NOW()
                    """,
                    (
                        hoje_ref,
                        horario_log,
                        supervisor,
                        email_teams,
                        len(pendentes),
                        mensagem,
                        (
                            "ENVIADA"
                            if sucesso
                            else "ERRO"
                        ),
                        resposta.status_code,
                    ),
                )

                conn.commit()

        if sucesso:
            return (
                True,
                f"Cobrança enviada para {supervisor}: "
                f"{len(pendentes)} apontamento(s) atrasado(s).",
            )

        return (
            False,
            f"O Teams respondeu com HTTP "
            f"{resposta.status_code}.",
        )

    except Exception as exc:
        return (
            False,
            "Não foi possível enviar a cobrança agora. "
            f"Detalhe: {str(exc)[:140]}",
        )


# --- DISPONIBILIDADE — V4.1 (carregamento leve e robusto) -------------------
@st.cache_data(ttl=45, show_spinner=False)
def _carregar_indisponibilidades_disponibilidade():
    """
    Leitura leve para a página de disponibilidade.
    Evita executar a migração legada toda vez que a aba é aberta.
    """
    try:
        if schema_producao_disponivel():
            estruturadas = listar_indisponibilidades_estruturadas()
            if estruturadas is not None:
                return estruturadas
    except Exception:
        pass

    saida = []
    try:
        for item in obras_todas:
            dados = decodificar_indisponibilidade(item)
            if dados:
                dados["_origem"] = "legado"
                saida.append(dados)
    except Exception:
        pass
    return saida


def render_aba_disponibilidade(key_suffix=""):
    cabecalho_pagina_aproar(
        "Disponibilidade da equipe",
        "Veja rapidamente quem pode ser convocado no turno selecionado.",
        categoria="OPERAÇÃO",
    )

    f1, f2 = st.columns([1, 1])
    with f1:
        data_disp = st.date_input(
            "Data de referência",
            value=proximo_dia_util(agora_aproar().date()),
            format="DD/MM/YYYY",
            key=f"data_disp_{key_suffix}",
        )
    with f2:
        turno_disp = st.selectbox(
            "Turno",
            ["Integral", "Manhã", "Tarde", "Noite"],
            key=f"turno_disp_{key_suffix}",
        )

    # Convocações: usa a consulta operacional cacheada que já é usada
    # pelo restante do sistema, evitando uma consulta exclusiva mais lenta.
    try:
        convs_disp = _buscar_convocacoes_intervalo(data_disp, data_disp) or []
    except Exception:
        convs_disp = []

    # Indisponibilidades: consulta direta/cacheada, sem migração na abertura.
    indisponibilidades = _carregar_indisponibilidades_disponibilidade() or []

    indisponiveis_map = {}
    for item in indisponibilidades:
        alvo = str(item.get("colaborador_id") or "").strip()
        if not alvo:
            continue
        try:
            ini = datetime.date.fromisoformat(str(item.get("inicio")))
            fim = datetime.date.fromisoformat(str(item.get("fim")))
        except Exception:
            continue
        if ini <= data_disp <= fim:
            indisponiveis_map[alvo] = item

    por_colaborador = {}
    for conv in convs_disp:
        cid = str(conv.get("colaborador_id") or "").strip()
        if cid:
            por_colaborador.setdefault(cid, []).append(conv)

    linhas = []
    ocupados = 0
    indisponiveis_qtd = 0
    disponiveis = 0

    for colab in colaboradores:
        cid = str(colab.get("id") or "").strip()
        nome = str(colab.get("nome") or "-").strip()
        funcao = str(colab.get("funcao") or "INDEFINIDA").strip()

        if cid in indisponiveis_map:
            ind = indisponiveis_map[cid]
            indisponiveis_qtd += 1
            linhas.append({
                "Colaborador": nome,
                "Função": funcao,
                "Situação": "Indisponível",
                "Alocação": "-",
                "Observação": f"{ind.get('motivo','Indisponível')} • {ind.get('inicio','')} a {ind.get('fim','')}",
            })
            continue

        alocacoes = por_colaborador.get(cid, [])
        sobrepostas = [
            conv for conv in alocacoes
            if turnos_se_sobrepoem(turno_da_convocacao(conv), turno_disp)
        ]

        if sobrepostas:
            ocupados += 1
            detalhes = []
            for conv in sobrepostas:
                obra = dict_obras.get(conv.get("obra_id"), {})
                detalhes.append(
                    f"{turno_da_convocacao(conv)} • {obra.get('unidade','-')} • {conv.get('engenheiro','-')}"
                )
            linhas.append({
                "Colaborador": nome,
                "Função": funcao,
                "Situação": "Ocupado",
                "Alocação": " | ".join(detalhes),
                "Observação": "",
            })
        else:
            disponiveis += 1
            outras = []
            for conv in alocacoes:
                obra = dict_obras.get(conv.get("obra_id"), {})
                outras.append(
                    f"{turno_da_convocacao(conv)} • {obra.get('unidade','-')}"
                )
            linhas.append({
                "Colaborador": nome,
                "Função": funcao,
                "Situação": "Disponível",
                "Alocação": "Outro turno: " + " | ".join(outras) if outras else "-",
                "Observação": "",
            })

    total = ocupados + indisponiveis_qtd + disponiveis
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Disponíveis", disponiveis)
    m2.metric("Ocupados", ocupados)
    m3.metric("Indisponíveis", indisponiveis_qtd)
    m4.metric("Total analisado", total)

    st.caption(
        f"{data_disp.strftime('%d/%m/%Y')} • turno {turno_disp}. "
        "Integral bloqueia os demais turnos; manhã, tarde e noite só conflitam quando houver sobreposição."
    )

    if not linhas:
        st.info("Nenhum colaborador cadastrado.")
        return

    df_disp = pd.DataFrame(linhas)

    ordem_status = {"Disponível": 0, "Ocupado": 1, "Indisponível": 2}
    df_disp["_ordem"] = df_disp["Situação"].map(ordem_status).fillna(9)
    df_disp = df_disp.sort_values(
        ["_ordem", "Função", "Colaborador"],
        ascending=[True, True, True],
    ).drop(columns=["_ordem"])

    # Filtro opcional por situação sem nova consulta ao banco.
    situacoes = st.multiselect(
        "Mostrar",
        ["Disponível", "Ocupado", "Indisponível"],
        default=["Disponível", "Ocupado", "Indisponível"],
        key=f"filtro_situacao_disp_{key_suffix}",
    )
    if situacoes:
        df_disp = df_disp[df_disp["Situação"].isin(situacoes)]

    tabela_aproar(
        df_disp,
        key=f"tbl_disponibilidade_{key_suffix}",
        altura_max=620,
    )


# --- COMPONENTES COMPARTILHADOS: APONTAMENTO, DASHBOARD, RELATÓRIO E AUDITORIA ---

# --- COMPONENTES VISUAIS PADRONIZADOS V3 ------------------------------------
def cabecalho_pagina_aproar(titulo, subtitulo="", categoria="GESTÃO DE EQUIPES", lateral=""):
    """Cabeçalho visual padrão das páginas administrativas."""
    import html as _ap_html
    titulo_h = _ap_html.escape(str(titulo or ""))
    subtitulo_h = _ap_html.escape(str(subtitulo or ""))
    categoria_h = _ap_html.escape(str(categoria or ""))
    lateral_h = _ap_html.escape(str(lateral or ""))
    st.markdown(
        f"""
        <div class="ap3-page-head">
            <div>
                <div class="ap3-page-kicker">{categoria_h}</div>
                <div class="ap3-page-title">{titulo_h}</div>
                <div class="ap3-page-sub">{subtitulo_h}</div>
            </div>
            <div class="ap3-page-side">{lateral_h}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titulo_secao_aproar(titulo, subtitulo=""):
    import html as _ap_html
    st.markdown(
        f"""
        <div class="ap3-section">
            <div>
                <div class="ap3-section-title">{_ap_html.escape(str(titulo or ""))}</div>
                <div class="ap3-section-sub">{_ap_html.escape(str(subtitulo or ""))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tabela_aproar(df, key=None, altura_max=520, ocultar_indice=True):
    """
    Exibe DataFrames com altura proporcional, formatação de moeda/percentual
    e o padrão visual único da plataforma.
    """
    if df is None:
        df = pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    config = {}
    for coluna in df.columns:
        nome = str(coluna)
        serie = df[coluna]
        eh_numerica = pd.api.types.is_numeric_dtype(serie)

        if eh_numerica and (
            "(R$)" in nome
            or nome.lower().startswith(("custo", "diária", "diaria", "extra", "impacto"))
            or "valor" in nome.lower()
        ):
            try:
                config[coluna] = st.column_config.NumberColumn(nome, format="R$ %.2f")
            except Exception:
                pass
        elif eh_numerica and ("%" in nome or "taxa" in nome.lower()):
            try:
                config[coluna] = st.column_config.NumberColumn(nome, format="%.1f%%")
            except Exception:
                pass

    # Evita tabelas minúsculas e também aquelas que ocupam a tela inteira.
    linhas = max(1, len(df))
    altura = min(int(altura_max), max(122, 40 * min(linhas + 1, 13)))

    kwargs = dict(
        use_container_width=True,
        hide_index=ocultar_indice,
        height=altura,
    )
    if key:
        kwargs["key"] = key
    if config:
        kwargs["column_config"] = config

    try:
        st.dataframe(df, row_height=36, **kwargs)
    except TypeError:
        # Compatibilidade com versões do Streamlit sem row_height/key em dataframe.
        kwargs.pop("key", None)
        st.dataframe(df, **kwargs)


OPCOES_STATUS_PRESENCA = [
    "Presente (Integral)", "Presente (Só Manhã)", "Presente (Só Tarde)",
    "Saída Antecipada", "Falta", "Atestado"
]


@st.cache_data(ttl=45, show_spinner=False)
def _buscar_convocacoes_intervalo(data_inicio, data_fim, engenheiro=None):
    try:
        q = supabase.table("convocacoes").select("*").gte("data", data_inicio.isoformat()).lte("data", data_fim.isoformat())
        if engenheiro:
            q = q.eq("engenheiro", engenheiro)
        return q.execute().data or []
    except Exception:
        return []


def _periodo_por_tipo(tipo, data_base):
    if tipo == "Diário":
        return data_base, data_base
    if tipo == "Semanal":
        inicio = data_base - datetime.timedelta(days=data_base.weekday())
        return inicio, inicio + datetime.timedelta(days=6)
    if tipo == "Mensal":
        inicio = data_base.replace(day=1)
        if inicio.month == 12:
            prox = datetime.date(inicio.year + 1, 1, 1)
        else:
            prox = datetime.date(inicio.year, inicio.month + 1, 1)
        return inicio, prox - datetime.timedelta(days=1)
    return data_base, data_base


def _processar_registro_operacional(registro):
    obra = dict_obras.get(registro.get("obra_id"), {"unidade": "GERAL", "nome": "Desconhecida"})
    colab = dict_colaboradores.get(registro.get("colaborador_id"), {"nome": "Desconhecido", "funcao": "-"})
    status = normalizar_status_operacional(registro.get("status"))
    tipo_diaria = tipo_diaria_registro(registro)
    custo_encargos = custo_encargos_base_registro(registro, colab)
    extra = valor_extra_registro(registro)
    adicional_noturno = valor_adicional_noturno_registro(registro)
    acordo = valor_acordo_registro(registro)
    total_controladoria = (
        custo_encargos
        + extra
        + adicional_noturno
        + acordo
    ) if status_eh_presenca(status) else 0.0
    diaria_financeiro = (
        valor_diaria_financeiro_registro(
            registro,
            colab,
        )
    )

    total_financeiro = (
        diaria_financeiro
        + extra
        + adicional_noturno
        + acordo
    ) if status_eh_presenca(status) else 0.0
    meta = obter_metadata_operacional(registro.get("observacao") or "")
    _, obs_livre = decompor_observacao_operacional(registro.get("observacao") or "")
    return {
        "id": registro.get("id"),
        "Data": str(registro.get("data") or ""),
        "Engenheiro": str(registro.get("engenheiro") or "N/A"),
        "Unidade": str(obra.get("unidade") or "GERAL"),
        "Serviço(s)": descricao_servicos_convocacao(registro, obra),
        "Colaborador": str(colab.get("nome") or "Desconhecido"),
        "Função": str(colab.get("funcao") or "-"),
        "Status": status,
        "Tipo": tipo_diaria,
        "Diária Financeiro (R$)": float(diaria_financeiro),
        "Custo c/ encargos (R$)": float(custo_encargos),
        "Extra (R$)": float(extra),
        "Adicional noturno (R$)": float(adicional_noturno),
        "Acordos / Bonificações (R$)": float(acordo),
        "Custo (R$)": float(total_controladoria),
        "Total Financeiro (R$)": float(total_financeiro),
        "Observação": obs_livre,
        "Convocação após 16h": bool(meta.get("convocacao_atrasada")),
        "Apontamento atrasado": bool(meta.get("apontamento_atrasado")),
        "Apontado em": str(meta.get("apontado_em") or ""),
    }



def _peso_periodo_relatorio(periodo):
    """Converte o período do serviço em blocos de custo."""
    p = normalizar_turno_convocacao(periodo)
    if p == "Manhã":
        return {"M": 0.5}
    if p == "Tarde":
        return {"T": 0.5}
    if p == "Noite":
        # O sistema atual remunera Noite como diária integral.
        return {"N": 1.0}
    return {"M": 0.5, "T": 0.5}


def _blocos_presenca_registro_relatorio(registro):
    """
    Retorna os blocos de diária efetivamente remunerados pelo registro.

    O uso de MAX por bloco no agrupamento evita pagar duas meias-diárias
    quando a mesma pessoa executou dois serviços na mesma manhã.
    """
    status = normalizar_status_operacional(
        registro.get("status")
    )
    turno = turno_da_convocacao(registro)

    if not status_eh_presenca(status):
        return {}

    if status == "Presente (Só Manhã)":
        return {"M": 0.5}

    if status == "Presente (Só Tarde)":
        return {"T": 0.5}

    if status == "Saída Antecipada":
        if turno == "Tarde":
            return {"T": 0.5}
        if turno == "Noite":
            return {"N": 0.5}
        return {"M": 0.5}

    # Para registros presentes integrais, o turno específico prevalece.
    # Integral/legado ocupa manhã + tarde.
    if turno == "Manhã":
        return {"M": 0.5}
    if turno == "Tarde":
        return {"T": 0.5}
    if turno == "Noite":
        return {"N": 1.0}

    return {"M": 0.5, "T": 0.5}


def _localizar_obra_por_nome_relatorio(nome, unidade_preferida=""):
    alvo = normalizar(nome or "")
    unidade_pref = normalizar(unidade_preferida or "")
    candidatas = [
        o for o in obras
        if normalizar(o.get("nome") or "") == alvo
    ]
    if unidade_pref:
        mesma_unidade = next(
            (
                o for o in candidatas
                if normalizar(o.get("unidade") or "") == unidade_pref
            ),
            None,
        )
        if mesma_unidade:
            return mesma_unidade
    return candidatas[0] if candidatas else {}


def _servicos_do_registro_relatorio(registro):
    """Expande principal + serviços adicionais em itens individualizados."""
    obra_principal = dict_obras.get(
        registro.get("obra_id"),
        {},
    )
    meta = obter_metadata_operacional(
        registro.get("observacao") or ""
    )

    turno_registro = turno_da_convocacao(registro)
    periodo_principal = str(
        meta.get("periodo_servico_principal")
        or turno_registro
        or "Integral"
    )

    itens = []

    if obra_principal and not eh_obra_placeholder(obra_principal):
        itens.append({
            "obra_id": str(obra_principal.get("id") or registro.get("obra_id") or ""),
            "obra": str(obra_principal.get("nome") or "N/A"),
            "unidade": str(obra_principal.get("unidade") or "GERAL"),
            "periodo": normalizar_turno_convocacao(periodo_principal),
            "principal": True,
        })

    for adicional in _normalizar_servicos_adicionais(meta):
        nome = str(adicional.get("servico") or "").strip()
        if not nome:
            continue

        periodo = str(
            adicional.get("periodo")
            or periodo_principal
            or turno_registro
            or "Integral"
        )
        if periodo == "Não informado":
            periodo = periodo_principal or turno_registro or "Integral"

        obra_id_add = str(
            adicional.get("obra_id")
            or ""
        ).strip()

        obra_add = (
            dict_obras.get(obra_id_add, {})
            if obra_id_add
            else {}
        )

        if not obra_add:
            obra_add = _localizar_obra_por_nome_relatorio(
                nome,
                adicional.get("unidade")
                or (
                    obra_principal.get("unidade")
                    if obra_principal
                    else ""
                ),
            )

        itens.append({
            "obra_id": str(
                obra_add.get("id")
                or obra_id_add
                or ""
            ),
            "obra": nome,
            "unidade": str(
                adicional.get("unidade")
                or obra_add.get("unidade")
                or (
                    obra_principal.get("unidade")
                    if obra_principal
                    else ""
                )
                or "GERAL"
            ),
            "periodo": normalizar_turno_convocacao(periodo),
            "principal": False,
        })

    # Evita duplicar o mesmo serviço/período dentro de um registro.
    saida = []
    vistos = set()
    for item in itens:
        chave = (
            str(item.get("obra_id") or ""),
            normalizar(item.get("obra") or ""),
            normalizar(item.get("unidade") or ""),
            item.get("periodo"),
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(item)

    return saida


def ratear_registros_por_servico(registros):
    """
    Rateia custos por serviço preservando duas visões:

    Financeiro = Diária efetiva (Profissional 120/60 · Ajudante 80/40, editável) + Extra + Adicional noturno + Acordos/Bonificações.
    Controladoria = Custo padrão da categoria (Profissional 241,74 · Ajudante 182,34) + Extra + Adicional noturno + Acordos/Bonificações.

    Se a mesma meia-diária tiver 2 serviços na mesma manhã, a base é dividida
    entre eles; não é duplicada.
    """
    grupos = {}

    for registro in registros or []:
        data = str(registro.get("data") or "")
        colaborador_id = str(registro.get("colaborador_id") or "")
        grupos.setdefault((data, colaborador_id), []).append(registro)

    linhas = []

    for (data, colaborador_id), regs in grupos.items():
        colab = dict_colaboradores.get(regs[0].get("colaborador_id"), {})

        servicos = {}
        extra_por_servico = {}
        adicional_noturno_por_servico = {}
        acordo_por_servico = {}
        tipos_por_servico = {}

        # Orçamentos monetários por bloco M/T/N. MAX impede duplicar a mesma
        # meia-diária quando existem dois registros no mesmo bloco.
        base_fin_bloco = {}
        base_fin_padrao_bloco = {}
        base_ctrl_bloco = {}

        for reg in regs:
            status_reg = normalizar_status_operacional(reg.get("status"))
            itens_reg = _servicos_do_registro_relatorio(reg)
            if not itens_reg:
                continue

            tipo_reg = tipo_diaria_registro(reg)
            presente = status_eh_presenca(status_reg)
            base_fin_reg = (
                valor_diaria_financeiro_registro(
                    reg,
                    colab,
                )
                if presente
                else 0.0
            )

            base_fin_padrao_reg = (
                valor_financeiro_padrao_colaborador(
                    colab,
                    tipo_reg,
                )
                if presente
                else 0.0
            )

            base_ctrl_reg = (
                custo_encargos_base_registro(
                    reg,
                    colab,
                )
                if presente
                else 0.0
            )
            extra_reg = valor_extra_registro(reg) if presente else 0.0
            adicional_noturno_reg = valor_adicional_noturno_registro(reg) if presente else 0.0
            acordo_reg = valor_acordo_registro(reg) if presente else 0.0

            # Descobre os blocos reais do registro a partir dos períodos dos serviços.
            blocos_reg = []
            for item in itens_reg:
                periodo_item = normalizar_turno_convocacao(
                    item.get("periodo") or turno_da_convocacao(reg)
                )
                for bloco in _peso_periodo_relatorio(periodo_item).keys():
                    if bloco not in blocos_reg:
                        blocos_reg.append(bloco)

            if not blocos_reg:
                blocos_reg = list(_blocos_presenca_registro_relatorio(reg).keys()) or ["M"]

            # A opção Diária/Meia diária é a fonte do valor. Os blocos servem
            # somente para não duplicar e para distribuir o custo entre serviços.
            parte_fin_bloco = (
                base_fin_reg / len(blocos_reg)
                if blocos_reg
                else 0.0
            )

            parte_fin_padrao_bloco = (
                base_fin_padrao_reg / len(blocos_reg)
                if blocos_reg
                else 0.0
            )

            parte_ctrl_bloco = (
                base_ctrl_reg / len(blocos_reg)
                if blocos_reg
                else 0.0
            )

            for bloco in blocos_reg:
                base_fin_bloco[bloco] = max(
                    float(
                        base_fin_bloco.get(
                            bloco,
                            0.0,
                        )
                    ),
                    float(
                        parte_fin_bloco
                    ),
                )

                base_fin_padrao_bloco[bloco] = max(
                    float(
                        base_fin_padrao_bloco.get(
                            bloco,
                            0.0,
                        )
                    ),
                    float(
                        parte_fin_padrao_bloco
                    ),
                )

                base_ctrl_bloco[bloco] = max(
                    float(
                        base_ctrl_bloco.get(
                            bloco,
                            0.0,
                        )
                    ),
                    float(
                        parte_ctrl_bloco
                    ),
                )

            extra_por_item = (
                extra_reg / len(itens_reg)
                if itens_reg
                else 0.0
            )

            itens_sebrae_reg = [
                item
                for item in itens_reg
                if eh_unidade_sebrae(
                    item.get("unidade")
                    or ""
                )
            ]

            adicional_noturno_por_item_sebrae = (
                adicional_noturno_reg
                / len(itens_sebrae_reg)
                if itens_sebrae_reg
                else 0.0
            )

            acordo_por_item = (
                acordo_reg / len(itens_reg)
                if itens_reg
                else 0.0
            )

            _, obs_livre = decompor_observacao_operacional(
                reg.get("observacao")
                or ""
            )

            for item in itens_reg:
                chave_serv = (
                    str(item.get("obra_id") or ""),
                    normalizar(item.get("obra") or ""),
                    normalizar(item.get("unidade") or ""),
                )
                atual = servicos.setdefault(
                    chave_serv,
                    {
                        "obra_id": str(item.get("obra_id") or ""),
                        "obra": str(item.get("obra") or "N/A"),
                        "unidade": str(item.get("unidade") or "GERAL"),
                        "periodos": set(),
                        "engenheiros": set(),
                        "status": [],
                        "observacoes": [],
                        "blocos": set(),
                    },
                )

                periodo = normalizar_turno_convocacao(item.get("periodo") or turno_da_convocacao(reg))
                atual["periodos"].add(periodo)
                atual["engenheiros"].add(str(reg.get("engenheiro") or "N/A"))
                atual["status"].append(status_reg)
                atual["blocos"].update(_peso_periodo_relatorio(periodo).keys())
                if obs_livre:
                    atual["observacoes"].append(obs_livre)

                extra_por_servico[chave_serv] = float(extra_por_servico.get(chave_serv, 0.0)) + extra_por_item
                adicional_noturno_por_servico[chave_serv] = (
                    float(
                        adicional_noturno_por_servico.get(
                            chave_serv,
                            0.0,
                        )
                    )
                    + (
                        adicional_noturno_por_item_sebrae
                        if eh_unidade_sebrae(
                            item.get("unidade")
                            or ""
                        )
                        else 0.0
                    )
                )
                acordo_por_servico[chave_serv] = float(acordo_por_servico.get(chave_serv, 0.0)) + acordo_por_item
                tipos_por_servico.setdefault(chave_serv, []).append(tipo_reg)

        if not servicos:
            continue

        # Distribui cada orçamento de bloco entre os serviços que realmente
        # participaram daquele bloco.
        base_fin_por_servico = {
            chave: 0.0
            for chave in servicos
        }
        base_fin_padrao_por_servico = {
            chave: 0.0
            for chave in servicos
        }
        base_ctrl_por_servico = {
            chave: 0.0
            for chave in servicos
        }

        blocos_todos = (
            set(base_fin_bloco)
            | set(base_fin_padrao_bloco)
            | set(base_ctrl_bloco)
        )
        for bloco in blocos_todos:
            participantes = [
                chave
                for chave, serv in servicos.items()
                if bloco in serv.get("blocos", set())
            ]
            if not participantes:
                participantes = list(servicos.keys())
            if not participantes:
                continue

            parte_fin = (
                float(
                    base_fin_bloco.get(
                        bloco,
                        0.0,
                    )
                )
                / len(participantes)
            )

            parte_fin_padrao = (
                float(
                    base_fin_padrao_bloco.get(
                        bloco,
                        0.0,
                    )
                )
                / len(participantes)
            )

            parte_ctrl = (
                float(
                    base_ctrl_bloco.get(
                        bloco,
                        0.0,
                    )
                )
                / len(participantes)
            )

            for chave in participantes:
                base_fin_por_servico[
                    chave
                ] += parte_fin
                base_fin_padrao_por_servico[
                    chave
                ] += parte_fin_padrao
                base_ctrl_por_servico[
                    chave
                ] += parte_ctrl

        for chave_serv, serv in servicos.items():
            base_fin_rateada = round(
                float(
                    base_fin_por_servico.get(
                        chave_serv,
                        0.0,
                    )
                ),
                2,
            )

            base_fin_padrao_rateada = round(
                float(
                    base_fin_padrao_por_servico.get(
                        chave_serv,
                        0.0,
                    )
                ),
                2,
            )

            base_ctrl_rateada = round(
                float(
                    base_ctrl_por_servico.get(
                        chave_serv,
                        0.0,
                    )
                ),
                2,
            )
            extra_rateada = round(float(extra_por_servico.get(chave_serv, 0.0)), 2)
            adicional_noturno_rateado = round(
                float(
                    adicional_noturno_por_servico.get(
                        chave_serv,
                        0.0,
                    )
                ),
                2,
            )
            acordo_rateado = round(float(acordo_por_servico.get(chave_serv, 0.0)), 2)

            periodos = sorted(
                serv["periodos"],
                key=lambda p: {"Manhã": 1, "Tarde": 2, "Noite": 3, "Integral": 4}.get(p, 9),
            )
            statuses = [s for s in serv["status"] if s]
            status_exibido = (
                statuses[0]
                if statuses and len(set(statuses)) == 1
                else " / ".join(dict.fromkeys(statuses))
            )
            tipos_unicos = list(dict.fromkeys(tipos_por_servico.get(chave_serv, [])))
            tipo_exibido = tipos_unicos[0] if len(tipos_unicos) == 1 else " / ".join(tipos_unicos)

            linhas.append({
                "Data": data,
                "obra_id": serv["obra_id"],
                "Obra": serv["obra"],
                "Unidade": serv["unidade"],
                "Período do serviço": " + ".join(periodos),
                "Engenheiro": " / ".join(sorted(serv["engenheiros"])),
                "Colaborador": str(colab.get("nome") or "Desconhecido"),
                "Função": str(colab.get("funcao") or "-"),
                "Status": status_exibido,
                "Tipo": tipo_exibido,
                "Base Financeiro (R$)": base_fin_rateada,
                "Base Padrão Financeiro (R$)": base_fin_padrao_rateada,
                "Diária Financeiro (R$)": base_fin_rateada,
                "Custo c/ encargos (R$)": base_ctrl_rateada,
                "Extra (R$)": extra_rateada,
                "Adicional noturno (R$)": adicional_noturno_rateado,
                "Acordos / Bonificações (R$)": acordo_rateado,
                "Total Financeiro (R$)": round(
                    base_fin_rateada
                    + extra_rateada
                    + adicional_noturno_rateado
                    + acordo_rateado,
                    2,
                ),
                "Custo (R$)": round(
                    base_ctrl_rateada
                    + extra_rateada
                    + adicional_noturno_rateado
                    + acordo_rateado,
                    2,
                ),
                "Observação": (
                    " | ".join(
                        dict.fromkeys(
                            serv["observacoes"]
                        )
                    )
                    or (
                        "Jornada noturna 17h–02h"
                        if eh_unidade_sebrae(
                            serv["unidade"]
                        )
                        else ""
                    )
                ),
                "_colaborador_id": colaborador_id,
            })

    return linhas


def _filtrar_rateio_por_obra(linhas, obra_id=None, obra_nome=None):
    if not obra_id and not obra_nome:
        return list(linhas or [])

    alvo_id = str(obra_id or "")
    alvo_nome = normalizar(obra_nome or "")

    return [
        linha
        for linha in linhas or []
        if (
            alvo_id
            and str(linha.get("obra_id") or "") == alvo_id
        )
        or (
            alvo_nome
            and normalizar(linha.get("Obra") or "") == alvo_nome
        )
    ]


def _gerar_excel_dataframe(df, titulo="APROAR - RELATÓRIO"):
    buffer = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatório"
    total_cols = max(1, len(df.columns))
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    c = ws.cell(1, 1, titulo)
    c.font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    c.fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    c.alignment = Alignment(horizontal="center")
    for ci, col in enumerate(df.columns, 1):
        cell = ws.cell(3, ci, str(col))
        cell.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="1D4ED8", end_color="1D4ED8", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    for ri, (_, row) in enumerate(df.iterrows(), 4):
        for ci, col in enumerate(df.columns, 1):
            val = row[col]
            if pd.isna(val):
                val = ""
            cell = ws.cell(ri, ci, val)
            cell.font = Font(name="Arial", size=9)
            if "(R$)" in str(col) and isinstance(val, (int, float)):
                cell.number_format = 'R$ #,##0.00'
    for ci, col in enumerate(df.columns, 1):
        amostra = [len(str(col))] + [len(str(v)) for v in df[col].head(100).tolist()]
        ws.column_dimensions[openpyxl.utils.get_column_letter(ci)].width = min(max(amostra) + 3, 42)
    ws.freeze_panes = "A4"
    wb.save(buffer)
    return buffer.getvalue()


def gerar_excel_dashboard_consolidado(df, tipo, inicio, fim):
    """Excel do Dashboard com resumo, custo por Unidade/Engenheiro e detalhamento."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumo"

    total = len(df)
    presentes = int(df["Status"].apply(status_eh_presenca).sum()) if not df.empty else 0
    faltas = int((df["Status"] == "Falta").sum()) if not df.empty else 0
    atestados = int((df["Status"] == "Atestado").sum()) if not df.empty else 0
    custo = float(df["Custo (R$)"].sum()) if not df.empty else 0.0
    extras = float(df["Extra (R$)"].sum()) if not df.empty else 0.0
    adicionais_noturnos = (
        float(df["Adicional noturno (R$)"].sum())
        if (
            not df.empty
            and "Adicional noturno (R$)" in df.columns
        )
        else 0.0
    )
    taxa = (presentes / total * 100) if total else 0.0

    ws["A1"] = f"APROAR - DASHBOARD {str(tipo).upper()}"
    ws["A1"].font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    ws.merge_cells("A1:B1")
    ws["A2"] = f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
    resumo = [
        ("Convocados / registros", total),
        ("Presentes", presentes),
        ("Faltas", faltas),
        ("Atestados", atestados),
        ("Presença (%)", round(taxa, 1)),
        ("Extras (R$)", extras),
        ("Adicional noturno (R$)", adicionais_noturnos),
        ("Custo total (R$)", custo),
    ]
    for i, (rotulo, valor) in enumerate(resumo, 4):
        ws.cell(i, 1, rotulo).font = Font(name="Arial", size=10, bold=True)
        ws.cell(i, 2, valor)
        if "(R$)" in rotulo:
            ws.cell(i, 2).number_format = 'R$ #,##0.00'
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 18

    def add_df_sheet(nome, dados):
        sh = wb.create_sheet(nome)
        if dados is None or dados.empty:
            sh["A1"] = "Sem dados"
            return
        for ci, col in enumerate(dados.columns, 1):
            cell = sh.cell(1, ci, str(col))
            cell.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1D4ED8", end_color="1D4ED8", fill_type="solid")
        for ri, (_, row) in enumerate(dados.iterrows(), 2):
            for ci, col in enumerate(dados.columns, 1):
                val = row[col]
                if pd.isna(val):
                    val = ""
                cell = sh.cell(ri, ci, val)
                if "(R$)" in str(col) and isinstance(val, (int, float)):
                    cell.number_format = 'R$ #,##0.00'
        for ci, col in enumerate(dados.columns, 1):
            vals = [len(str(col))] + [len(str(v)) for v in dados[col].head(200).tolist()]
            sh.column_dimensions[openpyxl.utils.get_column_letter(ci)].width = min(max(vals) + 3, 42)
        sh.freeze_panes = "A2"

    por_unidade = df.groupby("Unidade", dropna=False)["Custo (R$)"].sum().reset_index().sort_values("Custo (R$)", ascending=False) if not df.empty else pd.DataFrame()
    por_eng = df.groupby("Engenheiro", dropna=False)["Custo (R$)"].sum().reset_index().sort_values("Custo (R$)", ascending=False) if not df.empty else pd.DataFrame()
    add_df_sheet("Custo por Unidade", por_unidade)
    add_df_sheet("Custo por Engenheiro", por_eng)
    add_df_sheet("Detalhamento", df)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def gerar_excel_indicador_prazos(df_resumo, df_eventos, inicio, fim):
    """Relatório de cumprimento com resumo e as datas de cada evento auditável."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    def add(nome, dados, titulo):
        ws = wb.create_sheet(nome)
        total_cols = max(1, len(dados.columns))
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
        ws.cell(1, 1, titulo).font = Font(name="Arial", size=12, bold=True, color="FFFFFF")
        ws.cell(1, 1).fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
        ws.cell(2, 1, f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}")
        if dados.empty:
            ws.cell(4, 1, "Sem dados")
            return
        for ci, col in enumerate(dados.columns, 1):
            c = ws.cell(4, ci, str(col))
            c.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
            c.fill = PatternFill(start_color="1D4ED8", end_color="1D4ED8", fill_type="solid")
        for ri, (_, row) in enumerate(dados.iterrows(), 5):
            for ci, col in enumerate(dados.columns, 1):
                val = row[col]
                if pd.isna(val):
                    val = ""
                ws.cell(ri, ci, val)
        for ci, col in enumerate(dados.columns, 1):
            vals = [len(str(col))] + [len(str(v)) for v in dados[col].head(200).tolist()]
            ws.column_dimensions[openpyxl.utils.get_column_letter(ci)].width = min(max(vals) + 3, 42)
        ws.freeze_panes = "A5"

    add("Resumo", df_resumo, "APROAR - CUMPRIMENTO DE PRAZOS")
    add("Ocorrências", df_eventos, "APROAR - DATAS E OCORRÊNCIAS DE PRAZO")
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def render_dashboard_consulta(key_prefix="dash", engenheiro_fixo=None):
    cabecalho_pagina_aproar(
        "Dashboard",
        "Presença, custos e distribuição da equipe no período selecionado.",
        categoria="ANÁLISE E FECHAMENTO",
    )

    st.markdown('<div class="aproar-filter-shell">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tipo = st.selectbox("Período", ["Diário", "Semanal", "Mensal"], key=f"{key_prefix}_tipo")
    with c2:
        base = st.date_input("Data de referência", value=agora_aproar().date(), format="DD/MM/YYYY", key=f"{key_prefix}_base")
    inicio, fim = _periodo_por_tipo(tipo, base)
    with c3:
        unidades = sorted({o.get("unidade") for o in obras if o.get("unidade")})
        unidade = st.selectbox("Unidade", ["TODAS"] + unidades, key=f"{key_prefix}_unidade")
    with c4:
        if engenheiro_fixo:
            engenheiro = engenheiro_fixo
            st.text_input("Engenheiro", value=engenheiro_fixo, disabled=True, key=f"{key_prefix}_engfix")
        else:
            engenheiro = st.selectbox("Engenheiro", ["TODOS"] + ENGENHEIROS, key=f"{key_prefix}_eng")
    st.markdown('</div>', unsafe_allow_html=True)

    registros = _buscar_convocacoes_intervalo(inicio, fim, None if engenheiro == "TODOS" else engenheiro)
    processados = []
    for r in registros:
        item = _processar_registro_operacional(r)
        if unidade != "TODAS" and item["Unidade"] != unidade:
            continue
        processados.append(item)

    total = len(processados)
    presentes = sum(1 for x in processados if status_eh_presenca(x["Status"]))
    faltas = sum(1 for x in processados if x["Status"] == "Falta")
    atestados = sum(1 for x in processados if x["Status"] == "Atestado")
    custo = sum(float(x["Custo (R$)"]) for x in processados)
    total_extra = sum(float(x["Extra (R$)"]) for x in processados)
    total_adicional_noturno = sum(
        float(x.get("Adicional noturno (R$)") or 0.0)
        for x in processados
    )
    taxa_presenca = (presentes / total * 100) if total else 0.0

    st.markdown(
        f"""
        <div class="aproar-dash-metrics">
            <div class="aproar-dash-card"><div class="aproar-dash-label">Convocados / registros</div><div class="aproar-dash-value">{total}</div><div class="aproar-dash-note">no período</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Presentes</div><div class="aproar-dash-value">{presentes}</div><div class="aproar-dash-note">{taxa_presenca:.1f}% de presença</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Faltas</div><div class="aproar-dash-value">{faltas}</div><div class="aproar-dash-note">registro(s)</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Atestados</div><div class="aproar-dash-value">{atestados}</div><div class="aproar-dash-note">registro(s)</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Custo total</div><div class="aproar-dash-value" style="font-size:24px">{formatar_reais(custo)}</div><div class="aproar-dash-note">Extras: {formatar_reais(total_extra)} · Adic. noturno: {formatar_reais(total_adicional_noturno)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')} • "
        f"Presença: {taxa_presenca:.1f}% • Extras e adicional noturno já incluídos no custo"
    )

    if not processados:
        st.markdown(
            '<div class="aproar-empty-card">Nenhum registro encontrado para os filtros selecionados.</div>',
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(processados)

    titulo_secao_aproar("Custos consolidados", "Distribuição do custo por unidade e por engenheiro.")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Por unidade**")
        por_unidade = (
            df.groupby("Unidade", dropna=False)["Custo (R$)"]
            .sum().reset_index().sort_values("Custo (R$)", ascending=False)
        )
        tabela_aproar(por_unidade, key=f"{key_prefix}_tbl_unidade", altura_max=360)
        if not por_unidade.empty:
            st.bar_chart(por_unidade.set_index("Unidade")["Custo (R$)"], use_container_width=True)
    with g2:
        st.markdown("**Por engenheiro**")
        por_eng = (
            df.groupby("Engenheiro", dropna=False)["Custo (R$)"]
            .sum().reset_index().sort_values("Custo (R$)", ascending=False)
        )
        tabela_aproar(por_eng, key=f"{key_prefix}_tbl_eng", altura_max=360)
        if not por_eng.empty:
            st.bar_chart(por_eng.set_index("Engenheiro")["Custo (R$)"], use_container_width=True)

    titulo_secao_aproar("Detalhamento", "Registros que compõem os totais acima.")
    cols = [
        "Data", "Engenheiro", "Unidade", "Serviço(s)", "Colaborador", "Status", "Tipo",
        "Custo c/ encargos (R$)", "Extra (R$)", "Adicional noturno (R$)",
        "Acordos / Bonificações (R$)", "Custo (R$)"
    ]
    tabela_aproar(df[cols], key=f"{key_prefix}_tbl_detalhe")

    # Excel sob demanda: antes era montado em todo rerun, mesmo sem download.
    assinatura = f"{tipo}|{inicio}|{fim}|{unidade}|{engenheiro}|{len(df)}|{float(df['Custo (R$)'].sum()):.2f}"
    chave_assinatura = f"{key_prefix}_excel_assinatura"
    chave_bytes = f"{key_prefix}_excel_bytes"
    if st.session_state.get(chave_assinatura) != assinatura:
        st.session_state.pop(chave_bytes, None)
        st.session_state[chave_assinatura] = assinatura

    if chave_bytes not in st.session_state:
        if st.button("Preparar Excel", icon=":material/download:", key=f"{key_prefix}_preparar_excel"):
            with st.spinner("Preparando arquivo..."):
                st.session_state[chave_bytes] = gerar_excel_dashboard_consolidado(df, tipo, inicio, fim)
            st.rerun()
    else:
        st.download_button(
            "Baixar Dashboard em Excel",
            data=st.session_state[chave_bytes],
            file_name=f"dashboard_{tipo.lower()}_{inicio.isoformat()}_a_{fim.isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
            use_container_width=True,
            key=f"{key_prefix}_download",
        )

def render_relatorio_visualizador(key_prefix="rel_view", engenheiro_fixo=None):
    cabecalho_pagina_aproar(
        "Relatórios",
        "Consulte os registros da equipe e exporte os dados necessários para conferência.",
        categoria="ANÁLISE E FECHAMENTO",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        inicio = st.date_input(
            "Início",
            value=agora_aproar().date().replace(day=1),
            format="DD/MM/YYYY",
            key=f"{key_prefix}_ini",
        )
    with c2:
        fim = st.date_input(
            "Fim",
            value=agora_aproar().date(),
            format="DD/MM/YYYY",
            key=f"{key_prefix}_fim",
        )
    with c3:
        unidades = sorted(
            {
                o.get("unidade")
                for o in obras
                if o.get("unidade")
            }
        )
        unidade = st.selectbox(
            "Unidade",
            ["TODAS"] + unidades,
            key=f"{key_prefix}_unid",
        )
    with c4:
        obras_opcoes = sorted(
            {
                o.get("nome")
                for o in obras
                if o.get("nome")
                and not eh_obra_placeholder(o)
            }
        )
        obra_filtro = st.selectbox(
            "Obra / Serviço",
            ["TODAS"] + obras_opcoes,
            key=f"{key_prefix}_obra",
        )

    if inicio > fim:
        st.error(
            "A data inicial não pode ser maior que a final."
        )
        return

    registros = _buscar_convocacoes_intervalo(
        inicio,
        fim,
        engenheiro_fixo,
    )

    linhas = ratear_registros_por_servico(registros)

    if unidade != "TODAS":
        linhas = [
            x for x in linhas
            if x["Unidade"] == unidade
        ]

    if obra_filtro != "TODAS":
        linhas = _filtrar_rateio_por_obra(
            linhas,
            obra_nome=obra_filtro,
        )

    if not linhas:
        st.info("Sem registros para o período.")
        return

    df = pd.DataFrame(linhas)

    total = float(df["Custo (R$)"].sum())

    pessoas_dia = (
        df[["Data", "_colaborador_id"]]
        .drop_duplicates()
        .shape[0]
    )

    e1, e2, e3 = st.columns(3)
    e1.metric("CUSTO TOTAL", formatar_reais(total))
    e2.metric("PESSOAS/DIA", pessoas_dia)
    e3.metric(
        "DIAS COM REGISTRO",
        df["Data"].nunique(),
    )

    tabela_aproar(
        df[
            [
                "Data",
                "Unidade",
                "Obra",
                "Período do serviço",
                "Colaborador",
                "Status",
                "Tipo",
                "Custo c/ encargos (R$)",
                "Extra (R$)",
                "Adicional noturno (R$)",
                "Acordos / Bonificações (R$)",
                "Custo (R$)",
            ]
        ],
        key=f"{key_prefix}_tbl_relatorio",
    )

    df_export = df.drop(
        columns=["_colaborador_id"],
        errors="ignore",
    )

    st.download_button(
        "📥 BAIXAR RELATÓRIO EXCEL",
        data=_gerar_excel_dataframe(
            df_export,
            "APROAR - RELATÓRIO DE APONTAMENTOS",
        ),
        file_name=(
            f"relatorio_apontamentos_"
            f"{inicio.isoformat()}_a_{fim.isoformat()}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
        key=f"{key_prefix}_download",
    )


def render_indicadores_cumprimento(key_prefix="ind", engenheiro_fixo=None, mostrar_absenteismo=True):
    cabecalho_pagina_aproar(
        "Indicadores",
        "Acompanhe prazos, ausências e comportamento operacional das equipes.",
        categoria="ANÁLISE E FECHAMENTO",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        inicio = st.date_input("Início", value=agora_aproar().date() - datetime.timedelta(days=30), format="DD/MM/YYYY", key=f"{key_prefix}_ini")
    with c2:
        fim = st.date_input("Fim", value=agora_aproar().date(), format="DD/MM/YYYY", key=f"{key_prefix}_fim")
    with c3:
        unidades = sorted({o.get("unidade") for o in obras if o.get("unidade")})
        unidade_filtro = st.selectbox("Unidade", ["TODAS"] + unidades, key=f"{key_prefix}_unidade")
    if inicio > fim:
        st.error("Período inválido.")
        return

    registros_brutos = _buscar_convocacoes_intervalo(inicio, fim, engenheiro_fixo)
    registros = []
    eventos_prazo = []

    for r in registros_brutos:
        obra = dict_obras.get(r.get("obra_id"), {"unidade": "GERAL"})
        if unidade_filtro != "TODAS" and obra.get("unidade") != unidade_filtro:
            continue
        colab = dict_colaboradores.get(r.get("colaborador_id"), {"nome": "Desconhecido", "valor_diaria": VALOR_DIARIA_PROFISSIONAL})
        status = normalizar_status_operacional(r.get("status"))
        meta = obter_metadata_operacional(r.get("observacao") or "")
        try:
            data_dt = pd.to_datetime(r.get("data"), errors="coerce")
        except Exception:
            data_dt = pd.NaT
        eng = str(r.get("engenheiro") or "N/A")
        nome_colab = str(colab.get("nome") or "Desconhecido")
        registros.append({
            "raw": r,
            "engenheiro": eng,
            "unidade": str(obra.get("unidade") or "GERAL"),
            "colaborador": nome_colab,
            "status": status,
            "valor_diaria": obter_valor_diaria_colaborador(colab),
            "data": data_dt,
            "meta": meta,
        })

        if meta.get("convocado_em"):
            eventos_prazo.append({
                "Engenheiro": eng,
                "Data do serviço": str(r.get("data") or ""),
                "Colaborador": nome_colab,
                "Tipo": "Convocação",
                "Registrado em": str(meta.get("convocado_em") or "").replace("T", " ")[:19],
                "Atrasado": "SIM" if meta.get("convocacao_atrasada") else "NÃO",
            })
        if meta.get("apontado_em"):
            eventos_prazo.append({
                "Engenheiro": eng,
                "Data do serviço": str(r.get("data") or ""),
                "Colaborador": nome_colab,
                "Tipo": "Apontamento",
                "Registrado em": str(meta.get("apontado_em") or "").replace("T", " ")[:19],
                "Atrasado": "SIM" if meta.get("apontamento_atrasado") else "NÃO",
            })

    if not registros:
        st.info("Sem registros no período.")
        return

    por_eng = {}
    for item in registros:
        eng = item["engenheiro"]
        meta = item["meta"]
        d = por_eng.setdefault(eng, {
            "Engenheiro": eng,
            "Convocações auditáveis": 0,
            "Convocações atrasadas": 0,
            "Apontamentos auditáveis": 0,
            "Apontamentos atrasados": 0,
        })
        if meta.get("convocado_em"):
            d["Convocações auditáveis"] += 1
            d["Convocações atrasadas"] += int(bool(meta.get("convocacao_atrasada")))
        if meta.get("apontado_em"):
            d["Apontamentos auditáveis"] += 1
            d["Apontamentos atrasados"] += int(bool(meta.get("apontamento_atrasado")))

    linhas = []
    for d in por_eng.values():
        auditaveis = d["Convocações auditáveis"] + d["Apontamentos auditáveis"]
        atrasos = d["Convocações atrasadas"] + d["Apontamentos atrasados"]
        d["No prazo (%)"] = round(((auditaveis - atrasos) / auditaveis * 100), 1) if auditaveis else None
        linhas.append(d)
    df_prazos = pd.DataFrame(linhas).sort_values("Engenheiro")

    titulo_secao_aproar("Cumprimento por engenheiro", "Convocações e apontamentos realizados dentro e fora do prazo.")
    st.caption("Convocação atrasada = feita após 16h para o próximo dia útil. Apontamento atrasado = salvo em dia posterior ao serviço. Os dois atrasos são medidos separadamente.")
    tabela_aproar(df_prazos, key=f"{key_prefix}_tbl_prazos")

    # Detalhamento clicável/selecionável das datas que geraram atraso.
    df_eventos = pd.DataFrame(eventos_prazo)
    if not df_eventos.empty:
        st.markdown("**Ver datas e ocorrências**")
        op_eng = sorted(df_eventos["Engenheiro"].dropna().astype(str).unique().tolist())
        eng_det = engenheiro_fixo or st.selectbox("Engenheiro para detalhar", op_eng, key=f"{key_prefix}_eng_detalhe")
        somente_atrasos = st.checkbox("Mostrar somente atrasos", value=True, key=f"{key_prefix}_somente_atrasos")
        det = df_eventos[df_eventos["Engenheiro"] == eng_det].copy()
        if somente_atrasos:
            det = det[det["Atrasado"] == "SIM"]
        if det.empty:
            st.success("Nenhuma ocorrência atrasada para este engenheiro no período.")
        else:
            tabela_aproar(det.sort_values(["Data do serviço", "Tipo"], ascending=[False, True]), key=f"{key_prefix}_tbl_ocorrencias")

    st.download_button(
        "📥 BAIXAR INDICADOR DE PRAZOS",
        data=gerar_excel_indicador_prazos(df_prazos, df_eventos, inicio, fim),
        file_name=f"indicador_prazos_{inicio.isoformat()}_a_{fim.isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_download",
    )

    if not mostrar_absenteismo:
        return

    df = pd.DataFrame([{k: v for k, v in x.items() if k not in ["raw", "meta"]} for x in registros])
    total_conv = len(df)
    total_faltas = int((df["status"] == "Falta").sum())
    total_atestados = int((df["status"] == "Atestado").sum())
    total_ausencias = total_faltas + total_atestados
    taxa_absenteismo = (total_ausencias / total_conv * 100) if total_conv else 0.0
    mask_ausencia = df["status"].isin(["Falta", "Atestado"])
    impacto_financeiro = float(df.loc[mask_ausencia, "valor_diaria"].sum())

    st.markdown("---")
    titulo_secao_aproar("Absenteísmo", "Faltas, atestados e impacto por colaborador, dia e unidade.")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("CONVOCAÇÕES", total_conv)
    m2.metric("FALTAS", total_faltas)
    m3.metric("ATESTADOS", total_atestados)
    m4.metric("ABSENTEÍSMO", f"{taxa_absenteismo:.1f}%")
    m5.metric("IMPACTO EST.", formatar_reais(impacto_financeiro))
    st.caption("Impacto estimado = soma das diárias-base associadas às faltas e atestados.")

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("**Colaboradores com mais faltas**")
        df_faltas = df[df["status"] == "Falta"]
        if df_faltas.empty:
            st.info("Nenhuma falta registrada no período.")
        else:
            ranking = (
                df_faltas.groupby("colaborador").size().reset_index(name="Faltas")
                .sort_values(["Faltas", "colaborador"], ascending=[False, True]).reset_index(drop=True)
            )
            ranking.insert(0, "Posição", range(1, len(ranking) + 1))
            tabela_aproar(ranking, key=f"{key_prefix}_tbl_ranking", altura_max=380)

    with r2:
        st.markdown("**Ausências por dia da semana**")
        dias_ordem = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        mapa_dias = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
        df_aus = df[mask_ausencia].copy()
        if df_aus.empty or df_aus["data"].isna().all():
            st.info("Sem ausências com data válida.")
        else:
            df_aus = df_aus.dropna(subset=["data"])
            df_aus["Dia"] = df_aus["data"].dt.weekday.map(mapa_dias)
            resumo_semana = df_aus.groupby(["Dia", "status"]).size().unstack(fill_value=0).reindex(dias_ordem, fill_value=0)
            for coluna in ["Falta", "Atestado"]:
                if coluna not in resumo_semana.columns:
                    resumo_semana[coluna] = 0
            st.bar_chart(resumo_semana[["Falta", "Atestado"]], use_container_width=True)

    st.markdown("**Detalhamento por unidade**")
    resumo_unidades = []
    for und in sorted(df["unidade"].unique()):
        df_u = df[df["unidade"] == und]
        t_u = len(df_u)
        f_u = int((df_u["status"] == "Falta").sum())
        a_u = int((df_u["status"] == "Atestado").sum())
        aus_u = f_u + a_u
        taxa_u = (aus_u / t_u * 100) if t_u else 0.0
        impacto_u = float(df_u.loc[df_u["status"].isin(["Falta", "Atestado"]), "valor_diaria"].sum())
        resumo_unidades.append({
            "Unidade": und,
            "Convocações": t_u,
            "Faltas": f_u,
            "Atestados": a_u,
            "Total Ausências": aus_u,
            "Taxa Absenteísmo (%)": round(taxa_u, 1),
            "Impacto Estimado (R$)": round(impacto_u, 2),
        })
    tabela_aproar(pd.DataFrame(resumo_unidades).sort_values("Taxa Absenteísmo (%)", ascending=False), key=f"{key_prefix}_tbl_abs_unidades")


def incluir_colaborador_direto_apontamento(
    colaborador_id,
    engenheiro,
    data_servico,
    obra_id,
    turno="Integral",
):
    """
    Inclusão direta para apontamento, inclusive retroativo.

    O mesmo colaborador pode ter mais de um serviço no mesmo dia desde que
    os turnos não se sobreponham. Ex.: Manhã + Tarde é permitido.
    """
    turno_novo = normalizar_turno_convocacao(turno)

    cid_alvo = str(colaborador_id or "").strip()

    # Caminho rápido do portal do engenheiro: reaproveita os dados já
    # carregados/cacheados em vez de rodar a rotina completa novamente.
    if indisponiveis_map is not None:
        ind = dict(indisponiveis_map or {}).get(cid_alvo)
    else:
        ind = obter_indisponibilidade_colaborador(
            colaborador_id,
            data_servico,
        )

    if ind:
        return False, (
            f"Colaborador indisponível: {ind.get('motivo','Indisponível')} "
            f"({ind.get('inicio')} a {ind.get('fim')})."
        )

    if existentes_data is not None:
        existentes = [
            reg
            for reg in (existentes_data or [])
            if str(reg.get("colaborador_id") or "").strip() == cid_alvo
        ]
    else:
        existentes = buscar_convocacao_existente(
            colaborador_id,
            data_servico,
        )

    obra_nova = dict_obras.get(obra_id, {}) if "dict_obras" in globals() else {}
    unidade_nova = str(obra_nova.get("unidade") or "")

    for reg in existentes:
        turno_existente = turno_da_convocacao(reg)

        # Outro serviço em turno diferente é permitido.
        if not turnos_se_sobrepoem(
            turno_existente,
            turno_novo,
        ):
            continue

        eng_existente = str(
            reg.get("engenheiro")
            or "outro engenheiro"
        )

        if normalizar(eng_existente) != normalizar(engenheiro):
            registrar_conflito_convocacao(
                reg,
                engenheiro,
                turno_tentativa=turno_novo,
                unidade_tentativa=unidade_nova,
            )
            return False, (
                f"Esse colaborador já está com {eng_existente} em "
                f"{turno_existente}. O conflito foi registrado para o Paulo."
            )

        return False, (
            f"Esse colaborador já está no seu apontamento em {turno_existente}. "
            f"Escolha outro turno para adicionar um segundo serviço."
        )

    _garantir_multiturno_neon()

    agora = agora_aproar()
    meta = {
        "convocado_em": agora.isoformat(),
        "convocado_por": str(engenheiro),
        "incluido_direto_apontamento": True,
        "convocacao_atrasada": bool(
            agora.hour >= 16
            and data_servico == proximo_dia_util(agora.date())
        ),
        "apontado_em": agora.isoformat(),
        "ultimo_apontamento_em": agora.isoformat(),
        "apontado_por": str(engenheiro),
        "apontamento_atrasado": bool(
            agora.date() > data_servico
        ),
        "servicos_extras": [],
        "servicos_adicionais": [],
        "periodo_servico_principal": turno_novo,
    }

    status_inicial = {
        "Manhã": "Presente (Só Manhã)",
        "Tarde": "Presente (Só Tarde)",
    }.get(turno_novo, "Presente (Integral)")

    payload = {
        "obra_id": obra_id,
        "colaborador_id": colaborador_id,
        "data": data_servico.isoformat(),
        "engenheiro": engenheiro,
        "status": status_inicial,
        "valor_extra": 0,
        "observacao": montar_observacao_operacional(
            turno_novo,
            "",
            meta,
        ),
    }

    if schema_producao_disponivel():
        payload.update({
            "turno": turno_novo,
            "criado_em": agora.isoformat(),
            "criado_por": str(engenheiro),
        })

    try:
        retorno = (
            supabase.table("convocacoes")
            .insert(payload)
            .execute()
            .data
            or []
        )

        novo_id = (
            retorno[0].get("id")
            if retorno
            else ""
        )

        registrar_auditoria_prod(
            "convocacao",
            novo_id,
            "INCLUIR_DIRETO_APONTAMENTO",
            engenheiro,
            depois={
                "colaborador_id": str(colaborador_id),
                "data": data_servico,
                "turno": turno_novo,
                "obra_id": str(obra_id),
            },
            contexto={
                "retroativo": bool(
                    agora.date() > data_servico
                )
            },
        )

        limpar_cache_operacional()
        return True, (
            f"Colaborador incluído em {turno_novo}. "
            "Você pode adicioná-lo novamente em outro turno compatível."
        )

    except Exception:
        return False, (
            "Não foi possível incluir o colaborador neste serviço/turno."
        )


def incluir_multiplos_servicos_direto_apontamento(
    colaborador_id,
    engenheiro,
    data_servico,
    servicos,
    existentes_data=None,
    indisponiveis_map=None,
):
    """
    Inclui um ou vários serviços para o mesmo colaborador.

    Regras:
    - Vários serviços no MESMO turno são permitidos e ficam no mesmo registro,
      para que a meia diária daquele turno seja rateada entre as obras.
    - Turnos compatíveis diferentes (Manhã + Tarde, etc.) viram registros separados.
    - Integral + outro turno diferente continua bloqueado.
    """
    itens = []
    vistos = set()

    for item in servicos or []:
        if not isinstance(item, dict):
            continue

        obra_id = item.get("obra_id")
        turno = normalizar_turno_convocacao(
            item.get("turno") or "Integral"
        )

        if not obra_id:
            continue

        obra_ref = (
            dict_obras.get(obra_id, {})
            if "dict_obras" in globals()
            else {}
        )

        chave = (str(obra_id), turno)
        if chave in vistos:
            continue

        vistos.add(chave)
        itens.append({
            "obra_id": obra_id,
            "obra": str(
                obra_ref.get("nome")
                or "Serviço"
            ),
            "unidade": str(
                obra_ref.get("unidade")
                or ""
            ),
            "turno": turno,
        })

    if not itens:
        return False, "Selecione pelo menos um serviço."

    if len({str(x["obra_id"]) for x in itens}) != len(itens):
        return False, "Os serviços selecionados devem ser diferentes."

    # Agrupa serviços do mesmo turno. Mesmo turno = rateio dentro do mesmo registro.
    grupos_turno = {}
    for item in itens:
        grupos_turno.setdefault(
            item["turno"],
            [],
        ).append(item)

    turnos_novos = list(grupos_turno.keys())

    # Entre grupos diferentes, não pode haver sobreposição.
    for i, turno_atual in enumerate(turnos_novos):
        for turno_outro in turnos_novos[i + 1:]:
            if turnos_se_sobrepoem(
                turno_atual,
                turno_outro,
            ):
                return False, (
                    f"Os turnos {turno_atual} e {turno_outro} se sobrepõem. "
                    "Use o mesmo turno nos dois serviços quando ambos ocorreram "
                    "no mesmo período, ou escolha períodos compatíveis."
                )

    cid_alvo = str(
        colaborador_id
        or ""
    ).strip()

    if indisponiveis_map is not None:
        ind = dict(
            indisponiveis_map
            or {}
        ).get(cid_alvo)
    else:
        ind = obter_indisponibilidade_colaborador(
            colaborador_id,
            data_servico,
        )

    if ind:
        return False, (
            f"Colaborador indisponível: {ind.get('motivo','Indisponível')} "
            f"({ind.get('inicio')} a {ind.get('fim')})."
        )

    if existentes_data is not None:
        existentes = [
            reg
            for reg in (existentes_data or [])
            if str(
                reg.get("colaborador_id")
                or ""
            ).strip() == cid_alvo
        ]
    else:
        existentes = buscar_convocacao_existente(
            colaborador_id,
            data_servico,
        )

    # Valida cada grupo/turno contra registros que já existiam antes do clique.
    for turno_novo, itens_turno in grupos_turno.items():
        unidade_nova = str(
            itens_turno[0].get("unidade")
            or ""
        )

        for reg in existentes:
            turno_existente = turno_da_convocacao(reg)

            if not turnos_se_sobrepoem(
                turno_existente,
                turno_novo,
            ):
                continue

            eng_existente = str(
                reg.get("engenheiro")
                or "outro engenheiro"
            )

            if normalizar(eng_existente) != normalizar(engenheiro):
                registrar_conflito_convocacao(
                    reg,
                    engenheiro,
                    turno_tentativa=turno_novo,
                    unidade_tentativa=unidade_nova,
                )
                return False, (
                    f"Esse colaborador já está com {eng_existente} em "
                    f"{turno_existente}. O conflito foi registrado para o Paulo."
                )

            # Mesmo engenheiro + mesmo turno: não é conflito.
            # É o caso de uma pessoa fazer duas obras/serviços no mesmo período.
            if (
                normalizar_turno_convocacao(turno_existente)
                == normalizar_turno_convocacao(turno_novo)
            ):
                meta_existente = obter_metadata_operacional(
                    reg.get("observacao")
                    or ""
                )
                obra_principal_existente = dict_obras.get(
                    reg.get("obra_id"),
                    {},
                )

                periodo_principal_existente = str(
                    meta_existente.get(
                        "periodo_servico_principal"
                    )
                    or turno_existente
                    or turno_novo
                )

                adicionais_existentes = list(
                    _normalizar_servicos_adicionais(
                        meta_existente
                    )
                )

                # Se o registro ainda era placeholder, o primeiro serviço novo
                # vira principal. Caso contrário, preservamos o principal atual
                # e anexamos apenas os novos serviços como adicionais.
                principal_real = bool(
                    obra_principal_existente
                    and not eh_obra_placeholder(
                        obra_principal_existente
                    )
                )

                novos_para_anexar = list(itens_turno)

                if not principal_real and novos_para_anexar:
                    novo_principal = novos_para_anexar.pop(0)
                    obra_id_principal_final = novo_principal[
                        "obra_id"
                    ]
                    periodo_principal_existente = turno_novo
                else:
                    obra_id_principal_final = reg.get(
                        "obra_id"
                    )

                chaves_existentes = set()

                if principal_real:
                    chaves_existentes.add(
                        str(reg.get("obra_id") or "")
                    )

                for adicional in adicionais_existentes:
                    chave_adic = str(
                        adicional.get("obra_id")
                        or ""
                    )
                    if not chave_adic:
                        chave_adic = normalizar(
                            adicional.get("servico")
                            or ""
                        )
                    chaves_existentes.add(chave_adic)

                for novo_servico in novos_para_anexar:
                    chave_nova = str(
                        novo_servico.get("obra_id")
                        or ""
                    )
                    if not chave_nova:
                        chave_nova = normalizar(
                            novo_servico.get("obra")
                            or ""
                        )

                    if chave_nova in chaves_existentes:
                        continue

                    adicionais_existentes.append({
                        "servico": novo_servico[
                            "obra"
                        ],
                        "periodo": turno_novo,
                        "obra_id": str(
                            novo_servico[
                                "obra_id"
                            ]
                        ),
                        "unidade": novo_servico[
                            "unidade"
                        ],
                    })
                    chaves_existentes.add(
                        chave_nova
                    )

                meta_existente[
                    "periodo_servico_principal"
                ] = periodo_principal_existente
                meta_existente[
                    "servicos_adicionais"
                ] = adicionais_existentes
                meta_existente[
                    "servicos_extras"
                ] = [
                    x.get("servico")
                    for x in adicionais_existentes
                    if x.get("servico")
                ]
                meta_existente[
                    "ultimo_apontamento_em"
                ] = agora_aproar().isoformat()
                meta_existente[
                    "apontado_por"
                ] = str(engenheiro)

                _turno_obs, obs_livre_existente = (
                    decompor_observacao_operacional(
                        reg.get("observacao")
                        or ""
                    )
                )

                nova_obs_existente = (
                    montar_observacao_operacional(
                        turno_novo,
                        obs_livre_existente,
                        meta_existente,
                    )
                )

                try:
                    supabase.table(
                        "convocacoes"
                    ).update(
                        {
                            "obra_id": obra_id_principal_final,
                            "observacao": nova_obs_existente,
                        }
                    ).eq(
                        "id",
                        reg.get("id"),
                    ).execute()

                    limpar_cache_convocacoes()

                    return True, (
                        f"{len(itens_turno)} serviço(s) vinculado(s) "
                        f"ao apontamento existente de {turno_novo}."
                    )

                except Exception as e:
                    return False, (
                        "Não foi possível vincular o novo serviço ao "
                        f"apontamento existente. Detalhe: {str(e)[:120]}"
                    )

            return False, (
                f"Esse colaborador já está no seu apontamento em "
                f"{turno_existente}. Escolha um período compatível."
            )

    _garantir_multiturno_neon()

    agora = agora_aproar()
    payloads = []
    grupos_payload = []

    for turno_novo, itens_turno in grupos_turno.items():
        principal = itens_turno[0]
        adicionais = []

        for extra in itens_turno[1:]:
            adicionais.append({
                "servico": extra["obra"],
                "periodo": turno_novo,
                "obra_id": str(extra["obra_id"]),
                "unidade": extra["unidade"],
            })

        meta = {
            "convocado_em": agora.isoformat(),
            "convocado_por": str(engenheiro),
            "incluido_direto_apontamento": True,
            "convocacao_atrasada": bool(
                agora.hour >= 16
                and data_servico
                == proximo_dia_util(agora.date())
            ),
            "apontado_em": agora.isoformat(),
            "ultimo_apontamento_em": agora.isoformat(),
            "apontado_por": str(engenheiro),
            "apontamento_atrasado": bool(
                agora.date() > data_servico
            ),
            "periodo_servico_principal": turno_novo,
            "servicos_adicionais": adicionais,
            "servicos_extras": [
                x["servico"]
                for x in adicionais
            ],
        }

        status_inicial = {
            "Manhã": "Presente (Só Manhã)",
            "Tarde": "Presente (Só Tarde)",
        }.get(
            turno_novo,
            "Presente (Integral)",
        )

        payload = {
            "obra_id": principal["obra_id"],
            "colaborador_id": colaborador_id,
            "data": data_servico.isoformat(),
            "engenheiro": engenheiro,
            "status": status_inicial,
            "valor_extra": 0,
            "observacao": montar_observacao_operacional(
                turno_novo,
                "",
                meta,
            ),
        }

        if schema_producao_disponivel():
            payload.update({
                "turno": turno_novo,
                "criado_em": agora.isoformat(),
                "criado_por": str(engenheiro),
            })

        payloads.append(payload)
        grupos_payload.append({
            "turno": turno_novo,
            "servicos": itens_turno,
        })

    try:
        retorno = (
            supabase.table("convocacoes")
            .insert(payloads)
            .execute()
            .data
            or []
        )

        for idx, grupo in enumerate(grupos_payload):
            registro = (
                retorno[idx]
                if idx < len(retorno)
                else {}
            )

            registrar_auditoria_prod(
                "convocacao",
                registro.get("id") or "",
                "INCLUIR_DIRETO_APONTAMENTO",
                engenheiro,
                depois={
                    "colaborador_id": str(colaborador_id),
                    "data": data_servico,
                    "turno": grupo["turno"],
                    "servicos": [
                        {
                            "obra_id": str(x["obra_id"]),
                            "obra": x["obra"],
                            "unidade": x["unidade"],
                        }
                        for x in grupo["servicos"]
                    ],
                },
                contexto={
                    "retroativo": bool(
                        agora.date() > data_servico
                    ),
                    "origem": "portal_engenheiro_multisservico",
                },
            )

        limpar_cache_convocacoes()

        return True, (
            f"{len(itens)} serviço(s) adicionado(s) para o colaborador."
        )

    except Exception as e:
        return False, (
            "Não foi possível incluir os serviços do colaborador. "
            f"Detalhe: {str(e)[:120]}"
        )


def render_apontamento_operacional(engenheiro_fixo=None, key_prefix="apont"):
    cabecalho_pagina_aproar(
        "Apontamento",
        "Registre presença, ausência, extras e serviços executados pela equipe.",
        categoria="OPERAÇÃO",
    )
    st.caption("Presença e extra são independentes. O mesmo colaborador pode atuar em mais de um serviço da mesma Unidade sem duplicar convocação nem diária.")
    c1, c2, c3 = st.columns(3)
    with c1:
        if engenheiro_fixo:
            # O engenheiro vem do seletor principal do portal. A chave do campo
            # acompanha o nome para o Streamlit não reaproveitar um valor antigo
            # (ex.: trocar NETO por JOEL e o campo desabilitado continuar mostrando JOEL).
            engenheiro = str(engenheiro_fixo)
            eng_key = re.sub(r"[^A-Za-z0-9_-]+", "_", normalizar(engenheiro)) or "ENG"
            st.text_input(
                "Engenheiro",
                value=engenheiro,
                disabled=True,
                key=f"{key_prefix}_engfix_{eng_key}",
            )
        else:
            engenheiro = st.selectbox("Engenheiro", ENGENHEIROS, key=f"{key_prefix}_eng")
    with c2:
        data_apont = st.date_input("Data do serviço", value=agora_aproar().date(), format="DD/MM/YYYY", key=f"{key_prefix}_data")

    try:
        convs = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro).eq("data", data_apont.isoformat()).execute().data or []
    except Exception:
        convs = []
    for c in convs:
        c["dados_obra"] = dict_obras.get(c.get("obra_id"), {"unidade": "Desconhecida", "nome": NOME_OBRA_PLACEHOLDER})
    unidades_conv = sorted({(c.get("dados_obra") or {}).get("unidade", "Desconhecida") for c in convs})
    with c3:
        unidade_filtro = st.selectbox("Unidade", ["TODAS"] + unidades_conv, key=f"{key_prefix}_unidade")

    with st.expander("➕ Incluir colaborador que não estava na convocação", expanded=False):
        st.caption("A lista contém todos os colaboradores cadastrados e serve para correções ou inclusões excepcionais.")
        labels = {f"{c.get('nome')} ({c.get('funcao','-')})": c.get("id") for c in sorted(colaboradores, key=lambda x: normalizar(x.get('nome','')))}
        inc1, inc2 = st.columns(2)
        with inc1:
            nome_sel = st.selectbox("Colaborador", ["— Selecione —"] + list(labels.keys()), key=f"{key_prefix}_inc_colab")
        with inc2:
            unidades = sorted({o.get("unidade") for o in obras if o.get("unidade")})
            unid_inc = st.selectbox("Unidade", unidades, key=f"{key_prefix}_inc_unid") if unidades else None
        obras_inc = obras_reais_da_unidade(unid_inc) if unid_inc else []
        mapa_inc = {o.get("nome"): o.get("id") for o in obras_inc}
        obra_inc = st.selectbox("Obra / Serviço", ["— Selecione —"] + list(mapa_inc.keys()), key=f"{key_prefix}_inc_obra")
        if st.button("INCLUIR NO APONTAMENTO", type="primary", use_container_width=True, key=f"{key_prefix}_inc_btn"):
            if nome_sel == "— Selecione —" or obra_inc not in mapa_inc:
                st.warning("Selecione colaborador, Unidade e Obra/Serviço.")
            else:
                ok, msg = incluir_colaborador_direto_apontamento(labels[nome_sel], engenheiro, data_apont, mapa_inc[obra_inc])
                (st.success if ok else st.warning)(msg)
                if ok:
                    st.rerun()

    render = [c for c in convs if unidade_filtro == "TODAS" or (c.get("dados_obra") or {}).get("unidade") == unidade_filtro]
    if not render:
        st.info("Nenhuma equipe para os filtros selecionados.")
        return

    if st.button("✅ MARCAR EXIBIDOS COMO PRESENTE INTEGRAL", use_container_width=True, key=f"{key_prefix}_allpres"):
        for c in render:
            try:
                supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", c.get("id")).execute()
            except Exception:
                pass
        st.rerun()

    periodos_servico = ["Integral", "Manhã", "Tarde", "Noite", "Outro"]

    # Precisamos enxergar TODAS as convocações do dia, inclusive as feitas por
    # outros engenheiros. Assim, se uma pessoa já tem Manhã em uma Unidade e
    # Tarde em outra, cada convocação vira seu próprio apontamento e não faz
    # sentido oferecer um "2º serviço" dentro de nenhum dos dois registros.
    try:
        todas_convs_data = (
            supabase.table("convocacoes")
            .select("*")
            .eq("data", data_apont.isoformat())
            .execute().data or []
        )
    except Exception:
        todas_convs_data = list(convs)

    convs_por_colaborador = {}
    for item_conv in todas_convs_data:
        chave_colab = str(item_conv.get("colaborador_id") or "")
        convs_por_colaborador.setdefault(chave_colab, []).append(item_conv)

    for conv in render:
        c_id = conv.get("id")
        colab = dict_colaboradores.get(conv.get("colaborador_id"), {"nome": "Desconhecido", "funcao": "-"})
        unidade = (conv.get("dados_obra") or {}).get("unidade", "Desconhecida")
        obras_card = obras_reais_da_unidade(unidade)
        mapa_obras = {o.get("nome"): o.get("id") for o in obras_card}
        opcoes_obras = ["— Selecione a Obra/Serviço —"] + list(mapa_obras.keys())
        obra_atual = dict_obras.get(conv.get("obra_id"), {})
        nome_obra = obra_atual.get("nome", "")
        idx_obra = opcoes_obras.index(nome_obra) if nome_obra in mapa_obras else 0
        status_atual = normalizar_status_operacional(conv.get("status"))
        idx_st = OPCOES_STATUS_PRESENCA.index(status_atual) if status_atual in OPCOES_STATUS_PRESENCA else 0
        turno, obs_livre = decompor_observacao_operacional(conv.get("observacao") or "")
        meta_atual = obter_metadata_operacional(conv.get("observacao") or "")
        adicionais_atuais = [x for x in _normalizar_servicos_adicionais(meta_atual) if x.get("servico") in mapa_obras]
        atraso = bool(meta_atual.get("apontamento_atrasado"))
        periodo_principal_atual = str(meta_atual.get("periodo_servico_principal") or turno or "Integral")
        if periodo_principal_atual not in periodos_servico:
            periodo_principal_atual = "Outro"

        mesma_pessoa_no_dia = convs_por_colaborador.get(str(conv.get("colaborador_id") or ""), [])
        outras_convocacoes_dia = [
            outra for outra in mesma_pessoa_no_dia
            if str(outra.get("id")) != str(c_id)
        ]
        tem_convocacao_separada_no_dia = bool(outras_convocacoes_dia)

        resumo_outras_alocacoes = []
        for outra in outras_convocacoes_dia:
            outra_obra = dict_obras.get(outra.get("obra_id"), {})
            outra_unidade = str(outra_obra.get("unidade") or "-")
            outro_turno, _ = decompor_observacao_operacional(outra.get("observacao") or "")
            outro_eng = str(outra.get("engenheiro") or "-")
            resumo_outras_alocacoes.append(f"{outro_turno} • {outra_unidade} • {outro_eng}")

        with st.container(border=True):
            st.markdown(f"### {colab.get('nome','-')}")
            st.caption(f"{colab.get('funcao','-')} • {unidade} • Convocado: {turno}")
            if atraso:
                st.warning("🟧 Apontamento realizado com atraso — salvo em data posterior ao serviço.")
            elif (
                apontamento_esta_atrasado(
                    data_apont,
                    unidade=unidade,
                    agora=agora_aproar(),
                )
                and not meta_atual.get("apontado_em")
            ):
                st.warning("🟧 Este apontamento é retroativo. Ao salvar, o atraso será registrado.")
            elif (
                eh_unidade_sebrae(unidade)
                and data_apont < agora_aproar().date()
                and not meta_atual.get("apontado_em")
            ):
                st.info(
                    "🌙 SEBRAE: a jornada 17h–02h pertence ao dia do serviço. "
                    "O apontamento feito até 09:29 do dia seguinte continua no prazo."
                )

            with st.container():
                f1, f2 = st.columns([1, 1.7])
                with f1:
                    status_sel = st.selectbox("Status", OPCOES_STATUS_PRESENCA, index=idx_st, key=f"{key_prefix}_st_{c_id}")
                with f2:
                    obra_sel = st.selectbox("Obra / Serviço principal", opcoes_obras, index=idx_obra, key=f"{key_prefix}_obra_{c_id}")

                idx_pp = periodos_servico.index(periodo_principal_atual)
                periodo_principal = st.selectbox("Período no serviço principal", periodos_servico, index=idx_pp, key=f"{key_prefix}_periodo_principal_{c_id}")

                # O 2º serviço só aparece quando esta é a ÚNICA convocação da
                # pessoa no dia. Se já existe outra convocação (ex.: Manhã em
                # Maracanaú e Tarde em FIEC), cada turno/unidade deve ser
                # apontado no seu próprio registro.
                segundo_servico = "— Nenhum —"
                segundo_periodo = "Tarde"
                if not tem_convocacao_separada_no_dia:
                    st.markdown("**Outro serviço na mesma Unidade (opcional)**")
                    opcoes_adic = ["— Nenhum —"] + list(mapa_obras.keys())
                    adic_atual = adicionais_atuais[0]["servico"] if adicionais_atuais else "— Nenhum —"
                    idx_adic = opcoes_adic.index(adic_atual) if adic_atual in opcoes_adic else 0
                    s1, s2 = st.columns([1.7, 1])
                    with s1:
                        segundo_servico = st.selectbox(
                            "2º serviço",
                            opcoes_adic,
                            index=idx_adic,
                            key=f"{key_prefix}_seg_serv_{c_id}",
                        )
                    with s2:
                        periodo_adic_atual = adicionais_atuais[0].get("periodo", "Tarde") if adicionais_atuais else "Tarde"
                        if periodo_adic_atual not in periodos_servico:
                            periodo_adic_atual = "Outro"
                        segundo_periodo = st.selectbox(
                            "Período do 2º serviço",
                            periodos_servico,
                            index=periodos_servico.index(periodo_adic_atual),
                            key=f"{key_prefix}_seg_periodo_{c_id}",
                        )
                else:
                    detalhe_aloc = " | ".join(resumo_outras_alocacoes)
                    st.caption(
                        "Este colaborador já possui outra convocação neste dia. "
                        "Cada turno/unidade será apontado separadamente."
                        + (f" Outra alocação: {detalhe_aloc}." if detalhe_aloc else "")
                    )

                tipo_key = f"{key_prefix}_tipo_diaria_{c_id}"
                diaria_key = f"{key_prefix}_custo_pago_{c_id}"
                extra_key = f"{key_prefix}_valor_extra_{c_id}"
                adicional_noturno_key = (
                    f"{key_prefix}_adicional_noturno_{c_id}"
                )

                tipo_atual = tipo_diaria_registro(
                    conv
                )
                diaria_atual = (
                    valor_diaria_financeiro_registro(
                        conv,
                        colab,
                    )
                )
                extra_atual = valor_extra_registro(
                    conv
                )
                adicional_noturno_atual = (
                    valor_adicional_noturno_registro(
                        conv
                    )
                )
                eh_sebrae_card = eh_unidade_sebrae(
                    unidade
                )

                if eh_sebrae_card:
                    st.session_state[
                        tipo_key
                    ] = "Diária"
                elif tipo_key not in st.session_state:
                    st.session_state[
                        tipo_key
                    ] = tipo_atual

                if diaria_key not in st.session_state:
                    st.session_state[
                        diaria_key
                    ] = (
                        diaria_atual
                        if diaria_atual > 0
                        else valor_financeiro_padrao_colaborador(
                            colab,
                            (
                                "Diária"
                                if eh_sebrae_card
                                else tipo_atual
                            ),
                        )
                    )

                if extra_key not in st.session_state:
                    st.session_state[
                        extra_key
                    ] = extra_atual

                if (
                    adicional_noturno_key
                    not in st.session_state
                ):
                    st.session_state[
                        adicional_noturno_key
                    ] = (
                        adicional_noturno_atual
                        if adicional_noturno_atual > 0
                        else (
                            VALOR_ADICIONAL_NOTURNO_SEBRAE
                            if eh_sebrae_card
                            else 0.0
                        )
                    )

                def _ajustar_diaria_desktop(
                    _tipo_key=tipo_key,
                    _diaria_key=diaria_key,
                    _colab=colab,
                ):
                    st.session_state[
                        _diaria_key
                    ] = (
                        valor_financeiro_padrao_colaborador(
                            _colab,
                            st.session_state.get(
                                _tipo_key,
                                "Diária",
                            ),
                        )
                    )

                categoria_txt = (
                    categoria_diaria_colaborador(
                        colab
                    )
                )

                if eh_sebrae_card:
                    p1, p2, p3, p4, p5 = st.columns(
                        [1, 1, 1, 1, 1.2]
                    )
                else:
                    p1, p2, p3, p5 = st.columns(
                        [1, 1, 1, 1.2]
                    )
                    p4 = None

                with p1:
                    tipo_diaria_sel = st.selectbox(
                        "Diária / Meia diária",
                        TIPOS_DIARIA,
                        key=tipo_key,
                        on_change=_ajustar_diaria_desktop,
                        disabled=eh_sebrae_card,
                    )

                with p2:
                    valor_diaria_financeiro = (
                        st.number_input(
                            "Diária (R$)",
                            min_value=0.0,
                            step=10.0,
                            disabled=(
                                not status_eh_presenca(
                                    status_sel
                                )
                            ),
                            key=diaria_key,
                            help=(
                                "Valor efetivamente pago pela diária. "
                                "Pode ser alterado; ex.: R$ 150."
                            ),
                        )
                    )

                with p3:
                    valor_extra = st.number_input(
                        "Extra (R$)",
                        min_value=0.0,
                        step=10.0,
                        disabled=(
                            not status_eh_presenca(
                                status_sel
                            )
                        ),
                        key=extra_key,
                        help=(
                            "Horas extras, produção ou outro valor "
                            "que não faça parte da diária."
                        ),
                    )

                if eh_sebrae_card:
                    with p4:
                        valor_adicional_noturno = (
                            st.number_input(
                                "Adic. noturno (R$)",
                                min_value=0.0,
                                step=10.0,
                                disabled=(
                                    not status_eh_presenca(
                                        status_sel
                                    )
                                ),
                                key=(
                                    adicional_noturno_key
                                ),
                            )
                        )
                else:
                    valor_adicional_noturno = 0.0

                with p5:
                    valor_acordo = st.number_input(
                        "Acordos / Bonificações (R$)",
                        min_value=0.0,
                        value=(
                            float(
                                conv.get(
                                    "valor_acordo"
                                )
                                or 0.0
                            )
                            if status_eh_presenca(
                                status_sel
                            )
                            else 0.0
                        ),
                        step=10.0,
                        disabled=(
                            not status_eh_presenca(
                                status_sel
                            )
                        ),
                        key=(
                            f"{key_prefix}_acordo_{c_id}"
                        ),
                    )

                custo_ctrl_preview = (
                    valor_controladoria_padrao_colaborador(
                        colab,
                        tipo_diaria_sel,
                    )
                    if status_eh_presenca(
                        status_sel
                    )
                    else 0.0
                )

                total_fin_preview = (
                    float(
                        valor_diaria_financeiro
                    )
                    + float(valor_extra)
                    + float(
                        valor_adicional_noturno
                    )
                    + float(valor_acordo)
                    if status_eh_presenca(
                        status_sel
                    )
                    else 0.0
                )

                st.caption(
                    f"{categoria_txt} · "
                    f"Diária {formatar_reais(valor_diaria_financeiro)} · "
                    f"Extra {formatar_reais(valor_extra)}"
                    + (
                        f" · Noturno {formatar_reais(valor_adicional_noturno)}"
                        if eh_sebrae_card
                        else ""
                    )
                    + f" · Acordos/Bonificações {formatar_reais(valor_acordo)} "
                    f"· Financeiro {formatar_reais(total_fin_preview)} "
                    f"· Controladoria base {formatar_reais(custo_ctrl_preview)}"
                )

                if eh_sebrae_card:
                    st.caption(
                        "🌙 SEBRAE: 17h–02h = diária integral. "
                        "Adicional noturno padrão de R$ 90,00."
                    )
                obs_nova = st.text_input("Observação / justificativa", value=obs_livre, key=f"{key_prefix}_obs_{c_id}")
                salvar = st.button("💾 SALVAR APONTAMENTO", type="primary", use_container_width=True, key=f"{key_prefix}_salvar_{c_id}")

            if salvar:
                if obra_sel not in mapa_obras:
                    st.warning("Selecione a Obra/Serviço principal antes de salvar.")
                elif segundo_servico == obra_sel:
                    st.warning("O 2º serviço deve ser diferente do serviço principal.")
                else:
                    adicionais = []
                    # Se já há outra convocação separada no mesmo dia, limpamos
                    # qualquer 2º serviço antigo desse registro para não duplicar
                    # a informação entre os dois apontamentos.
                    if (not tem_convocacao_separada_no_dia) and segundo_servico in mapa_obras:
                        adicionais.append({"servico": segundo_servico, "periodo": segundo_periodo})
                    meta = registrar_metadata_apontamento(
                        conv,
                        data_apont,
                        apontado_por=engenheiro,
                        periodo_principal=periodo_principal,
                        servicos_adicionais=adicionais,
                        unidade_servico=unidade,
                    )
                    nova_obs = montar_observacao_operacional(turno, obs_nova, meta)
                    try:
                        presente_final = status_eh_presenca(status_sel)
                        tipo_diaria_final = (
                            "Diária"
                            if eh_sebrae_card
                            else normalizar_tipo_diaria(tipo_diaria_sel)
                        )
                        custo_pago_final = (
                            float(
                                valor_diaria_financeiro
                            )
                            if presente_final
                            else 0.0
                        )
                        valor_extra_final = (
                            float(
                                valor_extra
                            )
                            if presente_final
                            else 0.0
                        )
                        valor_adicional_noturno_final = (
                            float(valor_adicional_noturno)
                            if presente_final
                            else 0.0
                        )
                        valor_acordo_final = float(valor_acordo) if presente_final else 0.0
                        custo_encargos_final = (
                            valor_controladoria_padrao_colaborador(
                                colab,
                                tipo_diaria_final,
                            )
                            if presente_final
                            else 0.0
                        )
                        supabase.table("convocacoes").update({
                            "obra_id": mapa_obras[obra_sel],
                            "status": status_sel,
                            "tipo_diaria": tipo_diaria_final,
                            "custo_pago": custo_pago_final,
                            "valor_extra": valor_extra_final,
                            "valor_adicional_noturno": valor_adicional_noturno_final,
                            "valor_acordo": valor_acordo_final,
                            "custo_encargos_base": custo_encargos_final,
                            "observacao": nova_obs,
                        }).eq("id", c_id).execute()
                        salvar_apontamento_estruturado(
                            conv,
                            data_apont,
                            engenheiro,
                            status_sel,
                            valor_extra_final,
                            obs_nova,
                            mapa_obras[obra_sel],
                            periodo_principal,
                            adicionais,
                            tipo_diaria=tipo_diaria_final,
                            custo_pago=custo_pago_final,
                            valor_acordo=valor_acordo_final,
                            valor_adicional_noturno=valor_adicional_noturno_final,
                            custo_encargos_base=custo_encargos_final,
                        )
                        limpar_cache_operacional()
                        st.success(f"Apontamento de {colab.get('nome','-')} salvo.")
                        st.rerun()
                    except Exception:
                        st.error("Não foi possível salvar. Tente novamente.")


def render_indisponibilidades_admin():
    cabecalho_pagina_aproar(
        "Indisponibilidade",
        "Registre férias, atestados, afastamentos e outros períodos em que o colaborador não pode ser convocado.",
        categoria="OPERAÇÃO",
    )
    st.caption("Controle manual do Paulo para férias, atestados e afastamentos. Pessoas indisponíveis ficam bloqueadas na convocação.")
    if not colaboradores:
        st.info("Nenhum colaborador cadastrado.")
        return
    labels = {f"{c.get('nome')} ({c.get('funcao','-')})": c.get("id") for c in sorted(colaboradores, key=lambda x: normalizar(x.get('nome','')))}
    c1, c2 = st.columns(2)
    with c1:
        pessoa = st.selectbox("Colaborador", list(labels.keys()), key="indisp_pessoa")
        motivo = st.selectbox("Motivo", ["Férias", "Atestado", "Afastamento", "Outro"], key="indisp_motivo")
    with c2:
        inicio = st.date_input("Início", value=agora_aproar().date(), format="DD/MM/YYYY", key="indisp_ini")
        fim = st.date_input("Fim", value=agora_aproar().date(), format="DD/MM/YYYY", key="indisp_fim")
    obs = st.text_input("Observação (opcional)", key="indisp_obs")
    if st.button("REGISTRAR INDISPONIBILIDADE", type="primary", use_container_width=True):
        ok, msg = salvar_indisponibilidade(labels[pessoa], motivo, inicio, fim, obs)
        (st.success if ok else st.error)(msg)
        if ok:
            st.rerun()

    titulo_secao_aproar("Registros ativos", "Períodos de indisponibilidade cadastrados.")
    registros = listar_indisponibilidades()
    registros.sort(key=lambda x: (x.get("inicio", ""), x.get("fim", "")), reverse=True)
    if not registros:
        st.info("Nenhuma indisponibilidade registrada.")
        return
    for item in registros:
        colab = obter_colaborador_por_id(item.get("colaborador_id"))
        nome_colab = (
            str(colab.get("nome") or "").strip()
            or str(item.get("colaborador_nome") or "").strip()
            or "Colaborador não encontrado"
        )
        try:
            inicio_br = datetime.date.fromisoformat(str(item.get("inicio"))).strftime("%d/%m/%Y")
        except Exception:
            inicio_br = str(item.get("inicio") or "")
        try:
            fim_br = datetime.date.fromisoformat(str(item.get("fim"))).strftime("%d/%m/%Y")
        except Exception:
            fim_br = str(item.get("fim") or "")

        with st.container(border=True):
            a, b = st.columns([4, 1])
            with a:
                st.markdown(f"**{nome_colab}** — {item.get('motivo','Indisponível')}")
                st.caption(f"{inicio_br} a {fim_br}" + (f" • {item.get('observacao')}" if item.get('observacao') else ""))
            with b:
                if st.button("Excluir", key=f"indisp_del_{item.get('id')}", use_container_width=True):
                    if excluir_indisponibilidade(item.get("id")):
                        st.rerun()
                    st.error("Não foi possível excluir.")

# --- FUNÇÕES DO PORTAL FINANCEIRO ---
def obter_ciclo_financeiro(data_ref=None):
    """Retorna o ciclo semanal de extras: terça-feira até segunda-feira."""
    data_ref = data_ref or datetime.date.today()
    dias_desde_terca = (data_ref.weekday() - 1) % 7  # terça = 1
    inicio = data_ref - datetime.timedelta(days=dias_desde_terca)
    fim = inicio + datetime.timedelta(days=6)
    pagamento = fim + datetime.timedelta(days=1)
    return inicio, fim, pagamento


def listar_ciclos_financeiros(qtd=26):
    """Gera ciclos semanais recentes para consulta do Financeiro."""
    hoje = datetime.date.today()
    inicio_atual, _, _ = obter_ciclo_financeiro(hoje)
    ciclos = []
    for i in range(qtd):
        inicio = inicio_atual - datetime.timedelta(days=7 * i)
        fim = inicio + datetime.timedelta(days=6)
        pagamento = fim + datetime.timedelta(days=1)
        em_aberto = hoje <= fim and hoje >= inicio
        ciclos.append({
            "inicio": inicio,
            "fim": fim,
            "pagamento": pagamento,
            "em_aberto": em_aberto,
            "rotulo": (
                f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
                + (" • EM ABERTO" if em_aberto else f" • pagamento {pagamento.strftime('%d/%m/%Y')}")
            )
        })
    return ciclos


def carregar_dados_financeiro(data_inicio, data_fim):
    """Retorna pagamentos líquidos e ausências do período."""
    registros = _buscar_convocacoes_intervalo(data_inicio, data_fim)
    linhas_rateadas = ratear_registros_por_servico(registros)

    pagamentos = []
    if linhas_rateadas:
        df = pd.DataFrame(linhas_rateadas)

        # O Relatório Financeiro é um relatório de pagamentos excepcionais:
        # não deve listar toda a equipe que teve somente a diária normal.
        #
        # Entra no relatório quem tiver pelo menos UM destes valores:
        # - Extra;
        # - Adicional noturno;
        # - Acordos / Bonificações.
        #
        # Depois de entrar no relatório, a Base Financeiro continua compondo
        # o Total a Pagar, conforme a regra financeira já definida.
        diaria_real_fin = pd.to_numeric(
            df["Base Financeiro (R$)"],
            errors="coerce",
        ).fillna(0.0)

        diaria_padrao_fin = pd.to_numeric(
            df.get(
                "Base Padrão Financeiro (R$)",
                0.0,
            ),
            errors="coerce",
        ).fillna(0.0)

        df = df[
            (
                (
                    diaria_real_fin
                    - diaria_padrao_fin
                ).abs()
                > 0.005
            )
            |
            (
                pd.to_numeric(
                    df["Extra (R$)"],
                    errors="coerce",
                ).fillna(0.0) > 0.005
            )
            |
            (
                pd.to_numeric(
                    df["Adicional noturno (R$)"],
                    errors="coerce",
                ).fillna(0.0) > 0.005
            )
            |
            (
                pd.to_numeric(
                    df["Acordos / Bonificações (R$)"],
                    errors="coerce",
                ).fillna(0.0) > 0.005
            )
        ].copy()

        if not df.empty:
            agrupados = (
                df.groupby(
                    ["Data", "_colaborador_id", "Colaborador", "Função"],
                    dropna=False,
                )
                .agg(
                    Unidades=("Unidade", lambda s: ", ".join(sorted(set(str(v) for v in s if str(v).strip())))),
                    Engenheiros=("Engenheiro", lambda s: " / ".join(sorted(set(str(v) for v in s if str(v).strip())))),
                    Tipo=("Tipo", lambda s: " / ".join(dict.fromkeys(str(v) for v in s if str(v).strip()))),
                    **{
                        "Base Financeiro (R$)": ("Base Financeiro (R$)", "sum"),
                        "Extra (R$)": ("Extra (R$)", "sum"),
                        "Adicional noturno (R$)": ("Adicional noturno (R$)", "sum"),
                        "Acordos / Bonificações (R$)": ("Acordos / Bonificações (R$)", "sum"),
                        "Total a Pagar (R$)": ("Total Financeiro (R$)", "sum"),
                    },
                )
                .reset_index()
            )
            for _, row in agrupados.iterrows():
                try:
                    data_br = datetime.date.fromisoformat(str(row["Data"])).strftime("%d/%m/%Y")
                except Exception:
                    data_br = str(row["Data"])
                pagamentos.append({
                    "Data": data_br,
                    "Data ISO": str(row["Data"]),
                    "Colaborador": row["Colaborador"],
                    "Função": row["Função"],
                    "Unidade": row["Unidades"],
                    "Engenheiro": row["Engenheiros"],
                    "Tipo": row["Tipo"],
                    "Base Financeiro (R$)": round(float(row["Base Financeiro (R$)"]), 2),
                    "Extra (R$)": round(float(row["Extra (R$)"]), 2),
                    "Adicional noturno (R$)": round(float(row["Adicional noturno (R$)"]), 2),
                    "Acordos / Bonificações (R$)": round(float(row["Acordos / Bonificações (R$)"]), 2),
                    "Total a Pagar (R$)": round(float(row["Total a Pagar (R$)"]), 2),
                })

    ausencias = []
    for row in registros:
        status = normalizar_status_operacional(row.get("status") or "")
        if status not in ["Falta", "Atestado"]:
            continue
        obra = dict_obras.get(row.get("obra_id"), {})
        colab = dict_colaboradores.get(row.get("colaborador_id"), {})
        data_iso = str(row.get("data") or "")
        try:
            data_br = datetime.date.fromisoformat(data_iso).strftime("%d/%m/%Y")
        except Exception:
            data_br = data_iso
        ausencias.append({
            "Data": data_br,
            "Data ISO": data_iso,
            "Colaborador": str(colab.get("nome") or "NÃO IDENTIFICADO"),
            "Função": str(colab.get("funcao") or "-"),
            "Unidade": str(obra.get("unidade") or "NÃO IDENTIFICADA"),
            "Engenheiro": str(row.get("engenheiro") or "N/A"),
            "Status": status,
        })

    pagamentos.sort(key=lambda x: (x.get("Data ISO", ""), normalizar(x.get("Colaborador", ""))))
    ausencias.sort(key=lambda x: (x.get("Data ISO", ""), normalizar(x.get("Colaborador", ""))))
    return pagamentos, ausencias


def resumir_pagamentos_financeiro(pagamentos):
    if not pagamentos:
        return pd.DataFrame(columns=[
            "Colaborador", "Função", "Unidades", "Dias/Lançamentos",
            "Diária (R$)", "Extra (R$)", "Adic. noturno (R$)", "Acordos / Bonificações (R$)", "Total a Pagar (R$)"
        ])

    df = pd.DataFrame(pagamentos)
    return (
        df.groupby(["Colaborador", "Função"], dropna=False)
        .agg(
            Unidades=("Unidade", lambda s: ", ".join(sorted(set(str(v) for v in s if str(v).strip())))),
            **{
                "Dias/Lançamentos": ("Data", "size"),
                "Diária (R$)": ("Base Financeiro (R$)", "sum"),
                "Extra (R$)": ("Extra (R$)", "sum"),
                "Adic. noturno (R$)": ("Adicional noturno (R$)", "sum"),
                "Acordos / Bonificações (R$)": ("Acordos / Bonificações (R$)", "sum"),
                "Total a Pagar (R$)": ("Total a Pagar (R$)", "sum"),
            },
        )
        .reset_index()
        .sort_values(by=["Total a Pagar (R$)", "Colaborador"], ascending=[False, True])
    )


def gerar_excel_financeiro(pagamentos, ausencias, data_inicio, data_fim, data_pagamento):
    wb = openpyxl.Workbook()
    ws_resumo = wb.active
    ws_resumo.title = "Resumo Pagamentos"

    fill_titulo = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_header = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    font_titulo = Font(name="Arial", size=12, bold=True, color="FFFFFF")
    font_header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    borda = Border(
        left=Side(style="thin", color="CBD5E1"), right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"), bottom=Side(style="thin", color="CBD5E1")
    )

    def cabecalho_planilha(ws, titulo, subtitulo, total_colunas):
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_colunas)
        c = ws.cell(1, 1, titulo)
        c.font = font_titulo
        c.fill = fill_titulo
        c.alignment = Alignment(horizontal="center")
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_colunas)
        ws.cell(2, 1, subtitulo).font = Font(name="Arial", size=9, italic=True, color="64748B")

    resumo = resumir_pagamentos_financeiro(pagamentos)
    total_pagar = sum(float(x.get("Total a Pagar (R$)") or 0) for x in pagamentos)
    subtitulo = (
        f"Ciclo: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} | "
        f"Pagamento: {data_pagamento.strftime('%d/%m/%Y')} | Total: {formatar_reais(total_pagar)}"
    )
    headers_resumo = [
        "Colaborador", "Função", "Unidades", "Dias/Lançamentos",
        "Diária (R$)", "Extra (R$)", "Adic. noturno (R$)", "Acordos / Bonificações (R$)", "Total a Pagar (R$)"
    ]
    cabecalho_planilha(ws_resumo, "APROAR - RELATÓRIO FINANCEIRO", subtitulo, len(headers_resumo))
    for ci, nome in enumerate(headers_resumo, 1):
        cell = ws_resumo.cell(4, ci, nome)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
    for ri, (_, r) in enumerate(resumo.iterrows(), 5):
        vals = [r[h] for h in headers_resumo]
        for ci, val in enumerate(vals, 1):
            cell = ws_resumo.cell(ri, ci, val)
            cell.border = borda
            cell.font = Font(name="Arial", size=9)
            if "(R$)" in headers_resumo[ci-1]:
                cell.number_format = 'R$ #,##0.00'
    ws_resumo.freeze_panes = "A5"

    ws_det = wb.create_sheet("Detalhe Pagamentos")
    headers_det = [
        "Data", "Colaborador", "Função", "Unidade", "Engenheiro", "Tipo",
        "Base Financeiro (R$)", "Extra (R$)", "Adicional noturno (R$)",
        "Acordos / Bonificações (R$)", "Total a Pagar (R$)"
    ]
    cabecalho_planilha(ws_det, "DETALHAMENTO DE PAGAMENTOS", subtitulo, len(headers_det))
    for ci, nome in enumerate(headers_det, 1):
        cell = ws_det.cell(4, ci, nome)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
    for ri, item in enumerate(pagamentos, 5):
        vals = [item.get(h, "") for h in headers_det]
        for ci, val in enumerate(vals, 1):
            cell = ws_det.cell(ri, ci, val)
            cell.border = borda
            cell.font = Font(name="Arial", size=9)
            if "(R$)" in headers_det[ci-1]:
                cell.number_format = 'R$ #,##0.00'
    ws_det.freeze_panes = "A5"

    ws_aus = wb.create_sheet("Faltas e Atestados")
    headers_aus = ["Data", "Colaborador", "Função", "Unidade", "Status", "Engenheiro"]
    cabecalho_planilha(
        ws_aus,
        "FALTAS E ATESTADOS DO CICLO",
        f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        len(headers_aus),
    )
    for ci, nome in enumerate(headers_aus, 1):
        cell = ws_aus.cell(4, ci, nome)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
    for ri, item in enumerate(ausencias, 5):
        for ci, h in enumerate(headers_aus, 1):
            cell = ws_aus.cell(ri, ci, item.get(h, ""))
            cell.border = borda
            cell.font = Font(name="Arial", size=9)

    for ws in wb.worksheets:
        for col in ws.columns:
            letter = openpyxl.utils.get_column_letter(col[0].column)
            max_len = max(
                [len(str(c.value or "")) for c in col]
                + [10]
            )
            ws.column_dimensions[letter].width = min(
                max_len + 3,
                38,
            )

    # Ajustes específicos das colunas longas do Financeiro.
    if "Resumo Pagamentos" in wb.sheetnames:
        ws_resumo.column_dimensions["H"].width = 24
        ws_resumo.column_dimensions["I"].width = 19
        ws_resumo.row_dimensions[4].height = 30

    if "Detalhe Pagamentos" in wb.sheetnames:
        ws_det.column_dimensions["J"].width = 24
        ws_det.column_dimensions["K"].width = 19
        ws_det.row_dimensions[4].height = 30

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def gerar_pdf_financeiro(pagamentos, ausencias, data_inicio, data_fim, data_pagamento):
    pdf = FPDF(orientation="L")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 9, to_latin("APROAR - RELATÓRIO FINANCEIRO"), ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(
        0, 7,
        to_latin(
            f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} | "
            f"Pagamento previsto: {data_pagamento.strftime('%d/%m/%Y')}"
        ),
        ln=True, align="C"
    )
    pdf.ln(3)

    resumo = resumir_pagamentos_financeiro(pagamentos)
    total_pagar = sum(float(x.get("Total a Pagar (R$)") or 0) for x in pagamentos)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, to_latin(f"TOTAL A PAGAR: {formatar_reais(total_pagar)}"), ln=True)

    # A4 paisagem: larguras compactas para evitar estouro do cabeçalho.
    widths = [47, 31, 35, 15, 22, 22, 24, 32, 27]
    headers = [
        "Colaborador",
        "Função",
        "Unidade(s)",
        "Dias",
        "Diária",
        "Extra",
        "Adic. not.",
        "Acordos / Bonif.",
        "Total",
    ]
    pdf.set_font("Arial", "B", 7.5)
    for w, h in zip(widths, headers):
        pdf.cell(w, 6, to_latin(h), border=1, align="C")
    pdf.ln()
    pdf.set_font("Arial", "", 7.5)
    if resumo.empty:
        pdf.cell(
            sum(widths),
            6,
            to_latin(
                "Nenhum Extra, Adicional noturno ou Acordo / Bonificação lançado neste ciclo."
            ),
            border=1,
            ln=True,
        )
    else:
        for _, r in resumo.iterrows():
            vals = [
                str(r["Colaborador"])[:27],
                str(r["Função"])[:17],
                str(r["Unidades"])[:20],
                str(int(r["Dias/Lançamentos"])),
                formatar_reais(float(r["Diária (R$)"])),
                formatar_reais(float(r["Extra (R$)"])),
                formatar_reais(float(r["Adic. noturno (R$)"])),
                formatar_reais(float(r["Acordos / Bonificações (R$)"])),
                formatar_reais(float(r["Total a Pagar (R$)"])),
            ]
            aligns = ["L", "L", "L", "C", "R", "R", "R", "R", "R"]
            for w, v, a in zip(widths, vals, aligns):
                pdf.cell(w, 6, to_latin(v), border=1, align=a)
            pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, to_latin("FALTAS E ATESTADOS"), ln=True)
    widths2 = [25, 68, 45, 45, 30, 40]
    headers2 = ["Data", "Colaborador", "Função", "Unidade", "Status", "Engenheiro"]
    pdf.set_font("Arial", "B", 8)
    for w, h in zip(widths2, headers2):
        pdf.cell(w, 6, to_latin(h), border=1, align="C")
    pdf.ln()
    pdf.set_font("Arial", "", 8)
    if not ausencias:
        pdf.cell(sum(widths2), 6, to_latin("Nenhuma falta ou atestado neste ciclo."), border=1, ln=True)
    else:
        for item in ausencias:
            vals = [
                item["Data"], item["Colaborador"][:32], item["Função"][:20],
                item["Unidade"][:20], item["Status"], item["Engenheiro"][:18]
            ]
            for w, v in zip(widths2, vals):
                pdf.cell(w, 6, to_latin(v), border=1)
            pdf.ln()

    return bytes(pdf.output(dest="S").encode("latin1"))

# --- ACESSO POR PERFIL -------------------------------------------------------
# Controladoria e Financeiro usam senha.
# Portal do Supervisor e Somente visualizar não exigem senha.

SENHA_CONTROLADORIA = "aproaradmin"
SENHA_FINANCEIRO = "financeiro"


def _edicao_liberada():
    return bool(
        st.session_state.get(
            "edicao_liberada",
            False,
        )
    )


def _financeiro_liberado():
    return bool(
        st.session_state.get(
            "financeiro_liberado",
            False,
        )
    )


def _limpar_acesso():
    st.session_state["edicao_liberada"] = False
    st.session_state["financeiro_liberado"] = False
    st.session_state.pop("perfil_acesso", None)


def _ir_portal_supervisor():
    _limpar_acesso()
    st.query_params.clear()
    st.query_params["eng"] = "1"


def _ir_visualizacao():
    _limpar_acesso()
    st.query_params.clear()
    st.query_params["view"] = "1"


def _render_login_aproar(
    acesso_inicial="Controladoria",
):
    """Tela inicial de acesso da Gestão de Equipes."""

    st.html("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer{
        display:none !important;
    }

    [data-testid="stHeader"]{
        display:none !important;
        height:0 !important;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"]{
        background:#F4F7FC !important;
    }

    [data-testid="stMainBlockContainer"],
    main .block-container{
        max-width:520px !important;
        padding:72px 20px 40px !important;
        margin:0 auto !important;
    }

    /* Card real do Streamlit — não depende de HTML envolvendo widgets */
    div[class*="st-key-login_card_aproar"]{
        background:#FFFFFF !important;
        border:1px solid #E2E8F0 !important;
        border-radius:14px !important;
        padding:28px 28px 26px !important;
        box-shadow:0 12px 34px rgba(15,23,42,.08) !important;
    }

    div[class*="st-key-login_card_aproar"] > div{
        gap:.48rem !important;
    }

    .aproar-login-brand{
        font-size:27px;
        line-height:1;
        font-weight:850;
        letter-spacing:-.8px;
        color:#102442;
        margin:0 0 7px;
    }

    .aproar-login-sub{
        font-size:11px;
        color:#8290A6;
        margin-bottom:19px;
    }

    .aproar-login-label{
        font-size:9px;
        font-weight:800;
        color:#4B5B72;
        text-transform:uppercase;
        margin:0 0 4px;
        letter-spacing:.15px;
    }

    div[class*="st-key-login_perfil_aproar"]{
        margin:0 0 2px !important;
    }

    div[class*="st-key-login_perfil_aproar"] label{
        display:none !important;
    }

    div[class*="st-key-login_perfil_aproar"] div[data-baseweb="select"] > div{
        min-height:45px !important;
        border-radius:8px !important;
        background:#FFFFFF !important;
        border:1px solid #273445 !important;
        font-size:13px !important;
    }

    div[class*="st-key-login_senha_aproar"]{
        margin:0 0 2px !important;
    }

    div[class*="st-key-login_senha_aproar"] label{
        display:none !important;
    }

    div[class*="st-key-login_senha_aproar"] [data-baseweb="base-input"]{
        border-radius:8px !important;
        background:#FFFFFF !important;
        border:1px solid #D6DEE9 !important;
        min-height:45px !important;
    }

    div[class*="st-key-login_senha_aproar"] input{
        min-height:43px !important;
        font-size:14px !important;
        background:#FFFFFF !important;
        color:#172235 !important;
    }

    div[class*="st-key-btn_login_aproar"] button{
        min-height:44px !important;
        width:100% !important;
        background:#2D63E7 !important;
        border-color:#2D63E7 !important;
        color:#FFFFFF !important;
        border-radius:7px !important;
        font-size:12px !important;
        font-weight:800 !important;
        text-transform:uppercase !important;
        margin-top:3px !important;
    }

    div[class*="st-key-btn_login_aproar"] button *{
        color:#FFFFFF !important;
    }

    div[class*="st-key-btn_login_aproar"] button:hover{
        background:#2557CF !important;
        border-color:#2557CF !important;
    }

    div[class*="st-key-btn_portal_supervisor"] button,
    div[class*="st-key-btn_somente_visualizar"] button{
        min-height:44px !important;
        width:100% !important;
        border-radius:7px !important;
        background:#FFFFFF !important;
        color:#314562 !important;
        border:1px solid #DDE4ED !important;
        font-size:11.5px !important;
        font-weight:750 !important;
    }

    div[class*="st-key-btn_portal_supervisor"] button *,
    div[class*="st-key-btn_somente_visualizar"] button *{
        color:#314562 !important;
    }

    div[class*="st-key-btn_portal_supervisor"] button:hover,
    div[class*="st-key-btn_somente_visualizar"] button:hover{
        border-color:#AEBBD0 !important;
        background:#F8FAFD !important;
    }

    .aproar-login-error{
        color:#B42337;
        background:#FFF2F4;
        border:1px solid #FFD7DD;
        border-radius:7px;
        padding:9px 11px;
        font-size:10.5px;
        margin:6px 0 1px;
    }

    @media(max-width:560px){
        [data-testid="stMainBlockContainer"],
        main .block-container{
            padding:36px 14px 28px !important;
        }

        div[class*="st-key-login_card_aproar"]{
            padding:24px 20px 22px !important;
            border-radius:12px !important;
        }

        .aproar-login-brand{
            font-size:25px;
        }

        div[class*="st-key-login_botoes_secundarios"] [data-testid="stHorizontalBlock"]{
            gap:.5rem !important;
        }
    }
    </style>
    """)

    with st.container(
        key="login_card_aproar"
    ):
        st.markdown(
            """
            <div class="aproar-login-brand">APROAR</div>
            <div class="aproar-login-sub">
                GESTÃO DE EQUIPES · sistema operacional
            </div>
            <div class="aproar-login-label">ACESSO</div>
            """,
            unsafe_allow_html=True,
        )

        opcoes_acesso = [
            "Controladoria",
            "Financeiro",
        ]

        indice_acesso = (
            opcoes_acesso.index(acesso_inicial)
            if acesso_inicial in opcoes_acesso
            else 0
        )

        perfil_login = st.selectbox(
            "Acesso",
            opcoes_acesso,
            index=indice_acesso,
            label_visibility="collapsed",
            key="login_perfil_aproar",
        )

        st.markdown(
            '<div class="aproar-login-label">SENHA</div>',
            unsafe_allow_html=True,
        )

        senha_digitada = st.text_input(
            "Senha",
            type="password",
            label_visibility="collapsed",
            key="login_senha_aproar",
        )

        entrar = st.button(
            "Entrar",
            type="primary",
            use_container_width=True,
            key="btn_login_aproar",
        )

        erro_login = None

        if entrar:
            if perfil_login == "Controladoria":
                senha_ctrl = str(
                    senha_digitada
                    or ""
                ).strip()

                if hmac.compare_digest(
                    senha_ctrl,
                    SENHA_CONTROLADORIA,
                ):
                    _limpar_acesso()
                    st.session_state[
                        "edicao_liberada"
                    ] = True
                    st.session_state[
                        "perfil_acesso"
                    ] = "controladoria"

                    try:
                        st.query_params.clear()
                    except Exception:
                        pass

                    st.rerun()
                else:
                    erro_login = (
                        "Senha da Controladoria incorreta."
                    )

            elif perfil_login == "Financeiro":
                senha_fin = str(
                    senha_digitada
                    or ""
                ).strip()

                if hmac.compare_digest(
                    senha_fin,
                    SENHA_FINANCEIRO,
                ):
                    _limpar_acesso()
                    st.session_state[
                        "financeiro_liberado"
                    ] = True
                    st.session_state[
                        "perfil_acesso"
                    ] = "financeiro"

                    # O setor passa a ser definido pela sessão.
                    # Limpa parâmetros antigos sem precisar recriar ?financeiro.
                    try:
                        st.query_params.clear()
                    except Exception:
                        pass

                    st.rerun()
                else:
                    erro_login = (
                        "Senha do Financeiro incorreta."
                    )

        if erro_login:
            st.markdown(
                f'<div class="aproar-login-error">{erro_login}</div>',
                unsafe_allow_html=True,
            )

        with st.container(
            key="login_botoes_secundarios"
        ):
            c_login_1, c_login_2 = st.columns(2)

            with c_login_1:
                if st.button(
                    "Portal do Supervisor",
                    use_container_width=True,
                    key="btn_portal_supervisor",
                ):
                    _ir_portal_supervisor()
                    st.rerun()

            with c_login_2:
                if st.button(
                    "Somente visualizar",
                    use_container_width=True,
                    key="btn_somente_visualizar",
                ):
                    _ir_visualizacao()
                    st.rerun()


parametros_url = st.query_params

# Logout universal. O link ?logout=1 funciona em qualquer setor
# e sempre retorna à tela inicial de login.
if "logout" in parametros_url:
    _limpar_acesso()
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()

modo_campo_solicitado = (
    "eng" in parametros_url
    or parametros_url.get("modo") in [
        "campo",
        "eng",
        "supervisor",
    ]
)

modo_financeiro_solicitado = (
    "financeiro" in parametros_url
    or "fin" in parametros_url
    or parametros_url.get("modo") in [
        "financeiro",
        "fin",
    ]
)

modo_visualizador_solicitado = (
    "view" in parametros_url
    or parametros_url.get("modo") in [
        "visualizador",
        "view",
        "consulta",
    ]
)

edicao_liberada = _edicao_liberada()
financeiro_liberado = _financeiro_liberado()
perfil_autenticado = str(
    st.session_state.get("perfil_acesso")
    or ""
).strip().lower()

# Regras:
# - ?eng / Portal do Supervisor: sem senha.
# - ?view / Somente visualizar: sem senha.
# - Financeiro: senha "financeiro".
# - Controladoria/Admin: senha "aproaradmin".
# - Depois do login, a sessão autenticada é a fonte de verdade.
#   Isso evita depender de query params para continuar no setor correto.
if perfil_autenticado == "controladoria" and edicao_liberada:
    modo_login = False
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = False

elif perfil_autenticado == "financeiro" and financeiro_liberado:
    modo_login = False
    modo_campo = False
    modo_financeiro = True
    modo_visualizador = False

elif modo_campo_solicitado:
    modo_login = False
    modo_campo = True
    modo_financeiro = False
    modo_visualizador = False

elif modo_visualizador_solicitado:
    modo_login = False
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = True

elif modo_financeiro_solicitado:
    # A URL direta ?financeiro abre o login do Financeiro,
    # mas só libera o portal depois da autenticação.
    modo_login = True
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = False

else:
    modo_login = True
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = False

if modo_login:
    _render_login_aproar(
        acesso_inicial=(
            "Financeiro"
            if modo_financeiro_solicitado
            else "Controladoria"
        )
    )

elif modo_visualizador:
    c_view_titulo, c_view_sair = st.columns(
        [6, 1],
        vertical_alignment="center",
    )

    with c_view_titulo:
        st.markdown("## 👁️ Painel Administrativo — Visualização")
        st.caption(
            "Dashboard, Relatórios e Indicadores disponíveis para consulta."
        )

    with c_view_sair:
        if st.button(
            "Sair",
            key="btn_sair_visualizador",
            use_container_width=True,
        ):
            _limpar_acesso()
            st.query_params.clear()
            st.rerun()
    secao_view = st.radio(
        "Navegação",
        [
            "🎛️ DASHBOARD",
            "📊 RELATÓRIOS",
            "📈 INDICADORES",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="nav_visualizador_geral",
    )

    if secao_view == "🎛️ DASHBOARD":
        render_dashboard_consulta(
            "view_dash"
        )
    elif secao_view == "📊 RELATÓRIOS":
        render_relatorio_visualizador(
            "view_rel"
        )
    else:
        render_indicadores_cumprimento(
            "view_ind"
        )

elif modo_campo:
    # =====================================================================
    # PORTAL DO ENGENHEIRO — MOBILE FIRST / MENOS CLIQUES
    # =====================================================================
    import html as _html

    # Limpa elementos visuais do próprio Streamlit no Portal do Supervisor.
    # Isso não altera a lógica dos widgets; remove apenas chrome/menu/toolbar.
    st.html("""
    <style>
    /* =========================================================
       APROAR — LIMPEZA VISUAL DO STREAMLIT (PORTAL SUPERVISOR)
       ========================================================= */

    /* Menu superior, toolbar, decoração e indicadores internos */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stHeaderActionElements"],
    [data-testid="stMainMenu"],
    #MainMenu {
        display:none !important;
        visibility:hidden !important;
    }

    /* Botões de deploy/share quando aparecem */
    [data-testid="stAppDeployButton"],
    [data-testid="stDeployButton"] {
        display:none !important;
        visibility:hidden !important;
    }

    /* Cabeçalho padrão do Streamlit */
    [data-testid="stHeader"] {
        display:none !important;
        visibility:hidden !important;
        height:0 !important;
        min-height:0 !important;
    }

    /* Sidebar e controles para abrir/recolher */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display:none !important;
        visibility:hidden !important;
    }

    /* Toolbar flutuante em gráficos/tabelas/elementos */
    [data-testid="stElementToolbar"] {
        display:none !important;
        visibility:hidden !important;
    }

    /* Badges do viewer / branding eventual */
    [data-testid="stViewerBadge"],
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137 {
        display:none !important;
        visibility:hidden !important;
    }

    /* Rodapé padrão */
    footer {
        display:none !important;
        visibility:hidden !important;
    }

    /* Remove o espaço residual do cabeçalho */
    [data-testid="stMainBlockContainer"],
    main .block-container {
        padding-top:.55rem !important;
    }
    </style>
    """)

    st.html("""
    <style>
    /* Portal de campo: uma única coluna, sem sidebar e sem chrome do Streamlit. */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer{
        display:none !important;
    }

    [data-testid="stHeader"]{
        display:none !important;
        height:0 !important;
    }

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"]{
        background:var(
            --st-background-color,
            var(--background-color,#F5F7FA)
        ) !important;
    }

    [data-testid="stMainBlockContainer"],
    main .block-container{
        max-width:760px !important;
        padding:.75rem .78rem 5.5rem !important;
        margin:0 auto !important;
    }

    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]{
        gap:.65rem !important;
    }

    /* Cabeçalho do portal */
    .engm-head{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:12px;
        margin:2px 0 5px;
    }

    .engm-brand{
        min-width:0;
    }

    .engm-kicker{
        font-size:9px;
        line-height:1;
        letter-spacing:1.15px;
        font-weight:780;
        color:var(
            --st-primary-color,
            var(--primary-color,#245FD6)
        );
        text-transform:uppercase;
        margin-bottom:5px;
    }

    .engm-title{
        font-size:24px;
        line-height:1.08;
        font-weight:760;
        letter-spacing:-.025em;
        color:var(
            --st-text-color,
            var(--text-color,#172235)
        );
    }

    .engm-date{
        flex:0 0 auto;
        font-size:10px;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 55%,
            transparent
        );
        text-align:right;
        line-height:1.35;
    }


    .engm-head-v2{
        align-items:flex-start;
        margin:0 0 8px;
        padding:16px 16px 14px;
        border-radius:20px;
        background:linear-gradient(135deg,#0C3176 0%, #1250BA 100%);
        box-shadow:0 14px 32px rgba(16,36,66,.18);
    }

    .engm-brand-top{
        display:flex;
        align-items:center;
        gap:14px;
        margin:0 0 8px;
    }

    .engm-brand-logo-wrap{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        width:98px;
        height:88px;
        margin:0;
        background:transparent;
        border:none;
        box-shadow:none;
        overflow:visible;
        flex:0 0 auto;
    }

    .engm-brand-logo-img{
        display:block;
        width:94px;
        height:82px;
        object-fit:contain;
        filter:drop-shadow(0 3px 8px rgba(6,20,48,.10));
    }

    .engm-brand-copy{
        min-width:0;
        display:flex;
        flex-direction:column;
        gap:4px;
    }

    .engm-brand-wordmark{
        font-size:28px;
        line-height:1;
        font-weight:650;
        letter-spacing:.16em;
        color:#FFFFFF;
        text-transform:uppercase;
        margin:0;
    }

    .engm-head-v2 .engm-kicker,
    .engm-head-v2 .engm-title,
    .engm-head-v2 .engm-date,
    .engm-head-v2 .engm-date b,
    .engm-head-v2 .engm-date-chip-label{
        color:#FFFFFF !important;
    }

    .engm-head-v2 .engm-kicker{
        opacity:.86;
        letter-spacing:.02em;
        text-transform:none;
        font-size:13px;
        margin-bottom:8px;
    }

    .engm-head-v2 .engm-title{
        font-size:40px;
        margin-top:2px;
    }

    .engm-date-v2{
        flex:0 0 auto;
        min-width:120px;
        text-align:right;
        font-size:12px;
        background:rgba(255,255,255,.10);
        border:1px solid rgba(255,255,255,.18);
        border-radius:14px;
        padding:10px 12px;
    }

    .engm-date-chip-label{ font-size:11px; opacity:.85; margin-bottom:3px; }

    .engm-summary-v2{
        grid-template-columns:repeat(3,minmax(0,1fr));
        background:transparent;
        border:none;
        gap:10px;
        margin:8px 0 10px;
    }

    .engm-summary-v2 .engm-summary-item{
        background:linear-gradient(135deg,#0C3176 0%, #1250BA 100%);
        border-radius:16px;
        border:none;
        text-align:center;
        padding:14px 10px 13px;
    }

    .engm-summary-v2 .engm-summary-label{
        margin-top:5px;
        font-size:11px;
        letter-spacing:0;
        text-transform:none;
        color:#EAF1FF !important;
    }

    .engm-summary-v2 .engm-summary-value{
        color:#FFFFFF !important;
        font-size:32px;
    }

    .engm-summary-v2 .engm-summary-note{ display:none; }

    .engm-summary-v2 .engm-summary-item.warn .engm-summary-value,
    .engm-summary-v2 .engm-summary-item.warn .engm-summary-label{
        color:#FFD84D !important;
    }

    /* Seletor do engenheiro */
    div[class*="st-key-engenheiro_campo_mobile"]{
        margin-bottom:2px !important;
    }

    div[class*="st-key-engenheiro_campo_mobile"] label p{
        font-size:9px !important;
        text-transform:uppercase !important;
        letter-spacing:.7px !important;
        font-weight:740 !important;
    }

    div[class*="st-key-engenheiro_campo_mobile"] div[data-baseweb="select"] > div{
        min-height:44px !important;
        border-radius:9px !important;
        font-size:14px !important;
        font-weight:630 !important;
    }

    /* Saída do Portal do Supervisor */
    div[class*="st-key-btn_sair_supervisor"] button{
        min-height:34px !important;
        border-radius:7px !important;
        font-size:10px !important;
        font-weight:650 !important;
        padding:4px 10px !important;
    }

    /* Navegação em 3 áreas: Hoje / Amanhã / Disponibilidade */
    div[class*="st-key-eng_mobile_nav"]{
        position:sticky !important;
        top:0 !important;
        z-index:90 !important;
        padding:5px 0 7px !important;
        background:var(
            --st-background-color,
            var(--background-color,#F5F7FA)
        ) !important;
    }

    div[class*="st-key-eng_mobile_nav"] [role="radiogroup"]{
        display:grid !important;
        grid-template-columns:repeat(3,minmax(0,1fr)) !important;
        gap:5px !important;
        background:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 5%,
            var(--st-background-color,var(--background-color,#F5F7FA))
        ) !important;
        border:1px solid color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 10%,
            transparent
        ) !important;
        padding:4px !important;
        border-radius:10px !important;
    }

    div[class*="st-key-eng_mobile_nav"] [role="radio"]{
        min-height:39px !important;
        border-radius:7px !important;
        justify-content:center !important;
        padding:0 5px !important;
        margin:0 !important;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 65%,
            transparent
        ) !important;
        font-size:11px !important;
        font-weight:650 !important;
    }

    div[class*="st-key-eng_mobile_nav"] [role="radio"] > div:first-child{
        display:none !important;
    }

    div[class*="st-key-eng_mobile_nav"] [aria-checked="true"]{
        background:var(
            --st-secondary-background-color,
            var(--secondary-background-color,#FFFFFF)
        ) !important;
        color:var(
            --st-primary-color,
            var(--primary-color,#245FD6)
        ) !important;
        box-shadow:0 1px 3px rgba(15,23,42,.08) !important;
    }

    /* Resumo compacto */
    .engm-summary{
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        border:1px solid color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 11%,
            transparent
        );
        border-radius:10px;
        overflow:hidden;
        background:var(
            --st-secondary-background-color,
            var(--secondary-background-color,#FFFFFF)
        );
        margin:4px 0 3px;
    }

    .engm-summary-item{
        padding:12px 11px 11px;
        min-width:0;
        border-right:1px solid color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 9%,
            transparent
        );
    }

    .engm-summary-item:last-child{
        border-right:0;
    }

    .engm-summary-label{
        font-size:8px;
        letter-spacing:.45px;
        text-transform:uppercase;
        font-weight:730;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 52%,
            transparent
        );
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }

    .engm-summary-value{
        margin-top:5px;
        font-size:23px;
        line-height:1;
        font-weight:760;
        color:var(
            --st-text-color,
            var(--text-color,#172235)
        );
    }

    .engm-summary-note{
        margin-top:5px;
        font-size:8.5px;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 42%,
            transparent
        );
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }

    .engm-summary-item.warn .engm-summary-value{
        color:#B86B16;
    }

    .engm-summary-item.danger .engm-summary-value{
        color:#C54053;
    }

    .engm-section-title{
        font-size:15px;
        line-height:1.2;
        font-weight:720;
        color:var(
            --st-text-color,
            var(--text-color,#172235)
        );
        margin:9px 0 1px;
    }

    .engm-section-sub{
        font-size:10px;
        line-height:1.35;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 50%,
            transparent
        );
        margin-bottom:5px;
    }

    /* Cards dos colaboradores */
    .engm-person-head{
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:10px;
        margin-bottom:3px;
    }

    .engm-person-name{
        font-size:13px;
        line-height:1.2;
        font-weight:700;
        color:var(
            --st-text-color,
            var(--text-color,#172235)
        );
    }

    .engm-person-meta{
        margin-top:3px;
        font-size:9.5px;
        line-height:1.3;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 50%,
            transparent
        );
    }

    .engm-chip{
        flex:0 0 auto;
        max-width:115px;
        padding:4px 7px;
        border-radius:999px;
        font-size:8.5px;
        line-height:1.1;
        font-weight:680;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
        color:var(
            --st-primary-color,
            var(--primary-color,#245FD6)
        );
        background:color-mix(
            in srgb,
            var(--st-primary-color,var(--primary-color,#245FD6)) 9%,
            transparent
        );
    }

    /* Containers do portal: menos espaço, bons alvos de toque */
    main [data-testid="stVerticalBlockBorderWrapper"] > div{
        border-radius:10px !important;
        padding:.72rem .78rem !important;
        border-color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 10%,
            transparent
        ) !important;
        box-shadow:none !important;
    }

    main [data-testid="stExpander"]{
        border-radius:9px !important;
    }

    main [data-testid="stExpander"] summary{
        min-height:42px !important;
        font-size:11px !important;
        font-weight:640 !important;
        position:relative !important;
        padding-left:30px !important;
    }

    /* Em algumas versões do Streamlit o ícone Material do expander aparece
       como texto ("arrow_right"). Escondemos o ícone interno e desenhamos
       uma seta simples via CSS. */
    main [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    main [data-testid="stExpander"] summary .material-symbols-rounded,
    main [data-testid="stExpander"] summary .material-symbols-outlined{
        display:none !important;
    }

    main [data-testid="stExpander"] summary::before{
        content:"›";
        position:absolute;
        left:11px;
        top:50%;
        transform:translateY(-50%);
        font-size:20px;
        line-height:1;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 70%,
            transparent
        );
        transition:transform .15s ease;
    }

    main [data-testid="stExpander"] details[open] summary::before{
        transform:translateY(-50%) rotate(90deg);
    }

    /* Campos grandes o suficiente para celular */
    main label p{
        font-size:9.5px !important;
        font-weight:650 !important;
    }

    main div[data-baseweb="select"] > div,
    main div[data-baseweb="base-input"] > div,
    main div[data-baseweb="input"] > div,
    main [data-baseweb="textarea"] > div,
    main div[role="combobox"]{
        min-height:43px !important;
        border-radius:8px !important;
        font-size:12px !important;
    }

    main input{
        font-size:13px !important;
    }

    /* Botões: grandes para toque, mas sem parecer cartões gigantes */
    main .stButton > button,
    main .stDownloadButton > button,
    main [data-testid="stFormSubmitButton"] > button{
        min-height:44px !important;
        border-radius:8px !important;
        font-size:11.5px !important;
        font-weight:660 !important;
    }

    /* Botões principais do fluxo */
    div[class*="st-key-engm_all_present"] button,
    div[class*="st-key-engm_confirm_conv"] button{
        width:100% !important;
    }

    /* Salvar equipe e confirmar convocação ficam sempre à mão. */
    main [data-testid="stForm"] [data-testid="stFormSubmitButton"]{
        position:sticky !important;
        bottom:8px !important;
        z-index:80 !important;
        padding-top:6px !important;
        background:linear-gradient(
            to top,
            var(--st-background-color,var(--background-color,#F5F7FA)) 68%,
            transparent
        ) !important;
    }

    main [data-testid="stForm"] [data-testid="stFormSubmitButton"] button{
        box-shadow:0 6px 20px rgba(15,23,42,.15) !important;
    }

    /* Alertas */
    [data-testid="stAlert"]{
        border-radius:9px !important;
        font-size:10.5px !important;
        padding:.65rem .72rem !important;
    }

    /* Listas compactas de convocados */
    .engm-list{
        display:flex;
        flex-direction:column;
        gap:6px;
        margin:4px 0;
    }

    .engm-list-item{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:9px;
        padding:9px 10px;
        border:1px solid color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 9%,
            transparent
        );
        border-radius:8px;
        background:var(
            --st-secondary-background-color,
            var(--secondary-background-color,#FFFFFF)
        );
    }

    .engm-list-main{
        min-width:0;
    }

    .engm-list-name{
        font-size:11px;
        line-height:1.2;
        font-weight:680;
        color:var(
            --st-text-color,
            var(--text-color,#172235)
        );
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }

    .engm-list-meta{
        margin-top:3px;
        font-size:9px;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 48%,
            transparent
        );
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }

    .engm-list-side{
        flex:0 0 auto;
        font-size:9px;
        font-weight:650;
        color:color-mix(
            in srgb,
            var(--st-text-color,var(--text-color,#172235)) 58%,
            transparent
        );
    }

    /* Disponibilidade */
    .engm-avail-ok{color:#14805D !important;}
    .engm-avail-busy{color:#B66C18 !important;}
    .engm-avail-off{color:#C44557 !important;}

    /* Menos desperdício vertical no celular. */
    /* Linha Engenheiro + Unidade + Data no apontamento */
    div[class*="st-key-engenheiro_campo_mobile"],
    div[class*="st-key-engm_unidade_apont_top"],
    div[class*="st-key-engm_data_apont"]{
        margin-bottom:0 !important;
    }

    @media(max-width:520px){
        [data-testid="stMainBlockContainer"],
        main .block-container{
            padding:.55rem .6rem 5rem !important;
        }

        .engm-title{
            font-size:22px;
        }

        .engm-date{
            font-size:9px;
        }

        .engm-summary-item{
            padding:11px 9px 10px;
        }

        .engm-summary-value{
            font-size:21px;
        }

        main [data-testid="stHorizontalBlock"]{
            gap:.45rem !important;
        }
    }

    /* ============================================================
       APROAR V6.15 — NORMALIZAÇÃO FINAL DE CORES DO PORTAL CAMPO
       Evita que Safari/iOS, modo escuro ou tema do Streamlit
       sobrescrevam campos, alertas, tags, toasts e expanders.
       ============================================================ */

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    main{
        color-scheme:light !important;
        background:#F5F7FB !important;
        color:#172235 !important;
    }

    /* Campos de texto / selects / datas sempre claros e legíveis */
    main div[data-baseweb="select"] > div,
    main div[data-baseweb="base-input"],
    main div[data-baseweb="base-input"] > div,
    main div[data-baseweb="input"],
    main div[data-baseweb="input"] > div,
    main [data-baseweb="textarea"],
    main [data-baseweb="textarea"] > div,
    main div[role="combobox"],
    main [data-testid="stDateInput"] > div,
    main [data-testid="stTextInput"] > div{
        background:#FFFFFF !important;
        color:#172235 !important;
        border-color:#D6DFEA !important;
        box-shadow:none !important;
    }

    main input,
    main textarea,
    main select,
    main [data-baseweb="select"] span{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
        caret-color:#172235 !important;
    }

    main input::placeholder,
    main textarea::placeholder{
        color:#94A3B8 !important;
        -webkit-text-fill-color:#94A3B8 !important;
        opacity:1 !important;
    }

    /* Campo somente leitura/desabilitado não fica preto/cinza escuro */
    main input:disabled,
    main textarea:disabled,
    main select:disabled,
    main [aria-disabled="true"] input{
        background:#F1F4F8 !important;
        color:#7A8698 !important;
        -webkit-text-fill-color:#7A8698 !important;
        border-color:#D9E1EB !important;
        opacity:1 !important;
    }

    main [data-testid="stDateInput"] input{
        background:#FFFFFF !important;
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    main div[data-baseweb="select"] svg,
    main div[data-baseweb="select"] [role="button"]{
        color:#475569 !important;
        fill:#475569 !important;
    }

    /* Expander: elimina cabeçalho preto herdado do tema/iOS */
    main [data-testid="stExpander"]{
        background:#FFFFFF !important;
        border-color:#DCE3EC !important;
        color:#172235 !important;
    }

    main [data-testid="stExpander"] details,
    main [data-testid="stExpander"] summary{
        background:#FFFFFF !important;
        color:#172235 !important;
    }

    main [data-testid="stExpander"] summary *,
    main [data-testid="stExpander"] details *{
        color:#172235;
    }

    main [data-testid="stExpander"] summary:hover{
        background:#F8FAFC !important;
    }

    /* Navegação Hoje / Amanhã / Disponibilidade como segmented control */
    div[class*="st-key-eng_mobile_nav"] [role="radiogroup"]{
        background:#EDF1F6 !important;
        border:1px solid #D7DFE9 !important;
    }

    div[class*="st-key-eng_mobile_nav"] [role="radio"]{
        background:transparent !important;
        color:#172235 !important;
        white-space:nowrap !important;
        overflow:hidden !important;
        text-overflow:ellipsis !important;
    }

    div[class*="st-key-eng_mobile_nav"] [role="radio"] *{
        color:#172235 !important;
    }

    /* Esconde as bolinhas do radio, pois alguns Safari/iOS as pintam de preto */
    div[class*="st-key-eng_mobile_nav"] [role="radio"] svg,
    div[class*="st-key-eng_mobile_nav"] [role="radio"] [data-baseweb="radio"] > div:first-child{
        display:none !important;
    }

    div[class*="st-key-eng_mobile_nav"] [aria-checked="true"]{
        background:#FFFFFF !important;
        color:#245FD6 !important;
        box-shadow:0 1px 3px rgba(15,23,42,.10) !important;
    }

    div[class*="st-key-eng_mobile_nav"] [aria-checked="true"] *{
        color:#245FD6 !important;
    }

    /* Não quebra Disponibilidade no meio da palavra */
    div[class*="st-key-eng_mobile_nav"] [role="radio"] p,
    div[class*="st-key-eng_mobile_nav"] [role="radio"] span{
        white-space:nowrap !important;
        word-break:normal !important;
        overflow-wrap:normal !important;
    }

    /* Tags do multiselect: azul claro, sem rosa automático do tema */
    main div[data-baseweb="tag"]{
        background:#EAF1FF !important;
        border:1px solid #C8D8FF !important;
        color:#1D4ED8 !important;
        border-radius:9px !important;
    }

    main div[data-baseweb="tag"] *,
    main div[data-baseweb="tag"] svg{
        color:#1D4ED8 !important;
        fill:#1D4ED8 !important;
        -webkit-text-fill-color:#1D4ED8 !important;
    }

    /* Botões principais */
    main .stButton > button[kind="primary"],
    main [data-testid="stFormSubmitButton"] > button{
        background:#2F64E8 !important;
        border-color:#2F64E8 !important;
        color:#FFFFFF !important;
    }

    main .stButton > button[kind="primary"] *,
    main [data-testid="stFormSubmitButton"] > button *{
        color:#FFFFFF !important;
        -webkit-text-fill-color:#FFFFFF !important;
    }

    /* Sair é ação secundária, não ação principal */
    div[class*="st-key-btn_sair_supervisor"]{
        display:flex !important;
        justify-content:flex-end !important;
    }

    div[class*="st-key-btn_sair_supervisor"] button{
        width:auto !important;
        min-width:74px !important;
        min-height:32px !important;
        padding:4px 14px !important;
        background:#FFFFFF !important;
        border:1px solid #CBD7E6 !important;
        color:#2D5FCA !important;
        box-shadow:none !important;
    }

    div[class*="st-key-btn_sair_supervisor"] button *{
        color:#2D5FCA !important;
        -webkit-text-fill-color:#2D5FCA !important;
    }

    div[class*="st-key-btn_sair_supervisor"] button:hover{
        background:#EEF4FF !important;
        border-color:#AFC5F5 !important;
        color:#244FAF !important;
        transform:none !important;
    }

    /* Remover avulso: evita quadrado preto no iPhone */
    div[class*="st-key-engm_remover_manual_"] button{
        width:34px !important;
        min-width:34px !important;
        min-height:34px !important;
        padding:0 !important;
        background:#FFF5F6 !important;
        border:1px solid #F4C7CD !important;
        color:#B4233B !important;
        border-radius:8px !important;
        box-shadow:none !important;
    }

    div[class*="st-key-engm_remover_manual_"] button *{
        color:#B4233B !important;
        -webkit-text-fill-color:#B4233B !important;
    }

    /* Alertas: texto sempre escuro e legível */
    main [data-testid="stAlert"]{
        color:#172235 !important;
        border-color:#D7E0EB !important;
    }

    main [data-testid="stAlert"] p,
    main [data-testid="stAlert"] span,
    main [data-testid="stAlert"] div{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    /* Toast: fundo escuro exige texto branco */
    div[data-baseweb="toast"],
    [data-testid="stToast"]{
        background:#111827 !important;
        color:#FFFFFF !important;
        border:1px solid #273449 !important;
        border-radius:12px !important;
        box-shadow:0 12px 30px rgba(15,23,42,.28) !important;
    }

    div[data-baseweb="toast"] *,
    [data-testid="stToast"] *{
        color:#FFFFFF !important;
        -webkit-text-fill-color:#FFFFFF !important;
    }

    div[data-baseweb="toast"] svg,
    [data-testid="stToast"] svg{
        color:#FFFFFF !important;
        fill:#FFFFFF !important;
    }

    /* Cards e resumo */
    .engm-summary,
    .engm-list-item{
        background:#FFFFFF !important;
        border-color:#DCE3EC !important;
    }

    .engm-summary-label,
    .engm-summary-note,
    .engm-list-meta,
    .engm-section-sub,
    .engm-date{
        color:#7C899B !important;
    }

    .engm-summary-value,
    .engm-list-name,
    .engm-section-title,
    .engm-person-name,
    .engm-title{
        color:#172235 !important;
    }

    @media(max-width:520px){
        /* Dá espaço suficiente para "Disponibilidade" sem quebrar */
        div[class*="st-key-eng_mobile_nav"] [role="radio"]{
            font-size:10px !important;
            padding:0 3px !important;
        }

        /* Sair fica discreto também no celular */
        div[class*="st-key-btn_sair_supervisor"] button{
            min-width:68px !important;
            font-size:10px !important;
        }
    }
    </style>
    """)


    st.html("""
    <style>
    /* =========================================================
       APROAR V6.16 — MOBILE COLOR FIX
       Seletores deliberadamente genéricos dentro do portal Campo.
       ========================================================= */

    :root,
    html,
    body,
    .stApp{
        color-scheme:light !important;
        --primary-color:#2F64E8 !important;
        --background-color:#F5F7FB !important;
        --secondary-background-color:#FFFFFF !important;
        --text-color:#172235 !important;
        --st-primary-color:#2F64E8 !important;
        --st-background-color:#F5F7FB !important;
        --st-secondary-background-color:#FFFFFF !important;
        --st-text-color:#172235 !important;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    main{
        background:#F5F7FB !important;
        color:#172235 !important;
    }

    /* ----- SAIR ----- */
    .engm-logout-row{
        display:flex;
        justify-content:flex-end;
        margin:0 0 2px;
    }

    .engm-logout-link{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        min-height:34px;
        padding:0 15px;
        border:1px solid #CCD8E6;
        border-radius:8px;
        background:#FFFFFF;
        color:#2859BD !important;
        text-decoration:none !important;
        font-size:11px;
        font-weight:700;
    }

    .engm-logout-link:visited{
        color:#2859BD !important;
    }

    /* ----- NAVEGAÇÃO: três botões limpos ----- */
    [class*="st-key-eng_nav_hoje_v16"] button,
    [class*="st-key-eng_nav_amanha_v16"] button,
    [class*="st-key-eng_nav_disp_v16"] button{
        min-height:42px !important;
        border-radius:9px !important;
        font-size:12px !important;
        font-weight:700 !important;
        white-space:nowrap !important;
        padding-left:5px !important;
        padding-right:5px !important;
        box-shadow:none !important;
    }

    [class*="st-key-eng_nav_hoje_v16"] button[kind="secondary"],
    [class*="st-key-eng_nav_amanha_v16"] button[kind="secondary"],
    [class*="st-key-eng_nav_disp_v16"] button[kind="secondary"]{
        background:#EDF1F6 !important;
        border-color:#D7DFE9 !important;
        color:#172235 !important;
    }

    [class*="st-key-eng_nav_hoje_v16"] button[kind="secondary"] *,
    [class*="st-key-eng_nav_amanha_v16"] button[kind="secondary"] *,
    [class*="st-key-eng_nav_disp_v16"] button[kind="secondary"] *{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    [class*="st-key-eng_nav_hoje_v16"] button[kind="primary"],
    [class*="st-key-eng_nav_amanha_v16"] button[kind="primary"],
    [class*="st-key-eng_nav_disp_v16"] button[kind="primary"],
    [class*="st-key-eng_nav_hoje_v16"] [data-testid="stBaseButton-primary"],
    [class*="st-key-eng_nav_amanha_v16"] [data-testid="stBaseButton-primary"],
    [class*="st-key-eng_nav_disp_v16"] [data-testid="stBaseButton-primary"]{
        background:#2F64E8 !important;
        border-color:#2F64E8 !important;
        color:#FFFFFF !important;
    }

    [class*="st-key-eng_nav_hoje_v16"] button[kind="primary"] *,
    [class*="st-key-eng_nav_amanha_v16"] button[kind="primary"] *,
    [class*="st-key-eng_nav_disp_v16"] button[kind="primary"] *,
    [class*="st-key-eng_nav_hoje_v16"] [data-testid="stBaseButton-primary"] *,
    [class*="st-key-eng_nav_amanha_v16"] [data-testid="stBaseButton-primary"] *,
    [class*="st-key-eng_nav_disp_v16"] [data-testid="stBaseButton-primary"] *{
        color:#FFFFFF !important;
        -webkit-text-fill-color:#FFFFFF !important;
    }

    /* ----- INPUTS NATIVOS: Safari/iOS não pode inverter ----- */
    main input,
    main input[type="text"],
    main input[type="date"],
    main input[type="number"],
    main input[type="password"],
    main textarea{
        color-scheme:light !important;
        background-color:#FFFFFF !important;
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
        caret-color:#172235 !important;
        opacity:1 !important;
    }

    main input[type="date"]::-webkit-date-and-time-value{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    main input[type="date"]::-webkit-calendar-picker-indicator{
        opacity:.75 !important;
    }

    /* ----- SELECTS BASEWEB ----- */
    main [data-baseweb="select"],
    main [data-baseweb="select"] > div,
    main [data-baseweb="select"] > div > div,
    main [role="combobox"]{
        background:#FFFFFF !important;
        color:#172235 !important;
        border-color:#D8E0EA !important;
    }

    main [data-baseweb="select"] span,
    main [data-baseweb="select"] input,
    main [role="combobox"] *{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    /* ----- MULTISELECT TAGS: selector correto é span[data-baseweb=tag] ----- */
    main [data-baseweb="tag"]{
        background:#EAF1FF !important;
        border:1px solid #C8D8FF !important;
        color:#1D4ED8 !important;
        border-radius:9px !important;
    }

    main [data-baseweb="tag"] *,
    main [data-baseweb="tag"] span,
    main [data-baseweb="tag"] svg{
        color:#1D4ED8 !important;
        fill:#1D4ED8 !important;
        -webkit-text-fill-color:#1D4ED8 !important;
    }

    /* ----- CHECKBOXES: azul, não vermelho ----- */
    main input[type="checkbox"],
    main input[type="radio"]{
        accent-color:#2F64E8 !important;
    }

    main [data-baseweb="checkbox"] [aria-checked="true"],
    main [data-baseweb="checkbox"] input:checked + div,
    main label:has(input[type="checkbox"]:checked) > div:first-of-type{
        background-color:#2F64E8 !important;
        border-color:#2F64E8 !important;
    }

    /* ----- CAMPO ESTÁTICO ----- */
    .engm-static-field{
        margin:0;
    }

    .engm-static-label{
        font-size:9.5px;
        font-weight:650;
        margin-bottom:6px;
        color:#172235;
    }

    .engm-static-value{
        min-height:43px;
        display:flex;
        align-items:center;
        padding:0 12px;
        border:1px solid #D9E1EB;
        border-radius:8px;
        background:#F1F4F8;
        color:#7A8698;
        font-size:12px;
    }

    /* ----- MENSAGEM DE SUCESSO PRÓPRIA ----- */
    .engm-success-message{
        display:flex;
        align-items:center;
        gap:9px;
        padding:9px 11px;
        margin:2px 0 5px;
        border:1px solid #B9E3C9;
        border-radius:9px;
        background:#ECF8F0;
        color:#176B3A;
        font-size:11px;
        font-weight:650;
    }

    .engm-success-icon{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        width:19px;
        height:19px;
        flex:0 0 19px;
        border-radius:50%;
        background:#22A35A;
        color:#FFFFFF !important;
        font-size:12px;
        line-height:1;
    }

    /* ----- EXPANDERS ----- */
    main [data-testid="stExpander"],
    main [data-testid="stExpander"] details,
    main [data-testid="stExpander"] summary{
        background:#FFFFFF !important;
        color:#172235 !important;
        border-color:#DCE3EC !important;
    }

    main [data-testid="stExpander"] summary *{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    /* ----- BOTÕES SECUNDÁRIOS (inclui Remover) ----- */
    main [data-testid="stBaseButton-secondary"],
    main button[kind="secondary"]{
        background:#FFFFFF !important;
        border-color:#D7E0EB !important;
        color:#31506F !important;
    }

    main [data-testid="stBaseButton-secondary"] *,
    main button[kind="secondary"] *{
        color:#31506F !important;
        -webkit-text-fill-color:#31506F !important;
    }

    [class*="st-key-engm_remover_manual_"] button{
        min-height:34px !important;
        padding:3px 6px !important;
        background:#FFF4F5 !important;
        border-color:#F2C6CC !important;
        color:#A92C3F !important;
        font-size:9.5px !important;
    }

    [class*="st-key-engm_remover_manual_"] button *{
        color:#A92C3F !important;
        -webkit-text-fill-color:#A92C3F !important;
    }

    /* ----- ALERTAS NATIVOS ----- */
    main [data-testid="stAlert"]{
        color:#172235 !important;
    }

    main [data-testid="stAlert"] p,
    main [data-testid="stAlert"] span{
        color:#172235 !important;
        -webkit-text-fill-color:#172235 !important;
    }

    @media(max-width:520px){
        [class*="st-key-eng_nav_hoje_v16"] button,
        [class*="st-key-eng_nav_amanha_v16"] button,
        [class*="st-key-eng_nav_disp_v16"] button{
            font-size:10.5px !important;
            padding-left:2px !important;
            padding-right:2px !important;
        }

        .engm-logout-link{
            min-height:31px;
            padding:0 13px;
            font-size:10px;
        }
    }
    </style>
    """)

    def _feedback_salvo_mobile(mensagem):
        """Confirmação pequena, previsível e independente do tema do aparelho."""
        st.markdown(
            (
                '<div class="engm-success-message">'
                '<span class="engm-success-icon">✓</span>'
                f'<span>{_html.escape(str(mensagem).replace("✓", "").strip())}</span>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    def _mostrar_confirmacao_campo():
        """Exibe uma confirmação pequena e confiável após o rerun."""
        mensagem = st.session_state.pop(
            "_engm_success_message",
            None,
        )
        if mensagem:
            _feedback_salvo_mobile(mensagem)

    def _salvar_apontamentos_lote_mobile(
        itens,
        data_servico,
        engenheiro,
    ):
        """
        Salva toda a equipe em uma única conexão no Neon.
        Mantém exatamente os mesmos dados gravados pelo fluxo anterior,
        mas evita 2+ conexões por colaborador.
        """
        itens = list(itens or [])
        if not itens:
            return 0, []

        # Caminho rápido de produção.
        if (
            DB_BACKEND == "NEON"
            and hasattr(supabase, "_connect")
        ):
            try:
                usar_estrutura = schema_producao_disponivel()
                agora_lote = agora_aproar()

                with supabase._connect() as conn:
                    with conn.cursor() as cur:
                        for item in itens:
                            conv = item["conv"]
                            conv_id = str(
                                conv.get("id")
                                or ""
                            )
                            colab_id = str(
                                conv.get("colaborador_id")
                                or ""
                            )

                            retroativo_item = apontamento_esta_atrasado(
                                data_servico,
                                unidade=item.get("unidade_contexto") or "",
                                agora=agora_lote,
                            )

                            cur.execute(
                                """
                                UPDATE convocacoes
                                   SET obra_id = %s,
                                       status = %s,
                                       tipo_diaria = %s,
                                       custo_pago = %s,
                                       valor_extra = %s,
                                       valor_adicional_noturno = %s,
                                       valor_acordo = %s,
                                       custo_encargos_base = %s,
                                       custos_separados = TRUE,
                                       migracao_sebrae_noturno_v2 = TRUE,
                                       observacao = %s
                                 WHERE id = %s
                                """,
                                (
                                    item["obra_id_final"],
                                    item["status"],
                                    item["tipo_diaria_final"],
                                    float(item["custo_pago_final"] or 0),
                                    float(item["valor_extra_final"] or 0),
                                    float(item["valor_adicional_noturno_final"] or 0),
                                    float(item["valor_acordo_final"] or 0),
                                    float(item["custo_encargos_final"] or 0),
                                    item["nova_obs"],
                                    conv_id,
                                ),
                            )

                            if not usar_estrutura:
                                continue

                            cur.execute(
                                """
                                INSERT INTO apontamentos (
                                    convocacao_id, data_servico, colaborador_id,
                                    engenheiro, status, valor_extra, observacao,
                                    apontado_em, apontado_por, retroativo, atualizado_em,
                                    tipo_diaria, custo_pago, valor_acordo,
                                    valor_adicional_noturno, custo_encargos_base,
                                    custos_separados
                                )
                                VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s,%s,NOW(),%s,%s,%s,%s,%s,TRUE)
                                ON CONFLICT (convocacao_id) DO UPDATE SET
                                    data_servico = EXCLUDED.data_servico,
                                    colaborador_id = EXCLUDED.colaborador_id,
                                    engenheiro = EXCLUDED.engenheiro,
                                    status = EXCLUDED.status,
                                    valor_extra = EXCLUDED.valor_extra,
                                    observacao = EXCLUDED.observacao,
                                    apontado_por = EXCLUDED.apontado_por,
                                    retroativo = EXCLUDED.retroativo,
                                    tipo_diaria = EXCLUDED.tipo_diaria,
                                    custo_pago = EXCLUDED.custo_pago,
                                    valor_acordo = EXCLUDED.valor_acordo,
                                    valor_adicional_noturno = EXCLUDED.valor_adicional_noturno,
                                    custo_encargos_base = EXCLUDED.custo_encargos_base,
                                    custos_separados = TRUE,
                                    migracao_sebrae_noturno_v2 = TRUE,
                                    atualizado_em = NOW()
                                """,
                                (
                                    conv_id,
                                    data_servico,
                                    colab_id,
                                    str(engenheiro),
                                    str(item["status"]),
                                    float(item["valor_extra_final"] or 0),
                                    str(item["obs_livre"] or ""),
                                    str(engenheiro),
                                    retroativo_item,
                                    item["tipo_diaria_final"],
                                    float(item["custo_pago_final"] or 0),
                                    float(item["valor_acordo_final"] or 0),
                                    float(item["valor_adicional_noturno_final"] or 0),
                                    float(item["custo_encargos_final"] or 0),
                                ),
                            )

                            cur.execute(
                                """
                                DELETE FROM servicos_apontamento
                                WHERE convocacao_id = %s
                                """,
                                (conv_id,),
                            )

                            obra_principal = dict_obras.get(
                                item["obra_id_final"],
                                {},
                            )

                            cur.execute(
                                """
                                INSERT INTO servicos_apontamento (
                                    convocacao_id, obra_id, obra_nome_snapshot,
                                    unidade_snapshot, periodo, principal
                                )
                                VALUES (%s,%s,%s,%s,%s,TRUE)
                                """,
                                (
                                    conv_id,
                                    str(
                                        item["obra_id_final"]
                                        or ""
                                    ),
                                    str(
                                        obra_principal.get("nome")
                                        or ""
                                    ),
                                    str(
                                        obra_principal.get("unidade")
                                        or ""
                                    ),
                                    str(
                                        item["periodo_principal"]
                                        or ""
                                    ),
                                ),
                            )

                            for adicional in (
                                item["adicionais"]
                                or []
                            ):
                                nome = str(
                                    adicional.get("servico")
                                    or ""
                                ).strip()
                                if not nome:
                                    continue

                                obra_id_adic = str(
                                    adicional.get("obra_id")
                                    or ""
                                ).strip()
                                obra_adic = (
                                    dict_obras.get(
                                        obra_id_adic,
                                        {},
                                    )
                                    if obra_id_adic
                                    else {}
                                )

                                if not obra_adic:
                                    obra_adic = next(
                                        (
                                            o for o in obras
                                            if normalizar(
                                                o.get("nome")
                                            )
                                            == normalizar(nome)
                                        ),
                                        {},
                                    )

                                cur.execute(
                                    """
                                    INSERT INTO servicos_apontamento (
                                        convocacao_id, obra_id, obra_nome_snapshot,
                                        unidade_snapshot, periodo, principal
                                    )
                                    VALUES (%s,%s,%s,%s,%s,FALSE)
                                    """,
                                    (
                                        conv_id,
                                        str(
                                            obra_adic.get("id")
                                            or obra_id_adic
                                            or ""
                                        ),
                                        nome,
                                        str(
                                            adicional.get("unidade")
                                            or obra_adic.get("unidade")
                                            or obra_principal.get("unidade")
                                            or ""
                                        ),
                                        str(
                                            adicional.get("periodo")
                                            or ""
                                        ),
                                    ),
                                )

                            # Auditoria no mesmo commit: sem abrir outra conexão.
                            cur.execute(
                                """
                                INSERT INTO auditoria
                                    (entidade, entidade_id, acao, usuario,
                                     antes, depois, contexto)
                                VALUES
                                    (%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)
                                """,
                                (
                                    "apontamento",
                                    conv_id,
                                    "SALVAR",
                                    str(engenheiro),
                                    None,
                                    _json_db({
                                        "data_servico": data_servico,
                                        "status": item["status"],
                                        "tipo_diaria": item["tipo_diaria_final"],
                                        "custo_pago": item["custo_pago_final"],
                                        "valor_extra": item["valor_extra_final"],
                                        "valor_adicional_noturno": item["valor_adicional_noturno_final"],
                                        "valor_acordo": item["valor_acordo_final"],
                                        "custo_encargos_base": item["custo_encargos_final"],
                                        "obra_principal_id": str(
                                            item["obra_id_final"]
                                        ),
                                        "periodo_principal": item["periodo_principal"],
                                        "servicos_adicionais": item["adicionais"],
                                        "retroativo": retroativo_item,
                                    }),
                                    _json_db({
                                        "origem": "portal_engenheiro_lote",
                                    }),
                                ),
                            )

                        conn.commit()

                limpar_cache_convocacoes()
                return len(itens), []

            except Exception:
                # Fallback abaixo mantém o comportamento antigo se houver
                # qualquer incompatibilidade inesperada no banco.
                pass

        salvos = 0
        falhas = []

        for item in itens:
            conv = item["conv"]
            nome_pessoa = item["nome_pessoa"]

            try:
                supabase.table(
                    "convocacoes"
                ).update(
                    {
                        "obra_id": item["obra_id_final"],
                        "status": item["status"],
                        "tipo_diaria": item["tipo_diaria_final"],
                        "custo_pago": item["custo_pago_final"],
                        "valor_extra": item["valor_extra_final"],
                        "valor_adicional_noturno": item["valor_adicional_noturno_final"],
                        "valor_acordo": item["valor_acordo_final"],
                        "custo_encargos_base": item["custo_encargos_final"],
                        "custos_separados": True,
                        "migracao_sebrae_noturno_v2": True,
                        "observacao": item["nova_obs"],
                    }
                ).eq(
                    "id",
                    conv.get("id"),
                ).execute()

                salvar_apontamento_estruturado(
                    conv,
                    data_servico,
                    engenheiro,
                    item["status"],
                    item["valor_extra_final"],
                    item["obs_livre"],
                    item["obra_id_final"],
                    item["periodo_principal"],
                    item["adicionais"],
                    tipo_diaria=item["tipo_diaria_final"],
                    custo_pago=item["custo_pago_final"],
                    valor_acordo=item["valor_acordo_final"],
                    valor_adicional_noturno=item["valor_adicional_noturno_final"],
                    custo_encargos_base=item["custo_encargos_final"],
                )

                salvos += 1

            except Exception as e:
                falhas.append(
                    f"{nome_pessoa}: {str(e)[:110]}"
                )

        limpar_cache_convocacoes()
        return salvos, falhas

    def _buscar_convocacoes_campo(engenheiro, data_ref):
        return _buscar_convocacoes_intervalo(
            data_ref,
            data_ref,
            engenheiro,
        ) or []

    def _enriquecer_convocacoes_campo(registros):
        saida = []
        for registro in registros or []:
            item = dict(registro)
            item["dados_obra"] = dict_obras.get(
                item.get("obra_id"),
                {
                    "unidade": "Desconhecida",
                    "nome": NOME_OBRA_PLACEHOLDER,
                },
            )
            saida.append(item)
        return saida

    def _convocacao_apontada_campo(conv):
        obra = conv.get("dados_obra") or dict_obras.get(
            conv.get("obra_id"),
            {},
        )
        return bool(obra) and not eh_obra_placeholder(obra)

    def _servicos_convocacao_mobile(conv):
        """
        Retorna todos os serviços reais vinculados ao registro:
        principal + adicionais, preservando unidade/obra_id.
        """
        servicos = []

        obra_principal = (
            conv.get("dados_obra")
            or dict_obras.get(conv.get("obra_id"), {})
            or {}
        )

        if obra_principal and not eh_obra_placeholder(obra_principal):
            servicos.append({
                "principal": True,
                "obra_id": str(
                    obra_principal.get("id")
                    or conv.get("obra_id")
                    or ""
                ),
                "obra": str(
                    obra_principal.get("nome")
                    or ""
                ),
                "unidade": str(
                    obra_principal.get("unidade")
                    or ""
                ),
                "periodo": turno_da_convocacao(conv),
            })

        meta = obter_metadata_operacional(
            conv.get("observacao")
            or ""
        )

        for adicional in _normalizar_servicos_adicionais(meta):
            nome = str(
                adicional.get("servico")
                or ""
            ).strip()
            obra_id = str(
                adicional.get("obra_id")
                or ""
            ).strip()
            unidade = str(
                adicional.get("unidade")
                or ""
            ).strip()

            obra_ref = (
                dict_obras.get(obra_id, {})
                if obra_id
                else {}
            )

            if not obra_ref and nome:
                obra_ref = next(
                    (
                        o for o in obras
                        if normalizar(
                            o.get("nome")
                        ) == normalizar(nome)
                        and (
                            not unidade
                            or normalizar(
                                o.get("unidade")
                            ) == normalizar(unidade)
                        )
                    ),
                    {},
                )

            servicos.append({
                "principal": False,
                "obra_id": str(
                    obra_ref.get("id")
                    or obra_id
                    or ""
                ),
                "obra": str(
                    nome
                    or obra_ref.get("nome")
                    or ""
                ),
                "unidade": str(
                    unidade
                    or obra_ref.get("unidade")
                    or ""
                ),
                "periodo": str(
                    adicional.get("periodo")
                    or turno_da_convocacao(conv)
                ),
            })

        # Remove duplicatas reais.
        saida = []
        vistos = set()
        for item in servicos:
            chave = (
                str(item.get("obra_id") or ""),
                normalizar(item.get("obra") or ""),
                normalizar(item.get("unidade") or ""),
                bool(item.get("principal")),
            )
            if chave in vistos:
                continue
            vistos.add(chave)
            saida.append(item)

        return saida

    def _unidades_convocacao_mobile(conv):
        """
        Unidades vinculadas à convocação.

        IMPORTANTE:
        antes do apontamento a obra principal é um placeholder da unidade.
        Mesmo sendo placeholder, a unidade precisa aparecer no seletor para
        que o engenheiro consiga escolher a obra/serviço real.
        """
        unidades = []

        obra_principal = (
            conv.get("dados_obra")
            or dict_obras.get(conv.get("obra_id"), {})
            or {}
        )

        unidade_principal = str(
            obra_principal.get("unidade")
            or ""
        ).strip()

        if (
            unidade_principal
            and normalizar(unidade_principal)
            not in {"", "desconhecida", "desconhecido"}
        ):
            unidades.append(unidade_principal)

        for serv in _servicos_convocacao_mobile(conv):
            unidade_serv = str(
                serv.get("unidade")
                or ""
            ).strip()

            if (
                unidade_serv
                and normalizar(unidade_serv)
                not in {
                    normalizar(u)
                    for u in unidades
                }
            ):
                unidades.append(unidade_serv)

        return unidades

    def _convocacao_tem_unidade_mobile(conv, unidade):
        alvo = normalizar(unidade or "")
        if not alvo:
            return False

        return any(
            normalizar(unid) == alvo
            for unid in _unidades_convocacao_mobile(conv)
        )

    def _servico_contexto_unidade_mobile(conv, unidade):
        alvo = normalizar(unidade or "")
        servicos = _servicos_convocacao_mobile(conv)

        # Se houver serviço real principal nessa unidade, ele tem prioridade.
        for serv in servicos:
            if (
                serv.get("principal")
                and normalizar(serv.get("unidade") or "") == alvo
            ):
                return serv

        # Depois, procura serviço adicional real nessa unidade.
        for serv in servicos:
            if normalizar(serv.get("unidade") or "") == alvo:
                return serv

        # Se ainda não há serviço real definido, usa o placeholder apenas
        # como contexto de UNIDADE. A obra continuará vazia para o engenheiro
        # escolher no apontamento.
        obra_principal = (
            conv.get("dados_obra")
            or dict_obras.get(conv.get("obra_id"), {})
            or {}
        )

        unidade_principal = str(
            obra_principal.get("unidade")
            or ""
        ).strip()

        if (
            unidade_principal
            and normalizar(unidade_principal) == alvo
        ):
            return {
                "principal": True,
                "placeholder": eh_obra_placeholder(
                    obra_principal
                ),
                "obra_id": (
                    ""
                    if eh_obra_placeholder(
                        obra_principal
                    )
                    else str(
                        obra_principal.get("id")
                        or conv.get("obra_id")
                        or ""
                    )
                ),
                "obra": (
                    ""
                    if eh_obra_placeholder(
                        obra_principal
                    )
                    else str(
                        obra_principal.get("nome")
                        or ""
                    )
                ),
                "unidade": unidade_principal,
                "periodo": turno_da_convocacao(conv),
            }

        return None

    def _lista_convocados_mobile(registros, mostrar_status=False):
        if not registros:
            st.caption("Nenhuma pessoa convocada.")
            return

        itens_html = []
        for conv in registros:
            colab = dict_colaboradores.get(
                conv.get("colaborador_id"),
                {},
            )
            obra = conv.get("dados_obra") or dict_obras.get(
                conv.get("obra_id"),
                {},
            )
            nome = str(colab.get("nome") or "Não identificado")
            funcao = str(colab.get("funcao") or "-")
            unidade = str(obra.get("unidade") or "-")
            turno = turno_da_convocacao(conv)
            status = normalizar_status_operacional(
                conv.get("status")
            )

            lado = status if mostrar_status else turno
            itens_html.append(
                f"""
                <div class="engm-list-item">
                    <div class="engm-list-main">
                        <div class="engm-list-name">{_html.escape(nome)}</div>
                        <div class="engm-list-meta">
                            {_html.escape(funcao)} · {_html.escape(unidade)} · {_html.escape(turno)}
                        </div>
                    </div>
                    <div class="engm-list-side">{_html.escape(str(lado))}</div>
                </div>
                """
            )

        st.html(
            '<div class="engm-list">'
            + "".join(itens_html)
            + "</div>"
        )

    hoje_campo = agora_aproar().date()
    amanha_campo = proximo_dia_util(hoje_campo)

    st.markdown(
        f"""
        <div class="engm-head engm-head-v2">
            <div class="engm-brand">
                <div class="engm-brand-top">
                    <div class="engm-brand-logo-wrap"><img class="engm-brand-logo-img" src="data:image/png;base64,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" alt="Logo APROAR"></div>
                    <div class="engm-brand-copy">
                        <div class="engm-brand-wordmark">APROAR</div>
                        <div class="engm-kicker">Portal do Supervisor</div>
                    </div>
                </div>
                <div class="engm-title">Minha equipe</div>
            </div>
            <div class="engm-date engm-date-v2">
                <div class="engm-date-chip-label">Data</div>
                <b>{hoje_campo.strftime('%d/%m/%Y')}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="engm-logout-row">
            <a class="engm-logout-link" href="?logout=1">Sair</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navegação por botões em vez de radio.
    # Isso elimina de vez as bolinhas pretas/vermelhas do Safari/iOS.
    if "_engm_area_campo" not in st.session_state:
        st.session_state["_engm_area_campo"] = "Hoje"

    area_campo = st.session_state["_engm_area_campo"]

    nav_c1, nav_c2, nav_c3 = st.columns(3)

    with nav_c1:
        if st.button(
            "Apontamentos",
            type=("primary" if area_campo == "Hoje" else "secondary"),
            use_container_width=True,
            key="eng_nav_hoje_v16",
        ):
            st.session_state["_engm_area_campo"] = "Hoje"
            st.rerun()

    with nav_c2:
        if st.button(
            "Convocação",
            type=("primary" if area_campo == "Amanhã" else "secondary"),
            use_container_width=True,
            key="eng_nav_amanha_v16",
        ):
            st.session_state["_engm_area_campo"] = "Amanhã"
            st.rerun()

    with nav_c3:
        if st.button(
            "Disponibilidade",
            type=("primary" if area_campo == "Disponibilidade" else "secondary"),
            use_container_width=True,
            key="eng_nav_disp_v16",
        ):
            st.session_state["_engm_area_campo"] = "Disponibilidade"
            st.rerun()

    _mostrar_confirmacao_campo()

    # =====================================================================
    # HOJE — RESUMO + CONVOCADOS + APONTAMENTO NA MESMA TELA
    # =====================================================================
    if area_campo == "Hoje":
        c_ap_eng, c_ap_unid, c_ap_data = st.columns(
            [1.05, 1.05, .82]
        )

        with c_ap_eng:
            engenheiro_campo = st.selectbox(
                "Engenheiro",
                ENGENHEIROS,
                key="engenheiro_campo_mobile",
            )

        with c_ap_data:
            data_apont = st.date_input(
                "Data",
                value=hoje_campo,
                format="DD/MM/YYYY",
                key="engm_data_apont",
            )

        convocacoes_todas_unidades = _enriquecer_convocacoes_campo(
            _buscar_convocacoes_campo(
                engenheiro_campo,
                data_apont,
            )
        )

        # Prioriza no seletor as unidades nas quais esse engenheiro realmente
        # tem equipe na data escolhida. As demais continuam disponíveis para
        # apontamento retroativo/inclusão excepcional.
        unidades_com_equipe = sorted(
            {
                str(unidade).strip()
                for c in convocacoes_todas_unidades
                for unidade in _unidades_convocacao_mobile(c)
                if str(unidade).strip()
            }
        )

        # No apontamento, o engenheiro só pode escolher unidades para as quais
        # ele realmente fez convocação na data selecionada.
        unidades_apontamento = list(
            unidades_com_equipe
        )

        with c_ap_unid:
            if unidades_apontamento:
                unidade_apont_campo = st.selectbox(
                    "Unidade",
                    unidades_apontamento,
                    key="engm_unidade_apont_top",
                )
            else:
                unidade_apont_campo = ""
                _texto_unidade_vazia = (
                    "Sem convocação nesta data"
                    if data_apont < hoje_campo
                    else "Nenhuma unidade convocada"
                )
                st.markdown(
                    (
                        '<div class="engm-static-field">'
                        '<div class="engm-static-label">Unidade convocada</div>'
                        f'<div class="engm-static-value">{_html.escape(_texto_unidade_vazia)}</div>'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

        # Daqui para baixo o apontamento inteiro considera SOMENTE a unidade
        # selecionada: resumo, colaboradores, ação em massa e salvamento.
        convocacoes_data = [
            c
            for c in convocacoes_todas_unidades
            if _convocacao_tem_unidade_mobile(
                c,
                unidade_apont_campo,
            )
        ]

        total_data = len(convocacoes_data)
        apontados_data = sum(
            1
            for c in convocacoes_data
            if _convocacao_apontada_campo(c)
        )
        pendentes_data = max(
            0,
            total_data - apontados_data,
        )
        ausencias_data = sum(
            1
            for c in convocacoes_data
            if normalizar_status_operacional(
                c.get("status")
            )
            in {"Falta", "Atestado"}
        )

        classe_pend = "warn" if pendentes_data else ""
        classe_aus = "danger" if ausencias_data else ""

        st.markdown(
            f"""
            <div class="engm-summary engm-summary-v2">
                <div class="engm-summary-item">
                    <div class="engm-summary-value">{total_data}</div>
                    <div class="engm-summary-label">convocados</div>
                </div>
                <div class="engm-summary-item">
                    <div class="engm-summary-value">{apontados_data}</div>
                    <div class="engm-summary-label">apontados</div>
                </div>
                <div class="engm-summary-item {classe_pend}">
                    <div class="engm-summary-value">{pendentes_data}</div>
                    <div class="engm-summary-label">pendentes</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if data_apont < hoje_campo:
            st.markdown(
                """
                <div style="
                    background:#FFF7BF;
                    color:#111827;
                    border:1px solid #F3E38B;
                    border-radius:10px;
                    padding:14px 16px;
                    font-size:14px;
                    line-height:1.45;
                    font-weight:500;
                    margin:6px 0 12px 0;
                ">
                    Apontamento retroativo. O sistema registrará o atraso automaticamente.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="engm-section-title">Equipe do dia</div>'
            '<div class="engm-section-sub">'
            'Preencha os apontamentos e salve tudo de uma vez.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.html("""
        <style>
        /* ==========================================================
           V6.30 — APONTAMENTO MOBILE COMPACTO
           ========================================================== */
        div[class*="st-key-engm_point_card_"]{
            padding:10px 11px !important;
        }

        div[class*="st-key-engm_point_card_"] [data-testid="stHorizontalBlock"]{
            gap:.5rem !important;
        }

        div[class*="st-key-engm_point_card_"] label p,
        div[class*="st-key-engm_inc_servico_"] label p{
            font-size:10px !important;
            line-height:1.15 !important;
            margin-bottom:3px !important;
        }

        div[class*="st-key-engm_point_card_"] div[data-baseweb="select"] > div,
        div[class*="st-key-engm_inc_servico_"] div[data-baseweb="select"] > div{
            min-height:40px !important;
            height:40px !important;
            border-radius:8px !important;
        }

        div[class*="st-key-engm_point_card_"] input,
        div[class*="st-key-engm_inc_servico_"] input{
            min-height:38px !important;
            height:38px !important;
            font-size:12px !important;
        }

        div[class*="st-key-engm_point_card_"] [data-testid="stNumberInput"] button{
            min-height:38px !important;
            height:38px !important;
            width:34px !important;
        }

        .engm-pay-summary{
            margin:3px 0 1px;
            padding:7px 9px;
            border-radius:8px;
            background:#F7F9FC;
            border:1px solid #E4E9F0;
            color:#738097;
            font-size:9.5px;
            line-height:1.35;
        }

        .engm-service-title{
            margin:5px 0 3px;
            color:#536176;
            font-size:9px;
            font-weight:800;
            text-transform:uppercase;
            letter-spacing:.035em;
        }

        div[class*="st-key-engm_add_serv_"] button,
        div[class*="st-key-engm_rem_serv_"] button,
        div[class*="st-key-engm_inc_add_serv"] button,
        div[class*="st-key-engm_inc_rem_serv"] button{
            min-height:34px !important;
            height:34px !important;
            padding:3px 8px !important;
            font-size:10px !important;
            border-radius:7px !important;
        }

        @media(max-width:560px){
            div[class*="st-key-engm_point_card_"]{
                padding:8px !important;
            }

            div[class*="st-key-engm_point_card_"] [data-testid="stHorizontalBlock"],
            div[class*="st-key-engm_inc_servico_"] [data-testid="stHorizontalBlock"]{
                gap:.35rem !important;
            }

            div[class*="st-key-engm_point_card_"] div[data-baseweb="select"] span,
            div[class*="st-key-engm_inc_servico_"] div[data-baseweb="select"] span{
                font-size:11px !important;
            }
        }
        </style>
        """)

        # Inclusão excepcional / retroativa.
        with st.expander(
            "Adicionar colaborador / avulso ao apontamento",
            expanded=False,
        ):
            st.caption(
                "Use para apontamento retroativo ou inclusão excepcional. "
                "Adicione quantos serviços forem necessários e salve tudo de uma vez."
            )

            tipo_inc = st.radio(
                "Tipo",
                ["Cadastrado", "Avulso"],
                horizontal=True,
                key="engm_inc_tipo",
            )

            colaborador_id_inc = None
            nome_exibicao_inc = ""

            if tipo_inc == "Cadastrado":
                labels_inc = {
                    f"{c.get('nome')} ({c.get('funcao','-')})": c.get("id")
                    for c in sorted(
                        colaboradores,
                        key=lambda x: normalizar(
                            x.get("nome", "")
                        ),
                    )
                }

                nome_inc = st.selectbox(
                    "Colaborador",
                    ["— Selecione —"] + list(labels_inc.keys()),
                    key="engm_inc_colab",
                )

                if nome_inc != "— Selecione —":
                    colaborador_id_inc = labels_inc.get(nome_inc)
                    nome_exibicao_inc = nome_inc

            else:
                nome_avulso_inc = st.text_input(
                    "Nome do avulso",
                    key="engm_inc_avulso_nome",
                    placeholder="Nome completo",
                )

                c_av1, c_av2 = st.columns(2)

                with c_av1:
                    tipo_diaria_inc = st.selectbox(
                        "Categoria",
                        ["Profissional", "Ajudante"],
                        key="engm_inc_avulso_tipo",
                    )

                with c_av2:
                    funcao_avulso_inc = st.text_input(
                        "Função (opcional)",
                        key="engm_inc_avulso_funcao",
                    )

            unidades_retro = sorted(
                {
                    str(o.get("unidade") or "").strip()
                    for o in obras
                    if str(o.get("unidade") or "").strip()
                    and not eh_obra_placeholder(o)
                }
            )

            eh_retroativo = data_apont < hoje_campo
            pode_escolher_unidade_inc = (
                eh_retroativo
                or not unidade_apont_campo
            )

            qtd_inc_key = "_engm_inc_qtd_servicos"
            if qtd_inc_key not in st.session_state:
                st.session_state[qtd_inc_key] = 1

            qtd_servicos_inc = max(
                1,
                int(
                    st.session_state.get(
                        qtd_inc_key,
                        1,
                    )
                ),
            )

            b_inc1, b_inc2, b_inc3 = st.columns(
                [1.35, 1.35, 2.3],
                vertical_alignment="center",
            )

            with b_inc1:
                if st.button(
                    "+ Adicionar serviço",
                    key="engm_inc_add_serv",
                    use_container_width=True,
                ):
                    st.session_state[qtd_inc_key] = (
                        qtd_servicos_inc + 1
                    )
                    st.rerun()

            with b_inc2:
                if st.button(
                    "− Remover último",
                    key="engm_inc_rem_serv",
                    use_container_width=True,
                    disabled=qtd_servicos_inc <= 1,
                ):
                    idx_rem = qtd_servicos_inc
                    for prefix in (
                        "engm_inc_unidade_",
                        "engm_inc_obra_",
                        "engm_inc_turno_",
                    ):
                        st.session_state.pop(
                            f"{prefix}{idx_rem}",
                            None,
                        )

                    st.session_state[qtd_inc_key] = max(
                        1,
                        qtd_servicos_inc - 1,
                    )
                    st.rerun()

            with b_inc3:
                st.caption(
                    f"{qtd_servicos_inc} serviço(s) no apontamento"
                )

            servicos_inc_ui = []

            for idx_serv in range(
                1,
                qtd_servicos_inc + 1,
            ):
                with st.container(
                    border=True,
                    key=f"engm_inc_servico_{idx_serv}",
                ):
                    st.markdown(
                        (
                            '<div class="engm-service-title">'
                            f'Serviço {idx_serv}'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )

                    if pode_escolher_unidade_inc:
                        unidade_default = (
                            unidade_apont_campo
                            if unidade_apont_campo in unidades_retro
                            else (
                                unidades_retro[0]
                                if unidades_retro
                                else ""
                            )
                        )

                        key_uni = (
                            f"engm_inc_unidade_{idx_serv}"
                        )

                        if (
                            key_uni not in st.session_state
                            and unidade_default
                        ):
                            st.session_state[key_uni] = unidade_default

                        c_uni, c_turno = st.columns(
                            [1.25, .75]
                        )

                        with c_uni:
                            unidade_inc = (
                                st.selectbox(
                                    "Unidade",
                                    unidades_retro,
                                    key=key_uni,
                                )
                                if unidades_retro
                                else ""
                            )

                        with c_turno:
                            turno_inc = st.selectbox(
                                "Turno",
                                [
                                    "Manhã",
                                    "Tarde",
                                    "Noite",
                                    "Integral",
                                ],
                                key=(
                                    f"engm_inc_turno_{idx_serv}"
                                ),
                            )

                        obras_inc = (
                            obras_reais_da_unidade(
                                unidade_inc
                            )
                            if unidade_inc
                            else []
                        )

                        mapa_inc = {
                            o.get("nome"): o.get("id")
                            for o in obras_inc
                        }

                        obra_inc = st.selectbox(
                            "Obra / Serviço",
                            ["— Selecione —"]
                            + list(mapa_inc.keys()),
                            key=(
                                f"engm_inc_obra_{idx_serv}"
                            ),
                        )

                    else:
                        unidade_inc = unidade_apont_campo
                        obras_inc = (
                            obras_reais_da_unidade(
                                unidade_inc
                            )
                            if unidade_inc
                            else []
                        )

                        mapa_inc = {
                            o.get("nome"): o.get("id")
                            for o in obras_inc
                        }

                        c_obra, c_turno = st.columns(
                            [1.55, .65]
                        )

                        with c_obra:
                            obra_inc = st.selectbox(
                                "Obra / Serviço",
                                ["— Selecione —"]
                                + list(mapa_inc.keys()),
                                key=(
                                    f"engm_inc_obra_{idx_serv}"
                                ),
                            )

                        with c_turno:
                            turno_inc = st.selectbox(
                                "Turno",
                                [
                                    "Manhã",
                                    "Tarde",
                                    "Noite",
                                    "Integral",
                                ],
                                key=(
                                    f"engm_inc_turno_{idx_serv}"
                                ),
                            )

                    servicos_inc_ui.append({
                        "idx": idx_serv,
                        "unidade": unidade_inc,
                        "obra": obra_inc,
                        "turno": turno_inc,
                        "mapa": mapa_inc,
                    })

            if st.button(
                "Adicionar ao apontamento",
                use_container_width=True,
                type="primary",
                key="engm_inc_btn",
            ):
                erros_inc = []
                servicos_inc = []
                obras_ids_inc = []

                for item_inc in servicos_inc_ui:
                    idx_serv = item_inc["idx"]

                    if not item_inc["unidade"]:
                        erros_inc.append(
                            f"Serviço {idx_serv}: selecione a unidade."
                        )
                        continue

                    if item_inc["obra"] not in item_inc["mapa"]:
                        erros_inc.append(
                            f"Serviço {idx_serv}: selecione a obra/serviço."
                        )
                        continue

                    obra_id_inc = item_inc["mapa"][
                        item_inc["obra"]
                    ]

                    if str(obra_id_inc) in {
                        str(x)
                        for x in obras_ids_inc
                    }:
                        erros_inc.append(
                            f"Serviço {idx_serv}: esta obra já foi adicionada."
                        )
                        continue

                    obras_ids_inc.append(
                        obra_id_inc
                    )

                    servicos_inc.append({
                        "obra_id": obra_id_inc,
                        "turno": item_inc["turno"],
                    })

                if erros_inc:
                    for erro_inc in erros_inc:
                        st.warning(erro_inc)

                else:
                    if tipo_inc == "Avulso":
                        if not nome_avulso_inc.strip():
                            st.warning(
                                "Digite o nome do funcionário avulso."
                            )
                            colaborador_id_inc = None
                        else:
                            (
                                colaborador_id_inc,
                                colab_criado_inc,
                                msg_criacao_inc,
                            ) = criar_ou_obter_colaborador_manual(
                                nome_avulso_inc,
                                tipo_diaria_inc,
                                funcao_avulso_inc,
                                avulso=True,
                            )

                            nome_exibicao_inc = str(
                                (
                                    colab_criado_inc
                                    or {}
                                ).get("nome")
                                or nome_avulso_inc
                            )

                            if not colaborador_id_inc:
                                st.warning(
                                    msg_criacao_inc
                                    or "Não foi possível cadastrar o avulso."
                                )

                    if not colaborador_id_inc:
                        if tipo_inc == "Cadastrado":
                            st.warning(
                                "Selecione um colaborador."
                            )

                    else:
                        try:
                            existentes_todos_data = (
                                _buscar_convocacoes_intervalo(
                                    data_apont,
                                    data_apont,
                                    None,
                                )
                                or []
                            )
                        except Exception:
                            existentes_todos_data = []

                        indisp_map_apont = {}

                        try:
                            for _ind in (
                                _carregar_indisponibilidades_disponibilidade()
                                or []
                            ):
                                _cid_ind = str(
                                    _ind.get("colaborador_id")
                                    or ""
                                ).strip()

                                if not _cid_ind:
                                    continue

                                try:
                                    _ini_ind = datetime.date.fromisoformat(
                                        str(_ind.get("inicio"))
                                    )
                                    _fim_ind = datetime.date.fromisoformat(
                                        str(_ind.get("fim"))
                                    )
                                except Exception:
                                    continue

                                if (
                                    _ini_ind
                                    <= data_apont
                                    <= _fim_ind
                                ):
                                    indisp_map_apont[
                                        _cid_ind
                                    ] = _ind

                        except Exception:
                            indisp_map_apont = {}

                        with st.spinner(
                            "Salvando apontamento..."
                        ):
                            ok, msg = (
                                incluir_multiplos_servicos_direto_apontamento(
                                    colaborador_id_inc,
                                    engenheiro_campo,
                                    data_apont,
                                    servicos_inc,
                                    existentes_data=existentes_todos_data,
                                    indisponiveis_map=indisp_map_apont,
                                )
                            )

                        if ok:
                            limpar_cache_convocacoes()

                            # Volta o formulário para 1 serviço após salvar.
                            for idx_limpa in range(
                                1,
                                qtd_servicos_inc + 1,
                            ):
                                for prefix in (
                                    "engm_inc_unidade_",
                                    "engm_inc_obra_",
                                    "engm_inc_turno_",
                                ):
                                    st.session_state.pop(
                                        f"{prefix}{idx_limpa}",
                                        None,
                                    )

                            st.session_state[
                                qtd_inc_key
                            ] = 1

                            st.session_state[
                                "_engm_success_message"
                            ] = (
                                f"✓ Apontamento salvo com sucesso · "
                                f"{nome_exibicao_inc} · "
                                f"{len(servicos_inc)} serviço(s)."
                            )
                            st.rerun()

                        else:
                            st.warning(msg)

        if not convocacoes_data:
            st.info(
                "Nenhuma equipe encontrada para esta data. "
                "Use a inclusão acima se precisar fazer um apontamento retroativo."
            )

        else:
            # A unidade já foi escolhida no topo, ao lado do engenheiro.
            render_campo = list(convocacoes_data)

            # Só libera a ação em massa quando todos os colaboradores exibidos
            # já possuem uma obra/serviço real definida.
            sem_servico_definido = [
                conv
                for conv in render_campo
                if not _convocacao_apontada_campo(conv)
            ]
            todos_com_servico = (
                bool(render_campo)
                and not sem_servico_definido
            )

            if not todos_com_servico:
                st.caption(
                    "Para marcar todos como presentes, defina primeiro a obra/serviço "
                    "de todos os colaboradores exibidos."
                )

            if st.button(
                "Marcar todos como presentes",
                use_container_width=True,
                key="engm_all_present",
                disabled=not todos_com_servico,
            ):
                for conv in render_campo:
                    try:
                        _turno_lote = turno_da_convocacao(
                            conv
                        )
                        _status_lote = {
                            "Manhã": "Presente (Só Manhã)",
                            "Tarde": "Presente (Só Tarde)",
                        }.get(
                            _turno_lote,
                            "Presente (Integral)",
                        )

                        supabase.table("convocacoes").update(
                            {"status": _status_lote}
                        ).eq(
                            "id",
                            conv.get("id"),
                        ).execute()
                    except Exception:
                        pass

                limpar_cache_convocacoes()
                st.session_state[
                    "_engm_success_message"
                ] = "✓ Presenças salvas com sucesso."
                st.rerun()

            # Todas as convocações do dia são necessárias para aplicar a regra
            # do 2º serviço sem duplicar alguém que já tem outra convocação.
            try:
                todas_convs_data = (
                    _buscar_convocacoes_intervalo(
                        data_apont,
                        data_apont,
                        None,
                    )
                    or []
                )
            except Exception:
                todas_convs_data = list(convocacoes_data)

            convs_por_colaborador = {}
            for item_conv in todas_convs_data:
                chave_colab = str(
                    item_conv.get("colaborador_id")
                    or ""
                )
                convs_por_colaborador.setdefault(
                    chave_colab,
                    [],
                ).append(item_conv)

            periodos_servico = [
                "Integral",
                "Manhã",
                "Tarde",
                "Noite",
                "Outro",
            ]

            dados_form = {}

            with st.container():
                for conv in render_campo:
                    c_id = conv.get("id")
                    colab = dict_colaboradores.get(
                        conv.get("colaborador_id"),
                        {
                            "nome": "Desconhecido",
                            "funcao": "-",
                        },
                    )
                    contexto_unidade = (
                        _servico_contexto_unidade_mobile(
                            conv,
                            unidade_apont_campo,
                        )
                    )

                    unidade = str(
                        (
                            contexto_unidade
                            or {}
                        ).get("unidade")
                        or unidade_apont_campo
                        or "Desconhecida"
                    )

                    obras_card = obras_reais_da_unidade(
                        unidade
                    )
                    mapa_obras = {
                        o.get("nome"): o.get("id")
                        for o in obras_card
                    }
                    opcoes_obras = [
                        "— Selecione o serviço —"
                    ] + list(mapa_obras.keys())

                    obra_atual = dict_obras.get(
                        conv.get("obra_id"),
                        {},
                    )

                    nome_obra_atual = str(
                        (
                            contexto_unidade
                            or {}
                        ).get("obra")
                        or obra_atual.get("nome")
                        or ""
                    )

                    idx_obra = (
                        opcoes_obras.index(
                            nome_obra_atual
                        )
                        if nome_obra_atual in mapa_obras
                        else 0
                    )

                    contexto_eh_principal = bool(
                        (contexto_unidade or {}).get(
                            "principal"
                        )
                    )

                    contexto_obra_id_original = str(
                        (contexto_unidade or {}).get(
                            "obra_id"
                        )
                        or ""
                    )

                    status_atual = (
                        normalizar_status_operacional(
                            conv.get("status")
                        )
                    )
                    idx_status = (
                        OPCOES_STATUS_PRESENCA.index(
                            status_atual
                        )
                        if status_atual
                        in OPCOES_STATUS_PRESENCA
                        else 0
                    )

                    turno_conv = turno_da_convocacao(
                        conv
                    )
                    _, obs_livre = (
                        decompor_observacao_operacional(
                            conv.get("observacao")
                            or ""
                        )
                    )

                    meta_atual = (
                        obter_metadata_operacional(
                            conv.get("observacao")
                            or ""
                        )
                    )

                    periodo_principal_meta = str(
                        meta_atual.get(
                            "periodo_servico_principal"
                        )
                        or turno_conv
                        or "Integral"
                    )

                    periodo_principal_atual = str(
                        (
                            contexto_unidade
                            or {}
                        ).get("periodo")
                        or periodo_principal_meta
                    )

                    if (
                        periodo_principal_atual
                        not in periodos_servico
                    ):
                        periodo_principal_atual = "Outro"

                    todos_adicionais_atuais = list(
                        _normalizar_servicos_adicionais(
                            meta_atual
                        )
                    )

                    adicionais_unidade_atual = []
                    adicionais_outras_unidades = []

                    for _adic in todos_adicionais_atuais:
                        _adic_unidade = str(
                            _adic.get("unidade")
                            or ""
                        ).strip()

                        if not _adic_unidade:
                            _adic_obra_id = str(
                                _adic.get("obra_id")
                                or ""
                            )
                            _adic_obra = (
                                dict_obras.get(
                                    _adic_obra_id,
                                    {},
                                )
                                if _adic_obra_id
                                else {}
                            )
                            _adic_unidade = str(
                                _adic_obra.get("unidade")
                                or ""
                            ).strip()

                        if normalizar(_adic_unidade) == normalizar(unidade):
                            adicionais_unidade_atual.append(
                                _adic
                            )
                        else:
                            adicionais_outras_unidades.append(
                                _adic
                            )

                    # Quando esta unidade representa um serviço adicional,
                    # o próprio serviço de contexto não deve aparecer como
                    # "2º serviço" dele mesmo.
                    if not contexto_eh_principal:
                        adicionais_unidade_atual = [
                            _adic
                            for _adic in adicionais_unidade_atual
                            if not (
                                contexto_obra_id_original
                                and str(
                                    _adic.get("obra_id")
                                    or ""
                                )
                                == contexto_obra_id_original
                            )
                        ]

                    mesma_pessoa = convs_por_colaborador.get(
                        str(
                            conv.get("colaborador_id")
                            or ""
                        ),
                        [],
                    )
                    outras_convs = [
                        outra
                        for outra in mesma_pessoa
                        if str(outra.get("id"))
                        != str(c_id)
                    ]
                    tem_conv_separada = bool(
                        outras_convs
                    )

                    with st.container(
                        border=True,
                        key=f"engm_point_card_{c_id}",
                    ):
                        st.markdown(
                            f"""
                            <div class="engm-person-head">
                                <div>
                                    <div class="engm-person-name">
                                        {_html.escape(str(colab.get('nome') or '-'))}
                                    </div>
                                    <div class="engm-person-meta">
                                        {_html.escape(str(colab.get('funcao') or '-'))}
                                        · {_html.escape(unidade)}
                                    </div>
                                </div>
                                <div class="engm-chip">
                                    {_html.escape(turno_conv)}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        c_status, c_periodo = st.columns(
                            [1.12, .88]
                        )

                        with c_status:
                            status_sel = st.selectbox(
                                "Status",
                                OPCOES_STATUS_PRESENCA,
                                index=idx_status,
                                key=f"engm_st_{c_id}",
                            )

                        with c_periodo:
                            periodo_principal = st.selectbox(
                                "Período",
                                periodos_servico,
                                index=periodos_servico.index(
                                    periodo_principal_atual
                                ),
                                key=f"engm_periodo_{c_id}",
                            )

                        obra_sel = st.selectbox(
                            "Obra / Serviço",
                            opcoes_obras,
                            index=idx_obra,
                            key=f"engm_obra_{c_id}",
                        )

                        servicos_adicionais_editados = []

                        # Pagamento compacto:
                        # diária, extra e acordos ficam separados.
                        tipo_key = f"engm_tipo_diaria_{c_id}"
                        diaria_key = f"engm_custo_pago_{c_id}"
                        extra_key = f"engm_valor_extra_{c_id}"
                        adicional_noturno_key = (
                            f"engm_adicional_noturno_{c_id}"
                        )

                        tipo_atual_pag = tipo_diaria_registro(
                            conv
                        )
                        diaria_atual_pag = (
                            valor_diaria_financeiro_registro(
                                conv,
                                colab,
                            )
                        )
                        extra_atual_pag = (
                            valor_extra_registro(
                                conv
                            )
                        )
                        adicional_noturno_atual = (
                            valor_adicional_noturno_registro(
                                conv
                            )
                        )
                        eh_sebrae_card = eh_unidade_sebrae(
                            unidade
                        )

                        if eh_sebrae_card:
                            st.session_state[
                                tipo_key
                            ] = "Diária"
                        elif tipo_key not in st.session_state:
                            st.session_state[
                                tipo_key
                            ] = tipo_atual_pag

                        if diaria_key not in st.session_state:
                            st.session_state[
                                diaria_key
                            ] = (
                                diaria_atual_pag
                                if diaria_atual_pag > 0
                                else valor_financeiro_padrao_colaborador(
                                    colab,
                                    (
                                        "Diária"
                                        if eh_sebrae_card
                                        else tipo_atual_pag
                                    ),
                                )
                            )

                        if extra_key not in st.session_state:
                            st.session_state[
                                extra_key
                            ] = extra_atual_pag

                        def _ajustar_diaria_mobile(
                            _tipo_key=tipo_key,
                            _diaria_key=diaria_key,
                            _colab=colab,
                        ):
                            st.session_state[
                                _diaria_key
                            ] = (
                                valor_financeiro_padrao_colaborador(
                                    _colab,
                                    st.session_state.get(
                                        _tipo_key,
                                        "Diária",
                                    ),
                                )
                            )

                        pg1, pg2 = st.columns(
                            [1, 1.12]
                        )

                        with pg1:
                            tipo_diaria_sel = st.selectbox(
                                "Diária / Meia",
                                TIPOS_DIARIA,
                                key=tipo_key,
                                on_change=_ajustar_diaria_mobile,
                                disabled=eh_sebrae_card,
                            )

                        with pg2:
                            valor_diaria_financeiro = (
                                st.number_input(
                                    "Diária (R$)",
                                    min_value=0.0,
                                    step=10.0,
                                    disabled=(
                                        not status_eh_presenca(
                                            status_sel
                                        )
                                    ),
                                    key=diaria_key,
                                )
                            )

                        pg3, pg4 = st.columns(2)

                        with pg3:
                            valor_extra = st.number_input(
                                "Extra (R$)",
                                min_value=0.0,
                                step=10.0,
                                disabled=(
                                    not status_eh_presenca(
                                        status_sel
                                    )
                                ),
                                key=extra_key,
                            )

                        if eh_sebrae_card:
                            if (
                                adicional_noturno_key
                                not in st.session_state
                            ):
                                st.session_state[
                                    adicional_noturno_key
                                ] = (
                                    adicional_noturno_atual
                                    if adicional_noturno_atual > 0
                                    else VALOR_ADICIONAL_NOTURNO_SEBRAE
                                )

                            with pg4:
                                valor_adicional_noturno = (
                                    st.number_input(
                                        "Adic. noturno (R$)",
                                        min_value=0.0,
                                        step=10.0,
                                        disabled=(
                                            not status_eh_presenca(
                                                status_sel
                                            )
                                        ),
                                        key=(
                                            adicional_noturno_key
                                        ),
                                    )
                                )

                            valor_acordo = st.number_input(
                                "Acordos / Bonificações (R$)",
                                min_value=0.0,
                                value=(
                                    float(
                                        conv.get(
                                            "valor_acordo"
                                        )
                                        or 0.0
                                    )
                                    if status_eh_presenca(
                                        status_sel
                                    )
                                    else 0.0
                                ),
                                step=10.0,
                                disabled=(
                                    not status_eh_presenca(
                                        status_sel
                                    )
                                ),
                                key=(
                                    f"engm_acordo_{c_id}"
                                ),
                            )

                        else:
                            valor_adicional_noturno = 0.0
                            st.session_state.pop(
                                adicional_noturno_key,
                                None,
                            )

                            with pg4:
                                valor_acordo = st.number_input(
                                    "Acordos / Bonificações (R$)",
                                    min_value=0.0,
                                    value=(
                                        float(
                                            conv.get(
                                                "valor_acordo"
                                            )
                                            or 0.0
                                        )
                                        if status_eh_presenca(
                                            status_sel
                                        )
                                        else 0.0
                                    ),
                                    step=10.0,
                                    disabled=(
                                        not status_eh_presenca(
                                            status_sel
                                        )
                                    ),
                                    key=(
                                        f"engm_acordo_{c_id}"
                                    ),
                                )

                        categoria_pag = (
                            categoria_diaria_colaborador(
                                colab
                            )
                        )

                        total_fin_prev = (
                            float(
                                valor_diaria_financeiro
                            )
                            + float(valor_extra)
                            + float(
                                valor_adicional_noturno
                            )
                            + float(valor_acordo)
                            if status_eh_presenca(
                                status_sel
                            )
                            else 0.0
                        )

                        resumo_pag = (
                            f"{categoria_pag} · "
                            f"Diária {formatar_reais(valor_diaria_financeiro)} · "
                            f"Extra {formatar_reais(valor_extra)}"
                        )

                        if eh_sebrae_card:
                            resumo_pag += (
                                f" · Noturno "
                                f"{formatar_reais(valor_adicional_noturno)}"
                            )

                        resumo_pag += (
                            f" · Acordos/Bonificações "
                            f"{formatar_reais(valor_acordo)} "
                            f"· Total {formatar_reais(total_fin_prev)}"
                        )

                        st.markdown(
                            (
                                '<div class="engm-pay-summary">'
                                f'{_html.escape(resumo_pag)}'
                                '</div>'
                            ),
                            unsafe_allow_html=True,
                        )

                        if eh_sebrae_card:
                            st.caption(
                                "🌙 SEBRAE: 17h–02h = diária integral. "
                                "Adicional noturno padrão R$ 90,00."
                            )

                        with st.expander(
                            "Mais opções",
                            expanded=False,
                        ):
                            obs_nova = st.text_input(
                                "Observação / justificativa",
                                value=obs_livre,
                                key=f"engm_obs_{c_id}",
                            )

                            if (
                                not tem_conv_separada
                                and contexto_eh_principal
                            ):
                                qtd_adic_key = (
                                    f"_engm_qtd_adic_{c_id}"
                                )

                                if (
                                    qtd_adic_key
                                    not in st.session_state
                                ):
                                    st.session_state[
                                        qtd_adic_key
                                    ] = len(
                                        adicionais_unidade_atual
                                    )

                                qtd_adic = max(
                                    0,
                                    int(
                                        st.session_state.get(
                                            qtd_adic_key,
                                            0,
                                        )
                                    ),
                                )

                                ca1, ca2, ca3 = st.columns(
                                    [1.25, 1.25, 1.5],
                                    vertical_alignment="center",
                                )

                                with ca1:
                                    if st.button(
                                        "+ Adicionar serviço",
                                        key=(
                                            f"engm_add_serv_{c_id}"
                                        ),
                                        use_container_width=True,
                                    ):
                                        st.session_state[
                                            qtd_adic_key
                                        ] = qtd_adic + 1
                                        st.rerun()

                                with ca2:
                                    if st.button(
                                        "− Remover último",
                                        key=(
                                            f"engm_rem_serv_{c_id}"
                                        ),
                                        use_container_width=True,
                                        disabled=(
                                            qtd_adic <= 0
                                        ),
                                    ):
                                        idx_rem = qtd_adic
                                        st.session_state.pop(
                                            (
                                                f"engm_adic_obra_"
                                                f"{c_id}_{idx_rem}"
                                            ),
                                            None,
                                        )
                                        st.session_state.pop(
                                            (
                                                f"engm_adic_periodo_"
                                                f"{c_id}_{idx_rem}"
                                            ),
                                            None,
                                        )

                                        st.session_state[
                                            qtd_adic_key
                                        ] = max(
                                            0,
                                            qtd_adic - 1,
                                        )
                                        st.rerun()

                                with ca3:
                                    st.caption(
                                        (
                                            f"{qtd_adic} serviço(s) "
                                            "adicional(is)"
                                        )
                                    )

                                opcoes_adic = (
                                    ["— Selecione —"]
                                    + list(
                                        mapa_obras.keys()
                                    )
                                )

                                for idx_adic in range(
                                    1,
                                    qtd_adic + 1,
                                ):
                                    existente_adic = (
                                        adicionais_unidade_atual[
                                            idx_adic - 1
                                        ]
                                        if (
                                            idx_adic - 1
                                            < len(
                                                adicionais_unidade_atual
                                            )
                                        )
                                        else {}
                                    )

                                    servico_atual_adic = str(
                                        existente_adic.get(
                                            "servico"
                                        )
                                        or ""
                                    )

                                    periodo_atual_adic = str(
                                        existente_adic.get(
                                            "periodo"
                                        )
                                        or "Tarde"
                                    )

                                    if (
                                        periodo_atual_adic
                                        not in periodos_servico
                                    ):
                                        periodo_atual_adic = (
                                            "Outro"
                                        )

                                    key_obra_adic = (
                                        f"engm_adic_obra_"
                                        f"{c_id}_{idx_adic}"
                                    )

                                    key_periodo_adic = (
                                        f"engm_adic_periodo_"
                                        f"{c_id}_{idx_adic}"
                                    )

                                    if (
                                        key_obra_adic
                                        not in st.session_state
                                        and servico_atual_adic
                                        in opcoes_adic
                                    ):
                                        st.session_state[
                                            key_obra_adic
                                        ] = (
                                            servico_atual_adic
                                        )

                                    if (
                                        key_periodo_adic
                                        not in st.session_state
                                    ):
                                        st.session_state[
                                            key_periodo_adic
                                        ] = (
                                            periodo_atual_adic
                                        )

                                    st.markdown(
                                        (
                                            '<div class="engm-service-title">'
                                            f'Serviço adicional {idx_adic}'
                                            '</div>'
                                        ),
                                        unsafe_allow_html=True,
                                    )

                                    ad_c1, ad_c2 = st.columns(
                                        [1.55, .65]
                                    )

                                    with ad_c1:
                                        obra_adic_sel = (
                                            st.selectbox(
                                                "Obra / Serviço",
                                                opcoes_adic,
                                                key=(
                                                    key_obra_adic
                                                ),
                                                label_visibility=(
                                                    "collapsed"
                                                ),
                                            )
                                        )

                                    with ad_c2:
                                        periodo_adic_sel = (
                                            st.selectbox(
                                                "Período",
                                                periodos_servico,
                                                key=(
                                                    key_periodo_adic
                                                ),
                                                label_visibility=(
                                                    "collapsed"
                                                ),
                                            )
                                        )

                                    servicos_adicionais_editados.append({
                                        "servico": obra_adic_sel,
                                        "periodo": periodo_adic_sel,
                                    })

                            else:
                                if not contexto_eh_principal:
                                    st.caption(
                                        "Este card representa um serviço adicional "
                                        "de outra unidade e está vinculado ao mesmo apontamento."
                                    )
                                else:
                                    st.caption(
                                        "Já existe outra convocação desta pessoa "
                                        "no mesmo dia. Cada turno é apontado separadamente."
                                    )

                    dados_form[str(c_id)] = {
                        "conv": conv,
                        "colab": colab,
                        "mapa_obras": mapa_obras,
                        "obra_sel": obra_sel,
                        "status_sel": status_sel,
                        "periodo_principal": periodo_principal,
                        "servicos_adicionais_editados": servicos_adicionais_editados,
                        "tem_conv_separada": tem_conv_separada,
                        "tipo_diaria_sel": tipo_diaria_sel,
                        "valor_diaria_financeiro": valor_diaria_financeiro,
                        "valor_extra": valor_extra,
                        "valor_adicional_noturno": valor_adicional_noturno,
                        "valor_acordo": valor_acordo,
                        "obs_nova": obs_nova,
                        "turno_conv": turno_conv,
                        "contexto_eh_principal": contexto_eh_principal,
                        "contexto_obra_id_original": contexto_obra_id_original,
                        "periodo_principal_meta": periodo_principal_meta,
                        "adicionais_outras_unidades": adicionais_outras_unidades,
                        "adicionais_unidade_atual": adicionais_unidade_atual,
                        "unidade_contexto": unidade,
                    }

                salvar_todos = st.button(
                    "Salvar equipe",
                    type="primary",
                    use_container_width=True,
                    key="engm_salvar_equipe_v630",
                )

            if salvar_todos:
                erros_validacao = []

                for item in dados_form.values():
                    nome_pessoa = str(
                        item["colab"].get("nome")
                        or "Colaborador"
                    )

                    if (
                        item["obra_sel"]
                        not in item["mapa_obras"]
                    ):
                        erros_validacao.append(
                            f"{nome_pessoa}: selecione a obra/serviço."
                        )

                    obras_usadas = {
                        str(item["obra_sel"])
                    }

                    for idx_adic, adic in enumerate(
                        item[
                            "servicos_adicionais_editados"
                        ],
                        start=1,
                    ):
                        servico_adic = str(
                            adic.get("servico")
                            or ""
                        )

                        if (
                            servico_adic
                            not in item["mapa_obras"]
                        ):
                            erros_validacao.append(
                                (
                                    f"{nome_pessoa}: selecione a obra do "
                                    f"serviço adicional {idx_adic}."
                                )
                            )
                            continue

                        if servico_adic in obras_usadas:
                            erros_validacao.append(
                                (
                                    f"{nome_pessoa}: o serviço "
                                    f"'{servico_adic}' está repetido."
                                )
                            )
                            continue

                        obras_usadas.add(
                            servico_adic
                        )

                if erros_validacao:
                    for msg in erros_validacao:
                        st.warning(msg)

                else:
                    itens_salvar = []

                    for item in dados_form.values():
                        conv = item["conv"]
                        nome_pessoa = str(
                            item["colab"].get("nome")
                            or "Colaborador"
                        )

                        # Começa preservando todos os serviços adicionais
                        # que pertencem a outras unidades.
                        adicionais = [
                            dict(x)
                            for x in item[
                                "adicionais_outras_unidades"
                            ]
                        ]

                        if item["contexto_eh_principal"]:
                            # A lista da tela representa TODOS os serviços
                            # adicionais desta unidade. Assim é possível adicionar
                            # 2, 3, 4... serviços e salvar tudo junto.
                            adicionais_mesma_unidade = []

                            if not item["tem_conv_separada"]:
                                for adic_edit in item[
                                    "servicos_adicionais_editados"
                                ]:
                                    nome_adic = str(
                                        adic_edit.get(
                                            "servico"
                                        )
                                        or ""
                                    )

                                    if (
                                        nome_adic
                                        not in item[
                                            "mapa_obras"
                                        ]
                                    ):
                                        continue

                                    _obra_adic_id = item[
                                        "mapa_obras"
                                    ][nome_adic]

                                    _obra_adic = dict_obras.get(
                                        _obra_adic_id,
                                        {},
                                    )

                                    adicionais_mesma_unidade.append({
                                        "servico": nome_adic,
                                        "periodo": str(
                                            adic_edit.get(
                                                "periodo"
                                            )
                                            or "Outro"
                                        ),
                                        "obra_id": str(
                                            _obra_adic_id
                                            or ""
                                        ),
                                        "unidade": str(
                                            _obra_adic.get(
                                                "unidade"
                                            )
                                            or item[
                                                "unidade_contexto"
                                            ]
                                            or ""
                                        ),
                                    })

                            adicionais.extend(
                                adicionais_mesma_unidade
                            )

                            obra_id_final = item[
                                "mapa_obras"
                            ][item["obra_sel"]]

                            periodo_meta_final = item[
                                "periodo_principal"
                            ]

                        else:
                            # O card atual representa um serviço adicional
                            # de outra unidade. O principal permanece intacto.
                            obra_id_final = conv.get(
                                "obra_id"
                            )

                            periodo_meta_final = item[
                                "periodo_principal_meta"
                            ]

                            # Preserva adicionais da mesma unidade, exceto o
                            # serviço atual, que será substituído pelo seletor.
                            adicionais.extend(
                                [
                                    dict(x)
                                    for x in item[
                                        "adicionais_unidade_atual"
                                    ]
                                ]
                            )

                            _obra_contexto_nova_id = item[
                                "mapa_obras"
                            ][item["obra_sel"]]
                            _obra_contexto_nova = dict_obras.get(
                                _obra_contexto_nova_id,
                                {},
                            )

                            adicionais.append({
                                "servico": item["obra_sel"],
                                "periodo": item[
                                    "periodo_principal"
                                ],
                                "obra_id": str(
                                    _obra_contexto_nova_id
                                    or ""
                                ),
                                "unidade": str(
                                    _obra_contexto_nova.get(
                                        "unidade"
                                    )
                                    or item[
                                        "unidade_contexto"
                                    ]
                                    or ""
                                ),
                            })

                        meta = registrar_metadata_apontamento(
                            conv,
                            data_apont,
                            apontado_por=engenheiro_campo,
                            periodo_principal=periodo_meta_final,
                            servicos_adicionais=adicionais,
                            unidade_servico=item["unidade_contexto"],
                        )

                        nova_obs = montar_observacao_operacional(
                            item["turno_conv"],
                            item["obs_nova"],
                            meta,
                        )

                        presente_final = status_eh_presenca(item["status_sel"])
                        tipo_diaria_final = (
                            "Diária"
                            if eh_unidade_sebrae(item["unidade_contexto"])
                            else normalizar_tipo_diaria(item["tipo_diaria_sel"])
                        )
                        custo_pago_final = (
                            float(
                                item[
                                    "valor_diaria_financeiro"
                                ]
                            )
                            if presente_final
                            else 0.0
                        )
                        valor_extra_final = (
                            float(
                                item[
                                    "valor_extra"
                                ]
                            )
                            if presente_final
                            else 0.0
                        )
                        valor_adicional_noturno_final = (
                            float(item["valor_adicional_noturno"])
                            if (
                                presente_final
                                and eh_unidade_sebrae(
                                    item["unidade_contexto"]
                                )
                            )
                            else 0.0
                        )
                        valor_acordo_final = float(item["valor_acordo"]) if presente_final else 0.0
                        custo_encargos_final = (
                            valor_controladoria_padrao_colaborador(
                                item["colab"],
                                tipo_diaria_final,
                            )
                            if presente_final
                            else 0.0
                        )

                        itens_salvar.append({
                            "conv": conv,
                            "nome_pessoa": nome_pessoa,
                            "status": item[
                                "status_sel"
                            ],
                            "tipo_diaria_final": tipo_diaria_final,
                            "custo_pago_final": custo_pago_final,
                            "valor_extra_final": valor_extra_final,
                            "valor_adicional_noturno_final": valor_adicional_noturno_final,
                            "valor_acordo_final": valor_acordo_final,
                            "custo_encargos_final": custo_encargos_final,
                            "obs_livre": item[
                                "obs_nova"
                            ],
                            "nova_obs": nova_obs,
                            "obra_id_final": obra_id_final,
                            "periodo_principal": periodo_meta_final,
                            "adicionais": adicionais,
                        })

                    with st.spinner(
                        "Salvando apontamento..."
                    ):
                        salvos, falhas = (
                            _salvar_apontamentos_lote_mobile(
                                itens_salvar,
                                data_apont,
                                engenheiro_campo,
                            )
                        )

                    for msg in falhas:
                        st.error(msg)

                    if salvos and not falhas:
                        st.session_state[
                            "_engm_success_message"
                        ] = (
                            f"✓ Apontamento salvo com sucesso · "
                            f"{salvos} registro(s)."
                        )
                        st.rerun()

                    elif salvos:
                        st.caption(
                            f"✓ {salvos} apontamento(s) foram salvos, "
                            "mas houve pendências abaixo."
                        )

    # =====================================================================
    # AMANHÃ — CONVOCADOS + NOVA CONVOCAÇÃO NA MESMA TELA
    # =====================================================================
    elif area_campo == "Amanhã":
        engenheiro_campo = st.selectbox(
            "Engenheiro",
            ENGENHEIROS,
            key="engenheiro_campo_mobile",
        )

        data_conv_auto = amanha_campo

        # Se a convocação anterior foi salva, limpa somente os campos de pessoas
        # ANTES de recriar os widgets. Isso evita conflito com o Session State.
        if st.session_state.pop("_engm_reset_convocacao", False):
            for _chave in (
                "engm_conv_pessoas",
                "engm_manual_nome",
                "engm_manual_funcao",
                "engm_manual_avulso",
            ):
                st.session_state.pop(_chave, None)

            st.session_state[
                "_engm_avulsos_convocacao"
            ] = []

        if st.session_state.pop(
            "_engm_limpar_manual_campos",
            False,
        ):
            for _campo_manual in (
                "engm_manual_nome",
                "engm_manual_funcao",
            ):
                st.session_state.pop(
                    _campo_manual,
                    None,
                )

        # Avisos de conflito/bloqueio sobrevivem ao rerun.
        # O sucesso é mostrado como toast pequeno antes da atualização.
        _feedback_conv = st.session_state.pop("_engm_conv_feedback", None)
        if _feedback_conv:
            _avisos_fb = list(
                _feedback_conv.get("avisos")
                or []
            )
            for _aviso_fb in _avisos_fb:
                st.warning(_aviso_fb)

        ja_convocados = _enriquecer_convocacoes_campo(
            _buscar_convocacoes_campo(
                engenheiro_campo,
                data_conv_auto,
            )
        )

        st.markdown(
            f"""
            <div class="engm-summary">
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Data</div>
                    <div class="engm-summary-value" style="font-size:17px">
                        {data_conv_auto.strftime('%d/%m')}
                    </div>
                    <div class="engm-summary-note">próximo dia útil</div>
                </div>
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Convocados</div>
                    <div class="engm-summary-value">{len(ja_convocados)}</div>
                    <div class="engm-summary-note">por você</div>
                </div>
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Ação</div>
                    <div class="engm-summary-value" style="font-size:17px">
                        Montar
                    </div>
                    <div class="engm-summary-note">e confirmar abaixo</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if ja_convocados:
            with st.expander(
                f"Já convocados · {len(ja_convocados)}",
                expanded=False,
            ):
                _lista_convocados_mobile(
                    ja_convocados,
                    mostrar_status=False,
                )

        st.markdown(
            '<div class="engm-section-title">Adicionar à equipe</div>'
            '<div class="engm-section-sub">'
            'Escolha unidade, turno e pessoas. Ao confirmar, a equipe é salva de uma vez.'
            '</div>',
            unsafe_allow_html=True,
        )

        if not obras:
            st.info(
                "Nenhuma obra/unidade cadastrada."
            )
        else:
            unidades_reais = sorted(
                {
                    str(o.get("unidade"))
                    for o in obras
                    if o.get("unidade")
                }
            )

            unidades_opcoes = []
            for u in UNIDADES_APROAR + unidades_reais:
                if u and u not in unidades_opcoes:
                    unidades_opcoes.append(u)

            unidade_selecionada = st.selectbox(
                "Unidade",
                unidades_opcoes,
                key="engm_conv_unidade",
            )

            turno_conv_campo = st.selectbox(
                "Turno",
                [
                    "Integral",
                    "Manhã",
                    "Tarde",
                    "Noite",
                ],
                key="engm_conv_turno",
            )

            funcoes_disponiveis = sorted(
                {
                    str(c.get("funcao"))
                    for c in colaboradores
                    if c.get("funcao")
                }
            )

            filtro_funcao = st.selectbox(
                "Função",
                ["Todas"] + funcoes_disponiveis,
                key="engm_conv_funcao",
            )

            colabs_filtrados = [
                c
                for c in colaboradores
                if filtro_funcao == "Todas"
                or str(c.get("funcao"))
                == filtro_funcao
            ]

            try:
                convs_data_todos = (
                    _buscar_convocacoes_intervalo(
                        data_conv_auto,
                        data_conv_auto,
                        None,
                    )
                    or []
                )
            except Exception:
                convs_data_todos = []

            convs_por_colab = {}
            for conv_exist in convs_data_todos:
                convs_por_colab.setdefault(
                    str(
                        conv_exist.get(
                            "colaborador_id"
                        )
                    ),
                    [],
                ).append(conv_exist)

            indisponibilidades_amanha = (
                _carregar_indisponibilidades_disponibilidade()
                or []
            )

            indisp_por_colab = {}
            for item in indisponibilidades_amanha:
                cid_ind = str(
                    item.get("colaborador_id")
                    or ""
                )

                try:
                    ini_ind = datetime.date.fromisoformat(
                        str(item.get("inicio"))
                    )
                    fim_ind = datetime.date.fromisoformat(
                        str(item.get("fim"))
                    )
                except Exception:
                    continue

                if (
                    ini_ind
                    <= data_conv_auto
                    <= fim_ind
                ):
                    indisp_por_colab[cid_ind] = item

            mapa_colab_opcoes = {}

            for c in colabs_filtrados:
                cid = c.get("id")
                nome = str(c.get("nome") or "-")
                funcao = str(c.get("funcao") or "-")
                alocacoes = convs_por_colab.get(
                    str(cid),
                    [],
                )

                sufixos = []

                if str(cid) in indisp_por_colab:
                    motivo = str(
                        indisp_por_colab[
                            str(cid)
                        ].get("motivo")
                        or "Indisponível"
                    )
                    sufixos.append(
                        f"INDISPONÍVEL: {motivo}"
                    )

                for aloc in alocacoes:
                    t_exist = turno_da_convocacao(
                        aloc
                    )
                    eng_exist = str(
                        aloc.get("engenheiro")
                        or "N/A"
                    )
                    obra_exist = dict_obras.get(
                        aloc.get("obra_id"),
                        {},
                    )
                    unid_exist = str(
                        obra_exist.get("unidade")
                        or "-"
                    )

                    if turnos_se_sobrepoem(
                        t_exist,
                        turno_conv_campo,
                    ):
                        sufixos.append(
                            f"OCUPADO {t_exist} · {eng_exist}"
                        )
                    else:
                        sufixos.append(
                            f"já {t_exist} · {eng_exist}"
                        )

                status_aloc = (
                    " — " + " | ".join(sufixos)
                    if sufixos
                    else ""
                )

                label = (
                    f"{nome} ({funcao}){status_aloc}"
                )

                mapa_colab_opcoes[label] = cid

            equipe_selecionada = st.multiselect(
                "Colaboradores",
                list(mapa_colab_opcoes.keys()),
                placeholder="Digite um nome para buscar...",
                key="engm_conv_pessoas",
            )

            if "_engm_avulsos_convocacao" not in st.session_state:
                st.session_state["_engm_avulsos_convocacao"] = []

            fila_avulsos = st.session_state[
                "_engm_avulsos_convocacao"
            ]

            nome_manual = ""
            tipo_manual = "Profissional"
            funcao_manual = ""
            avulso_manual = True

            with st.expander(
                (
                    "Adicionar pessoas que não estão na lista"
                    + (
                        f" · {len(fila_avulsos)} adicionada(s)"
                        if fila_avulsos
                        else ""
                    )
                ),
                expanded=False,
            ):
                st.caption(
                    "Adicione quantos avulsos precisar e confirme toda a equipe de uma vez."
                )

                nome_manual = st.text_input(
                    "Nome",
                    key="engm_manual_nome",
                    placeholder="Nome completo",
                )

                avulso_manual = st.checkbox(
                    "É avulso?",
                    value=True,
                    key="engm_manual_avulso",
                )

                c_manual_1, c_manual_2 = st.columns(2)

                with c_manual_1:
                    tipo_manual = st.selectbox(
                        "Categoria da diária",
                        [
                            "Profissional",
                            "Ajudante",
                        ],
                        key="engm_manual_tipo",
                    )

                with c_manual_2:
                    funcao_manual = st.text_input(
                        "Função (opcional)",
                        key="engm_manual_funcao",
                    )

                if st.button(
                    "Adicionar à convocação",
                    use_container_width=True,
                    key="engm_add_manual_fila",
                ):
                    nome_limpo = " ".join(
                        nome_manual.strip().split()
                    )

                    if not nome_limpo:
                        st.warning(
                            "Digite o nome da pessoa."
                        )
                    else:
                        ja_na_fila = any(
                            normalizar(
                                item.get("nome")
                                or ""
                            )
                            == normalizar(nome_limpo)
                            for item in fila_avulsos
                        )

                        if ja_na_fila:
                            st.warning(
                                "Essa pessoa já foi adicionada à convocação."
                            )
                        else:
                            fila_avulsos.append({
                                "nome": nome_limpo,
                                "tipo": tipo_manual,
                                "funcao": funcao_manual.strip(),
                                "avulso": bool(
                                    avulso_manual
                                ),
                            })

                            st.session_state[
                                "_engm_avulsos_convocacao"
                            ] = fila_avulsos

                            # Limpa os campos no próximo rerun.
                            st.session_state[
                                "_engm_limpar_manual_campos"
                            ] = True
                            st.rerun()

                if fila_avulsos:
                    st.markdown("**Adicionados à convocação**")

                    for idx, pessoa_fila in enumerate(
                        list(fila_avulsos)
                    ):
                        c_nome, c_remover = st.columns(
                            [3.9, 1.35]
                        )

                        with c_nome:
                            sufixo_avulso = (
                                " · Avulso"
                                if pessoa_fila.get(
                                    "avulso"
                                )
                                else ""
                            )
                            st.caption(
                                f"{pessoa_fila.get('nome')} · "
                                f"{pessoa_fila.get('tipo')}"
                                f"{sufixo_avulso}"
                            )

                        with c_remover:
                            if st.button(
                                "Remover",
                                type="secondary",
                                use_container_width=True,
                                key=(
                                    "engm_remover_manual_"
                                    f"{idx}"
                                ),
                                help="Remover da convocação",
                            ):
                                fila_avulsos.pop(idx)
                                st.session_state[
                                    "_engm_avulsos_convocacao"
                                ] = fila_avulsos
                                st.rerun()

            if st.button(
                "Confirmar convocação",
                type="primary",
                use_container_width=True,
                key="engm_confirm_conv",
            ):
                if (
                    not equipe_selecionada
                    and not fila_avulsos
                    and not nome_manual.strip()
                ):
                    st.warning("Selecione pelo menos uma pessoa.")
                else:
                    with st.spinner("Salvando convocação..."):
                        try:
                            obra_id_placeholder = obter_obra_placeholder_unidade(
                                unidade_selecionada
                            )

                            if not obra_id_placeholder:
                                detalhe_placeholder = str(
                                    st.session_state.get(
                                        "erro_placeholder_unidade",
                                        ""
                                    )
                                    or ""
                                )
                                st.error(
                                    "Não foi possível preparar a unidade para a convocação."
                                    + (
                                        f" Detalhe: {detalhe_placeholder}"
                                        if detalhe_placeholder
                                        else ""
                                    )
                                )
                            else:
                                pessoas = []
                                avisos = []

                                for label_colab in equipe_selecionada:
                                    c_id = mapa_colab_opcoes.get(label_colab)
                                    if not c_id:
                                        avisos.append(
                                            f"{label_colab}: colaborador não localizado. "
                                            "Atualize a página e tente novamente."
                                        )
                                        continue

                                    nome_existente = str(
                                        dict_colaboradores.get(
                                            c_id,
                                            {},
                                        ).get("nome")
                                        or label_colab.split(" (")[0]
                                    )
                                    pessoas.append((c_id, nome_existente))

                                manuais_processar = [
                                    dict(item)
                                    for item in fila_avulsos
                                ]

                                # Se o usuário digitou um último nome e clicou
                                # direto em "Confirmar convocação", ele também
                                # entra sem obrigar o clique "Adicionar".
                                if nome_manual.strip():
                                    nome_digitado = " ".join(
                                        nome_manual.strip().split()
                                    )

                                    if not any(
                                        normalizar(
                                            item.get("nome")
                                            or ""
                                        )
                                        == normalizar(
                                            nome_digitado
                                        )
                                        for item in manuais_processar
                                    ):
                                        manuais_processar.append({
                                            "nome": nome_digitado,
                                            "tipo": tipo_manual,
                                            "funcao": funcao_manual.strip(),
                                            "avulso": bool(
                                                avulso_manual
                                            ),
                                        })

                                for pessoa_manual in manuais_processar:
                                    nome_pessoa_manual = str(
                                        pessoa_manual.get("nome")
                                        or ""
                                    ).strip()

                                    if not nome_pessoa_manual:
                                        continue

                                    (
                                        c_id_manual,
                                        colab_manual,
                                        msg_manual,
                                    ) = criar_ou_obter_colaborador_manual(
                                        nome_pessoa_manual,
                                        pessoa_manual.get("tipo")
                                        or "Profissional",
                                        pessoa_manual.get("funcao")
                                        or "",
                                        avulso=bool(
                                            pessoa_manual.get("avulso")
                                        ),
                                    )

                                    if c_id_manual:
                                        pessoas.append(
                                            (
                                                c_id_manual,
                                                str(
                                                    (
                                                        colab_manual
                                                        or {}
                                                    ).get("nome")
                                                    or nome_pessoa_manual
                                                ),
                                            )
                                        )
                                    else:
                                        avisos.append(
                                            msg_manual
                                            or (
                                                f"{nome_pessoa_manual}: "
                                                "não foi possível cadastrar."
                                            )
                                        )

                                pessoas_unicas = []
                                ids_vistos = set()

                                for cid, nome_pessoa in pessoas:
                                    cid_ref = str(cid)
                                    if cid and cid_ref not in ids_vistos:
                                        pessoas_unicas.append((cid, nome_pessoa))
                                        ids_vistos.add(cid_ref)

                                sucessos, avisos_lote = (
                                    inserir_convocacoes_lote_mobile(
                                        obra_id_placeholder,
                                        pessoas_unicas,
                                        data_conv_auto,
                                        engenheiro_campo,
                                        turno_conv_campo,
                                        existentes_data=convs_data_todos,
                                        indisponiveis_map=indisp_por_colab,
                                    )
                                )
                                avisos.extend(avisos_lote)

                                # O resultado fica salvo na sessão para continuar
                                # aparecendo depois do rerun que atualiza "Já convocados".
                                if sucessos:
                                    limpar_cache_convocacoes()

                                    # Só os avisos precisam sobreviver ao rerun.
                                    if avisos:
                                        st.session_state["_engm_conv_feedback"] = {
                                            "avisos": avisos,
                                        }

                                    st.session_state["_engm_reset_convocacao"] = True
                                    st.session_state[
                                        "_engm_avulsos_convocacao"
                                    ] = []
                                    st.session_state[
                                        "_engm_success_message"
                                    ] = (
                                        f"✓ Convocação salva com sucesso · "
                                        f"{sucessos} pessoa(s)."
                                    )
                                    st.rerun()
                                else:
                                    if avisos:
                                        for aviso in avisos:
                                            st.warning(aviso)
                                    else:
                                        st.error(
                                            "A convocação não foi salva. "
                                            "Nenhum colaborador válido foi encontrado."
                                        )

                        except Exception as e:
                            exibir_erro_amigavel(
                                "engenheiro",
                                "confirmar_convocacao_mobile",
                                e,
                                "Não foi possível concluir a convocação. Tente novamente.",
                            )

    # =====================================================================
    # DISPONIBILIDADE — LISTA PENSADA PARA CELULAR
    # =====================================================================
    else:
        data_disp = st.date_input(
            "Data",
            value=amanha_campo,
            format="DD/MM/YYYY",
            key="engm_disp_data",
        )

        turno_disp = st.selectbox(
            "Turno",
            [
                "Integral",
                "Manhã",
                "Tarde",
                "Noite",
            ],
            key="engm_disp_turno",
        )

        try:
            convs_disp = (
                _buscar_convocacoes_intervalo(
                    data_disp,
                    data_disp,
                    None,
                )
                or []
            )
        except Exception:
            convs_disp = []

        indisponibilidades = (
            _carregar_indisponibilidades_disponibilidade()
            or []
        )

        indisponiveis_map = {}

        for item in indisponibilidades:
            alvo = str(
                item.get("colaborador_id")
                or ""
            )

            if not alvo:
                continue

            try:
                ini = datetime.date.fromisoformat(
                    str(item.get("inicio"))
                )
                fim = datetime.date.fromisoformat(
                    str(item.get("fim"))
                )
            except Exception:
                continue

            if ini <= data_disp <= fim:
                indisponiveis_map[alvo] = item

        por_colaborador = {}

        for conv in convs_disp:
            cid = str(
                conv.get("colaborador_id")
                or ""
            )

            if cid:
                por_colaborador.setdefault(
                    cid,
                    [],
                ).append(conv)

        disponiveis = []
        ocupados = []
        indisponiveis = []

        for colab in sorted(
            colaboradores,
            key=lambda c: normalizar(
                c.get("nome", "")
            ),
        ):
            cid = str(
                colab.get("id")
                or ""
            )
            nome = str(
                colab.get("nome")
                or "-"
            )
            funcao = str(
                colab.get("funcao")
                or "-"
            )

            if cid in indisponiveis_map:
                ind = indisponiveis_map[cid]
                indisponiveis.append(
                    {
                        "nome": nome,
                        "funcao": funcao,
                        "detalhe": str(
                            ind.get("motivo")
                            or "Indisponível"
                        ),
                    }
                )
                continue

            alocacoes = por_colaborador.get(
                cid,
                [],
            )

            sobrepostas = [
                conv
                for conv in alocacoes
                if turnos_se_sobrepoem(
                    turno_da_convocacao(conv),
                    turno_disp,
                )
            ]

            if sobrepostas:
                detalhes = []

                for conv in sobrepostas:
                    obra = dict_obras.get(
                        conv.get("obra_id"),
                        {},
                    )
                    detalhes.append(
                        f"{turno_da_convocacao(conv)} · "
                        f"{obra.get('unidade','-')} · "
                        f"{conv.get('engenheiro','-')}"
                    )

                ocupados.append(
                    {
                        "nome": nome,
                        "funcao": funcao,
                        "detalhe": " | ".join(
                            detalhes
                        ),
                    }
                )

            else:
                outras = []

                for conv in alocacoes:
                    obra = dict_obras.get(
                        conv.get("obra_id"),
                        {},
                    )
                    outras.append(
                        f"{turno_da_convocacao(conv)} · "
                        f"{obra.get('unidade','-')}"
                    )

                disponiveis.append(
                    {
                        "nome": nome,
                        "funcao": funcao,
                        "detalhe": (
                            "Outro turno: "
                            + " | ".join(outras)
                            if outras
                            else "Livre no dia"
                        ),
                    }
                )

        st.markdown(
            f"""
            <div class="engm-summary">
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Disponíveis</div>
                    <div class="engm-summary-value engm-avail-ok">{len(disponiveis)}</div>
                    <div class="engm-summary-note">{turno_disp}</div>
                </div>
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Ocupados</div>
                    <div class="engm-summary-value engm-avail-busy">{len(ocupados)}</div>
                    <div class="engm-summary-note">conflitam no turno</div>
                </div>
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Indisponíveis</div>
                    <div class="engm-summary-value engm-avail-off">{len(indisponiveis)}</div>
                    <div class="engm-summary-note">bloqueados</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        busca_disp = st.text_input(
            "Buscar colaborador",
            placeholder="Digite nome ou função...",
            key="engm_disp_busca",
        )

        termo_busca = normalizar(
            busca_disp
        ).strip()

        def _filtrar_lista_disp(lista):
            if not termo_busca:
                return lista

            return [
                item
                for item in lista
                if termo_busca
                in normalizar(
                    f"{item['nome']} {item['funcao']}"
                )
            ]

        disponiveis_view = _filtrar_lista_disp(
            disponiveis
        )
        ocupados_view = _filtrar_lista_disp(
            ocupados
        )
        indisponiveis_view = _filtrar_lista_disp(
            indisponiveis
        )

        st.markdown(
            f'<div class="engm-section-title">Disponíveis · {len(disponiveis_view)}</div>',
            unsafe_allow_html=True,
        )

        if disponiveis_view:
            itens = []

            for item in disponiveis_view:
                itens.append(
                    f"""
                    <div class="engm-list-item">
                        <div class="engm-list-main">
                            <div class="engm-list-name">
                                {_html.escape(item['nome'])}
                            </div>
                            <div class="engm-list-meta">
                                {_html.escape(item['funcao'])} · {_html.escape(item['detalhe'])}
                            </div>
                        </div>
                        <div class="engm-list-side engm-avail-ok">Livre</div>
                    </div>
                    """
                )

            st.html(
                '<div class="engm-list">'
                + "".join(itens)
                + "</div>"
            )
        else:
            st.caption(
                "Nenhum disponível para o filtro."
            )

        total_ocultos = (
            len(ocupados_view)
            + len(indisponiveis_view)
        )

        with st.expander(
            f"Ver ocupados e indisponíveis · {total_ocultos}",
            expanded=False,
        ):
            if ocupados_view:
                st.markdown(
                    "**Ocupados no turno**"
                )

                itens = []

                for item in ocupados_view:
                    itens.append(
                        f"""
                        <div class="engm-list-item">
                            <div class="engm-list-main">
                                <div class="engm-list-name">
                                    {_html.escape(item['nome'])}
                                </div>
                                <div class="engm-list-meta">
                                    {_html.escape(item['funcao'])} · {_html.escape(item['detalhe'])}
                                </div>
                            </div>
                            <div class="engm-list-side engm-avail-busy">Ocupado</div>
                        </div>
                        """
                    )

                st.html(
                    '<div class="engm-list">'
                    + "".join(itens)
                    + "</div>"
                )

            if indisponiveis_view:
                st.markdown(
                    "**Indisponíveis**"
                )

                itens = []

                for item in indisponiveis_view:
                    itens.append(
                        f"""
                        <div class="engm-list-item">
                            <div class="engm-list-main">
                                <div class="engm-list-name">
                                    {_html.escape(item['nome'])}
                                </div>
                                <div class="engm-list-meta">
                                    {_html.escape(item['funcao'])} · {_html.escape(item['detalhe'])}
                                </div>
                            </div>
                            <div class="engm-list-side engm-avail-off">Indisp.</div>
                        </div>
                        """
                    )

                st.html(
                    '<div class="engm-list">'
                    + "".join(itens)
                    + "</div>"
                )

elif modo_financeiro:
    # ==========================================
    # PORTAL FINANCEIRO (?financeiro)
    # ==========================================
    c_fin_titulo, c_fin_sair = st.columns(
        [5, 1]
    )

    with c_fin_titulo:
        st.markdown("### 💰 ACESSO FINANCEIRO")

    with c_fin_sair:
        if st.button(
            "Sair",
            key="btn_sair_financeiro",
            use_container_width=True,
        ):
            _limpar_acesso()
            st.query_params.clear()
            st.rerun()
    st.caption(
        "Conferência semanal de pagamentos adicionais. "
        "O Financeiro exibe somente colaboradores que tiveram Extra, Adicional noturno "
        "ou Acordos / Bonificações no ciclo. Para esses colaboradores, o total considera "
        "a base líquida da diária/meia diária + os adicionais. "
        "Ciclo de terça-feira a segunda-feira."
    )

    ciclos_fin = listar_ciclos_financeiros(26)
    mapa_ciclos_fin = {c["rotulo"]: c for c in ciclos_fin}

    # Na terça-feira, o financeiro normalmente paga o ciclo que encerrou na segunda anterior.
    indice_padrao_fin = 1 if datetime.date.today().weekday() == 1 and len(ciclos_fin) > 1 else 0
    ciclo_rotulo_fin = st.selectbox(
        "Ciclo semanal:",
        list(mapa_ciclos_fin.keys()),
        index=indice_padrao_fin,
        key="ciclo_financeiro"
    )
    ciclo_fin = mapa_ciclos_fin[ciclo_rotulo_fin]
    data_ini_fin = ciclo_fin["inicio"]
    data_fim_fin = ciclo_fin["fim"]
    data_pag_fin = ciclo_fin["pagamento"]

    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("INÍCIO", data_ini_fin.strftime("%d/%m/%Y"))
    cf2.metric("FIM", data_fim_fin.strftime("%d/%m/%Y"))
    cf3.metric("PAGAMENTO", data_pag_fin.strftime("%d/%m/%Y"))

    pagamentos_fin, ausencias_fin = carregar_dados_financeiro(data_ini_fin, data_fim_fin)
    total_pagar_fin = sum(float(x.get("Total a Pagar (R$)") or 0.0) for x in pagamentos_fin)
    nomes_pag_fin = {normalizar(x.get("Colaborador", "")) for x in pagamentos_fin}
    total_faltas_fin = sum(1 for x in ausencias_fin if x.get("Status") == "Falta")
    total_atest_fin = sum(1 for x in ausencias_fin if x.get("Status") == "Atestado")

    tab_fin_extra, tab_fin_aus, tab_fin_rel = st.tabs([
        "💸 EXTRAS / ADICIONAIS", "🚫 FALTAS / ATESTADOS", "📄 RELATÓRIO"
    ])

    with tab_fin_extra:
        fm1, fm2, fm3 = st.columns(3)
        fm1.metric("TOTAL A PAGAR", formatar_reais(total_pagar_fin))
        fm2.metric("COLABORADORES", len(nomes_pag_fin))
        fm3.metric("LANÇAMENTOS", len(pagamentos_fin))

        st.markdown("### Consolidado por colaborador")
        resumo_fin = resumir_pagamentos_financeiro(pagamentos_fin)
        if resumo_fin.empty:
            st.info(
                "Nenhum Extra, Adicional noturno ou Acordo / Bonificação "
                "foi lançado neste ciclo."
            )
        else:
            resumo_view = resumo_fin.copy()
            for _c in ["Diária (R$)", "Extra (R$)", "Adic. noturno (R$)", "Acordos / Bonificações (R$)", "Total a Pagar (R$)"]:
                if _c in resumo_view.columns:
                    resumo_view[_c.replace(" (R$)", "")] = resumo_view[_c].apply(formatar_reais)
                    resumo_view = resumo_view.drop(columns=[_c])
            tabela_aproar(resumo_view, key="tbl_fin_resumo")

            st.markdown("### Detalhamento por dia")
            detalhe_extra_view = pd.DataFrame(pagamentos_fin)[[
                "Data", "Colaborador", "Função", "Unidade", "Engenheiro", "Tipo",
                "Base Financeiro (R$)", "Extra (R$)", "Adicional noturno (R$)",
                "Acordos / Bonificações (R$)", "Total a Pagar (R$)"
            ]].copy()
            for _c in [
                "Base Financeiro (R$)",
                "Extra (R$)",
                "Adicional noturno (R$)",
                "Acordos / Bonificações (R$)",
                "Total a Pagar (R$)",
            ]:
                detalhe_extra_view[_c.replace(" (R$)", "")] = detalhe_extra_view[_c].apply(formatar_reais)
                detalhe_extra_view = detalhe_extra_view.drop(columns=[_c])
            tabela_aproar(detalhe_extra_view, key="tbl_fin_detalhe")

    with tab_fin_aus:
        fa1, fa2, fa3 = st.columns(3)
        fa1.metric("FALTAS", total_faltas_fin)
        fa2.metric("ATESTADOS", total_atest_fin)
        fa3.metric("TOTAL OCORRÊNCIAS", len(ausencias_fin))

        if not ausencias_fin:
            st.info("Nenhuma falta ou atestado foi registrado neste ciclo.")
        else:
            df_aus_fin = pd.DataFrame(ausencias_fin)[[
                "Data", "Colaborador", "Função", "Unidade", "Status", "Engenheiro"
            ]]
            tabela_aproar(df_aus_fin, key="tbl_fin_ausencias")

            st.markdown("### Resumo nominal")
            resumo_aus_fin = (
                df_aus_fin.groupby(["Colaborador", "Função"], dropna=False)
                .agg(
                    Faltas=("Status", lambda s: int((s == "Falta").sum())),
                    Atestados=("Status", lambda s: int((s == "Atestado").sum())),
                    Unidades=("Unidade", lambda s: ", ".join(sorted(set(str(v) for v in s if str(v).strip()))))
                )
                .reset_index()
            )
            resumo_aus_fin["Total"] = resumo_aus_fin["Faltas"] + resumo_aus_fin["Atestados"]
            resumo_aus_fin = resumo_aus_fin.sort_values(by=["Total", "Colaborador"], ascending=[False, True])
            tabela_aproar(resumo_aus_fin, key="tbl_fin_aus_resumo")

    with tab_fin_rel:
        st.markdown("### Relatório do ciclo")
        st.write(
            f"Período **{data_ini_fin.strftime('%d/%m/%Y')} a {data_fim_fin.strftime('%d/%m/%Y')}** • "
            f"Pagamento previsto em **{data_pag_fin.strftime('%d/%m/%Y')}**."
        )
        st.caption(
            "Este relatório não lista colaboradores que tiveram somente a diária normal. "
            "Entram apenas aqueles com Extra, Adicional noturno ou Acordos / Bonificações."
        )
        st.info(
            f"Total a pagar: {formatar_reais(total_pagar_fin)} • "
            f"Faltas: {total_faltas_fin} • Atestados: {total_atest_fin}"
        )

        excel_fin = gerar_excel_financeiro(pagamentos_fin, ausencias_fin, data_ini_fin, data_fim_fin, data_pag_fin)
        pdf_fin = gerar_pdf_financeiro(pagamentos_fin, ausencias_fin, data_ini_fin, data_fim_fin, data_pag_fin)

        fr1, fr2 = st.columns(2)
        with fr1:
            st.download_button(
                "📊 BAIXAR RELATÓRIO EXCEL",
                data=excel_fin,
                file_name=f"financeiro_pagamentos_{data_ini_fin.strftime('%d-%m-%Y')}_a_{data_fim_fin.strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_fin_excel"
            )
        with fr2:
            st.download_button(
                "📄 BAIXAR RELATÓRIO PDF",
                data=pdf_fin,
                file_name=f"financeiro_pagamentos_{data_ini_fin.strftime('%d-%m-%Y')}_a_{data_fim_fin.strftime('%d-%m-%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_fin_pdf"
            )

else:
    # ==========================================
    # PAINEL ADMINISTRATIVO (TEMA ESCURO)
    # ==========================================
    
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "🏠 INÍCIO"

    def _ir_menu_admin(destino):
        st.session_state["menu_ativo"] = destino

    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=170)
        else:
            st.markdown("<h2 style='text-align:center;color:#fff;margin:0;'>APROAR</h2>", unsafe_allow_html=True)

        st.markdown("<div class='aproar-sidebar-subtitle'>GESTÃO DE EQUIPES</div>", unsafe_allow_html=True)

        def _nav_admin(label, destino, key):
            ativo = st.session_state.get("menu_ativo") == destino
            st.button(
                label,
                key=key,
                type="primary" if ativo else "secondary",
                use_container_width=True,
                on_click=_ir_menu_admin,
                args=(destino,),
            )

        _nav_admin("Início", "🏠 INÍCIO", "btn_nav_inicio_ui4")

        st.markdown("<div class='aproar-sidebar-section'>OPERAÇÃO</div>", unsafe_allow_html=True)
        _nav_admin("Convocação", "📋 CONVOCAÇÃO", "btn_nav_conv_ui4")
        _nav_admin("Conflitos", "🚨 CONFLITOS", "btn_nav_conf_ui4")
        _nav_admin("Apontamento", "✅ APONTAMENTO", "btn_nav_apon_ui4")
        _nav_admin("WhatsApp", "💬 WHATSAPP", "btn_nav_wpp_ui4")
        _nav_admin("Disponibilidade", "👥 DISPONIBILIDADE", "btn_nav_disp_ui4")
        _nav_admin("Indisponibilidade", "🚫 INDISPONIBILIDADE", "btn_nav_indisp_ui4")

        st.markdown("<div class='aproar-sidebar-section'>ANÁLISE E FECHAMENTO</div>", unsafe_allow_html=True)
        _nav_admin("Dashboard", "🎛️ DASHBOARD", "btn_nav_dash_ui4")
        _nav_admin("Relatórios", "📊 RELATÓRIOS", "btn_nav_rel_ui4")
        _nav_admin("Indicadores", "📈 INDICADORES", "btn_nav_ind_ui4")

        st.markdown("<div class='aproar-sidebar-section'>SISTEMA</div>", unsafe_allow_html=True)
        _nav_admin("Configurações", "⚙️ CONFIGURAÇÕES", "btn_nav_cfg_ui4")

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.caption("Controladoria")
        if st.button(
            "Sair",
            key="bloquear_edicao_sidebar_ui4",
            use_container_width=True,
        ):
            _limpar_acesso()
            st.query_params.clear()
            st.rerun()

    menu_escolhido = st.session_state.menu_ativo

    # --- HOME ADMINISTRATIVA — REDESIGN V2 ---
    if menu_escolhido == "🏠 INÍCIO":
        import html as _html

        hoje_real = datetime.date.today()
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        meses_nome = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        data_extenso = f"{dias_semana[hoje_real.weekday()]}, {hoje_real.day:02d} de {meses_nome[hoje_real.month]} de {hoje_real.year}"

        st.markdown(
            f"""
            <div class="ap-home-head">
                <div>
                    <div class="ap-home-title">Visão do dia</div>
                    <div class="ap-home-sub">O que precisa de atenção e como está a equipe hoje.</div>
                </div>
                <div class="ap-home-date">{data_extenso}<span>Atualizado conforme os filtros abaixo</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        unidades_home = sorted({str(o.get("unidade") or "").strip() for o in obras if str(o.get("unidade") or "").strip()})
        with st.container(border=True, key="ap2_filters"):
            f1, f2, f3, f4 = st.columns([1.0, 1.1, 1.1, .55], vertical_alignment="bottom")
            with f1:
                data_home = st.date_input("Data", value=hoje_real, format="DD/MM/YYYY", key="ap2_home_data")
            with f2:
                unidade_home = st.selectbox("Unidade", ["Todas"] + unidades_home, key="ap2_home_unidade")
            with f3:
                engenheiro_home = st.selectbox("Engenheiro", ["Todos"] + ENGENHEIROS, key="ap2_home_engenheiro")
            with f4:
                if st.button("Atualizar", type="primary", use_container_width=True, key="ap2_home_atualizar"):
                    try:
                        _buscar_convocacoes_intervalo.clear()
                    except Exception:
                        pass
                    st.rerun()

        amanha_home = proximo_dia_util(data_home)
        registros_periodo = _buscar_convocacoes_intervalo(data_home, amanha_home)
        data_iso = data_home.isoformat()
        amanha_iso = amanha_home.isoformat()

        def _filtrar_home(registros, data_alvo=None):
            saida = []
            for c in registros or []:
                if data_alvo and str(c.get("data") or "") != data_alvo:
                    continue
                if engenheiro_home != "Todos" and str(c.get("engenheiro") or "") != engenheiro_home:
                    continue
                if unidade_home != "Todas":
                    obra_c = dict_obras.get(c.get("obra_id"), {})
                    if str(obra_c.get("unidade") or "") != unidade_home:
                        continue
                saida.append(c)
            return saida

        conv_dia = _filtrar_home(registros_periodo, data_iso)
        conv_amanha = _filtrar_home(registros_periodo, amanha_iso)

        pendentes = []
        for conv in conv_dia:
            obra_conv = dict_obras.get(conv.get("obra_id"), {})
            if not obra_conv or eh_obra_placeholder(obra_conv):
                pendentes.append(conv)

        total = len(conv_dia)
        apontados = max(0, total - len(pendentes))
        faltas = sum(1 for c in conv_dia if normalizar_status_operacional(c.get("status")) == "Falta")
        atestados = sum(1 for c in conv_dia if normalizar_status_operacional(c.get("status")) == "Atestado")
        pct_apontado = round((apontados / total * 100), 0) if total else 0
        pct_pendente = round((len(pendentes) / total * 100), 0) if total else 0

        dia_anterior = data_home - datetime.timedelta(days=1)
        while dia_anterior.weekday() >= 5:
            dia_anterior -= datetime.timedelta(days=1)
        conv_anterior_raw = _buscar_convocacoes_intervalo(dia_anterior, dia_anterior)
        conv_anterior = _filtrar_home(conv_anterior_raw, dia_anterior.isoformat())
        if len(conv_anterior):
            pct_delta = round(((total - len(conv_anterior)) / len(conv_anterior)) * 100)
            nota_total = f"{'+' if pct_delta > 0 else ''}{pct_delta}% vs. dia útil anterior"
        else:
            nota_total = "registros no dia"

        status_faltas = "danger" if (faltas + atestados) > 0 else ""
        status_pend = "warn" if pendentes else ""
        status_apont = "ok" if total and pct_apontado >= 90 else ""

        st.markdown(
            f"""
            <div class="ap-kpi-strip">
                <div class="ap-kpi">
                    <div class="ap-kpi-label">Equipe hoje</div>
                    <div class="ap-kpi-row"><div class="ap-kpi-value">{total}</div></div>
                    <div class="ap-kpi-note">{_html.escape(nota_total)}</div>
                </div>
                <div class="ap-kpi {status_apont}">
                    <div class="ap-kpi-label">Apontados</div>
                    <div class="ap-kpi-row"><div class="ap-kpi-value">{apontados}</div><div class="ap-kpi-badge">{int(pct_apontado)}%</div></div>
                    <div class="ap-kpi-note">da equipe selecionada</div>
                </div>
                <div class="ap-kpi {status_pend}">
                    <div class="ap-kpi-label">Pendentes do dia</div>
                    <div class="ap-kpi-row"><div class="ap-kpi-value">{len(pendentes)}</div><div class="ap-kpi-badge">{int(pct_pendente)}%</div></div>
                    <div class="ap-kpi-note">ainda não são atraso Teams no próprio dia</div>
                </div>
                <div class="ap-kpi {status_faltas}">
                    <div class="ap-kpi-label">Faltas / atestados</div>
                    <div class="ap-kpi-row"><div class="ap-kpi-value">{faltas + atestados}</div></div>
                    <div class="ap-kpi-note">{faltas} falta(s) · {atestados} atestado(s)</div>
                </div>
                <div class="ap-kpi">
                    <div class="ap-kpi-label">Convocados amanhã</div>
                    <div class="ap-kpi-row"><div class="ap-kpi-value">{len(conv_amanha)}</div></div>
                    <div class="ap-kpi-note">{amanha_home.strftime('%d/%m/%Y')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        conflitos_pendentes = listar_conflitos_convocacao_pendentes(90)
        conflitos_flat = []
        for reg, itens in conflitos_pendentes:
            for item in itens:
                conflitos_flat.append((reg, item))
        conflitos_flat.sort(key=lambda x: str((x[1] or {}).get("em") or ""), reverse=True)
        qtd_conflitos = len(conflitos_flat)

        tarefas_html = []
        if pendentes:
            tarefas_html.append(
                f'<div class="ap-task amber"><div><strong>{len(pendentes)} apontamento(s) pendente(s)</strong>'
                '<span>Há colaboradores ainda sem Obra/Serviço definida no dia selecionado. '
                'No próprio dia eles são pendentes, não atrasados para o Teams. '
                'Se continuarem sem apontamento, entram na cobrança do dia seguinte; no SEBRAE, a partir de 09:30.</span></div>'
                f'<div class="ap-task-count">{len(pendentes)}</div></div>'
            )
        if qtd_conflitos:
            tarefas_html.append(
                f'<div class="ap-task red"><div><strong>{qtd_conflitos} conflito(s) de convocação</strong>'
                '<span>Tentativas de convocação em turnos que se sobrepõem.</span></div>'
                f'<div class="ap-task-count">{qtd_conflitos}</div></div>'
            )
        if faltas or atestados:
            tarefas_html.append(
                f'<div class="ap-task red"><div><strong>{faltas + atestados} ausência(s) registrada(s)</strong>'
                f'<span>{faltas} falta(s) · {atestados} atestado(s).</span></div>'
                f'<div class="ap-task-count">{faltas + atestados}</div></div>'
            )
        if not tarefas_html:
            tarefas_html.append(
                '<div class="ap-task green"><div><strong>Nenhuma pendência imediata</strong>'
                '<span>O filtro selecionado não apresenta itens que exijam ação agora.</span></div>'
                '<div class="ap-task-count">OK</div></div>'
            )

        conflitos_html = []
        for reg, item in conflitos_flat[:3]:
            nome = str(item.get("colaborador_nome") or dict_colaboradores.get(reg.get("colaborador_id"), {}).get("nome") or "Colaborador")
            turno_original = str(item.get("turno_original") or turno_da_convocacao(reg))
            turno_tentativa = str(item.get("turno_tentativa") or "")
            eng_original = str(item.get("engenheiro_original") or reg.get("engenheiro") or "")
            eng_tent = str(item.get("tentativa_por") or "")
            hora = ""
            try:
                dt = datetime.datetime.fromisoformat(str(item.get("em") or "").replace("Z", "+00:00"))
                hora = dt.astimezone(ZoneInfo("America/Fortaleza")).strftime("%H:%M")
            except Exception:
                pass
            conflitos_html.append(
                '<div class="ap-conflict"><div class="ap-conflict-top">'
                f'<div class="ap-conflict-name">{_html.escape(nome)}</div>'
                f'<div class="ap-conflict-time">{_html.escape(hora)}</div></div>'
                f'<div class="ap-conflict-detail">{_html.escape(eng_original)} · {_html.escape(turno_original)} × {_html.escape(eng_tent)} · {_html.escape(turno_tentativa)}</div>'
                '</div>'
            )
        if not conflitos_html:
            conflitos_html.append(
                '<div class="ap-task green"><div><strong>Nenhum conflito pendente</strong>'
                '<span>A fila de conflitos está limpa.</span></div><div class="ap-task-count">OK</div></div>'
            )

        st.markdown(
            f"""
            <div class="ap-action-grid">
                <div class="ap-card">
                    <div class="ap-card-head">
                        <div><div class="ap-card-title">Precisa de atenção</div><div class="ap-card-sub">Itens que podem exigir alguma ação hoje.</div></div>
                        <div class="ap-pill amber">{len(tarefas_html)} item(ns)</div>
                    </div>
                    <div class="ap-task-list">{''.join(tarefas_html)}</div>
                </div>
                <div class="ap-card">
                    <div class="ap-card-head">
                        <div><div class="ap-card-title">Conflitos</div><div class="ap-card-sub">Últimas tentativas bloqueadas.</div></div>
                        <div class="ap-pill red">{qtd_conflitos}</div>
                    </div>
                    <div class="ap-conflict-list">{''.join(conflitos_html)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Mostra exatamente quais são os apontamentos pendentes.
        if pendentes:
            with st.expander(
                f"Ver apontamentos pendentes · {len(pendentes)}",
                expanded=False,
            ):
                linhas_pendentes = []

                for conv in pendentes:
                    colaborador = dict_colaboradores.get(
                        conv.get("colaborador_id"),
                        {},
                    )
                    obra_placeholder = dict_obras.get(
                        conv.get("obra_id"),
                        {},
                    )

                    linhas_pendentes.append({
                        "Colaborador": str(
                            colaborador.get("nome")
                            or "Não identificado"
                        ),
                        "Função": str(
                            colaborador.get("funcao")
                            or "-"
                        ),
                        "Engenheiro": str(
                            conv.get("engenheiro")
                            or "-"
                        ),
                        "Unidade": str(
                            obra_placeholder.get("unidade")
                            or "-"
                        ),
                        "Turno": turno_da_convocacao(
                            conv
                        ),
                        "Data": data_home.strftime(
                            "%d/%m/%Y"
                        ),
                        "Pendência": "Definir Obra / Serviço",
                    })

                df_pendentes_home = pd.DataFrame(
                    linhas_pendentes
                ).sort_values(
                    [
                        "Engenheiro",
                        "Unidade",
                        "Colaborador",
                    ]
                )

                tabela_aproar(
                    df_pendentes_home,
                    key="ap2_home_pendentes_detalhe",
                    altura_max=360,
                )

                if st.button(
                    "Ir para Apontamentos",
                    type="primary",
                    use_container_width=True,
                    key="ap2_home_ir_apontamentos",
                ):
                    _ir_menu_admin(
                        "✅ APONTAMENTO"
                    )
                    st.rerun()

        st.markdown('<div class="ap-quick-head">Ações rápidas</div>', unsafe_allow_html=True)
        with st.container(key="ap2_quick"):
            q1, q2, q3, q4 = st.columns(4)
            q1.button("Nova convocação", use_container_width=True, on_click=_ir_menu_admin, args=("📋 CONVOCAÇÃO",), key="ap2_quick_conv")
            q2.button("Apontamentos", use_container_width=True, on_click=_ir_menu_admin, args=("✅ APONTAMENTO",), key="ap2_quick_apon")
            q3.button("Disponibilidade", use_container_width=True, on_click=_ir_menu_admin, args=("👥 DISPONIBILIDADE",), key="ap2_quick_disp")
            q4.button("Indicadores", use_container_width=True, on_click=_ir_menu_admin, args=("📈 INDICADORES",), key="ap2_quick_ind")

    # --- CONFLITOS DE CONVOCAÇÃO / PAULO ---
    elif menu_escolhido == "🚨 CONFLITOS":
        cabecalho_pagina_aproar(
            "Conflitos de convocação",
            "Confira tentativas bloqueadas por sobreposição de turnos e marque as situações já resolvidas.",
            categoria="OPERAÇÃO",
        )
        st.caption(
            "Fila para conferência do Paulo. Só entra aqui quando dois supervisores tentam convocar "
            "a mesma pessoa em turnos que se sobrepõem. Manhã + Tarde, por exemplo, é permitido."
        )

        conflitos_pendentes = listar_conflitos_convocacao_pendentes(90)
        total_conflitos = sum(len(p) for _, p in conflitos_pendentes)
        st.metric("CONFLITOS PENDENTES", total_conflitos)

        if not conflitos_pendentes:
            st.success("Nenhum conflito de convocação pendente.")
        else:
            for reg, pend_conf in conflitos_pendentes:
                colab_conf = obter_colaborador_por_id(reg.get("colaborador_id"))
                nome_colab = (colab_conf or {}).get("nome") or next(
                    (str(x.get("colaborador_nome") or "") for x in pend_conf if x.get("colaborador_nome")),
                    "Colaborador não identificado",
                )
                eng_original = str(reg.get("engenheiro") or pend_conf[0].get("engenheiro_original") or "N/A")
                data_reg = str(reg.get("data") or pend_conf[0].get("data_convocacao") or "")

                with st.container(border=True):
                    st.markdown(f"### {nome_colab}")
                    st.markdown(f"**Data:** {data_reg}  \n**Convocado originalmente por:** {eng_original}")
                    for conflito in pend_conf:
                        instante = str(conflito.get("em") or "")
                        instante_fmt = instante[:16].replace("T", " ") if instante else "horário não registrado"
                        turno_original = conflito.get("turno_original") or turno_da_convocacao(reg)
                        turno_tentativa = conflito.get("turno_tentativa") or "Integral"
                        unidade_tentativa = conflito.get("unidade_tentativa") or ""
                        detalhe_unidade = f" • Unidade tentada: {unidade_tentativa}" if unidade_tentativa else ""
                        st.warning(
                            f"⚠️ **{eng_original}** já tinha o colaborador em **{turno_original}**. "
                            f"**{conflito.get('tentativa_por','N/A')}** tentou **{turno_tentativa}** "
                            f"em {instante_fmt}{detalhe_unidade}. A sobreposição foi bloqueada."
                        )

                    if st.button(
                        "✅ MARCAR CONFLITO COMO RESOLVIDO",
                        key=f"resolver_conf_pagina_{reg.get('id')}",
                        use_container_width=True,
                    ):
                        if resolver_conflitos_convocacao(reg):
                            st.success("Conflito marcado como resolvido.")
                            st.rerun()
                        else:
                            st.error("Não foi possível atualizar o conflito.")

    # --- DASHBOARD / AUDITORIA ---
    elif menu_escolhido == "🎛️ DASHBOARD":
        render_dashboard_consulta("admin_dash_melhorias")

    # --- 2. CONVOCAÇÃO ---
    elif menu_escolhido == "📋 CONVOCAÇÃO":
        cabecalho_pagina_aproar(
            "Convocação",
            "Monte a equipe do próximo dia e faça correções administrativas quando necessário.",
            categoria="OPERAÇÃO",
        )
        tab_nova_conv, tab_corrigir_conv = st.tabs(["➕ Nova Convocação", "✏️ Correção / Exclusão Administrativa"])

        with tab_nova_conv:
            if obras:
                col_eng, col_info, col_turno = st.columns(3)
                with col_eng:
                    engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv_adm")

                data_conv_auto = proximo_dia_util(datetime.date.today())
                with col_info:
                    st.info(f"📅 **Próximo dia:** {data_conv_auto.strftime('%d/%m/%Y')}")
                with col_turno:
                    turno_conv_adm = st.selectbox("Turno:", ["Integral", "Manhã", "Tarde", "Noite"], key="turno_conv_adm")

                unidades_unicas = UNIDADES_APROAR.copy()
                unidade_selecionada = st.selectbox("Unidade:", unidades_unicas, key="u_adm_sel")

                funcoes_disponiveis = sorted(list(set([c.get('funcao', '') for c in colaboradores if c.get('funcao')])))
                filtro_funcao_adm = st.selectbox("Filtrar por Função (Opcional):", ["TODAS"] + funcoes_disponiveis, key="f_adm_sel")

                if filtro_funcao_adm != "TODAS":
                    colabs_filtrados_adm = [c for c in colaboradores if c.get('funcao') == filtro_funcao_adm]
                else:
                    colabs_filtrados_adm = colaboradores

                try:
                    convs_data_adm = (
                        supabase.table("convocacoes")
                        .select("*")
                        .eq("data", data_conv_auto.isoformat())
                        .execute().data or []
                    )
                except Exception:
                    convs_data_adm = []

                convs_por_colab_adm = {}
                for conv_exist in convs_data_adm:
                    convs_por_colab_adm.setdefault(str(conv_exist.get("colaborador_id")), []).append(conv_exist)

                mapa_colab_adm = {}
                for c in colabs_filtrados_adm:
                    cid = c["id"]
                    alocacoes = convs_por_colab_adm.get(str(cid), [])
                    sufixos = []
                    for aloc in alocacoes:
                        t_exist = turno_da_convocacao(aloc)
                        eng_exist = str(aloc.get("engenheiro") or "N/A")
                        obra_exist = dict_obras.get(aloc.get("obra_id"), {})
                        unid_exist = obra_exist.get("unidade", "-")
                        # Mantém todos os colaboradores selecionáveis. Se houver sobreposição,
                        # a confirmação será bloqueada e o conflito será enviado ao Paulo.
                        sufixos.append(f"já {t_exist} - {eng_exist} / {unid_exist}")

                    status_aloc = f" — {' | '.join(sufixos)}" if sufixos else ""
                    mapa_colab_adm[f"{c['nome']}  ({c.get('funcao','-')}){status_aloc}"] = cid

                st.caption(
                    "Os nomes já convocados continuam liberados para seleção. O sistema só bloqueia "
                    "na confirmação quando os turnos se sobrepõem, registrando o conflito para o Paulo."
                )
                equipe_selecionada = st.multiselect(
                    "Buscar ou Selecionar Colaboradores Cadastrados:",
                    list(mapa_colab_adm.keys()),
                    key="eq_adm_sel"
                )

                st.markdown("#### ➕ Incluir nome digitado")
                avulso_adm = st.checkbox("É avulso?", key="avulso_conv_adm")
                nome_manual_adm = st.text_input(
                    "Nome do avulso:" if avulso_adm else "Adicionar colaborador pelo nome (opcional):",
                    placeholder="Digite o nome completo...",
                    key="nome_manual_conv_adm"
                )

                tipo_manual_adm = "Profissional"
                funcao_manual_adm = ""
                if avulso_adm or nome_manual_adm.strip():
                    ca1, ca2 = st.columns(2)
                    with ca1:
                        tipo_manual_adm = st.selectbox(
                            "Categoria da diária:",
                            ["Profissional", "Ajudante"],
                            key="tipo_manual_conv_adm"
                        )
                    with ca2:
                        funcao_manual_adm = st.text_input(
                            "Função (opcional):",
                            placeholder="Ex.: pintor, eletricista...",
                            key="funcao_manual_conv_adm"
                        )
                    st.caption(
                        f"Diária aplicada: Profissional = {formatar_reais(VALOR_DIARIA_PROFISSIONAL)} • "
                        f"Ajudante = {formatar_reais(VALOR_DIARIA_AJUDANTE)}"
                    )

                with st.container(border=True):
                    st.markdown(f"**Panorama de {engenheiro_conv} ({data_conv_auto.strftime('%d/%m/%Y')} • {turno_conv_adm})**")
                    try:
                        convs_eng_data = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_conv).eq("data", data_conv_auto.isoformat()).execute().data
                    except Exception:
                        convs_eng_data = []
                    ids_ja_alocados_eng = {c['colaborador_id'] for c in convs_eng_data}
                    nomes_ja_alocados = [dict_colaboradores.get(cid, {}).get('nome', '') for cid in ids_ja_alocados_eng]
                    if nomes_ja_alocados:
                        st.caption("Já escalados por este engenheiro nesta data: " + ", ".join([n for n in nomes_ja_alocados if n]))
                    else:
                        st.caption("Nenhum escalado por este engenheiro ainda para o próximo dia.")
                    st.caption("A demanda específica será escolhida individualmente no Apontamento Diário.")

                if st.button("CONFIRMAR CONVOCAÇÃO", type="primary", use_container_width=True, key="btn_confirm_conv_adm"):
                    if avulso_adm and not nome_manual_adm.strip():
                        st.warning("Para convocar como avulso, digite o nome do colaborador.")
                    elif not equipe_selecionada and not nome_manual_adm.strip():
                        st.warning("Selecione um colaborador cadastrado ou digite um nome.")
                    else:
                        obra_id_placeholder = obter_obra_placeholder_unidade(unidade_selecionada)
                        if not obra_id_placeholder:
                            st.error(f"Não foi possível preparar a Unidade **{unidade_selecionada}** para a convocação.")
                        else:
                            pessoas = []
                            for label_colab in equipe_selecionada:
                                c_id = mapa_colab_adm[label_colab]
                                nome_existente = dict_colaboradores.get(c_id, {}).get('nome', label_colab.split('  (')[0])
                                pessoas.append((c_id, nome_existente))

                            if nome_manual_adm.strip():
                                c_id_manual, colab_manual, msg_manual = criar_ou_obter_colaborador_manual(
                                    nome_manual_adm,
                                    tipo_manual_adm,
                                    funcao_manual_adm,
                                    avulso=avulso_adm
                                )
                                if c_id_manual:
                                    pessoas.append((c_id_manual, colab_manual.get('nome', nome_manual_adm)))
                                    if "existente" in msg_manual.lower():
                                        st.info(msg_manual)
                                else:
                                    st.error(msg_manual)

                            pessoas_unicas = []
                            ids_vistos = set()
                            for cid, nome_pessoa in pessoas:
                                if cid and cid not in ids_vistos:
                                    pessoas_unicas.append((cid, nome_pessoa))
                                    ids_vistos.add(cid)

                            sucessos = 0
                            avisos = []
                            for c_id, nome_pessoa in pessoas_unicas:
                                ok, motivo = inserir_convocacao_segura(
                                    obra_id_placeholder,
                                    c_id,
                                    data_conv_auto,
                                    engenheiro_conv,
                                    turno_conv_adm
                                )
                                if ok:
                                    sucessos += 1
                                else:
                                    avisos.append(f"{nome_pessoa}: {motivo}.")

                            if sucessos:
                                limpar_cache_operacional()
                                st.success(
                                    f"✅ {sucessos} colaborador(es) convocado(s) para {unidade_selecionada} "
                                    f"em {data_conv_auto.strftime('%d/%m/%Y')} • Turno {turno_conv_adm}."
                                )
                            for aviso in avisos:
                                st.warning(aviso)
            else:
                st.info("Cadastre pelo menos uma Unidade/Obra na aba Configurações.")

        with tab_corrigir_conv:
            st.markdown("### ✏️ Correção / Exclusão Administrativa")
            st.write("Realocar um colaborador para outra Unidade/Obra ou excluir uma convocação lançada incorretamente pelo campo.")

            c_corr1, c_corr2 = st.columns(2)
            with c_corr1:
                data_corr = st.date_input(
                    "Data da Convocação para Corrigir:",
                    value=proximo_dia_util(datetime.date.today()),
                    format="DD/MM/YYYY",
                    key="d_corr"
                )

            try:
                convs_existentes = supabase.table("convocacoes").select("*").eq("data", data_corr.isoformat()).execute().data
            except Exception:
                convs_existentes = []

            if not convs_existentes:
                st.info("Nenhuma convocação encontrada nesta data para correção.")
            else:
                mapa_convs_corr = {}
                for item in convs_existentes:
                    colab_inf = dict_colaboradores.get(item['colaborador_id'], {})
                    obra_inf = dict_obras.get(item['obra_id'], {})
                    nome_obra_exib = obra_inf.get('nome', 'N/A')
                    if eh_obra_placeholder(obra_inf):
                        nome_obra_exib = "Obra/Serviço a definir"
                    rotulo = (
                        f"{colab_inf.get('nome','N/A')} | "
                        f"{obra_inf.get('unidade','N/A')} | {nome_obra_exib} | "
                        f"Eng: {item.get('engenheiro','N/A')}"
                    )
                    mapa_convs_corr[rotulo] = item

                with c_corr2:
                    conv_selecionada_rotulo = st.selectbox(
                        "Selecione o colaborador/convocação:",
                        list(mapa_convs_corr.keys()),
                        key="conv_sel_corr"
                    )

                registro_corr = mapa_convs_corr[conv_selecionada_rotulo]
                colab_corr = dict_colaboradores.get(registro_corr.get('colaborador_id'), {})
                obra_corr = dict_obras.get(registro_corr.get('obra_id'), {})
                unidade_atual_corr = obra_corr.get('unidade', '')
                nome_obra_atual_corr = obra_corr.get('nome', '')

                st.markdown(f"**Colaborador:** {colab_corr.get('nome', 'N/A')}")

                unidades_disponiveis = UNIDADES_APROAR.copy()
                idx_unidade = unidades_disponiveis.index(unidade_atual_corr) if unidade_atual_corr in unidades_disponiveis else 0

                c_dest1, c_dest2, c_dest3 = st.columns(3)
                with c_dest1:
                    nova_unidade_corr = st.selectbox(
                        "Unidade de destino:",
                        unidades_disponiveis,
                        index=idx_unidade,
                        key="u_dest_corr"
                    )

                obras_nova_u_lista = obras_reais_da_unidade(nova_unidade_corr)
                mapa_obras_nova_u = {o['nome']: o['id'] for o in obras_nova_u_lista}
                opcao_a_definir = "A DEFINIR NO APONTAMENTO"
                opcoes_obra_corr = [opcao_a_definir] + list(mapa_obras_nova_u.keys())

                if nova_unidade_corr == unidade_atual_corr and nome_obra_atual_corr in mapa_obras_nova_u:
                    idx_obra_corr = opcoes_obra_corr.index(nome_obra_atual_corr)
                else:
                    idx_obra_corr = 0

                with c_dest2:
                    nova_obra_corr = st.selectbox(
                        "Obra / Serviço de destino:",
                        opcoes_obra_corr,
                        index=idx_obra_corr,
                        key="o_dest_corr"
                    )
                with c_dest3:
                    eng_atual = registro_corr.get('engenheiro', ENGENHEIROS[0])
                    idx_eng = ENGENHEIROS.index(eng_atual) if eng_atual in ENGENHEIROS else 0
                    novo_eng_corr = st.selectbox(
                        "Engenheiro responsável:",
                        ENGENHEIROS,
                        index=idx_eng,
                        key="eng_dest_corr"
                    )

                b_corr1, b_corr2 = st.columns(2)
                with b_corr1:
                    if st.button("💾 SALVAR REALOCAÇÃO", type="primary", use_container_width=True):
                        if nova_obra_corr == opcao_a_definir:
                            nova_obra_id = obter_obra_placeholder_unidade(nova_unidade_corr)
                        else:
                            nova_obra_id = mapa_obras_nova_u.get(nova_obra_corr)

                        if not nova_obra_id:
                            st.error("Não foi possível definir a Unidade/Obra de destino.")
                        else:
                            antes_realocacao = dict(registro_corr)
                            depois_realocacao = dict(antes_realocacao)
                            depois_realocacao.update({
                                "obra_id": nova_obra_id,
                                "engenheiro": novo_eng_corr
                            })
                            supabase.table("convocacoes").update({
                                "obra_id": nova_obra_id,
                                "engenheiro": novo_eng_corr
                            }).eq("id", registro_corr['id']).execute()
                            registrar_auditoria_prod(
                                "convocacao", registro_corr['id'], "REALOCAÇÃO_ADMIN", "ADMIN",
                                antes=antes_realocacao, depois=depois_realocacao,
                                contexto={"origem": "correcao_administrativa"}
                            )
                            st.success("✅ Colaborador realocado com sucesso.")
                            st.rerun()

                with b_corr2:
                    id_corr_atual = registro_corr["id"]

                    if st.button(
                        "🗑️ EXCLUIR CONVOCAÇÃO",
                        use_container_width=True,
                        key=f"exc_conv_{id_corr_atual}"
                    ):
                        st.session_state["conv_exclusao_pendente"] = id_corr_atual
                        st.rerun()

                    if st.session_state.get("conv_exclusao_pendente") == id_corr_atual:
                        st.markdown(
                            f"""
                            <div style="
                                background:#F8FAFC;
                                border:1px solid #CBD5E1;
                                border-left:4px solid #EF4444;
                                border-radius:12px;
                                padding:14px 16px;
                                margin:8px 0 12px 0;
                                color:#0F172A;
                                line-height:1.45;
                            ">
                                <div style="font-weight:700; font-size:15px; margin-bottom:4px;">
                                    Confirmar exclusão
                                </div>
                                <div style="font-size:14px;">
                                    Excluir a convocação de
                                    <strong>{colab_corr.get('nome', 'N/A')}</strong>
                                    em <strong>{data_corr.strftime('%d/%m/%Y')}</strong>?
                                </div>
                                <div style="font-size:12px; color:#64748B; margin-top:5px;">
                                    Esta ação não pode ser desfeita.
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        conf1, conf2 = st.columns(2)

                        with conf1:
                            if st.button(
                                "✅ SIM, EXCLUIR",
                                type="primary",
                                use_container_width=True,
                                key=f"confirma_exc_conv_{id_corr_atual}"
                            ):
                                try:
                                    antes_exclusao = dict(registro_corr)
                                    retorno_exc = (
                                        supabase.table("convocacoes")
                                        .delete()
                                        .eq("id", id_corr_atual)
                                        .execute()
                                    )
                                    registrar_auditoria_prod(
                                        "convocacao", id_corr_atual, "EXCLUIR_ADMIN", "ADMIN",
                                        antes=antes_exclusao,
                                        contexto={
                                            "origem": "correcao_administrativa",
                                            "colaborador_nome": colab_corr.get('nome', 'N/A')
                                        }
                                    )

                                    st.session_state.pop("conv_exclusao_pendente", None)
                                    st.session_state["msg_corr_admin"] = (
                                        f"✅ Convocação de {colab_corr.get('nome', 'N/A')} excluída com sucesso."
                                    )
                                    limpar_cache_operacional()
                                    st.rerun()

                                except Exception as e:
                                    exibir_erro_amigavel("convocacao", "excluir", e, "Não foi possível excluir a convocação.")

                        with conf2:
                            if st.button(
                                "↩️ CANCELAR",
                                use_container_width=True,
                                key=f"cancela_exc_conv_{id_corr_atual}"
                            ):
                                st.session_state.pop("conv_exclusao_pendente", None)
                                st.rerun()

    # --- MENSAGEM PARA WHATSAPP ---
    elif menu_escolhido == "💬 WHATSAPP":
        cabecalho_pagina_aproar(
            "WhatsApp",
            "Gere a mensagem de convocação já organizada para copiar e enviar aos grupos.",
            categoria="OPERAÇÃO",
        )
        st.write("Gere a divisão de equipes no padrão do grupo de Colaboradores e copie a mensagem pronta.")

        c_wpp1, c_wpp2 = st.columns([1, 1])
        with c_wpp1:
            data_wpp = st.date_input(
                "Data da divisão:",
                value=proximo_dia_util(datetime.date.today()),
                format="DD/MM/YYYY",
                key="data_mensagem_wpp"
            )
        with c_wpp2:
            mostrar_funcao_wpp = st.checkbox(
                "Mostrar função entre parênteses",
                value=False,
                key="mostrar_funcao_wpp"
            )

        try:
            convocacoes_wpp = (
                supabase.table("convocacoes")
                .select("*")
                .eq("data", data_wpp.isoformat())
                .execute().data or []
            )
        except Exception as e:
            convocacoes_wpp = []
            exibir_erro_amigavel("convocacao", "carregar_whatsapp", e, "Não foi possível carregar as convocações.")

        agrupado_wpp = organizar_convocacoes_whatsapp(convocacoes_wpp, mostrar_funcao=mostrar_funcao_wpp)
        unidades_com_divisao = list(agrupado_wpp.keys())

        unidades_cadastradas_wpp = sorted({
            o.get("unidade") for o in obras
            if o.get("unidade") and normalizar(o.get("unidade")) not in ["GERAL", "NAO IDENTIFICADA"]
        }, key=lambda x: normalizar(x))
        unidades_sem_divisao = [u for u in unidades_cadastradas_wpp if u not in unidades_com_divisao]

        if unidades_com_divisao:
            st.success(
                f"{len(convocacoes_wpp)} convocação(ões) encontrada(s) em "
                f"{len(unidades_com_divisao)} unidade(s)."
            )
        else:
            st.warning("Ainda não há nenhuma convocação registrada para a data selecionada.")

        if unidades_sem_divisao:
            with st.expander("🔎 Unidades sem convocação registrada nesta data"):
                st.write(", ".join(formatar_unidade_whatsapp(u) for u in unidades_sem_divisao))
                st.caption("Essa lista é apenas uma referência; podem existir unidades sem atividade nesta data.")

        aviso_pendentes_wpp = st.checkbox(
            "Ainda existem demandas que serão enviadas por outros responsáveis",
            value=bool(unidades_sem_divisao),
            key="aviso_pendentes_wpp",
            help="Ao marcar, o texto acrescenta: 'As demais demandas serão enviadas pelos respectivos responsáveis.'"
        )

        mensagem_geral_wpp = montar_mensagem_whatsapp(
            data_wpp,
            convocacoes_wpp,
            mostrar_funcao=mostrar_funcao_wpp,
            aviso_pendentes=aviso_pendentes_wpp
        )

        st.markdown("### 📋 Mensagem completa")
        st.caption("Use o ícone de copiar no canto do bloco abaixo e cole diretamente no WhatsApp.")
        st.code(mensagem_geral_wpp, language=None, wrap_lines=True)

        if unidades_com_divisao:
            st.markdown("### 🏢 Mensagem separada por Unidade")
            st.caption("Caso prefira enviar a divisão de cada Unidade separadamente.")
            for unidade in unidades_com_divisao:
                with st.expander(f"📌 {formatar_unidade_whatsapp(unidade)}"):
                    mensagem_unidade = montar_mensagem_whatsapp(
                        data_wpp,
                        convocacoes_wpp,
                        mostrar_funcao=mostrar_funcao_wpp,
                        aviso_pendentes=False,
                        somente_unidade=unidade
                    )
                    st.code(mensagem_unidade, language=None, wrap_lines=True)

        st.markdown("---")
        st.caption(
            "A mensagem usa somente a Unidade da convocação. Obra/Serviço não é exibida, "
            "e os colaboradores são numerados automaticamente."
        )

    # --- 3. APONTAMENTO ---
    elif menu_escolhido == "✅ APONTAMENTO":
        render_apontamento_operacional(None, "admin_apont_melhorias")

    # --- 4. RELATÓRIOS ---
    elif menu_escolhido == "📊 RELATÓRIOS":
        cabecalho_pagina_aproar(
            "Relatórios",
            "Controladoria: Profissional R$ 241,74 / Ajudante R$ 182,34 + Extra + Adicional noturno + Acordos/Bonificações. O Total de cada colaborador é a soma desses valores. No SEBRAE, o adicional noturno é sempre R$ 90,00 por colaborador presente.",
            categoria="ANÁLISE E FECHAMENTO",
        )
        
        # Filtro de Periodicidade
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            periodicidade = st.selectbox("Periodicidade:", ["Personalizado", "Diário", "Semanal", "Mensal"], key="rel_periodo")
        
        hoje = datetime.date.today()
        if periodicidade == "Diário":
            dt_inicio_def = hoje
            dt_fim_def = hoje
        elif periodicidade == "Semanal":
            dt_inicio_def = hoje - datetime.timedelta(days=7)
            dt_fim_def = hoje
        elif periodicidade == "Mensal":
            dt_inicio_def = hoje.replace(day=1)
            dt_fim_def = hoje
        else:
            dt_inicio_def = hoje
            dt_fim_def = hoje

        with c_p2:
            data_inicio_rel = st.date_input("Início:", value=dt_inicio_def, format="DD/MM/YYYY", key="data_ini_rel")
        with c_p3:
            data_fim_rel = st.date_input("Fim:", value=dt_fim_def, format="DD/MM/YYYY", key="data_fim_rel")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            eng_relatorio = st.selectbox("Engenheiro:", ["TODOS OS ENGENHEIROS"] + ENGENHEIROS, key="eng_rel")
        with col_r2:
            # "A DEFINIR NO APONTAMENTO - UNIDADE" é apenas um registro técnico
            # interno. Ele não deve aparecer para o usuário como obra real.
            obras_rel_lista = (
                sorted(
                    {
                        str(o.get("nome") or "").strip()
                        for o in obras
                        if str(o.get("nome") or "").strip()
                        and not eh_obra_placeholder(o)
                    }
                )
                if obras
                else []
            )

            opcoes_obras_rel = [
                "TODAS AS OBRAS",
                *obras_rel_lista,
            ]

            # Se a sessão ainda estiver com um placeholder selecionado de uma
            # versão anterior, volta automaticamente para "TODAS AS OBRAS".
            if (
                st.session_state.get("obra_rel")
                not in opcoes_obras_rel
            ):
                st.session_state["obra_rel"] = "TODAS AS OBRAS"

            obra_relatorio = st.selectbox(
                "Filtro por Obra:",
                opcoes_obras_rel,
                key="obra_rel",
            )

        eng_rel_filtro = None if eng_relatorio == "TODOS OS ENGENHEIROS" else eng_relatorio
        obra_id_filtro = None
        if obra_relatorio != "TODAS AS OBRAS":
            obra_id_filtro = next((o['id'] for o in obras if o['nome'] == obra_relatorio), None)

        dados_relatorio = (
            _buscar_convocacoes_intervalo(
                data_inicio_rel,
                data_fim_rel,
                eng_rel_filtro,
            )
            if data_inicio_rel <= data_fim_rel
            else []
        )

        # Expande cada colaborador por obra/serviço e rateia a diária.
        # O filtro por obra é aplicado DEPOIS do rateio para trazer apenas
        # a parcela financeira correspondente ao serviço selecionado.
        linhas_relatorio = ratear_registros_por_servico(
            dados_relatorio
        )

        if obra_relatorio != "TODAS AS OBRAS":
            linhas_relatorio = _filtrar_rateio_por_obra(
                linhas_relatorio,
                obra_id=obra_id_filtro,
                obra_nome=obra_relatorio,
            )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button(
                "Gerar PDF",
                use_container_width=True,
                key="rel_gerar_pdf_v42",
            ):
                try:
                    if data_inicio_rel > data_fim_rel:
                        st.error("Data inicial maior que a final.")
                    elif not linhas_relatorio:
                        st.warning("Sem dados no período.")
                    else:
                        df_pdf = pd.DataFrame(
                            linhas_relatorio
                        )

                        grupos_obra = []
                        for (
                            obra_nome,
                            unidade_nome,
                        ), df_obra in df_pdf.groupby(
                            ["Obra", "Unidade"],
                            dropna=False,
                            sort=True,
                        ):
                            grupos_obra.append(
                                (
                                    str(obra_nome),
                                    str(unidade_nome),
                                    df_obra.sort_values(
                                        [
                                            "Data",
                                            "Colaborador",
                                            "Período do serviço",
                                        ]
                                    ),
                                )
                            )

                        pdf = FPDF(orientation="L")

                        periodo_rotulo_pdf = (
                            f"{data_inicio_rel.strftime('%d/%m/%Y')} "
                            f"a {data_fim_rel.strftime('%d/%m/%Y')} "
                            f"({periodicidade})"
                        )

                        for (
                            obra_nome,
                            unidade_nome,
                            df_obra,
                        ) in grupos_obra:
                            pdf.add_page()

                            pdf.set_font(
                                "Arial",
                                "B",
                                13,
                            )
                            pdf.cell(
                                0,
                                9,
                                txt=to_latin(
                                    "APROAR - RELATÓRIO DA CONTROLADORIA"
                                ),
                                ln=True,
                                align="C",
                            )

                            # Um único cabeçalho para a obra e o período.
                            pdf.set_font(
                                "Arial",
                                "B",
                                10,
                            )
                            pdf.set_fill_color(
                                30,
                                41,
                                59,
                            )
                            pdf.set_text_color(
                                255,
                                255,
                                255,
                            )
                            pdf.cell(
                                0,
                                8,
                                txt=to_latin(
                                    f"UNIDADE: {unidade_nome} | "
                                    f"OBRA: {obra_nome} | "
                                    f"PERÍODO: {periodo_rotulo_pdf}"
                                ),
                                ln=True,
                                fill=True,
                                align="C",
                            )
                            pdf.set_text_color(0, 0, 0)
                            pdf.ln(3)

                            # A4 paisagem: 277 mm úteis com margens padrão.
                            # Cabeçalhos longos usam 2 linhas para não invadir
                            # a coluna vizinha.
                            cabecalhos = [
                                ("Data", 16, "C"),
                                ("Colaborador", 37, "L"),
                                ("Função", 24, "L"),
                                ("Engenheiro", 20, "C"),
                                ("Status", 22, "C"),
                                ("Tipo", 15, "C"),
                                ("Custo c/\nencargos", 25, "C"),
                                ("Extra", 16, "C"),
                                ("Adic.\nnoturno", 18, "C"),
                                ("Acordos /\nBonificações", 23, "C"),
                                ("Total", 20, "C"),
                                ("Observação", 21, "L"),
                            ]

                            altura_header = 10
                            y_header = pdf.get_y()
                            x_header = pdf.get_x()

                            pdf.set_fill_color(
                                244,
                                246,
                                249,
                            )
                            pdf.set_text_color(
                                30,
                                41,
                                59,
                            )
                            pdf.set_font(
                                "Arial",
                                "B",
                                7,
                            )

                            x_atual = x_header

                            for (
                                titulo,
                                largura,
                                alinhamento,
                            ) in cabecalhos:
                                pdf.set_xy(
                                    x_atual,
                                    y_header,
                                )

                                pdf.rect(
                                    x_atual,
                                    y_header,
                                    largura,
                                    altura_header,
                                    style="DF",
                                )

                                linhas_titulo = str(
                                    titulo
                                ).split("\n")

                                if len(linhas_titulo) == 1:
                                    pdf.set_xy(
                                        x_atual,
                                        y_header + 2,
                                    )
                                    pdf.cell(
                                        largura,
                                        6,
                                        to_latin(
                                            linhas_titulo[0]
                                        ),
                                        border=0,
                                        align=alinhamento,
                                    )
                                else:
                                    pdf.set_xy(
                                        x_atual,
                                        y_header + 1,
                                    )

                                    for linha_header in linhas_titulo:
                                        pdf.cell(
                                            largura,
                                            4,
                                            to_latin(
                                                linha_header
                                            ),
                                            border=0,
                                            align=alinhamento,
                                            ln=True,
                                        )
                                        pdf.set_x(
                                            x_atual
                                        )

                                x_atual += largura

                            pdf.set_xy(
                                x_header,
                                y_header
                                + altura_header,
                            )
                            pdf.set_text_color(
                                0,
                                0,
                                0,
                            )
                            pdf.set_font(
                                "Arial",
                                "",
                                7.2,
                            )

                            for _, row in df_obra.iterrows():
                                valores = [
                                    (
                                        str(row["Data"]),
                                        16,
                                        "C",
                                    ),
                                    (
                                        str(
                                            row["Colaborador"]
                                        )[:20],
                                        37,
                                        "L",
                                    ),
                                    (
                                        str(
                                            row["Função"]
                                        )[:13],
                                        24,
                                        "L",
                                    ),
                                    (
                                        str(
                                            row["Engenheiro"]
                                        )[:10],
                                        20,
                                        "C",
                                    ),
                                    (
                                        str(
                                            row["Status"]
                                        )[:11],
                                        22,
                                        "C",
                                    ),
                                    (
                                        str(
                                            row.get(
                                                "Tipo",
                                                "",
                                            )
                                        )[:8],
                                        15,
                                        "C",
                                    ),
                                    (
                                        formatar_reais(
                                            float(
                                                row[
                                                    "Custo c/ encargos (R$)"
                                                ]
                                            )
                                        ),
                                        25,
                                        "C",
                                    ),
                                    (
                                        formatar_reais(
                                            float(
                                                row[
                                                    "Extra (R$)"
                                                ]
                                            )
                                        ),
                                        16,
                                        "C",
                                    ),
                                    (
                                        formatar_reais(
                                            float(
                                                row[
                                                    "Adicional noturno (R$)"
                                                ]
                                            )
                                        ),
                                        18,
                                        "C",
                                    ),
                                    (
                                        formatar_reais(
                                            float(
                                                row[
                                                    "Acordos / Bonificações (R$)"
                                                ]
                                            )
                                        ),
                                        23,
                                        "C",
                                    ),
                                    (
                                        formatar_reais(
                                            float(
                                                row[
                                                    "Custo (R$)"
                                                ]
                                            )
                                        ),
                                        20,
                                        "C",
                                    ),
                                    (
                                        str(
                                            row.get(
                                                "Observação",
                                                "",
                                            )
                                        )[:13],
                                        21,
                                        "L",
                                    ),
                                ]

                                for idx, (
                                    valor,
                                    largura,
                                    alinhamento,
                                ) in enumerate(valores):
                                    pdf.cell(
                                        largura,
                                        6,
                                        to_latin(valor),
                                        border=1,
                                        align=alinhamento,
                                        ln=(
                                            idx
                                            == len(valores) - 1
                                        ),
                                    )

                            total_obra = float(
                                df_obra[
                                    "Custo (R$)"
                                ].sum()
                            )

                            pdf.set_font(
                                "Arial",
                                "B",
                                9,
                            )
                            pdf.cell(
                                257,
                                7,
                                to_latin("TOTAL DA OBRA:"),
                                border=0,
                                align="R",
                            )
                            pdf.cell(
                                20,
                                7,
                                to_latin(
                                    formatar_reais(
                                        total_obra
                                    )
                                ),
                                border=1,
                                align="C",
                                ln=True,
                            )

                        pdf_output = (
                            pdf.output(dest="S")
                            .encode("latin1")
                        )

                        st.download_button(
                            label="📥 Baixar PDF Gerado",
                            data=pdf_output,
                            file_name=(
                                f"relatorio_controladoria_"
                                f"{data_inicio_rel.strftime('%d-%m-%Y')}"
                                f"_a_"
                                f"{data_fim_rel.strftime('%d-%m-%Y')}.pdf"
                            ),
                            mime="application/pdf",
                        )

                except Exception as e:
                    exibir_erro_amigavel(
                        "relatorios",
                        "gerar_pdf",
                        e,
                        "Não foi possível gerar o PDF.",
                    )

        with col_btn2:
            if st.button(
                "Gerar Excel",
                use_container_width=True,
                key="rel_gerar_excel_v42",
            ):
                try:
                    if data_inicio_rel > data_fim_rel:
                        st.error(
                            "Data inicial maior que a final."
                        )
                    elif not linhas_relatorio:
                        st.warning(
                            "Sem dados no período."
                        )
                    else:
                        df_excel = pd.DataFrame(
                            linhas_relatorio
                        )

                        cores_engenheiros = {
                            "VICTOR": "E0F2FE",
                            "EDUARDO": "DCFCE7",
                            "JOEL": "F3E8FF",
                            "NETO": "FFEDD5",
                            "SOARES": "FFE4E6",
                            "GABRIEL": "CCFBF1",
                            "PAULO": "F1F5F9",
                            "HELENA": "DBEAFE",
                        }

                        wb = openpyxl.Workbook()
                        wb.remove(wb.active)

                        font_titulo = Font(
                            name="Arial",
                            size=9,
                            bold=True,
                            color="FFFFFF",
                        )
                        fill_cabecalho = PatternFill(
                            start_color="1E293B",
                            end_color="1E293B",
                            fill_type="solid",
                        )
                        font_obra_hdr = Font(
                            name="Arial",
                            size=10,
                            bold=True,
                            color="1E293B",
                        )
                        fill_obra_hdr = PatternFill(
                            start_color="FFF2CC",
                            end_color="FFF2CC",
                            fill_type="solid",
                        )
                        borda_fina = Border(
                            left=Side(
                                style="thin",
                                color="CBD5E1",
                            ),
                            right=Side(
                                style="thin",
                                color="CBD5E1",
                            ),
                            top=Side(
                                style="thin",
                                color="CBD5E1",
                            ),
                            bottom=Side(
                                style="thin",
                                color="CBD5E1",
                            ),
                        )

                        periodo_rotulo_excel = (
                            f"{data_inicio_rel.strftime('%d/%m/%Y')} "
                            f"a {data_fim_rel.strftime('%d/%m/%Y')} "
                            f"({periodicidade})"
                        )

                        for data_str in sorted(
                            df_excel["Data"].unique()
                        ):
                            df_dia = df_excel[
                                df_excel["Data"] == data_str
                            ]

                            titulo_aba = str(data_str)[-31:]
                            ws = wb.create_sheet(
                                title=titulo_aba
                            )

                            current_row = 1

                            ws.cell(
                                row=current_row,
                                column=1,
                                value=(
                                    "APONTAMENTO DIÁRIO DE EQUIPES "
                                    f"- DATA: {data_str}"
                                ),
                            ).font = Font(
                                name="Arial",
                                size=12,
                                bold=True,
                            )
                            current_row += 2

                            grupos = df_dia.groupby(
                                ["Obra", "Unidade"],
                                dropna=False,
                                sort=True,
                            )

                            for (
                                obra_nome,
                                unidade_nome,
                            ), df_obra in grupos:

                                # Apenas um cabeçalho da obra para todos os colaboradores.
                                ws.cell(
                                    row=current_row,
                                    column=1,
                                    value=(
                                        f"UNIDADE: {unidade_nome}  |  "
                                        f"OBRA: {obra_nome}  |  "
                                        f"PERÍODO: {periodo_rotulo_excel}"
                                    ),
                                ).font = font_obra_hdr

                                for c_idx in range(1, 12):
                                    ws.cell(
                                        row=current_row,
                                        column=c_idx,
                                    ).fill = fill_obra_hdr

                                current_row += 1

                                colunas_tabela = [
                                    "Colaborador",
                                    "Função",
                                    "Engenheiro Resp.",
                                    "Status",
                                    "Tipo",
                                    "Custo c/ Encargos (R$)",
                                    "Extra (R$)",
                                    "Adicional Noturno (R$)",
                                    "Acordos / Bonificações (R$)",
                                    "Total (R$)",
                                    "Observação",
                                ]

                                for c_idx, col_nome in enumerate(
                                    colunas_tabela,
                                    1,
                                ):
                                    cell = ws.cell(
                                        row=current_row,
                                        column=c_idx,
                                        value=col_nome,
                                    )
                                    cell.font = font_titulo
                                    cell.fill = fill_cabecalho
                                    cell.alignment = Alignment(
                                        horizontal="center",
                                        vertical="center",
                                    )

                                current_row += 1
                                inicio_dados_obra = current_row

                                df_obra = df_obra.sort_values(
                                    [
                                        "Colaborador",
                                        "Período do serviço",
                                    ]
                                )

                                for _, r in df_obra.iterrows():
                                    eng_resp = r["Engenheiro"]
                                    eng_cor_chave = str(
                                        eng_resp
                                    ).split(" / ")[0].upper()

                                    cor_hex = cores_engenheiros.get(
                                        eng_cor_chave,
                                        "FFFFFF",
                                    )

                                    fill_engenheiro = PatternFill(
                                        start_color=cor_hex,
                                        end_color=cor_hex,
                                        fill_type="solid",
                                    )

                                    celula_custo_formula = (
                                        f"=F{current_row}+G{current_row}+H{current_row}+I{current_row}"
                                    )

                                    linha_dados = [
                                        r["Colaborador"],
                                        r["Função"],
                                        r["Engenheiro"],
                                        r["Status"],
                                        r.get("Tipo", ""),
                                        float(r["Custo c/ encargos (R$)"]),
                                        float(r["Extra (R$)"]),
                                        float(r.get("Adicional noturno (R$)") or 0.0),
                                        float(r["Acordos / Bonificações (R$)"]),
                                        celula_custo_formula,
                                        r["Observação"],
                                    ]

                                    for c_idx, val in enumerate(
                                        linha_dados,
                                        1,
                                    ):
                                        c_cell = ws.cell(
                                            row=current_row,
                                            column=c_idx,
                                            value=val,
                                        )
                                        c_cell.font = Font(
                                            name="Arial",
                                            size=9,
                                        )
                                        c_cell.border = borda_fina
                                        c_cell.fill = fill_engenheiro

                                        if c_idx in [6, 7, 8, 9, 10]:
                                            c_cell.number_format = (
                                                'R$ #,##0.00'
                                            )
                                            c_cell.alignment = Alignment(
                                                horizontal="right"
                                            )
                                        elif c_idx in [3, 4, 5]:
                                            c_cell.alignment = Alignment(
                                                horizontal="center"
                                            )

                                    current_row += 1

                                fim_dados_obra = (
                                    current_row - 1
                                )

                                ws.cell(
                                    row=current_row,
                                    column=9,
                                    value="TOTAL DA OBRA:",
                                ).font = Font(
                                    name="Arial",
                                    size=10,
                                    bold=True,
                                )
                                ws.cell(
                                    row=current_row,
                                    column=9,
                                ).alignment = Alignment(
                                    horizontal="right"
                                )

                                celula_subtotal = ws.cell(
                                    row=current_row,
                                    column=10,
                                    value=(
                                        f"=SUM(J{inicio_dados_obra}:"
                                        f"J{fim_dados_obra})"
                                    ),
                                )
                                celula_subtotal.font = Font(
                                    name="Arial",
                                    size=10,
                                    bold=True,
                                )
                                celula_subtotal.number_format = (
                                    'R$ #,##0.00'
                                )
                                celula_subtotal.border = borda_fina

                                current_row += 2

                            for col in ws.columns:
                                max_len = 0
                                col_letter = (
                                    openpyxl.utils
                                    .get_column_letter(
                                        col[0].column
                                    )
                                )

                                for cell in col:
                                    if cell.value:
                                        val_str = str(
                                            cell.value
                                        )
                                        max_len = max(
                                            max_len,
                                            len(val_str),
                                        )

                                ws.column_dimensions[
                                    col_letter
                                ].width = min(
                                    max(max_len + 3, 13),
                                    38,
                                )

                            ws.freeze_panes = "A4"

                        buffer = io.BytesIO()
                        wb.save(buffer)

                        st.download_button(
                            label=(
                                "📥 Baixar Excel "
                                "(rateado por serviço)"
                            ),
                            data=buffer.getvalue(),
                            file_name=(
                                f"controladoria_rateada_"
                                f"{data_inicio_rel.strftime('%d-%m-%Y')}"
                                f"_a_"
                                f"{data_fim_rel.strftime('%d-%m-%Y')}.xlsx"
                            ),
                            mime=(
                                "application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet"
                            ),
                        )

                except Exception as e:
                    exibir_erro_amigavel(
                        "relatorios",
                        "gerar_excel",
                        e,
                        "Não foi possível gerar o Excel.",
                    )

    # --- 5. INDICADORES ---
    elif menu_escolhido == "📈 INDICADORES":
        render_indicadores_cumprimento("admin_ind_melhorias", None, mostrar_absenteismo=True)

    # --- INDISPONIBILIDADE ---
    elif menu_escolhido == "🚫 INDISPONIBILIDADE":
        render_indisponibilidades_admin()

    # --- 6. DISPONIBILIDADE ---
    elif str(menu_escolhido).strip().upper() in {
        "👥 DISPONIBILIDADE",
        "DISPONIBILIDADE",
        "👥 DISPONIBILIDADE DA EQUIPE",
    }:
        render_aba_disponibilidade("admin")

    # --- 7. CONFIGURAÇÕES E SINCRONIZAÇÃO TRELLO ---
    elif menu_escolhido == "⚙️ CONFIGURAÇÕES":
        cabecalho_pagina_aproar(
            "Configurações",
            "Cadastros, sincronização, auditoria e manutenção da plataforma.",
            categoria="SISTEMA",
        )
        with st.expander("🩺 Diagnóstico e saúde do sistema", expanded=False):
            render_diagnostico_sistema()

        if DB_BACKEND == "NEON":
            if schema_producao_disponivel():
                st.success("🟢 Estrutura de produção ativa: auditoria, conflitos, indisponibilidades e apontamentos estruturados.")
            else:
                st.warning(
                    "🟡 Estrutura de produção ainda não foi aplicada no Neon. "
                    "O sistema continua em compatibilidade legada até a migração SQL ser executada."
                )

        with st.expander("🧾 Histórico de auditoria", expanded=False):
            render_historico_auditoria()
        
        # Sincronização Dinâmica Trello (mês vigente, lista manual ou busca de card/lista)
        with st.container(border=True):
            st.markdown("**Sincronização com o Trello**")
            st.write("Sincronize o mês vigente ou localize manualmente listas e cards de medições anteriores.")

            lists_trello, cards_trello = obter_listas_trello()
            mapa_nome_lista = {l.get('id'): l.get('name', 'Lista sem nome') for l in lists_trello}

            if st.session_state.get("trello_usando_snapshot"):
                st.info(
                    "ℹ️ O Trello está demorando a responder. "
                    "Estou usando a última leitura válida salva para manter o sistema operacional."
                )

            c_tr1, c_tr2 = st.columns(2)
            with c_tr1:
                if st.button("🚀 SINCRONIZAR MÊS VIGENTE (AUTOMÁTICO)", type="primary"):
                    with st.spinner("Sincronizando mês vigente..."):
                        sucesso, me = executar_sincronizacao_trello(listas_precarregadas=lists_trello, cards_precarregados=cards_trello)
                        if sucesso:
                            st.success(me)
                            st.rerun()
                        else:
                            st.error(me)

            with c_tr2:
                listas_abertas = [l for l in lists_trello if not l.get('closed', False)]
                if listas_abertas:
                    mapa_listas = {l['name']: l['id'] for l in listas_abertas}
                    lista_manual_sel = st.selectbox("Selecionar lista diretamente:", list(mapa_listas.keys()), key="sel_trello_manual")
                    if st.button("🔄 SINCRONIZAR LISTA SELECIONADA"):
                        id_sel = mapa_listas[lista_manual_sel]
                        with st.spinner(f"Sincronizando {lista_manual_sel}..."):
                            sucesso, me = executar_sincronizacao_trello(id_lista_target=id_sel, listas_precarregadas=lists_trello, cards_precarregados=cards_trello)
                            if sucesso:
                                st.success(me)
                                st.rerun()
                            else:
                                st.error(me)
                else:
                    st.warning(
                        "Trello temporariamente indisponível e ainda não há uma leitura anterior salva. "
                        "As obras já cadastradas continuam disponíveis normalmente."
                    )
                    detalhe_trello = st.session_state.get("trello_ultimo_erro", "")
                    st.caption("Quadro público • sem API Key ou Token.")
                    if detalhe_trello:
                        with st.expander("Diagnóstico técnico"):
                            st.code(detalhe_trello)

            st.markdown("#### 🔎 Busca manual para medições retroativas")
            termo_trello = st.text_input(
                "Buscar card ou lista por nome:",
                placeholder="Ex.: MEDIÇÃO JUNHO 2026, APRL005, MARACANAÚ...",
                key="busca_trello_retroativa"
            )

            if termo_trello.strip():
                termo_norm = normalizar(termo_trello)
                resultados = {}

                for lst in lists_trello:
                    if termo_norm in normalizar(lst.get('name', '')):
                        rotulo = f"📋 LISTA | {lst.get('name', 'Sem nome')}"
                        resultados[rotulo] = ("lista", lst.get('id'))

                for card in cards_trello:
                    if termo_norm in normalizar(card.get('name', '')):
                        nome_lista = mapa_nome_lista.get(card.get('idList'), 'Lista não identificada')
                        situacao = "arquivado" if card.get('closed', False) else "ativo"
                        rotulo = f"🗂️ CARD | {card.get('name', 'Sem nome')} | {nome_lista} | {situacao} | {str(card.get('id',''))[-6:]}"
                        resultados[rotulo] = ("card", card.get('id'))

                if resultados:
                    resultado_sel = st.selectbox("Resultados encontrados:", list(resultados.keys()), key="resultado_busca_trello")
                    tipo_resultado, id_resultado = resultados[resultado_sel]
                    if st.button("➕ SINCRONIZAR RESULTADO DA BUSCA", type="primary", use_container_width=True):
                        with st.spinner("Sincronizando resultado selecionado..."):
                            if tipo_resultado == "lista":
                                sucesso, me = executar_sincronizacao_trello(id_lista_target=id_resultado, listas_precarregadas=lists_trello, cards_precarregados=cards_trello)
                            else:
                                sucesso, me = executar_sincronizacao_trello(id_card_target=id_resultado, listas_precarregadas=lists_trello, cards_precarregados=cards_trello)
                            if sucesso:
                                st.success(me)
                                st.rerun()
                            else:
                                st.error(me)
                else:
                    st.info("Nenhum card ou lista encontrado para esse termo.")

        st.markdown("---")
        tab_cad_obra, tab_cad_colab, tab_import_colab, tab_teams, tab_limpeza = st.tabs([
            "🏗️ Obras",
            "👷 Colaboradores",
            "📤 Importar Colaboradores",
            "💬 Cobranças Teams",
            "🗑️ Limpeza de Dados",
        ])
        
        with tab_cad_obra:
            st.markdown("**Cadastrar nova obra**")
            st.caption(
                "O mesmo nome pode existir em unidades diferentes. "
                "Nome + unidade iguais não serão duplicados."
            )

            if st.session_state.get("msg_cadastro_obra_admin"):
                st.success(
                    st.session_state.pop(
                        "msg_cadastro_obra_admin"
                    )
                )

            with st.form("form_cad_obra"):
                nome_obra = st.text_input(
                    "Nome da Obra (Ex: 1863, 1383...):"
                )
                unidade_obra = st.text_input(
                    "Unidade (Ex: CENTRO, MUSEU, FIEC...):"
                )
                submit_obra = st.form_submit_button(
                    "Cadastrar Obra"
                )

                if submit_obra:
                    nome_obra_limpo = " ".join(
                        str(nome_obra or "").strip().split()
                    ).upper()
                    unidade_obra_limpa = " ".join(
                        str(unidade_obra or "").strip().split()
                    ).upper()

                    if (
                        not nome_obra_limpo
                        or not unidade_obra_limpa
                    ):
                        st.warning(
                            "Preencha nome e unidade."
                        )

                    else:
                        duplicada = next(
                            (
                                o for o in buscar_obras()
                                if normalizar(
                                    o.get("nome")
                                )
                                == normalizar(nome_obra_limpo)
                                and normalizar(
                                    o.get("unidade")
                                )
                                == normalizar(
                                    unidade_obra_limpa
                                )
                            ),
                            None,
                        )

                        if duplicada:
                            st.info(
                                "Essa obra já está cadastrada "
                                "nessa unidade."
                            )

                        else:
                            try:
                                retorno_obra = (
                                    supabase.table("obras")
                                    .insert({
                                        "nome": nome_obra_limpo,
                                        "unidade": unidade_obra_limpa,
                                    })
                                    .execute()
                                    .data
                                    or []
                                )

                                limpar_cache_operacional()

                                registrar_auditoria_prod(
                                    "obra",
                                    (
                                        retorno_obra[0].get("id")
                                        if retorno_obra
                                        else ""
                                    ),
                                    "CRIAR",
                                    "ADMIN",
                                    depois={
                                        "nome": nome_obra_limpo,
                                        "unidade": unidade_obra_limpa,
                                    },
                                )

                                st.session_state[
                                    "msg_cadastro_obra_admin"
                                ] = (
                                    f"Obra {nome_obra_limpo} cadastrada "
                                    f"em {unidade_obra_limpa}."
                                )
                                st.rerun()

                            except Exception as e:
                                # Nunca abre traceback vermelho para o usuário.
                                exibir_erro_amigavel(
                                    "obras",
                                    "cadastrar_obra",
                                    e,
                                    (
                                        "Não foi possível cadastrar a obra. "
                                        "Se ela já existir, confira nome e unidade."
                                    ),
                                )

        with tab_cad_colab:
            MORADIAS_COLAB = [
                "Fortaleza",
                "Maracanaú",
                "Caucaia",
                "Horizonte",
            ]

            st.markdown("**Banco de funcionários**")
            st.caption(
                "Cadastre, consulte, edite ou retire colaboradores da base operacional. "
                "Ao excluir, o cadastro fica inativo para preservar o histórico de apontamentos."
            )

            if st.session_state.get(
                "msg_banco_funcionarios"
            ):
                st.success(
                    st.session_state.pop(
                        "msg_banco_funcionarios"
                    )
                )

            # ------------------------------------------------------------
            # NOVO CADASTRO
            # ------------------------------------------------------------
            with st.expander(
                "Cadastrar novo funcionário",
                expanded=False,
            ):
                with st.form(
                    "form_banco_novo_funcionario"
                ):
                    nome_colab = st.text_input(
                        "Nome completo"
                    )
                    funcao_colab = st.text_input(
                        "Função"
                    )

                    c_valor, c_moradia = st.columns(2)

                    with c_valor:
                        valor_colab = st.number_input(
                            "Custo diário c/ encargos (R$)",
                            min_value=0.01,
                            value=float(
                                VALOR_DIARIA_PROFISSIONAL
                            ),
                            step=0.01,
                            format="%.2f",
                        )

                    with c_moradia:
                        moradia_colab = st.selectbox(
                            "Local de moradia",
                            MORADIAS_COLAB,
                        )

                    submit_colab = (
                        st.form_submit_button(
                            "Cadastrar funcionário",
                            type="primary",
                            use_container_width=True,
                        )
                    )

                    if submit_colab:
                        nome_novo = " ".join(
                            str(
                                nome_colab
                                or ""
                            ).strip().split()
                        ).upper()

                        funcao_nova = limpar_funcao(
                            funcao_colab
                        )

                        if not nome_novo:
                            st.warning(
                                "Informe o nome do funcionário."
                            )

                        elif not str(
                            funcao_colab
                            or ""
                        ).strip():
                            st.warning(
                                "Informe a função do funcionário."
                            )

                        else:
                            atuais_banco = (
                                buscar_colaboradores_todos()
                                or []
                            )

                            existente = next(
                                (
                                    c
                                    for c in atuais_banco
                                    if normalizar(
                                        c.get("nome")
                                    )
                                    == normalizar(nome_novo)
                                ),
                                None,
                            )

                            payload_novo = {
                                "nome": nome_novo,
                                "funcao": funcao_nova,
                                "valor_diaria": float(
                                    valor_colab
                                ),
                                "categoria_diaria": inferir_tipo_colaborador(
                                    funcao_nova,
                                    valor_colab,
                                ),
                                "local_moradia": moradia_colab,
                                "ativo": True,
                            }

                            try:
                                if existente:
                                    (
                                        supabase.table(
                                            "colaboradores"
                                        )
                                        .update(payload_novo)
                                        .eq(
                                            "id",
                                            existente.get("id"),
                                        )
                                        .execute()
                                    )
                                    mensagem = (
                                        f"{nome_novo} já existia e "
                                        "foi atualizado/reativado."
                                    )
                                    acao_audit = "REATIVAR_ATUALIZAR"
                                    entidade_id = existente.get(
                                        "id"
                                    )
                                else:
                                    retorno = (
                                        supabase.table(
                                            "colaboradores"
                                        )
                                        .insert(payload_novo)
                                        .execute()
                                        .data
                                        or []
                                    )
                                    mensagem = (
                                        f"{nome_novo} cadastrado "
                                        "com sucesso."
                                    )
                                    acao_audit = "CRIAR"
                                    entidade_id = (
                                        retorno[0].get("id")
                                        if retorno
                                        else ""
                                    )

                                limpar_cache_operacional()

                                registrar_auditoria_prod(
                                    "colaboradores",
                                    entidade_id,
                                    acao_audit,
                                    "ADMIN",
                                    depois=payload_novo,
                                )

                                st.session_state[
                                    "msg_banco_funcionarios"
                                ] = mensagem
                                st.rerun()

                            except Exception as e:
                                exibir_erro_amigavel(
                                    "colaboradores",
                                    "cadastrar_funcionario",
                                    e,
                                    "Não foi possível salvar o funcionário.",
                                )

            # ------------------------------------------------------------
            # BASE ATIVA
            # ------------------------------------------------------------
            base_admin = (
                buscar_colaboradores_todos()
                or []
            )
            ativos_admin = [
                c
                for c in base_admin
                if c.get("ativo", True) is not False
            ]
            inativos_admin = [
                c
                for c in base_admin
                if c.get("ativo", True) is False
            ]

            st.markdown("**Funcionários ativos**")

            cf1, cf2 = st.columns(
                [1.5, .8]
            )

            with cf1:
                busca_funcionario = st.text_input(
                    "Buscar",
                    placeholder="Nome ou função...",
                    key="busca_banco_funcionarios",
                )

            with cf2:
                filtro_moradia = st.selectbox(
                    "Moradia",
                    ["Todas"] + MORADIAS_COLAB,
                    key="filtro_moradia_banco",
                )

            ativos_filtrados = []

            for colab in ativos_admin:
                atende_busca = (
                    not busca_funcionario.strip()
                    or normalizar(
                        busca_funcionario
                    )
                    in normalizar(
                        f"{colab.get('nome','')} "
                        f"{colab.get('funcao','')}"
                    )
                )

                atende_moradia = (
                    filtro_moradia == "Todas"
                    or normalizar(
                        colab.get(
                            "local_moradia"
                        )
                        or ""
                    )
                    == normalizar(
                        filtro_moradia
                    )
                )

                if (
                    atende_busca
                    and atende_moradia
                ):
                    ativos_filtrados.append(
                        colab
                    )

            if ativos_filtrados:
                st.html("""
                <style>
                /* ======================================================
                   BANCO DE FUNCIONÁRIOS — GRADE COMPACTA / ALINHADA
                   ====================================================== */

                div[class*="st-key-func_inline_header"]{
                    background:transparent !important;
                    border:none !important;
                    border-bottom:1px solid #DDE4ED !important;
                    border-radius:0 !important;
                    padding:7px 8px 8px !important;
                    margin:4px 0 4px !important;
                }

                div[class*="st-key-func_inline_header"] [data-testid="stHorizontalBlock"],
                div[class*="st-key-func_inline_row_"] [data-testid="stHorizontalBlock"]{
                    align-items:center !important;
                    gap:.35rem !important;
                }

                .func-head-label{
                    color:#6B7890;
                    font-size:8.5px;
                    line-height:1;
                    font-weight:800;
                    text-transform:uppercase;
                    letter-spacing:.04em;
                    white-space:nowrap;
                }

                div[class*="st-key-func_inline_row_"]{
                    background:#FFFFFF !important;
                    border:1px solid #E3E8EF !important;
                    border-radius:8px !important;
                    padding:4px 8px !important;
                    margin:0 0 5px !important;
                    box-shadow:none !important;
                }

                div[class*="st-key-func_inline_row_"]:hover{
                    background:#FBFCFE !important;
                    border-color:#D5DDE8 !important;
                }

                .func-inline-text{
                    height:34px;
                    display:flex;
                    align-items:center;
                    min-width:0;
                    overflow:hidden;
                    white-space:nowrap;
                    text-overflow:ellipsis;
                    color:#27364D;
                    font-size:10.5px;
                    line-height:1.15;
                }

                .func-inline-name{
                    font-weight:700;
                    color:#172235;
                }

                .func-inline-value{
                    font-weight:700;
                    color:#334155;
                }

                div[class*="st-key-func_inline_row_"] div[data-baseweb="select"] > div{
                    min-height:34px !important;
                    height:34px !important;
                    border-radius:7px !important;
                    border-color:#DCE3EC !important;
                    background:#FFFFFF !important;
                    font-size:10.5px !important;
                    box-shadow:none !important;
                }

                div[class*="st-key-func_inline_row_"] div[data-baseweb="select"] span{
                    font-size:10.5px !important;
                }

                div[class*="st-key-btn_inline_excluir_func_"]{
                    display:flex !important;
                    justify-content:center !important;
                    align-items:center !important;
                    width:100% !important;
                    min-width:36px !important;
                    overflow:visible !important;
                }

                div[class*="st-key-btn_inline_excluir_func_"] button{
                    width:32px !important;
                    min-width:32px !important;
                    height:32px !important;
                    min-height:32px !important;
                    padding:0 !important;
                    border-radius:50% !important;
                    background:#FFF2F3 !important;
                    border:1px solid #F5C2C7 !important;
                    color:#D92D20 !important;
                    font-size:15px !important;
                    line-height:1 !important;
                    box-shadow:none !important;
                }

                div[class*="st-key-btn_inline_excluir_func_"] button:hover{
                    background:#FFE4E6 !important;
                    border-color:#F28B95 !important;
                    transform:none !important;
                }

                div[class*="st-key-btn_inline_excluir_func_"] button *{
                    color:#D92D20 !important;
                    -webkit-text-fill-color:#D92D20 !important;
                }

                .func-bank-note{
                    display:flex;
                    align-items:center;
                    gap:7px;
                    margin:4px 0 8px;
                    color:#8491A5;
                    font-size:10px;
                }

                .func-pager-label{
                    height:32px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#56647A;
                    font-size:10px;
                    font-weight:700;
                    white-space:nowrap;
                }

                div[class*="st-key-func_pager_prev"] button,
                div[class*="st-key-func_pager_next"] button{
                    width:32px !important;
                    min-width:32px !important;
                    height:32px !important;
                    min-height:32px !important;
                    padding:0 !important;
                    border-radius:8px !important;
                    background:#FFFFFF !important;
                    border:1px solid #D8E0EA !important;
                    color:#334155 !important;
                    font-size:16px !important;
                    font-weight:800 !important;
                    box-shadow:none !important;
                }

                div[class*="st-key-func_pager_prev"] button:hover,
                div[class*="st-key-func_pager_next"] button:hover{
                    background:#F4F7FB !important;
                    border-color:#C7D2E0 !important;
                }

                div[class*="st-key-func_pager_prev"] button:disabled,
                div[class*="st-key-func_pager_next"] button:disabled{
                    opacity:.35 !important;
                    cursor:default !important;
                }

                div[class*="st-key-btn_salvar_moradias_lote"] button{
                    min-height:38px !important;
                    border-radius:8px !important;
                    background:#2F64E8 !important;
                    border-color:#2F64E8 !important;
                    color:#FFFFFF !important;
                    font-size:10.5px !important;
                    font-weight:750 !important;
                    box-shadow:none !important;
                }

                div[class*="st-key-btn_salvar_moradias_lote"] button *{
                    color:#FFFFFF !important;
                    -webkit-text-fill-color:#FFFFFF !important;
                }

                div[class*="st-key-btn_salvar_moradias_lote"] button:disabled{
                    background:#D9E1EC !important;
                    border-color:#D9E1EC !important;
                    color:#8D99AA !important;
                    opacity:1 !important;
                }

                .func-pending-changes{
                    min-height:38px;
                    display:flex;
                    align-items:center;
                    color:#6B7890;
                    font-size:10px;
                    font-weight:650;
                }

                .func-delete-dot{
                    display:inline-flex;
                    align-items:center;
                    justify-content:center;
                    width:17px;
                    height:17px;
                    border-radius:50%;
                    background:#FFE4E6;
                    color:#D92D20;
                    font-size:10px;
                    font-weight:800;
                }

                @media(max-width:900px){
                    div[class*="st-key-func_inline_header"]{
                        display:none !important;
                    }

                    div[class*="st-key-func_inline_row_"]{
                        border:1px solid #E1E7EF !important;
                        border-radius:9px !important;
                        margin-bottom:6px !important;
                        padding:6px !important;
                    }

                    .func-inline-text{
                        font-size:9.8px !important;
                    }

                    .func-pager-label{
                        font-size:9px !important;
                    }
                }
                </style>
                """)

                st.markdown(
                    """
                    <div class="func-bank-note">
                        <span>Escolha as moradias que quiser e clique em <b>Salvar alterações</b>.</span>
                        <span class="func-delete-dot">−</span>
                        <span>retira o funcionário sem apagar o histórico.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Fragmento = excluir/trocar moradia não reroda Configurações inteira.
                _decorador_fragmento_func = getattr(
                    st,
                    "fragment",
                    lambda func: func,
                )

                @_decorador_fragmento_func
                def _render_banco_funcionarios_inline(
                    lista_filtrada,
                ):
                    mensagem_grade = st.session_state.pop(
                        "_msg_grade_funcionarios",
                        None,
                    )
                    if mensagem_grade:
                        tipo_msg = mensagem_grade.get("tipo")
                        texto_msg = mensagem_grade.get("texto", "")

                        if tipo_msg == "erro":
                            st.error(
                                texto_msg,
                                icon="⚠️",
                            )
                        elif tipo_msg == "sucesso":
                            st.caption(
                                f"✓ {texto_msg}"
                            )
                    # IDs removidos na sessão somem imediatamente da grade,
                    # mesmo antes de qualquer rerun completo da página.
                    excluidos_sessao = set(
                        st.session_state.get(
                            "_func_inline_excluidos",
                            [],
                        )
                    )

                    lista_visivel = [
                        c
                        for c in lista_filtrada
                        if str(c.get("id"))
                        not in excluidos_sessao
                    ]

                    ativos_ordenados = sorted(
                        lista_visivel,
                        key=lambda x: normalizar(
                            x.get("nome")
                        ),
                    )

                    # Menos widgets simultâneos = resposta muito mais rápida.
                    TAMANHO_PAGINA_FUNC = 12

                    total_paginas_func = max(
                        1,
                        (
                            len(ativos_ordenados)
                            + TAMANHO_PAGINA_FUNC
                            - 1
                        )
                        // TAMANHO_PAGINA_FUNC,
                    )

                    # Página controlada por estado + setas.
                    pagina_state_key = "_pagina_banco_funcionarios"

                    if pagina_state_key not in st.session_state:
                        st.session_state[pagina_state_key] = 1

                    pagina_func = int(
                        st.session_state.get(
                            pagina_state_key,
                            1,
                        )
                    )

                    # Corrige automaticamente após exclusões/filtros.
                    pagina_func = max(
                        1,
                        min(
                            pagina_func,
                            total_paginas_func,
                        ),
                    )
                    st.session_state[
                        pagina_state_key
                    ] = pagina_func

                    c_info_func, c_pager_func = st.columns(
                        [5.2, 1.25],
                        vertical_alignment="center",
                    )

                    with c_info_func:
                        st.caption(
                            f"{len(ativos_ordenados)} funcionário(s) encontrado(s)"
                        )

                    with c_pager_func:
                        p_prev, p_num, p_next = st.columns(
                            [.7, 1.7, .7],
                            vertical_alignment="center",
                        )

                        def _pagina_anterior_func():
                            atual = int(
                                st.session_state.get(
                                    pagina_state_key,
                                    1,
                                )
                            )
                            st.session_state[
                                pagina_state_key
                            ] = max(
                                1,
                                atual - 1,
                            )

                        with p_prev:
                            st.button(
                                "‹",
                                disabled=(
                                    pagina_func <= 1
                                ),
                                key="func_pager_prev",
                                help="Página anterior",
                                on_click=_pagina_anterior_func,
                            )

                        with p_num:
                            st.markdown(
                                (
                                    '<div class="func-pager-label">'
                                    f'{pagina_func} / {total_paginas_func}'
                                    '</div>'
                                ),
                                unsafe_allow_html=True,
                            )

                        def _proxima_pagina_func():
                            atual = int(
                                st.session_state.get(
                                    pagina_state_key,
                                    1,
                                )
                            )
                            st.session_state[
                                pagina_state_key
                            ] = min(
                                total_paginas_func,
                                atual + 1,
                            )

                        with p_next:
                            st.button(
                                "›",
                                disabled=(
                                    pagina_func
                                    >= total_paginas_func
                                ),
                                key="func_pager_next",
                                help="Próxima página",
                                on_click=_proxima_pagina_func,
                            )

                    inicio_func = (
                        (pagina_func - 1)
                        * TAMANHO_PAGINA_FUNC
                    )
                    fim_func = (
                        inicio_func
                        + TAMANHO_PAGINA_FUNC
                    )

                    ativos_pagina = ativos_ordenados[
                        inicio_func:fim_func
                    ]

                    # Cabeçalho usa o MESMO sistema de colunas das linhas.
                    with st.container(
                        key="func_inline_header"
                    ):
                        h_nome, h_funcao, h_valor, h_moradia, h_excluir = st.columns(
                            [3.35, 2.25, 1.4, 1.65, .36],
                            vertical_alignment="center",
                        )

                        with h_nome:
                            st.markdown(
                                '<div class="func-head-label">Nome</div>',
                                unsafe_allow_html=True,
                            )
                        with h_funcao:
                            st.markdown(
                                '<div class="func-head-label">Função</div>',
                                unsafe_allow_html=True,
                            )
                        with h_valor:
                            st.markdown(
                                '<div class="func-head-label">Valor / custo</div>',
                                unsafe_allow_html=True,
                            )
                        with h_moradia:
                            st.markdown(
                                '<div class="func-head-label">Moradia</div>',
                                unsafe_allow_html=True,
                            )
                        with h_excluir:
                            st.markdown(
                                '<div class="func-head-label"></div>',
                                unsafe_allow_html=True,
                            )

                    opcoes_moradia_inline = [
                        "Não informado",
                        *MORADIAS_COLAB,
                    ]

                    # Baseline da sessão: após salvar em lote, não dependemos
                    # de um rerun completo para saber o valor já persistido.
                    baseline_key = "_moradia_baseline_funcionarios"
                    baseline_moradias = st.session_state.setdefault(
                        baseline_key,
                        {},
                    )

                    alteracoes_moradia_pagina = {}

                    for c in ativos_pagina:
                        colab_id_inline = c.get("id")
                        nome_inline = str(
                            c.get("nome")
                            or ""
                        )
                        funcao_inline = str(
                            c.get("funcao")
                            or "-"
                        )
                        valor_inline = formatar_reais(
                            obter_valor_diaria_colaborador(
                                c
                            )
                        )

                        moradia_db = str(
                            c.get("local_moradia")
                            or ""
                        ).strip()

                        moradia_atual_inline = (
                            moradia_db
                            if moradia_db in MORADIAS_COLAB
                            else "Não informado"
                        )

                        with st.container(
                            key=(
                                "func_inline_row_"
                                f"{colab_id_inline}"
                            )
                        ):
                            (
                                r_nome,
                                r_funcao,
                                r_valor,
                                r_moradia,
                                r_excluir,
                            ) = st.columns(
                                [3.35, 2.25, 1.4, 1.65, .36],
                                vertical_alignment="center",
                            )

                            with r_nome:
                                st.markdown(
                                    (
                                        '<div class="func-inline-text '
                                        'func-inline-name" '
                                        f'title="{_html.escape(nome_inline)}">'
                                        f'{_html.escape(nome_inline)}'
                                        '</div>'
                                    ),
                                    unsafe_allow_html=True,
                                )

                            with r_funcao:
                                st.markdown(
                                    (
                                        '<div class="func-inline-text" '
                                        f'title="{_html.escape(funcao_inline)}">'
                                        f'{_html.escape(funcao_inline)}'
                                        '</div>'
                                    ),
                                    unsafe_allow_html=True,
                                )

                            with r_valor:
                                st.markdown(
                                    (
                                        '<div class="func-inline-text '
                                        'func-inline-value">'
                                        f'{_html.escape(valor_inline)}'
                                        '</div>'
                                    ),
                                    unsafe_allow_html=True,
                                )

                            with r_moradia:
                                colab_id_str = str(
                                    colab_id_inline
                                )

                                # Primeiro acesso: usa o valor do banco como base.
                                if colab_id_str not in baseline_moradias:
                                    baseline_moradias[
                                        colab_id_str
                                    ] = moradia_atual_inline

                                moradia_base_inline = (
                                    baseline_moradias.get(
                                        colab_id_str,
                                        moradia_atual_inline,
                                    )
                                )

                                idx_moradia_inline = (
                                    opcoes_moradia_inline.index(
                                        moradia_base_inline
                                    )
                                    if moradia_base_inline
                                    in opcoes_moradia_inline
                                    else 0
                                )

                                chave_moradia = (
                                    "moradia_inline_func_"
                                    f"{colab_id_inline}"
                                )

                                moradia_selecionada = st.selectbox(
                                    "Moradia",
                                    opcoes_moradia_inline,
                                    index=idx_moradia_inline,
                                    label_visibility="collapsed",
                                    key=chave_moradia,
                                )

                                if (
                                    moradia_selecionada
                                    != moradia_base_inline
                                ):
                                    alteracoes_moradia_pagina[
                                        colab_id_inline
                                    ] = {
                                        "antes": (
                                            None
                                            if moradia_base_inline
                                            == "Não informado"
                                            else moradia_base_inline
                                        ),
                                        "depois": (
                                            None
                                            if moradia_selecionada
                                            == "Não informado"
                                            else moradia_selecionada
                                        ),
                                        "depois_label": (
                                            moradia_selecionada
                                        ),
                                        "nome": nome_inline,
                                    }


                            with r_excluir:
                                def _excluir_funcionario_inline(
                                    _colab_id=colab_id_inline,
                                    _nome=nome_inline,
                                ):
                                    ok = (
                                        _atualizar_colaborador_admin_rapido(
                                            _colab_id,
                                            {
                                                "ativo": False
                                            },
                                            "DESATIVAR",
                                            antes={
                                                "ativo": True,
                                                "nome": _nome,
                                            },
                                        )
                                    )

                                    if ok:
                                        ids_excluidos = set(
                                            st.session_state.get(
                                                "_func_inline_excluidos",
                                                [],
                                            )
                                        )

                                        ids_excluidos.add(
                                            str(_colab_id)
                                        )

                                        st.session_state[
                                            "_func_inline_excluidos"
                                        ] = list(
                                            ids_excluidos
                                        )

                                        st.session_state.get(
                                            "_moradia_baseline_funcionarios",
                                            {},
                                        ).pop(
                                            str(_colab_id),
                                            None,
                                        )

                                        st.session_state.pop(
                                            (
                                                "moradia_inline_func_"
                                                f"{_colab_id}"
                                            ),
                                            None,
                                        )

                                        st.session_state[
                                            "_msg_grade_funcionarios"
                                        ] = {
                                            "tipo": "sucesso",
                                            "texto": (
                                                f"{_nome} foi retirado "
                                                "da base operacional."
                                            ),
                                        }

                                    else:
                                        st.session_state[
                                            "_msg_grade_funcionarios"
                                        ] = {
                                            "tipo": "erro",
                                            "texto": (
                                                "Não foi possível excluir "
                                                f"{_nome}. Tente novamente."
                                            ),
                                        }

                                st.button(
                                    "⛔",
                                    key=(
                                        "btn_inline_excluir_func_"
                                        f"{colab_id_inline}"
                                    ),
                                    help=(
                                        f"Retirar {nome_inline} "
                                        "da base operacional"
                                    ),
                                    on_click=_excluir_funcionario_inline,
                                )


                    # -----------------------------------------------------
                    # SALVAR MORADIAS EM LOTE
                    # -----------------------------------------------------
                    qtd_alteracoes = len(
                        alteracoes_moradia_pagina
                    )

                    c_pendencias_moradia, c_salvar_moradia = st.columns(
                        [4.2, 1.6],
                        vertical_alignment="center",
                    )

                    with c_pendencias_moradia:
                        if qtd_alteracoes:
                            st.markdown(
                                (
                                    '<div class="func-pending-changes">'
                                    f'{qtd_alteracoes} alteração(ões) pendente(s)'
                                    '</div>'
                                ),
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                (
                                    '<div class="func-pending-changes">'
                                    'Nenhuma alteração pendente'
                                    '</div>'
                                ),
                                unsafe_allow_html=True,
                            )

                    with c_salvar_moradia:
                        salvar_moradias = st.button(
                            "Salvar alterações",
                            type="primary",
                            use_container_width=True,
                            disabled=(
                                qtd_alteracoes == 0
                            ),
                            key="btn_salvar_moradias_lote",
                        )

                    if salvar_moradias:
                        ok_lote, qtd_salvas = (
                            _salvar_moradias_em_lote_admin(
                                alteracoes_moradia_pagina
                            )
                        )

                        if ok_lote:
                            # Atualiza o baseline da sessão imediatamente.
                            for _cid, _info in (
                                alteracoes_moradia_pagina.items()
                            ):
                                baseline_moradias[
                                    str(_cid)
                                ] = _info.get(
                                    "depois_label",
                                    "Não informado",
                                )

                            st.session_state[
                                "_msg_grade_funcionarios"
                            ] = {
                                "tipo": "sucesso",
                                "texto": (
                                    f"{qtd_salvas} moradia(s) "
                                    "salva(s) com sucesso."
                                ),
                            }

                        else:
                            st.session_state[
                                "_msg_grade_funcionarios"
                            ] = {
                                "tipo": "erro",
                                "texto": (
                                    "Não foi possível salvar todas "
                                    "as alterações de moradia."
                                ),
                            }


                _render_banco_funcionarios_inline(
                    ativos_filtrados
                )

            else:
                st.info(
                    "Nenhum funcionário encontrado "
                    "com os filtros selecionados."
                )


            # ------------------------------------------------------------
            # EDITAR CADASTRO COMPLETO
            # ------------------------------------------------------------
            if ativos_admin:
                st.markdown("**Editar cadastro**")

                mapa_edicao = {
                    (
                        f"{c.get('nome')} · "
                        f"{c.get('funcao') or '-'}"
                    ): c
                    for c in sorted(
                        ativos_admin,
                        key=lambda x: normalizar(
                            x.get("nome")
                        ),
                    )
                }

                rotulo_edicao = st.selectbox(
                    "Funcionário",
                    list(
                        mapa_edicao.keys()
                    ),
                    key="sel_editar_funcionario_admin",
                )

                colab_edicao = mapa_edicao[
                    rotulo_edicao
                ]

                moradia_atual = str(
                    colab_edicao.get(
                        "local_moradia"
                    )
                    or ""
                )

                idx_moradia = (
                    MORADIAS_COLAB.index(
                        moradia_atual
                    )
                    if moradia_atual
                    in MORADIAS_COLAB
                    else 0
                )

                with st.form(
                    "form_editar_funcionario_admin"
                ):
                    nome_edit = st.text_input(
                        "Nome",
                        value=str(
                            colab_edicao.get(
                                "nome"
                            )
                            or ""
                        ),
                    )

                    funcao_edit = st.text_input(
                        "Função",
                        value=str(
                            colab_edicao.get(
                                "funcao"
                            )
                            or ""
                        ),
                    )

                    ce1, ce2 = st.columns(2)

                    with ce1:
                        valor_edit = st.number_input(
                            "Custo diário c/ encargos (R$)",
                            min_value=0.01,
                            value=float(
                                obter_valor_diaria_colaborador(
                                    colab_edicao
                                )
                            ),
                            step=0.01,
                            format="%.2f",
                        )

                    with ce2:
                        moradia_edit = st.selectbox(
                            "Local de moradia",
                            MORADIAS_COLAB,
                            index=idx_moradia,
                        )

                    salvar_edicao = (
                        st.form_submit_button(
                            "Salvar alterações",
                            type="primary",
                            use_container_width=True,
                        )
                    )

                    if salvar_edicao:
                        nome_editado = " ".join(
                            str(
                                nome_edit
                                or ""
                            ).strip().split()
                        ).upper()

                        if not nome_editado:
                            st.warning(
                                "O nome não pode ficar vazio."
                            )

                        elif not str(
                            funcao_edit
                            or ""
                        ).strip():
                            st.warning(
                                "A função não pode ficar vazia."
                            )

                        else:
                            payload_edit = {
                                "nome": nome_editado,
                                "funcao": limpar_funcao(
                                    funcao_edit
                                ),
                                "valor_diaria": float(
                                    valor_edit
                                ),
                                "categoria_diaria": inferir_tipo_colaborador(
                                    funcao_edit,
                                    valor_edit,
                                ),
                                "local_moradia": moradia_edit,
                            }

                            try:
                                ok_edit = (
                                    _atualizar_colaborador_admin_rapido(
                                        colab_edicao.get("id"),
                                        payload_edit,
                                        "EDITAR",
                                        antes={
                                            "nome": colab_edicao.get(
                                                "nome"
                                            ),
                                            "funcao": colab_edicao.get(
                                                "funcao"
                                            ),
                                            "valor_diaria": colab_edicao.get(
                                                "valor_diaria"
                                            ),
                                            "local_moradia": colab_edicao.get(
                                                "local_moradia"
                                            ),
                                        },
                                    )
                                )

                                if not ok_edit:
                                    raise RuntimeError(
                                        "Falha ao atualizar colaborador."
                                    )

                                st.session_state[
                                    "msg_banco_funcionarios"
                                ] = (
                                    "Cadastro atualizado "
                                    "com sucesso."
                                )
                                st.rerun()

                            except Exception as e:
                                exibir_erro_amigavel(
                                    "colaboradores",
                                    "editar_funcionario",
                                    e,
                                    "Não foi possível atualizar o cadastro.",
                                )


            # ------------------------------------------------------------
            # INATIVOS / RESTAURAR
            # ------------------------------------------------------------
            if inativos_admin:
                with st.expander(
                    f"Funcionários excluídos · {len(inativos_admin)}",
                    expanded=False,
                ):
                    mapa_inativos = {
                        (
                            f"{c.get('nome')} · "
                            f"{c.get('funcao') or '-'}"
                        ): c
                        for c in sorted(
                            inativos_admin,
                            key=lambda x: normalizar(
                                x.get("nome")
                            ),
                        )
                    }

                    rotulo_inativo = st.selectbox(
                        "Cadastro excluído",
                        list(
                            mapa_inativos.keys()
                        ),
                        key="sel_funcionario_inativo_admin",
                    )

                    colab_inativo = mapa_inativos[
                        rotulo_inativo
                    ]

                    if st.button(
                        "Restaurar funcionário",
                        use_container_width=True,
                        key=(
                            "btn_restaurar_func_"
                            f"{colab_inativo.get('id')}"
                        ),
                    ):
                        try:
                            (
                                supabase.table(
                                    "colaboradores"
                                )
                                .update({
                                    "ativo": True
                                })
                                .eq(
                                    "id",
                                    colab_inativo.get(
                                        "id"
                                    ),
                                )
                                .execute()
                            )

                            limpar_cache_operacional()

                            st.session_state[
                                "msg_banco_funcionarios"
                            ] = (
                                f"{colab_inativo.get('nome')} "
                                "foi restaurado."
                            )
                            st.rerun()

                        except Exception as e:
                            exibir_erro_amigavel(
                                "colaboradores",
                                "restaurar_funcionario",
                                e,
                                "Não foi possível restaurar o funcionário.",
                            )

        with tab_import_colab:
            st.markdown("**Importar planilha de colaboradores**")
            st.write(
                "Envie uma planilha para adicionar novos colaboradores ou atualizar cadastros existentes. "
                "A conferência é feita pelo nome e nenhum colaborador ausente da planilha será excluído. "
                "A planilha deve conter uma coluna com o valor da diária de cada colaborador."
            )

            if st.session_state.get("msg_import_colab"):
                st.success(st.session_state.pop("msg_import_colab"))

            arquivo_import = st.file_uploader(
                "Selecione a planilha de colaboradores:",
                type=["xlsx", "xls", "csv"],
                key="arquivo_import_colaboradores"
            )

            if arquivo_import is not None:

                def _localizar_linha_cabecalho_colaboradores(df_bruto, limite=20):
                    """
                    Procura automaticamente a linha de cabeçalho da tabela.
                    Isso permite importar planilhas que tenham título, total, observações
                    ou linhas em branco antes de 'Código | Nome | ...'.
                    """
                    candidatos_nome = {
                        "NOME",
                        "NOME COMPLETO",
                        "COLABORADOR",
                        "FUNCIONARIO",
                        "FUNCIONÁRIO",
                        "EMPREGADO",
                    }

                    qtd = min(len(df_bruto), limite)

                    for idx in range(qtd):
                        valores = []

                        for valor in df_bruto.iloc[idx].tolist():
                            if pd.isna(valor):
                                continue

                            txt = normalizar(str(valor))
                            if txt:
                                valores.append(txt)

                        # Prioridade: linha que realmente contém uma coluna de nome.
                        if any(v in candidatos_nome for v in valores):
                            return idx

                        # Também aceita cabeçalhos descritivos como
                        # "Nome do colaborador", sem confundir o título
                        # "COLABORADORES ADMITIDOS / ATIVOS" com cabeçalho.
                        for v in valores:
                            tokens = [t for t in re.split(r"[^A-Z0-9]+", v) if t]
                            if "NOME" in tokens:
                                return idx

                    return None


                def _ler_planilha_colaboradores(arquivo):
                    """
                    Lê XLS/XLSX/CSV detectando automaticamente o cabeçalho.
                    Retorna (dataframe, linha_cabecalho_1_based).
                    """
                    nome_arquivo = arquivo.name.lower()

                    if nome_arquivo.endswith(".csv"):
                        arquivo.seek(0)

                        try:
                            bruto = pd.read_csv(
                                arquivo,
                                sep=None,
                                engine="python",
                                header=None
                            )
                            encoding_usado = None

                        except UnicodeDecodeError:
                            arquivo.seek(0)
                            bruto = pd.read_csv(
                                arquivo,
                                sep=None,
                                engine="python",
                                header=None,
                                encoding="latin-1"
                            )
                            encoding_usado = "latin-1"

                        linha_header = _localizar_linha_cabecalho_colaboradores(bruto)

                        arquivo.seek(0)

                        kwargs = {
                            "sep": None,
                            "engine": "python",
                            "header": linha_header if linha_header is not None else 0,
                        }

                        if encoding_usado:
                            kwargs["encoding"] = encoding_usado

                        df = pd.read_csv(
                            arquivo,
                            **kwargs
                        )

                    else:
                        arquivo.seek(0)

                        # Primeiro lê sem cabeçalho para encontrar onde a tabela começa.
                        bruto = pd.read_excel(
                            arquivo,
                            header=None
                        )

                        linha_header = _localizar_linha_cabecalho_colaboradores(bruto)

                        arquivo.seek(0)

                        # Se não localizar nada, mantém compatibilidade com planilhas
                        # convencionais cujo cabeçalho já está na primeira linha.
                        df = pd.read_excel(
                            arquivo,
                            header=linha_header if linha_header is not None else 0
                        )

                    # Remove linhas e colunas completamente vazias.
                    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")

                    return df, (
                        linha_header + 1
                        if linha_header is not None
                        else 1
                    )


                try:
                    df_import, linha_cabecalho_detectada = _ler_planilha_colaboradores(
                        arquivo_import
                    )

                except Exception as e:
                    df_import = pd.DataFrame()
                    linha_cabecalho_detectada = None
                    exibir_erro_amigavel("colaboradores", "ler_planilha", e, "Não foi possível ler a planilha enviada.")


                if not df_import.empty:

                    if linha_cabecalho_detectada:
                        st.caption(
                            f"✅ Cabeçalho da tabela identificado automaticamente na linha "
                            f"{linha_cabecalho_detectada}."
                        )
                    df_import.columns = [str(c).strip() for c in df_import.columns]
                    colunas = list(df_import.columns)

                    def localizar_coluna_import(candidatos):
                        mapa = {normalizar(c): c for c in colunas}
                        for candidato in candidatos:
                            if normalizar(candidato) in mapa:
                                return mapa[normalizar(candidato)]
                        for c in colunas:
                            c_norm = normalizar(c)
                            if any(normalizar(cand) in c_norm for cand in candidatos):
                                return c
                        return None

                    col_nome_auto = localizar_coluna_import([
                        "NOME", "NOME COMPLETO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO", "EMPREGADO"
                    ])
                    col_funcao_auto = localizar_coluna_import([
                        "FUNCAO", "FUNÇÃO", "CARGO", "FUNCAO/CARGO", "FUNÇÃO/CARGO"
                    ])
                    col_categoria_auto = localizar_coluna_import([
                        "CATEGORIA", "TIPO", "CLASSIFICACAO", "CLASSIFICAÇÃO"
                    ])
                    col_valor_auto = localizar_coluna_import([
                        "VALOR DO COLABORADOR",
                        "VALOR COLABORADOR",
                        "VALOR DA DIARIA",
                        "VALOR DA DIÁRIA",
                        "VALOR DIARIA",
                        "VALOR DIÁRIA",
                        "CUSTO DIARIO",
                        "CUSTO DIÁRIO",
                        "CUSTO DIARIO DO COLABORADOR",
                        "CUSTO DIÁRIO DO COLABORADOR",
                        "DIARIA",
                        "DIÁRIA",
                        "VALOR"
                    ])
                    col_avulso_auto = localizar_coluna_import(["AVULSO"])
                    col_moradia_auto = localizar_coluna_import([
                        "LOCAL DE MORADIA",
                        "MORADIA",
                        "CIDADE",
                        "MUNICIPIO",
                        "MUNICÍPIO",
                    ])

                    c_imp1, c_imp2 = st.columns(2)
                    with c_imp1:
                        idx_nome = colunas.index(col_nome_auto) if col_nome_auto in colunas else 0
                        col_nome_import = st.selectbox(
                            "Coluna do NOME:",
                            colunas,
                            index=idx_nome,
                            key="map_nome_import"
                        )
                    with c_imp2:
                        opcoes_funcao = ["(não usar)"] + colunas
                        idx_funcao = opcoes_funcao.index(col_funcao_auto) if col_funcao_auto in colunas else 0
                        col_funcao_import = st.selectbox(
                            "Coluna da FUNÇÃO/CARGO:",
                            opcoes_funcao,
                            index=idx_funcao,
                            key="map_funcao_import"
                        )

                    c_imp3, c_imp4 = st.columns(2)
                    with c_imp3:
                        opcoes_categoria = ["(inferir pela função)"] + colunas
                        idx_categoria = opcoes_categoria.index(col_categoria_auto) if col_categoria_auto in colunas else 0
                        col_categoria_import = st.selectbox(
                            "Coluna PROFISSIONAL/AJUDANTE (opcional):",
                            opcoes_categoria,
                            index=idx_categoria,
                            key="map_categoria_import"
                        )
                    with c_imp4:
                        opcoes_avulso = ["(não usar)"] + colunas
                        idx_avulso = opcoes_avulso.index(col_avulso_auto) if col_avulso_auto in colunas else 0
                        col_avulso_import = st.selectbox(
                            "Coluna AVULSO (opcional):",
                            opcoes_avulso,
                            index=idx_avulso,
                            key="map_avulso_import"
                        )

                    opcoes_moradia = ["(não usar)"] + colunas
                    idx_moradia_import = (
                        opcoes_moradia.index(col_moradia_auto)
                        if col_moradia_auto in colunas
                        else 0
                    )
                    col_moradia_import = st.selectbox(
                        "Coluna LOCAL DE MORADIA (opcional):",
                        opcoes_moradia,
                        index=idx_moradia_import,
                        key="map_moradia_import",
                    )

                    opcoes_valor = ["(selecione)"] + colunas
                    idx_valor = (
                        opcoes_valor.index(col_valor_auto)
                        if col_valor_auto in colunas
                        else 0
                    )
                    col_valor_import = st.selectbox(
                        "Coluna CUSTO DIÁRIO C/ ENCARGOS (obrigatória):",
                        opcoes_valor,
                        index=idx_valor,
                        key="map_valor_import",
                        help=(
                            "Aceita 241,74, 241.74, R$ 241,74 e também o formato "
                            "contábil do Excel, em que 'R$' fica numa coluna e o valor "
                            "numérico aparece na coluna seguinte."
                        ),
                    )

                    def _converter_valor_colaborador_import(valor):
                        if pd.isna(valor):
                            return None

                        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                            try:
                                numero = float(valor)
                                return numero if numero > 0 else None
                            except Exception:
                                return None

                        txt = str(valor).strip()
                        if not txt:
                            return None

                        txt = (
                            txt.replace("R$", "")
                            .replace("r$", "")
                            .replace("\xa0", "")
                            .replace(" ", "")
                        )

                        # Se a célula contiver apenas o símbolo de moeda,
                        # o número pode estar na coluna seguinte (formato contábil do Excel).
                        if txt in {"", "-", "R$", "r$"}:
                            return None

                        # Formato brasileiro: 1.234,56
                        if "," in txt:
                            txt = txt.replace(".", "").replace(",", ".")
                        else:
                            txt = txt.replace(",", ".")

                        try:
                            numero = float(txt)
                            return numero if numero > 0 else None
                        except Exception:
                            return None

                    def _extrair_valor_colaborador_linha(linha, coluna_valor):
                        """
                        Suporta:
                        1) valor na própria coluna: 258,10 / 258.10 / R$ 258,10
                        2) formato contábil do Excel:
                           coluna 'Custo diário' = R$
                           coluna seguinte = 258,10
                        """
                        if coluna_valor == "(selecione)":
                            return None

                        valor_direto = _converter_valor_colaborador_import(
                            linha.get(coluna_valor)
                        )
                        if valor_direto is not None:
                            return valor_direto

                        try:
                            idx = colunas.index(coluna_valor)
                        except ValueError:
                            return None

                        # Procura nas duas colunas imediatamente seguintes.
                        # Isso cobre arquivos com uma coluna vazia/intermediária
                        # gerada pelo formato contábil/mesclagem do Excel.
                        for prox_idx in (idx + 1, idx + 2):
                            if prox_idx >= len(colunas):
                                continue

                            prox_col = colunas[prox_idx]
                            valor_prox = _converter_valor_colaborador_import(
                                linha.get(prox_col)
                            )
                            if valor_prox is not None:
                                return valor_prox

                        return None

                    # Diagnóstico visual: informa quando a planilha usa
                    # "R$" em uma coluna e o número na coluna ao lado.
                    if col_valor_import != "(selecione)":
                        amostra_valores = []
                        for _, _linha_teste in df_import.head(20).iterrows():
                            _v = _extrair_valor_colaborador_linha(
                                _linha_teste,
                                col_valor_import,
                            )
                            if _v is not None:
                                amostra_valores.append(_v)

                        if amostra_valores:
                            st.caption(
                                f"✓ Coluna de custo reconhecida. "
                                f"Exemplo detectado: {formatar_reais(amostra_valores[0])}."
                            )

                    registros_por_nome = {}
                    linhas_invalidas = 0
                    linhas_valor_invalido = 0

                    if col_valor_import == "(selecione)":
                        st.error(
                            "A planilha precisa ter uma coluna com o valor do colaborador. "
                            "Selecione a coluna correta acima."
                        )

                    for _, linha in df_import.iterrows():
                        nome_val = linha.get(col_nome_import)
                        if pd.isna(nome_val) or not str(nome_val).strip():
                            linhas_invalidas += 1
                            continue

                        nome_limpo = " ".join(str(nome_val).strip().split()).upper()

                        funcao_val = ""
                        if col_funcao_import != "(não usar)":
                            bruto_funcao = linha.get(col_funcao_import)
                            if not pd.isna(bruto_funcao):
                                funcao_val = str(bruto_funcao).strip()

                        if col_categoria_import != "(inferir pela função)":
                            bruto_categoria = linha.get(col_categoria_import)
                            categoria_txt = "" if pd.isna(bruto_categoria) else normalizar(bruto_categoria)
                            if "AJUD" in categoria_txt or "AUX" in categoria_txt or "SERVENT" in categoria_txt:
                                tipo_val = "Ajudante"
                            elif "PROF" in categoria_txt:
                                tipo_val = "Profissional"
                            else:
                                tipo_val = inferir_tipo_colaborador(funcao_val)
                        else:
                            tipo_val = inferir_tipo_colaborador(funcao_val)

                        avulso_val = False
                        if col_avulso_import != "(não usar)":
                            bruto_avulso = linha.get(col_avulso_import)
                            if not pd.isna(bruto_avulso):
                                avulso_txt = normalizar(bruto_avulso)
                                avulso_val = avulso_txt in ["SIM", "S", "TRUE", "VERDADEIRO", "1", "X"]

                        if not funcao_val:
                            funcao_val = tipo_val.upper()
                        if avulso_val and not normalizar(funcao_val).startswith("AVULSO -"):
                            funcao_val = f"AVULSO - {funcao_val}"

                        funcao_salva = limpar_funcao(funcao_val)

                        moradia_salva = ""
                        if col_moradia_import != "(não usar)":
                            bruto_moradia = linha.get(
                                col_moradia_import
                            )
                            if not pd.isna(bruto_moradia):
                                moradia_txt = normalizar(
                                    bruto_moradia
                                )

                                mapa_moradias = {
                                    "FORTALEZA": "Fortaleza",
                                    "MARACANAU": "Maracanaú",
                                    "CAUCAIA": "Caucaia",
                                    "HORIZONTE": "Horizonte",
                                }

                                moradia_salva = mapa_moradias.get(
                                    moradia_txt,
                                    "",
                                )

                        if col_valor_import == "(selecione)":
                            linhas_valor_invalido += 1
                            continue

                        diaria_salva = _extrair_valor_colaborador_linha(
                            linha,
                            col_valor_import,
                        )
                        if diaria_salva is None:
                            linhas_valor_invalido += 1
                            continue

                        # Se o mesmo nome aparecer mais de uma vez na planilha, mantém a última ocorrência.
                        registros_por_nome[normalizar(nome_limpo)] = {
                            "nome": nome_limpo,
                            "funcao": funcao_salva,
                            "tipo": tipo_val,
                            "valor_diaria": diaria_salva,
                            "local_moradia": moradia_salva,
                            "avulso": avulso_val,
                        }

                    registros_import = list(registros_por_nome.values())

                    if registros_import:
                        preview_import = pd.DataFrame([
                            {
                                "Nome": r["nome"],
                                "Função": r["funcao"],
                                "Categoria": r["tipo"],
                                "Custo diário c/ encargos": formatar_reais(r["valor_diaria"]),
                                "Moradia": r.get("local_moradia") or "Não informado",
                                "Avulso": "SIM" if r["avulso"] else "NÃO",
                            }
                            for r in registros_import
                        ])
                        avisos_import = []
                        if linhas_invalidas:
                            avisos_import.append(
                                f"{linhas_invalidas} linha(s) sem nome foram ignoradas"
                            )
                        if linhas_valor_invalido:
                            avisos_import.append(
                                f"{linhas_valor_invalido} linha(s) sem valor válido foram ignoradas"
                            )

                        st.caption(
                            f"{len(registros_import)} colaborador(es) pronto(s) para importar."
                            + (
                                " " + " • ".join(avisos_import) + "."
                                if avisos_import else ""
                            )
                        )
                        tabela_aproar(preview_import, key="tbl_import_preview", altura_max=360)

                        if st.button(
                            "📤 IMPORTAR / ATUALIZAR COLABORADORES",
                            type="primary",
                            use_container_width=True,
                            key="btn_importar_colaboradores"
                        ):
                            try:
                                atuais_import = supabase.table("colaboradores").select("*").execute().data or []
                                mapa_atuais = {
                                    normalizar(c.get("nome", "")): c
                                    for c in atuais_import
                                    if c.get("nome")
                                }

                                novos = 0
                                atualizados = 0
                                erros = []

                                for reg in registros_import:
                                    existente = mapa_atuais.get(normalizar(reg["nome"]))
                                    payload = {
                                        "nome": reg["nome"],
                                        "funcao": reg["funcao"],
                                        "valor_diaria": reg["valor_diaria"],
                                        "categoria_diaria": reg["tipo"],
                                        "ativo": True,
                                    }

                                    if reg.get("local_moradia"):
                                        payload["local_moradia"] = reg[
                                            "local_moradia"
                                        ]
                                    try:
                                        if existente:
                                            supabase.table("colaboradores").update(payload).eq("id", existente["id"]).execute()
                                            atualizados += 1
                                        else:
                                            retorno = supabase.table("colaboradores").insert(payload).execute().data or []
                                            novos += 1
                                            if retorno:
                                                mapa_atuais[normalizar(reg["nome"])] = retorno[0]
                                    except Exception:
                                        erros.append(reg["nome"])

                                limpar_cache_operacional()
                                mensagem = f"Importação concluída: {novos} novo(s) e {atualizados} atualizado(s)."
                                if erros:
                                    mensagem += f" Não foi possível importar {len(erros)} registro(s)."
                                registrar_auditoria_prod(
                                    "colaboradores", "", "IMPORTAR_PLANILHA", "ADMIN",
                                    depois={
                                        "novos": novos,
                                        "atualizados": atualizados,
                                        "erros": len(erros)
                                    },
                                    contexto={"nomes_com_erro": erros[:50]}
                                )
                                st.session_state["msg_import_colab"] = mensagem
                                st.rerun()
                            except Exception as e:
                                exibir_erro_amigavel("colaboradores", "importar", e, "Não foi possível concluir a importação.")
                    else:
                        st.warning("A planilha não possui colaboradores válidos para importar.")
                elif arquivo_import is not None:
                    st.warning("A planilha está vazia ou não pôde ser interpretada.")

        with tab_teams:
            st.markdown(
                "**Cobranças de apontamentos no Teams**"
            )
            st.caption(
                "Automático: demais unidades às 16:00 no próprio dia e, "
                "se continuar pendente, às 09:30 e 15:00 do dia seguinte. "
                "SEBRAE: um único lembrete às 21:00 do próprio dia; "
                "o prazo operacional do apontamento vai até 09:29 do dia seguinte. "
                "Depois disso, se continuar pendente, fica atrasado e disponível para cobrança manual."
            )

            st.info(
                "A cobrança é direcionada pelo responsável oficial de cada unidade. "
                "Se PAULO ou HELENA estiverem ativos e com e-mail configurado, "
                "eles recebem uma cópia com TODAS as pendências. "
                "O botão manual não substitui nem bloqueia as cobranças automáticas."
            )

            if not TEAMS_COBRANCA_WEBHOOK_URL:
                st.warning(
                    "Para usar o botão manual, adicione também "
                    "`TEAMS_COBRANCA_WEBHOOK_URL` nos Secrets do Streamlit "
                    "com a mesma URL já salva no GitHub."
                )

            if DB_BACKEND != "NEON":
                st.warning(
                    "A configuração automática desta rotina foi preparada "
                    "para o Neon/PostgreSQL."
                )

            else:
                try:
                    with supabase._connect() as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                SELECT
                                    engenheiro,
                                    email_teams,
                                    ativo
                                FROM engenheiros_teams
                                ORDER BY engenheiro
                                """
                            )
                            rows_cfg = cur.fetchall() or []

                    mapa_cfg_teams = {}

                    for row in rows_cfg:
                        if isinstance(row, dict):
                            eng = str(
                                row.get("engenheiro")
                                or ""
                            ).strip().upper()

                            mapa_cfg_teams[eng] = {
                                "email_teams": str(
                                    row.get("email_teams")
                                    or ""
                                ).strip(),
                                "ativo": bool(
                                    row.get("ativo", True)
                                ),
                            }

                        else:
                            eng = str(
                                row[0]
                                or ""
                            ).strip().upper()

                            mapa_cfg_teams[eng] = {
                                "email_teams": str(
                                    row[1]
                                    or ""
                                ).strip(),
                                "ativo": bool(row[2]),
                            }

                except Exception:
                    mapa_cfg_teams = {}

                if st.session_state.get(
                    "msg_cfg_teams"
                ):
                    st.success(
                        st.session_state.pop(
                            "msg_cfg_teams"
                        )
                    )

                if st.session_state.get(
                    "msg_cobranca_manual_teams"
                ):
                    msg_manual = st.session_state.pop(
                        "msg_cobranca_manual_teams"
                    )

                    if msg_manual.get("ok"):
                        st.success(
                            msg_manual.get("texto")
                        )
                    else:
                        st.error(
                            msg_manual.get("texto")
                        )

                st.markdown("**Supervisores e unidades**")
                st.caption(
                    "Ativo controla a cobrança automática. "
                    "O botão Cobrar agora funciona em qualquer pendência, "
                    "mesmo antes ou depois do automático."
                )

                configs_teams_form = []

                st.html("""
                <style>
                div[class*="st-key-btn_cobrar_teams_"] button{
                    min-height:34px !important;
                    padding:4px 10px !important;
                    font-size:10px !important;
                    font-weight:700 !important;
                    border-radius:7px !important;
                    white-space:nowrap !important;
                }

                .teams-resp-name{
                    font-size:12px;
                    font-weight:800;
                    color:#172235;
                    line-height:1.2;
                }

                .teams-resp-units{
                    margin-top:3px;
                    color:#7A879A;
                    font-size:9.5px;
                    line-height:1.35;
                }
                </style>
                """)

                for eng in SUPERVISORES_TEAMS:
                    atual = mapa_cfg_teams.get(
                        eng,
                        {},
                    )

                    unidades_eng = (
                        ["TODAS AS UNIDADES"]
                        if eng in OBSERVADORES_TEAMS
                        else RESPONSAVEIS_UNIDADES_TEAMS.get(
                            eng,
                            [],
                        )
                    )

                    (
                        c_nome,
                        c_email,
                        c_ativo,
                        c_cobrar,
                    ) = st.columns(
                        [2.25, 3.35, .75, 1.05],
                        vertical_alignment="center",
                    )

                    with c_nome:
                        st.markdown(
                            (
                                '<div class="teams-resp-name">'
                                f'{_html.escape(eng)}'
                                '</div>'
                                '<div class="teams-resp-units">'
                                + " · ".join(
                                    _html.escape(u)
                                    for u in unidades_eng
                                )
                                + '</div>'
                            ),
                            unsafe_allow_html=True,
                        )

                    with c_email:
                        email_eng = st.text_input(
                            f"E-mail Teams · {eng}",
                            value=atual.get(
                                "email_teams",
                                "",
                            ),
                            placeholder="nome@aproar.com.br",
                            label_visibility="collapsed",
                            key=f"teams_email_{eng}",
                        )

                    with c_ativo:
                        ativo_eng = st.checkbox(
                            "Ativo",
                            value=atual.get(
                                "ativo",
                                True,
                            ),
                            key=f"teams_ativo_{eng}",
                        )

                    with c_cobrar:
                        if st.button(
                            "Cobrar agora",
                            key=f"btn_cobrar_teams_{eng}",
                            use_container_width=True,
                            disabled=(
                                not str(
                                    email_eng
                                    or ""
                                ).strip()
                            ),
                        ):
                            with st.spinner(
                                f"Enviando para {eng}..."
                            ):
                                ok_manual, texto_manual = (
                                    _cobrar_supervisor_teams_agora(
                                        eng,
                                        email_eng,
                                    )
                                )

                            st.session_state[
                                "msg_cobranca_manual_teams"
                            ] = {
                                "ok": ok_manual,
                                "texto": texto_manual,
                            }
                            st.rerun()

                    configs_teams_form.append(
                        (
                            eng,
                            str(
                                email_eng
                                or ""
                            ).strip(),
                            bool(ativo_eng),
                        )
                    )

                if st.button(
                    "Salvar destinatários",
                    type="primary",
                    use_container_width=True,
                    key="btn_salvar_destinatarios_teams",
                ):
                    try:
                        with supabase._connect() as conn:
                            with conn.cursor() as cur:
                                for (
                                    eng,
                                    email_eng,
                                    ativo_eng,
                                ) in configs_teams_form:
                                    cur.execute(
                                        """
                                        INSERT INTO engenheiros_teams
                                            (
                                                engenheiro,
                                                email_teams,
                                                ativo,
                                                atualizado_em
                                            )
                                        VALUES
                                            (%s, %s, %s, NOW())
                                        ON CONFLICT (engenheiro)
                                        DO UPDATE SET
                                            email_teams = EXCLUDED.email_teams,
                                            ativo = EXCLUDED.ativo,
                                            atualizado_em = NOW()
                                        """,
                                        (
                                            eng,
                                            email_eng or None,
                                            ativo_eng,
                                        ),
                                    )

                                # Segurança adicional:
                                # Gustavo permanece inativo se existir no histórico.
                                cur.execute(
                                    """
                                    UPDATE engenheiros_teams
                                       SET ativo = FALSE,
                                           atualizado_em = NOW()
                                     WHERE UPPER(engenheiro) = 'GUSTAVO'
                                    """
                                )

                            conn.commit()

                        st.session_state[
                            "msg_cfg_teams"
                        ] = (
                            "Destinatários do Teams salvos com sucesso."
                        )
                        st.rerun()

                    except Exception as e:
                        exibir_erro_amigavel(
                            "teams",
                            "salvar_destinatarios",
                            e,
                            (
                                "Não foi possível salvar os "
                                "destinatários do Teams."
                            ),
                        )

                st.markdown("---")
                st.markdown(
                    "**Responsáveis cadastrados**"
                )

                df_responsaveis = pd.DataFrame([
                    {
                        "Supervisor": eng,
                        "Unidades": (
                            "TODAS AS UNIDADES · CÓPIA"
                            if eng in OBSERVADORES_TEAMS
                            else " · ".join(
                                RESPONSAVEIS_UNIDADES_TEAMS[
                                    eng
                                ]
                            )
                        ),
                    }
                    for eng in SUPERVISORES_TEAMS
                ])

                tabela_aproar(
                    df_responsaveis,
                    key="tbl_responsaveis_unidades_teams",
                    altura_max=260,
                )

                st.markdown("---")
                st.markdown(
                    "**Pendências de apontamento e destinatários**"
                )
                st.caption(
                    "A pendência fica nesta lista até ser regularizada. "
                    "Ela aparece inclusive no próprio dia do serviço."
                )

                try:
                    agora_preview = datetime.datetime.now(
                        ZoneInfo("America/Fortaleza")
                    )
                    hoje_preview = agora_preview.date()

                    with supabase._connect() as conn:
                        with conn.cursor() as cur:
                            # PAULO/HELENA usam a visão completa de pendências.
                            pendentes_preview = (
                                _carregar_pendentes_responsavel_teams(
                                    cur,
                                    "PAULO",
                                    hoje_preview,
                                )
                            )

                    ativos_com_email = {
                        eng
                        for eng, cfg in mapa_cfg_teams.items()
                        if cfg.get("ativo")
                        and str(
                            cfg.get("email_teams")
                            or ""
                        ).strip()
                    }

                    observadores_ativos = [
                        obs
                        for obs in OBSERVADORES_TEAMS
                        if obs in ativos_com_email
                    ]

                    linhas_preview = []

                    for item in pendentes_preview:
                        if isinstance(item, dict):
                            data_ref = item.get("data")
                            turno_ref = item.get("turno")
                            colaborador_ref = (
                                item.get("colaborador")
                                or ""
                            )
                            unidade_ref = (
                                item.get("unidade")
                                or "SEM UNIDADE"
                            )
                        else:
                            data_ref = item[1]
                            turno_ref = item[2]
                            colaborador_ref = item[4]
                            unidade_ref = (
                                item[5]
                                or "SEM UNIDADE"
                            )

                        responsavel_ref = (
                            _responsavel_por_unidade_teams(
                                unidade_ref
                            )
                        )

                        destinatarios_ref = []

                        if (
                            responsavel_ref
                            in ativos_com_email
                        ):
                            destinatarios_ref.append(
                                responsavel_ref
                            )

                        for observador in observadores_ativos:
                            if observador not in destinatarios_ref:
                                destinatarios_ref.append(
                                    observador
                                )

                        (
                            situacao_ref,
                            automatico_ref,
                        ) = _situacao_pendencia_teams(
                            data_ref,
                            unidade_ref,
                            agora_ref=agora_preview,
                        )

                        linhas_preview.append({
                            "Data": (
                                data_ref.strftime("%d/%m/%Y")
                                if hasattr(
                                    data_ref,
                                    "strftime",
                                )
                                else str(
                                    data_ref
                                    or ""
                                )
                            ),
                            "Unidade": unidade_ref,
                            "Colaborador": colaborador_ref,
                            "Turno": turno_ref or "-",
                            "Situação": situacao_ref,
                            "Automático": automatico_ref,
                            "Responsável": responsavel_ref,
                            "Será enviado para": (
                                " · ".join(
                                    destinatarios_ref
                                )
                                if destinatarios_ref
                                else "SEM DESTINATÁRIO ATIVO"
                            ),
                        })

                    if linhas_preview:
                        df_preview_teams = pd.DataFrame(
                            linhas_preview
                        )

                        qtd_sem_destino = int(
                            (
                                df_preview_teams[
                                    "Será enviado para"
                                ]
                                == "SEM DESTINATÁRIO ATIVO"
                            ).sum()
                        )

                        qtd_atrasados = int(
                            (
                                df_preview_teams["Situação"]
                                == "Atrasado"
                            ).sum()
                        )
                        qtd_hoje = int(
                            (
                                df_preview_teams["Situação"]
                                == "Pendente hoje"
                            ).sum()
                        )

                        c_prev1, c_prev2, c_prev3, c_prev4 = st.columns(4)

                        with c_prev1:
                            st.metric(
                                "Pendências",
                                len(df_preview_teams),
                            )

                        with c_prev2:
                            st.metric(
                                "Pendentes hoje",
                                qtd_hoje,
                            )

                        with c_prev3:
                            st.metric(
                                "Atrasados",
                                qtd_atrasados,
                            )

                        with c_prev4:
                            st.metric(
                                "Sem destinatário",
                                qtd_sem_destino,
                            )

                        tabela_aproar(
                            df_preview_teams,
                            key="tbl_preview_cobrancas_teams",
                            altura_max=420,
                        )

                        st.caption(
                            "PAULO e HELENA aparecem em todas as linhas "
                            "somente quando estiverem Ativos e com e-mail Teams preenchido."
                        )

                    else:
                        st.success(
                            "Não há pendências de apontamento neste momento."
                        )

                except Exception as e:
                    st.warning(
                        "Não foi possível carregar a prévia dos apontamentos atrasados."
                    )

                st.markdown("---")
                st.markdown(
                    "**Histórico recente de cobranças**"
                )

                try:
                    with supabase._connect() as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                SELECT
                                    data_execucao,
                                    horario,
                                    engenheiro,
                                    email_teams,
                                    qtd_pendentes,
                                    status,
                                    enviado_em
                                FROM cobrancas_teams
                                ORDER BY enviado_em DESC
                                LIMIT 40
                                """
                            )
                            logs_teams = cur.fetchall() or []

                    linhas_logs = []

                    for row in logs_teams:
                        if isinstance(row, dict):
                            data_exec = row.get(
                                "data_execucao"
                            )
                            enviado_em = row.get(
                                "enviado_em"
                            )

                            horario = str(
                                row.get("horario")
                                or ""
                            )

                            linhas_logs.append({
                                "Data": (
                                    data_exec.strftime(
                                        "%d/%m/%Y"
                                    )
                                    if hasattr(
                                        data_exec,
                                        "strftime",
                                    )
                                    else str(
                                        data_exec
                                        or ""
                                    )
                                ),
                                "Envio": (
                                    horario
                                    if not horario.startswith(
                                        "MANUAL "
                                    )
                                    else horario
                                ),
                                "Supervisor": (
                                    row.get(
                                        "engenheiro"
                                    )
                                    or ""
                                ),
                                "Pendentes": (
                                    row.get(
                                        "qtd_pendentes"
                                    )
                                    or 0
                                ),
                                "Status": (
                                    row.get("status")
                                    or ""
                                ),
                                "Enviado em": (
                                    enviado_em.astimezone(
                                        ZoneInfo(
                                            "America/Fortaleza"
                                        )
                                    ).strftime(
                                        "%d/%m %H:%M"
                                    )
                                    if hasattr(
                                        enviado_em,
                                        "astimezone",
                                    )
                                    else str(
                                        enviado_em
                                        or ""
                                    )
                                ),
                            })

                        else:
                            (
                                data_exec,
                                horario,
                                eng,
                                email,
                                qtd,
                                status,
                                enviado_em,
                            ) = row

                            linhas_logs.append({
                                "Data": (
                                    data_exec.strftime(
                                        "%d/%m/%Y"
                                    )
                                    if hasattr(
                                        data_exec,
                                        "strftime",
                                    )
                                    else str(
                                        data_exec
                                        or ""
                                    )
                                ),
                                "Envio": horario or "",
                                "Supervisor": eng or "",
                                "Pendentes": qtd or 0,
                                "Status": status or "",
                                "Enviado em": (
                                    enviado_em.astimezone(
                                        ZoneInfo(
                                            "America/Fortaleza"
                                        )
                                    ).strftime(
                                        "%d/%m %H:%M"
                                    )
                                    if hasattr(
                                        enviado_em,
                                        "astimezone",
                                    )
                                    else str(
                                        enviado_em
                                        or ""
                                    )
                                ),
                            })

                    if linhas_logs:
                        tabela_aproar(
                            pd.DataFrame(
                                linhas_logs
                            ),
                            key=(
                                "tbl_logs_cobrancas_teams"
                            ),
                            altura_max=330,
                        )

                    else:
                        st.caption(
                            "Ainda não há cobranças registradas."
                        )

                except Exception:
                    st.caption(
                        "Histórico de cobranças ainda indisponível."
                    )

                st.markdown("---")
                st.caption(
                    "Automático — demais unidades: 16:00 no dia do serviço, "
                    "09:30 e 15:00 no dia seguinte. SEBRAE: 21:00 no próprio dia, "
                    "uma única vez. Manual: disponível enquanto a pendência existir. "
                    "PAULO e HELENA recebem todas as pendências quando ativos."
                )

        with tab_limpeza:
            st.markdown("**Limpeza e manutenção de registros**")
            st.caption(
                "Use esta área apenas para corrigir registros operacionais incorretos. "
                "A exclusão é permanente."
            )

            with st.container(border=True):
                st.markdown("**Excluir convocações de uma data**")
                st.caption(
                    "Remove as convocações da data selecionada. "
                    "Use somente quando houver necessidade de correção administrativa."
                )

                c_limpa_data, c_limpa_btn = st.columns(
                    [1.45, .55],
                    vertical_alignment="bottom",
                )

                with c_limpa_data:
                    data_limpeza = st.date_input(
                        "Data",
                        value=datetime.date.today(),
                        format="DD/MM/YYYY",
                        key="data_limpeza_prod_v1",
                    )

                with c_limpa_btn:
                    limpar_data = st.button(
                        "Excluir esta data",
                        use_container_width=True,
                        key="btn_limpar_data_prod_v1",
                    )

                confirmar_exclusao_data = st.checkbox(
                    "Confirmo que desejo excluir as convocações desta data.",
                    key="confirmar_limpeza_data_prod_v1",
                )

                if limpar_data:
                    if not confirmar_exclusao_data:
                        st.warning(
                            "Marque a confirmação antes de excluir os registros."
                        )
                    else:
                        try:
                            registros_limpeza = (
                                supabase.table("convocacoes")
                                .select("*")
                                .eq("data", data_limpeza.isoformat())
                                .execute()
                                .data or []
                            )

                            if not registros_limpeza:
                                st.info(
                                    f"Não há convocações em {data_limpeza.strftime('%d/%m/%Y')}."
                                )
                            else:
                                supabase.table("convocacoes").delete().eq(
                                    "data",
                                    data_limpeza.isoformat(),
                                ).execute()

                                registrar_auditoria_prod(
                                    "convocacao",
                                    "",
                                    "EXCLUIR_EM_LOTE_ADMIN",
                                    "ADMIN",
                                    antes={
                                        "quantidade": len(registros_limpeza),
                                        "ids": [
                                            str(r.get("id"))
                                            for r in registros_limpeza[:200]
                                        ],
                                    },
                                    contexto={
                                        "data": data_limpeza.isoformat(),
                                        "origem": "limpeza_administrativa_producao",
                                    },
                                )

                                try:
                                    limpar_cache_operacional()
                                except Exception:
                                    pass

                                try:
                                    _buscar_convocacoes_intervalo.clear()
                                except Exception:
                                    pass

                                st.session_state["msg_limpeza_prod_v1"] = (
                                    f"{len(registros_limpeza)} convocação(ões) de "
                                    f"{data_limpeza.strftime('%d/%m/%Y')} removida(s)."
                                )
                                st.rerun()

                        except Exception as e:
                            exibir_erro_amigavel(
                                "administracao",
                                "limpar_dados_producao",
                                e,
                                "Não foi possível concluir a exclusão dos registros.",
                            )

            with st.container(border=True):
                st.markdown("**Limpar todos os dados operacionais**")
                st.caption(
                    "Use esta opção para apagar todos os testes realizados no sistema. "
                    "Serão removidos convocações, apontamentos, serviços apontados, "
                    "conflitos, indisponibilidades, auditoria e registros de erro. "
                    "Obras e colaboradores serão mantidos."
                )

                st.warning(
                    "Esta ação é permanente e deixa o sistema sem histórico operacional."
                )

                confirmar_limpeza_total = st.checkbox(
                    "Entendo que todos os dados operacionais serão excluídos.",
                    key="confirmar_limpeza_total_admin_v68",
                )

                texto_limpeza_total = st.text_input(
                    'Digite "LIMPAR DADOS" para confirmar',
                    placeholder="LIMPAR DADOS",
                    key="texto_limpeza_total_admin_v68",
                )

                pode_limpar_total = (
                    confirmar_limpeza_total
                    and texto_limpeza_total.strip().upper() == "LIMPAR DADOS"
                )

                if st.button(
                    "Limpar todos os dados operacionais",
                    type="primary",
                    use_container_width=True,
                    disabled=not pode_limpar_total,
                    key="btn_limpar_todos_dados_admin_v68",
                ):
                    try:
                        tabelas_limpeza = [
                            "servicos_apontamento",
                            "apontamentos",
                            "conflitos_convocacao",
                            "indisponibilidades",
                            "convocacoes",
                            "auditoria",
                            "erros_sistema",
                        ]

                        if (
                            DB_BACKEND == "NEON"
                            and hasattr(supabase, "_connect")
                        ):
                            with supabase._connect() as conn:
                                with conn.cursor() as cur:
                                    existentes = []

                                    for tabela in tabelas_limpeza:
                                        cur.execute(
                                            "SELECT to_regclass(%s) AS tabela",
                                            (f"public.{tabela}",),
                                        )
                                        row = cur.fetchone()

                                        existe = (
                                            row.get("tabela")
                                            if isinstance(row, dict)
                                            else (
                                                row[0]
                                                if row
                                                else None
                                            )
                                        )

                                        if existe:
                                            existentes.append(tabela)

                                    if existentes:
                                        nomes_sql = ", ".join(
                                            f'"{t}"'
                                            for t in existentes
                                        )

                                        cur.execute(
                                            f"TRUNCATE TABLE {nomes_sql} "
                                            "RESTART IDENTITY CASCADE"
                                        )

                                conn.commit()

                        else:
                            # Fallback compatível: remove registro a registro.
                            for tabela in tabelas_limpeza:
                                try:
                                    registros = (
                                        supabase.table(tabela)
                                        .select("id")
                                        .execute()
                                        .data
                                        or []
                                    )

                                    for reg in registros:
                                        reg_id = reg.get("id")
                                        if reg_id is not None:
                                            (
                                                supabase.table(tabela)
                                                .delete()
                                                .eq("id", reg_id)
                                                .execute()
                                            )
                                except Exception:
                                    pass

                        try:
                            st.cache_data.clear()
                        except Exception:
                            pass

                        try:
                            limpar_cache_operacional()
                        except Exception:
                            pass

                        st.session_state[
                            "msg_limpeza_total_admin_v68"
                        ] = (
                            "Dados operacionais apagados com sucesso. "
                            "Obras e colaboradores foram preservados."
                        )

                        st.rerun()

                    except Exception as e:
                        exibir_erro_amigavel(
                            "administracao",
                            "limpar_todos_dados_operacionais",
                            e,
                            "Não foi possível concluir a limpeza total dos dados.",
                        )

            if st.session_state.get("msg_limpeza_total_admin_v68"):
                st.success(
                    st.session_state.pop(
                        "msg_limpeza_total_admin_v68"
                    )
                )

            if st.session_state.get("msg_limpeza_prod_v1"):
                st.success(
                    st.session_state.pop("msg_limpeza_prod_v1")
                )


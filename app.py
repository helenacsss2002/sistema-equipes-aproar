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


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


# --- LIMPEZA SELETIVA DE CACHE ---
def limpar_cache_operacional():
    """
    Atualiza apenas os caches do banco local.
    Não limpa o cache do Trello: isso evita uma nova chamada desnecessária
    ao quadro público após cada inclusão, exclusão ou sincronização.
    """
    for nome_funcao in (
        "buscar_obras", "buscar_colaboradores",
        "_buscar_convocacoes_intervalo",
    ):
        funcao = globals().get(nome_funcao)
        if funcao is not None and hasattr(funcao, "clear"):
            try:
                funcao.clear()
            except Exception:
                pass


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

VALOR_DIARIA_PROFISSIONAL = 241.74
VALOR_DIARIA_AJUDANTE = 182.34

def inferir_tipo_colaborador(funcao):
    """Classifica cadastros antigos quando a diária ainda não está nos novos valores fixos."""
    f = normalizar(funcao or "")
    termos_ajudante = ["AJUDANTE", "AUXILIAR", "AUX.", "AUX ", "SERVENTE"]
    return "Ajudante" if any(t in f for t in termos_ajudante) else "Profissional"

def valor_diaria_por_tipo(tipo):
    return VALOR_DIARIA_AJUDANTE if normalizar(tipo) == "AJUDANTE" else VALOR_DIARIA_PROFISSIONAL

def obter_valor_diaria_colaborador(colab):
    """Aplica R$ 241,74 para profissional e R$ 182,34 para ajudante em todo o sistema."""
    colab = colab or {}
    try:
        valor_cadastrado = float(colab.get("valor_diaria") or 0.0)
    except Exception:
        valor_cadastrado = 0.0

    # Novos cadastros já persistem exatamente um dos dois valores oficiais.
    if abs(valor_cadastrado - VALOR_DIARIA_PROFISSIONAL) < 0.01:
        return VALOR_DIARIA_PROFISSIONAL
    if abs(valor_cadastrado - VALOR_DIARIA_AJUDANTE) < 0.01:
        return VALOR_DIARIA_AJUDANTE

    # Compatibilidade com cadastros antigos (ex.: diária antiga de R$ 240,00).
    return valor_diaria_por_tipo(inferir_tipo_colaborador(colab.get("funcao", "")))

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
):
    """Dual-write do apontamento nas tabelas novas, mantendo a convocação legada intacta."""
    if not schema_producao_disponivel():
        return False
    try:
        conv_id = str(convocacao.get("id") or "")
        colab_id = str(convocacao.get("colaborador_id") or "")
        retroativo = bool(agora_aproar().date() > data_servico)
        obra_principal = dict_obras.get(obra_principal_id, {}) if "dict_obras" in globals() else {}
        with supabase._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO apontamentos (
                        convocacao_id, data_servico, colaborador_id, engenheiro, status,
                        valor_extra, observacao, apontado_em, apontado_por, retroativo, atualizado_em
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s,%s,NOW())
                    ON CONFLICT (convocacao_id) DO UPDATE SET
                        data_servico = EXCLUDED.data_servico,
                        colaborador_id = EXCLUDED.colaborador_id,
                        engenheiro = EXCLUDED.engenheiro,
                        status = EXCLUDED.status,
                        valor_extra = EXCLUDED.valor_extra,
                        observacao = EXCLUDED.observacao,
                        apontado_por = EXCLUDED.apontado_por,
                        retroativo = EXCLUDED.retroativo,
                        atualizado_em = NOW()
                    """,
                    (
                        conv_id, data_servico, colab_id, str(engenheiro), str(status),
                        float(valor_extra or 0), str(observacao_livre or ""), str(engenheiro), retroativo,
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
                "data_servico": data_servico, "status": status, "valor_extra": valor_extra,
                "obra_principal_id": str(obra_principal_id), "periodo_principal": periodo_principal,
                "servicos_adicionais": servicos_adicionais or [], "retroativo": retroativo,
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
    """Compatibilidade entre o modelo antigo (lista de nomes) e o novo (serviço + período)."""
    meta = meta or {}
    saida = []
    vistos = set()

    for item in meta.get("servicos_adicionais", []) or []:
        if isinstance(item, dict):
            nome = str(item.get("servico") or "").strip()
            periodo = str(item.get("periodo") or "").strip() or "Não informado"
        else:
            nome = str(item or "").strip()
            periodo = "Não informado"
        chave = normalizar(nome)
        if nome and chave not in vistos:
            saida.append({"servico": nome, "periodo": periodo})
            vistos.add(chave)

    # Registros das versões anteriores continuam válidos.
    for nome in meta.get("servicos_extras", []) or []:
        nome = str(nome or "").strip()
        chave = normalizar(nome)
        if nome and chave not in vistos:
            saida.append({"servico": nome, "periodo": "Não informado"})
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
):
    meta = obter_metadata_operacional(convocacao.get("observacao") or "")
    agora = agora_aproar()
    if not meta.get("apontado_em"):
        meta["apontado_em"] = agora.isoformat()
    meta["ultimo_apontamento_em"] = agora.isoformat()
    meta["apontamento_atrasado"] = bool(agora.date() > data_servico)
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
        if nome:
            adicionais.append({"servico": nome, "periodo": periodo})

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
        existente = next((c for c in atuais if normalizar(c.get("nome", "")) == normalizar(nome_limpo)), None)
        if existente:
            return existente.get("id"), existente, "Cadastro existente localizado e reutilizado."

        funcao_texto = str(funcao_livre or "").strip()
        if avulso:
            funcao_salva = f"AVULSO - {funcao_texto}" if funcao_texto else f"AVULSO - {str(tipo).upper()}"
        else:
            funcao_salva = funcao_texto if funcao_texto else str(tipo).upper()

        valor = valor_diaria_por_tipo(tipo)
        criado = supabase.table("colaboradores").insert({
            "nome": nome_limpo.upper(),
            "funcao": limpar_funcao(funcao_salva),
            "valor_diaria": valor
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
    ws.merge_cells("A1:E1")
    ws["A1"] = "APROAR ENGENHARIA - BASE ATUALIZADA DE COLABORADORES"
    ws["A1"].font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 24

    ws.merge_cells("A2:E2")
    ws["A2"] = f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | Total de colaboradores: {len(lista_colaboradores)}"
    ws["A2"].font = Font(name="Arial", size=9, italic=True, color="64748B")
    ws["A2"].alignment = Alignment(horizontal="left")

    headers = ["Nome", "Função", "Categoria", "Valor da Diária (R$)", "Avulso"]
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
        categoria = "Ajudante" if abs(valor_diaria - VALOR_DIARIA_AJUDANTE) < 0.01 else "Profissional"
        avulso = "SIM" if normalizar(funcao).startswith("AVULSO -") else "NÃO"

        valores = [
            str(colab.get("nome") or "").strip(),
            funcao,
            categoria,
            valor_diaria,
            avulso,
        ]
        for col_idx, valor in enumerate(valores, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=valor)
            cell.font = Font(name="Arial", size=9)
            cell.border = borda
            cell.alignment = Alignment(vertical="center", horizontal="left" if col_idx in [1, 2] else "center")
            if col_idx == 4:
                cell.number_format = 'R$ #,##0.00'
                cell.alignment = Alignment(horizontal="right", vertical="center")

    fim = linha_header + len(ordenados)
    if fim >= linha_header:
        ws.auto_filter.ref = f"A{linha_header}:E{fim}"
    ws.freeze_panes = "A5"

    larguras = {"A": 38, "B": 30, "C": 16, "D": 22, "E": 12}
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

        limpar_cache_operacional()
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
def buscar_colaboradores():
    try: 
        res = supabase.table("colaboradores").select("*").execute().data
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
obras = [o for o in obras_todas if not eh_registro_indisponibilidade(o)]
colaboradores = buscar_colaboradores() or []

dict_colaboradores = {c['id']: c for c in colaboradores} if colaboradores else {}
dict_obras = {o['id']: o for o in obras} if obras else {}

ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

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
]

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
    diaria = calcular_diaria_proporcional(status, obter_valor_diaria_colaborador(colab))
    extra_bruta = float(registro.get("valor_extra") or 0.0)
    extra = extra_bruta if status_eh_presenca(status) else 0.0
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
        "Diária (R$)": float(diaria),
        "Extra (R$)": extra,
        "Custo (R$)": float(diaria + extra),
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

        obra_add = _localizar_obra_por_nome_relatorio(
            nome,
            obra_principal.get("unidade") if obra_principal else "",
        )

        itens.append({
            "obra_id": str(obra_add.get("id") or ""),
            "obra": nome,
            "unidade": str(
                obra_add.get("unidade")
                or obra_principal.get("unidade")
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
    Retorna uma linha por colaborador/data/serviço com a diária corretamente
    distribuída entre os serviços executados.

    Exemplos:
      - Só manhã + 1 serviço = 1/2 diária nesse serviço.
      - Só manhã + 2 serviços = 1/4 diária em cada serviço.
      - Manhã em 2 serviços + tarde em 1 = 1/4 + 1/4 + 1/2.
      - Obras podem ser da mesma unidade ou de unidades diferentes.
    """
    grupos = {}

    for registro in registros or []:
        data = str(registro.get("data") or "")
        colaborador_id = str(
            registro.get("colaborador_id")
            or ""
        )
        chave_grupo = (data, colaborador_id)
        grupos.setdefault(chave_grupo, []).append(registro)

    linhas = []

    for (data, colaborador_id), regs in grupos.items():
        colab = dict_colaboradores.get(
            regs[0].get("colaborador_id"),
            {},
        )
        valor_diaria = float(
            obter_valor_diaria_colaborador(colab)
        )

        # Orçamento diário por bloco de presença.
        orcamento_blocos = {}
        for reg in regs:
            for bloco, peso in _blocos_presenca_registro_relatorio(reg).items():
                orcamento_blocos[bloco] = max(
                    float(orcamento_blocos.get(bloco, 0.0)),
                    float(peso),
                )

        # Serviços únicos do dia, preservando de qual registro vieram.
        servicos = {}
        extras_por_servico = {}

        for reg in regs:
            itens_reg = _servicos_do_registro_relatorio(reg)
            status_reg = normalizar_status_operacional(
                reg.get("status")
            )
            extra_reg = (
                float(reg.get("valor_extra") or 0.0)
                if status_eh_presenca(status_reg)
                else 0.0
            )

            # Extra não pode ser repetida ao expandir um mesmo registro.
            extra_por_item = (
                extra_reg / len(itens_reg)
                if itens_reg
                else 0.0
            )

            _, obs_livre = decompor_observacao_operacional(
                reg.get("observacao") or ""
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
                    },
                )

                periodo = normalizar_turno_convocacao(
                    item.get("periodo") or turno_da_convocacao(reg)
                )
                atual["periodos"].add(periodo)
                atual["engenheiros"].add(
                    str(reg.get("engenheiro") or "N/A")
                )
                atual["status"].append(status_reg)

                if obs_livre:
                    atual["observacoes"].append(obs_livre)

                extras_por_servico[chave_serv] = (
                    float(extras_por_servico.get(chave_serv, 0.0))
                    + extra_por_item
                )

        # Se não há serviço real, não há o que atribuir no relatório por obra.
        if not servicos:
            continue

        # Quais serviços participam de cada bloco (M/T/N).
        servicos_por_bloco = {
            bloco: []
            for bloco in orcamento_blocos.keys()
        }

        for chave_serv, serv in servicos.items():
            blocos_serv = set()
            for periodo in serv["periodos"]:
                blocos_serv.update(
                    _peso_periodo_relatorio(periodo).keys()
                )

            for bloco in servicos_por_bloco:
                if bloco in blocos_serv:
                    servicos_por_bloco[bloco].append(chave_serv)

        rateio_fracao = {
            chave: 0.0
            for chave in servicos.keys()
        }

        # Divide cada meia-diária/diária noturna entre os serviços daquele bloco.
        for bloco, peso_bloco in orcamento_blocos.items():
            participantes = list(
                dict.fromkeys(
                    servicos_por_bloco.get(bloco)
                    or []
                )
            )

            # Compatibilidade com registros antigos sem período confiável.
            if not participantes:
                participantes = list(servicos.keys())

            if not participantes:
                continue

            parte = float(peso_bloco) / len(participantes)
            for chave_serv in participantes:
                rateio_fracao[chave_serv] += parte

        # Segurança: garante que 100% do valor remunerável seja atribuído.
        total_esperado = sum(
            float(x)
            for x in orcamento_blocos.values()
        )
        total_rateado = sum(
            float(x)
            for x in rateio_fracao.values()
        )
        residual = max(0.0, total_esperado - total_rateado)

        if residual > 0.000001 and servicos:
            parte_residual = residual / len(servicos)
            for chave_serv in rateio_fracao:
                rateio_fracao[chave_serv] += parte_residual

        for chave_serv, serv in servicos.items():
            diaria_rateada = round(
                valor_diaria
                * float(rateio_fracao.get(chave_serv, 0.0)),
                2,
            )
            extra_rateada = round(
                float(extras_por_servico.get(chave_serv, 0.0)),
                2,
            )

            periodos = sorted(
                serv["periodos"],
                key=lambda p: {
                    "Manhã": 1,
                    "Tarde": 2,
                    "Noite": 3,
                    "Integral": 4,
                }.get(p, 9),
            )

            statuses = [
                s for s in serv["status"]
                if s
            ]
            status_exibido = (
                statuses[0]
                if statuses
                and len(set(statuses)) == 1
                else " / ".join(dict.fromkeys(statuses))
            )

            linhas.append({
                "Data": data,
                "obra_id": serv["obra_id"],
                "Obra": serv["obra"],
                "Unidade": serv["unidade"],
                "Período do serviço": " + ".join(periodos),
                "Engenheiro": " / ".join(
                    sorted(serv["engenheiros"])
                ),
                "Colaborador": str(
                    colab.get("nome")
                    or "Desconhecido"
                ),
                "Função": str(
                    colab.get("funcao")
                    or "-"
                ),
                "Status": status_exibido,
                "Diária (R$)": diaria_rateada,
                "Extra (R$)": extra_rateada,
                "Custo (R$)": round(
                    diaria_rateada + extra_rateada,
                    2,
                ),
                "Observação": " | ".join(
                    dict.fromkeys(serv["observacoes"])
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
    taxa_presenca = (presentes / total * 100) if total else 0.0

    st.markdown(
        f"""
        <div class="aproar-dash-metrics">
            <div class="aproar-dash-card"><div class="aproar-dash-label">Convocados / registros</div><div class="aproar-dash-value">{total}</div><div class="aproar-dash-note">no período</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Presentes</div><div class="aproar-dash-value">{presentes}</div><div class="aproar-dash-note">{taxa_presenca:.1f}% de presença</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Faltas</div><div class="aproar-dash-value">{faltas}</div><div class="aproar-dash-note">registro(s)</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Atestados</div><div class="aproar-dash-value">{atestados}</div><div class="aproar-dash-note">registro(s)</div></div>
            <div class="aproar-dash-card"><div class="aproar-dash-label">Custo total</div><div class="aproar-dash-value" style="font-size:24px">{formatar_reais(custo)}</div><div class="aproar-dash-note">Extras: {formatar_reais(total_extra)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')} • "
        f"Presença: {taxa_presenca:.1f}% • Extras já incluídas no custo"
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
    cols = ["Data", "Engenheiro", "Unidade", "Serviço(s)", "Colaborador", "Status", "Diária (R$)", "Extra (R$)", "Custo (R$)"]
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
                "Diária (R$)",
                "Extra (R$)",
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

    ind = obter_indisponibilidade_colaborador(
        colaborador_id,
        data_servico,
    )
    if ind:
        return False, (
            f"Colaborador indisponível: {ind.get('motivo','Indisponível')} "
            f"({ind.get('inicio')} a {ind.get('fim')})."
        )

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
):
    """
    Inclui 1 ou mais serviços para o mesmo colaborador no apontamento.

    Cada item de `servicos` deve conter:
        {"obra_id": ..., "turno": ...}

    Os serviços são validados juntos e gravados em lote, evitando inclusão
    parcial quando o próprio formulário contém turnos incompatíveis.
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

        chave = (str(obra_id), turno)
        if chave in vistos:
            continue

        vistos.add(chave)
        itens.append({
            "obra_id": obra_id,
            "turno": turno,
        })

    if not itens:
        return False, "Selecione pelo menos um serviço."

    # Dois serviços do mesmo colaborador não podem ocupar turnos sobrepostos.
    for i, atual in enumerate(itens):
        for outro in itens[i + 1:]:
            if turnos_se_sobrepoem(
                atual["turno"],
                outro["turno"],
            ):
                return False, (
                    f"Os turnos {atual['turno']} e {outro['turno']} se sobrepõem. "
                    "Escolha turnos compatíveis para os dois serviços."
                )

    ind = obter_indisponibilidade_colaborador(
        colaborador_id,
        data_servico,
    )
    if ind:
        return False, (
            f"Colaborador indisponível: {ind.get('motivo','Indisponível')} "
            f"({ind.get('inicio')} a {ind.get('fim')})."
        )

    existentes = buscar_convocacao_existente(
        colaborador_id,
        data_servico,
    )

    # Valida todos os novos serviços contra o que já existe antes de gravar.
    for novo in itens:
        obra_nova = (
            dict_obras.get(novo["obra_id"], {})
            if "dict_obras" in globals()
            else {}
        )
        unidade_nova = str(
            obra_nova.get("unidade") or ""
        )

        for reg in existentes:
            turno_existente = turno_da_convocacao(reg)

            if not turnos_se_sobrepoem(
                turno_existente,
                novo["turno"],
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
                    turno_tentativa=novo["turno"],
                    unidade_tentativa=unidade_nova,
                )
                return False, (
                    f"Esse colaborador já está com {eng_existente} em "
                    f"{turno_existente}. O conflito foi registrado para o Paulo."
                )

            return False, (
                f"Esse colaborador já está no seu apontamento em "
                f"{turno_existente}. Escolha outro turno."
            )

    _garantir_multiturno_neon()

    agora = agora_aproar()
    payloads = []

    for novo in itens:
        turno_novo = novo["turno"]

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
            "servicos_extras": [],
            "servicos_adicionais": [],
            "periodo_servico_principal": turno_novo,
        }

        status_inicial = {
            "Manhã": "Presente (Só Manhã)",
            "Tarde": "Presente (Só Tarde)",
        }.get(
            turno_novo,
            "Presente (Integral)",
        )

        payload = {
            "obra_id": novo["obra_id"],
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

    try:
        retorno = (
            supabase.table("convocacoes")
            .insert(payloads)
            .execute()
            .data
            or []
        )

        # Mantém auditoria individual dos registros criados.
        for idx, novo in enumerate(itens):
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
                    "turno": novo["turno"],
                    "obra_id": str(novo["obra_id"]),
                },
                contexto={
                    "retroativo": bool(
                        agora.date() > data_servico
                    ),
                    "origem": "portal_engenheiro_multisservico",
                },
            )

        limpar_cache_operacional()

        if len(itens) == 1:
            return True, (
                f"Colaborador incluído em {itens[0]['turno']}."
            )

        return True, (
            f"{len(itens)} serviços adicionados para o colaborador."
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
            elif data_apont < agora_aproar().date() and not meta_atual.get("apontado_em"):
                st.warning("🟧 Este apontamento é retroativo. Ao salvar, o atraso será registrado.")

            with st.form(key=f"{key_prefix}_form_{c_id}"):
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

                d1, d2 = st.columns([1, 2])
                with d1:
                    val_extra = st.number_input(
                        "Extra (R$)",
                        min_value=0.0,
                        value=(float(conv.get("valor_extra") or 0.0) if status_eh_presenca(status_sel) else 0.0),
                        step=10.0,
                        disabled=not status_eh_presenca(status_sel),
                        key=f"{key_prefix}_extra_{c_id}",
                        help="Extra é valor adicional. O colaborador continua contando como presente.",
                    )
                with d2:
                    obs_nova = st.text_input("Observação / justificativa", value=obs_livre, key=f"{key_prefix}_obs_{c_id}")
                salvar = st.form_submit_button("💾 SALVAR APONTAMENTO", type="primary", use_container_width=True)

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
                    )
                    nova_obs = montar_observacao_operacional(turno, obs_nova, meta)
                    try:
                        valor_extra_final = float(val_extra) if status_eh_presenca(status_sel) else 0.0
                        supabase.table("convocacoes").update({
                            "obra_id": mapa_obras[obra_sel],
                            "status": status_sel,
                            "valor_extra": valor_extra_final,
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
    """Busca convocações do período e prepara extras e faltas/atestados sem expor Obra/Serviço."""
    # Reutiliza o cache curto compartilhado com Dashboard/Relatórios/Indicadores.
    registros = _buscar_convocacoes_intervalo(data_inicio, data_fim)

    extras = []
    ausencias = []
    for row in registros:
        obra = dict_obras.get(row.get("obra_id"), {})
        colab = dict_colaboradores.get(row.get("colaborador_id"), {})
        unidade = str(obra.get("unidade") or "NÃO IDENTIFICADA")
        nome = str(colab.get("nome") or "NÃO IDENTIFICADO")
        funcao = str(colab.get("funcao") or "-")
        status = normalizar_status_operacional(row.get("status") or "")
        data_iso = str(row.get("data") or "")
        try:
            data_br = datetime.date.fromisoformat(data_iso).strftime("%d/%m/%Y")
        except Exception:
            data_br = data_iso
        try:
            valor_extra = float(row.get("valor_extra") or 0.0)
        except Exception:
            valor_extra = 0.0

        base = {
            "Data": data_br,
            "Data ISO": data_iso,
            "Colaborador": nome,
            "Função": funcao,
            "Unidade": unidade,
            "Engenheiro": str(row.get("engenheiro") or "N/A"),
            "Status": status,
        }

        # Financeiro considera como extra qualquer valor lançado pelo engenheiro,
        # independentemente do status do apontamento.
        if valor_extra > 0 and status_eh_presenca(status):
            item_extra = dict(base)
            item_extra["Valor Extra (R$)"] = valor_extra
            extras.append(item_extra)

        if status in ["Falta", "Atestado"]:
            ausencias.append(dict(base))

    extras.sort(key=lambda x: (x.get("Data ISO", ""), normalizar(x.get("Colaborador", ""))))
    ausencias.sort(key=lambda x: (x.get("Data ISO", ""), normalizar(x.get("Colaborador", ""))))
    return extras, ausencias


def resumir_extras_financeiro(extras):
    """Consolida as extras por colaborador para o pagamento semanal."""
    if not extras:
        return pd.DataFrame(columns=["Colaborador", "Função", "Unidades", "Lançamentos", "Total Extra (R$)"])

    df = pd.DataFrame(extras)
    resumo = (
        df.groupby(["Colaborador", "Função"], dropna=False)
        .agg(
            Unidades=("Unidade", lambda s: ", ".join(sorted(set(str(v) for v in s if str(v).strip())))),
            Lançamentos=("Valor Extra (R$)", "size"),
            **{"Total Extra (R$)": ("Valor Extra (R$)", "sum")}
        )
        .reset_index()
        .sort_values(by=["Total Extra (R$)", "Colaborador"], ascending=[False, True])
    )
    return resumo


def gerar_excel_financeiro(extras, ausencias, data_inicio, data_fim, data_pagamento):
    """Gera relatório financeiro semanal em Excel."""
    wb = openpyxl.Workbook()
    ws_resumo = wb.active
    ws_resumo.title = "Resumo Extras"

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

    resumo = resumir_extras_financeiro(extras)
    total_extra = sum(float(x.get("Valor Extra (R$)") or 0) for x in extras)
    subtitulo = (
        f"Ciclo: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} | "
        f"Pagamento: {data_pagamento.strftime('%d/%m/%Y')} | Total: {formatar_reais(total_extra)}"
    )
    cabecalho_planilha(ws_resumo, "APROAR - RELATÓRIO SEMANAL DE EXTRAS", subtitulo, 5)
    headers_resumo = ["Colaborador", "Função", "Unidades", "Lançamentos", "Total Extra (R$)"]
    for ci, nome in enumerate(headers_resumo, 1):
        cell = ws_resumo.cell(4, ci, nome)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center")
    for ri, (_, r) in enumerate(resumo.iterrows(), 5):
        vals = [r["Colaborador"], r["Função"], r["Unidades"], int(r["Lançamentos"]), float(r["Total Extra (R$)"])]
        for ci, val in enumerate(vals, 1):
            cell = ws_resumo.cell(ri, ci, val)
            cell.border = borda
            cell.font = Font(name="Arial", size=9)
            if ci == 5:
                cell.number_format = 'R$ #,##0.00'
    ws_resumo.freeze_panes = "A5"
    for col, largura in {"A": 38, "B": 28, "C": 38, "D": 14, "E": 20}.items():
        ws_resumo.column_dimensions[col].width = largura

    ws_det = wb.create_sheet("Detalhe Extras")
    cabecalho_planilha(ws_det, "DETALHAMENTO DE EXTRAS", subtitulo, 6)
    headers_det = ["Data", "Colaborador", "Função", "Unidade", "Engenheiro", "Valor Extra (R$)"]
    for ci, nome in enumerate(headers_det, 1):
        cell = ws_det.cell(4, ci, nome)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center")
    for ri, item in enumerate(extras, 5):
        vals = [item["Data"], item["Colaborador"], item["Função"], item["Unidade"], item["Engenheiro"], item["Valor Extra (R$)"]]
        for ci, val in enumerate(vals, 1):
            cell = ws_det.cell(ri, ci, val)
            cell.border = borda
            cell.font = Font(name="Arial", size=9)
            if ci == 6:
                cell.number_format = 'R$ #,##0.00'
    ws_det.freeze_panes = "A5"
    for col, largura in {"A": 14, "B": 38, "C": 28, "D": 28, "E": 18, "F": 20}.items():
        ws_det.column_dimensions[col].width = largura

    ws_aus = wb.create_sheet("Faltas e Atestados")
    cabecalho_planilha(
        ws_aus,
        "FALTAS E ATESTADOS DO CICLO",
        f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        6
    )
    headers_aus = ["Data", "Colaborador", "Função", "Unidade", "Status", "Engenheiro"]
    for ci, nome in enumerate(headers_aus, 1):
        cell = ws_aus.cell(4, ci, nome)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center")
    for ri, item in enumerate(ausencias, 5):
        vals = [item["Data"], item["Colaborador"], item["Função"], item["Unidade"], item["Status"], item["Engenheiro"]]
        for ci, val in enumerate(vals, 1):
            cell = ws_aus.cell(ri, ci, val)
            cell.border = borda
            cell.font = Font(name="Arial", size=9)
    ws_aus.freeze_panes = "A5"
    for col, largura in {"A": 14, "B": 38, "C": 28, "D": 28, "E": 16, "F": 18}.items():
        ws_aus.column_dimensions[col].width = largura

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def gerar_pdf_financeiro(extras, ausencias, data_inicio, data_fim, data_pagamento):
    """Gera um relatório financeiro compacto em PDF, sem Obra/Serviço."""
    pdf = FPDF(orientation="L")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 9, to_latin("APROAR - RELATÓRIO FINANCEIRO SEMANAL"), ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(
        0, 7,
        to_latin(
            f"Ciclo de extras: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} | "
            f"Pagamento previsto: {data_pagamento.strftime('%d/%m/%Y')}"
        ),
        ln=True, align="C"
    )
    pdf.ln(3)

    resumo = resumir_extras_financeiro(extras)
    total_extra = sum(float(x.get("Valor Extra (R$)") or 0) for x in extras)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, to_latin(f"EXTRAS - TOTAL A PAGAR: {formatar_reais(total_extra)}"), ln=True)

    widths = [72, 48, 72, 28, 36]
    headers = ["Colaborador", "Função", "Unidade(s)", "Lanç.", "Total"]
    pdf.set_font("Arial", "B", 8)
    for w, h in zip(widths, headers):
        pdf.cell(w, 6, to_latin(h), border=1, align="C")
    pdf.ln()
    pdf.set_font("Arial", "", 8)
    if resumo.empty:
        pdf.cell(sum(widths), 6, to_latin("Nenhuma extra lançada neste ciclo."), border=1, ln=True)
    else:
        for _, r in resumo.iterrows():
            vals = [
                str(r["Colaborador"])[:34], str(r["Função"])[:22], str(r["Unidades"])[:33],
                str(int(r["Lançamentos"])), formatar_reais(float(r["Total Extra (R$)"]))
            ]
            aligns = ["L", "L", "L", "C", "R"]
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
            aligns = ["C", "L", "L", "L", "C", "C"]
            for w, v, a in zip(widths2, vals, aligns):
                pdf.cell(w, 6, to_latin(v), border=1, align=a)
            pdf.ln()

    return pdf.output(dest="S").encode("latin1")

# --- ACESSO SIMPLES: VISUALIZAÇÃO LIVRE + UMA SENHA ÚNICA DE EDIÇÃO ---
def _obter_senha_edicao():
    """
    Aceita qualquer um destes formatos no secrets.toml:

    SENHA_EDICAO = "sua_senha"

    ou:

    [acesso]
    senha_edicao = "sua_senha"

    Quem não informar a senha permanece em modo somente leitura.
    """
    senha = ""
    try:
        senha = str(st.secrets.get("SENHA_EDICAO", "") or "").strip()
    except Exception:
        senha = ""

    if senha:
        return senha

    try:
        bloco = st.secrets.get("acesso", {})
        senha = str(bloco.get("senha_edicao", "") or "").strip()
    except Exception:
        senha = ""
    return senha


def _edicao_liberada():
    return bool(st.session_state.get("edicao_liberada", False))


def _render_desbloqueio_edicao():
    """Mostra um acesso discreto para quem possui a senha única de edição."""
    senha_configurada = _obter_senha_edicao()
    with st.expander("🔐 Tenho acesso para editar", expanded=False):
        if not senha_configurada:
            st.info("A senha de edição ainda não foi configurada nos Secrets. O sistema está em modo somente leitura.")
            st.code('SENHA_EDICAO = "sua_senha"', language="toml")
            return

        st.caption("Digite a senha de edição. Não é necessário usuário individual.")
        with st.form("form_desbloquear_edicao", clear_on_submit=True):
            senha_digitada = st.text_input("Senha de edição", type="password")
            liberar = st.form_submit_button("LIBERAR EDIÇÃO", type="primary", use_container_width=True)

        if liberar:
            if hmac.compare_digest(str(senha_digitada), str(senha_configurada)):
                st.session_state["edicao_liberada"] = True
                st.success("Edição liberada.")
                st.rerun()
            else:
                st.error("Senha incorreta.")


def _logout_disponivel():
    """No novo modelo, 'sair' significa voltar ao modo somente leitura."""
    if _edicao_liberada():
        if st.button("🔒 BLOQUEAR EDIÇÃO", key="bloquear_edicao_topo"):
            st.session_state["edicao_liberada"] = False
            st.rerun()

parametros_url = st.query_params
modo_campo_solicitado = "eng" in parametros_url or parametros_url.get("modo") in ["campo", "eng"]
modo_financeiro_solicitado = (
    "financeiro" in parametros_url
    or "fin" in parametros_url
    or parametros_url.get("modo") in ["financeiro", "fin"]
)
modo_visualizador_solicitado = "view" in parametros_url or parametros_url.get("modo") in ["visualizador", "view"]

edicao_liberada = _edicao_liberada()

# REGRA DE ACESSO:
# 1) ?eng é SEMPRE o Portal do Engenheiro e mantém as funções operacionais.
# 2) ?financeiro é SEMPRE o Portal Financeiro.
# 3) A URL administrativa normal abre em visualização para quem não informou a senha.
# 4) A mesma URL administrativa libera o painel completo após a senha de edição.
# 5) ?view permanece apenas como atalho opcional para consulta, sem interferir no ?eng.
if modo_campo_solicitado:
    modo_campo = True
    modo_financeiro = False
    modo_visualizador = False
elif modo_financeiro_solicitado:
    modo_campo = False
    modo_financeiro = True
    modo_visualizador = False
elif modo_visualizador_solicitado:
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = True
elif not edicao_liberada:
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = True
else:
    modo_campo = False
    modo_financeiro = False
    modo_visualizador = False

if modo_visualizador:
    st.markdown("## 👁️ Painel Administrativo — Visualização")
    st.caption("Dashboard, Relatórios e Indicadores ficam disponíveis para consulta. Use a senha de edição para liberar o painel administrativo completo.")
    _render_desbloqueio_edicao()
    secao_view = st.radio(
        "Navegação",
        ["🎛️ DASHBOARD", "📊 RELATÓRIOS", "📈 INDICADORES"],
        horizontal=True,
        label_visibility="collapsed",
        key="nav_visualizador_geral",
    )
    if secao_view == "🎛️ DASHBOARD":
        render_dashboard_consulta("view_dash")
    elif secao_view == "📊 RELATÓRIOS":
        render_relatorio_visualizador("view_rel")
    else:
        render_indicadores_cumprimento("view_ind")

elif modo_campo:
    # =====================================================================
    # PORTAL DO ENGENHEIRO — MOBILE FIRST / MENOS CLIQUES
    # =====================================================================
    import html as _html

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
    </style>
    """)

    def _feedback_salvo_mobile(mensagem):
        """Mostra confirmação pequena por 2 segundos antes de atualizar a tela."""
        try:
            st.toast(mensagem)
        except Exception:
            st.caption(f"✓ {mensagem}")
        time.sleep(2)

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
        <div class="engm-head">
            <div class="engm-brand">
                <div class="engm-kicker">APROAR · Campo</div>
                <div class="engm-title">Minha equipe</div>
            </div>
            <div class="engm-date">
                Hoje<br><b>{hoje_campo.strftime('%d/%m')}</b>
                &nbsp;·&nbsp;
                Próximo<br><b>{amanha_campo.strftime('%d/%m')}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    engenheiro_campo = st.selectbox(
        "Engenheiro",
        ENGENHEIROS,
        key="engenheiro_campo_mobile",
    )

    area_campo = st.radio(
        "Navegação",
        ["Hoje", "Amanhã", "Disponibilidade"],
        horizontal=True,
        label_visibility="collapsed",
        key="eng_mobile_nav",
    )

    # =====================================================================
    # HOJE — RESUMO + CONVOCADOS + APONTAMENTO NA MESMA TELA
    # =====================================================================
    if area_campo == "Hoje":
        data_apont = st.date_input(
            "Data do apontamento",
            value=hoje_campo,
            format="DD/MM/YYYY",
            key="engm_data_apont",
        )

        convocacoes_data = _enriquecer_convocacoes_campo(
            _buscar_convocacoes_campo(
                engenheiro_campo,
                data_apont,
            )
        )

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
            <div class="engm-summary">
                <div class="engm-summary-item">
                    <div class="engm-summary-label">Equipe</div>
                    <div class="engm-summary-value">{total_data}</div>
                    <div class="engm-summary-note">na data</div>
                </div>
                <div class="engm-summary-item {classe_pend}">
                    <div class="engm-summary-label">Pendentes</div>
                    <div class="engm-summary-value">{pendentes_data}</div>
                    <div class="engm-summary-note">{apontados_data} concluído(s)</div>
                </div>
                <div class="engm-summary-item {classe_aus}">
                    <div class="engm-summary-label">Ausências</div>
                    <div class="engm-summary-value">{ausencias_data}</div>
                    <div class="engm-summary-note">falta / atestado</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if data_apont < hoje_campo:
            st.warning(
                "Apontamento retroativo. O sistema registrará o atraso automaticamente."
            )

        st.markdown(
            '<div class="engm-section-title">Apontar equipe</div>'
            '<div class="engm-section-sub">'
            'Status e serviço ficam visíveis. Extra, observação e 2º serviço ficam em “Mais opções”.'
            '</div>',
            unsafe_allow_html=True,
        )

        # Inclusão excepcional / retroativa.
        with st.expander(
            "Adicionar colaborador / avulso ao apontamento",
            expanded=False,
        ):
            st.caption(
                "Você pode lançar um ou dois serviços para a mesma pessoa. "
                "Quando houver 2 serviços, informe o turno de cada um."
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
                    ["— Selecione —"]
                    + list(labels_inc.keys()),
                    key="engm_inc_colab",
                )

                if nome_inc != "— Selecione —":
                    colaborador_id_inc = labels_inc.get(
                        nome_inc
                    )
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
                        "Categoria da diária",
                        ["Profissional", "Ajudante"],
                        key="engm_inc_avulso_tipo",
                    )

                with c_av2:
                    funcao_avulso_inc = st.text_input(
                        "Função (opcional)",
                        key="engm_inc_avulso_funcao",
                    )

            unidades_inc = sorted(
                {
                    str(o.get("unidade"))
                    for o in obras
                    if o.get("unidade")
                }
            )

            unidade_inc = (
                st.selectbox(
                    "Unidade",
                    unidades_inc,
                    key="engm_inc_unidade",
                )
                if unidades_inc
                else None
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

            # -------------------------------------------------------
            # 1º serviço
            # -------------------------------------------------------
            st.markdown("**1º serviço**")

            s1c1, s1c2 = st.columns(
                [1.55, .65]
            )

            with s1c1:
                obra_inc_1 = st.selectbox(
                    "Obra / Serviço",
                    ["— Selecione —"]
                    + list(mapa_inc.keys()),
                    key="engm_inc_obra_1",
                )

            with s1c2:
                turno_inc_1 = st.selectbox(
                    "Turno",
                    [
                        "Manhã",
                        "Tarde",
                        "Noite",
                        "Integral",
                    ],
                    key="engm_inc_turno_1",
                )

            adicionar_segundo = st.checkbox(
                "Adicionar 2º serviço",
                key="engm_inc_tem_segundo",
            )

            obra_inc_2 = "— Nenhum —"
            turno_inc_2 = "Tarde"

            if adicionar_segundo:
                st.markdown("**2º serviço**")

                s2c1, s2c2 = st.columns(
                    [1.55, .65]
                )

                with s2c1:
                    obra_inc_2 = st.selectbox(
                        "Obra / Serviço",
                        ["— Selecione —"]
                        + list(mapa_inc.keys()),
                        key="engm_inc_obra_2",
                    )

                with s2c2:
                    turno_inc_2 = st.selectbox(
                        "Turno",
                        [
                            "Manhã",
                            "Tarde",
                            "Noite",
                            "Integral",
                        ],
                        index=1,
                        key="engm_inc_turno_2",
                    )

            if st.button(
                "Adicionar ao apontamento",
                use_container_width=True,
                key="engm_inc_btn",
            ):
                # -----------------------------------------------
                # Validação dos serviços
                # -----------------------------------------------
                if obra_inc_1 not in mapa_inc:
                    st.warning(
                        "Selecione a obra/serviço principal."
                    )

                elif (
                    adicionar_segundo
                    and obra_inc_2 not in mapa_inc
                ):
                    st.warning(
                        "Selecione a 2ª obra/serviço."
                    )

                elif (
                    adicionar_segundo
                    and obra_inc_2 == obra_inc_1
                ):
                    st.warning(
                        "O 2º serviço deve ser diferente do 1º."
                    )

                elif (
                    adicionar_segundo
                    and turnos_se_sobrepoem(
                        turno_inc_1,
                        turno_inc_2,
                    )
                ):
                    st.warning(
                        "Os turnos dos dois serviços se sobrepõem. "
                        "Escolha turnos compatíveis, como Manhã + Tarde."
                    )

                else:
                    # -------------------------------------------
                    # Avulso: cria/localiza cadastro primeiro.
                    # -------------------------------------------
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
                        servicos_inc = [
                            {
                                "obra_id": mapa_inc[
                                    obra_inc_1
                                ],
                                "turno": turno_inc_1,
                            }
                        ]

                        if adicionar_segundo:
                            servicos_inc.append(
                                {
                                    "obra_id": mapa_inc[
                                        obra_inc_2
                                    ],
                                    "turno": turno_inc_2,
                                }
                            )

                        ok, msg = (
                            incluir_multiplos_servicos_direto_apontamento(
                                colaborador_id_inc,
                                engenheiro_campo,
                                data_apont,
                                servicos_inc,
                            )
                        )

                        (
                            st.success
                            if ok
                            else st.warning
                        )(msg)

                        if ok:
                            detalhe_servicos = (
                                f"{obra_inc_1} · {turno_inc_1}"
                            )

                            if adicionar_segundo:
                                detalhe_servicos += (
                                    f" + {obra_inc_2} · {turno_inc_2}"
                                )

                            limpar_cache_operacional()
                            _feedback_salvo_mobile(
                                f"Apontamento salvo · {nome_exibicao_inc}."
                            )
                            st.rerun()

        if not convocacoes_data:
            st.info(
                "Nenhuma equipe encontrada para esta data. "
                "Use a inclusão acima se precisar fazer um apontamento retroativo."
            )

        else:
            # Um único filtro aparece somente quando há mais de uma unidade.
            unidades_data = sorted(
                {
                    str(
                        (c.get("dados_obra") or {}).get(
                            "unidade",
                            "Desconhecida",
                        )
                    )
                    for c in convocacoes_data
                }
            )

            if len(unidades_data) > 1:
                unidade_filtro = st.selectbox(
                    "Filtrar unidade",
                    ["Todas"] + unidades_data,
                    key="engm_unidade_apont",
                )
            else:
                unidade_filtro = "Todas"

            render_campo = [
                c
                for c in convocacoes_data
                if unidade_filtro == "Todas"
                or str(
                    (c.get("dados_obra") or {}).get(
                        "unidade",
                        "",
                    )
                )
                == unidade_filtro
            ]

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
                        supabase.table("convocacoes").update(
                            {"status": "Presente (Integral)"}
                        ).eq(
                            "id",
                            conv.get("id"),
                        ).execute()
                    except Exception:
                        pass

                limpar_cache_operacional()
                _feedback_salvo_mobile(
                    "Todos foram marcados como presentes."
                )
                st.rerun()

            # Todas as convocações do dia são necessárias para aplicar a regra
            # do 2º serviço sem duplicar alguém que já tem outra convocação.
            try:
                todas_convs_data = (
                    supabase.table("convocacoes")
                    .select("*")
                    .eq("data", data_apont.isoformat())
                    .execute()
                    .data
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

            with st.form("engm_form_apontamentos"):
                for conv in render_campo:
                    c_id = conv.get("id")
                    colab = dict_colaboradores.get(
                        conv.get("colaborador_id"),
                        {
                            "nome": "Desconhecido",
                            "funcao": "-",
                        },
                    )
                    unidade = str(
                        (conv.get("dados_obra") or {}).get(
                            "unidade",
                            "Desconhecida",
                        )
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
                        obra_atual.get("nome")
                        or ""
                    )
                    idx_obra = (
                        opcoes_obras.index(
                            nome_obra_atual
                        )
                        if nome_obra_atual in mapa_obras
                        else 0
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

                    periodo_principal_atual = str(
                        meta_atual.get(
                            "periodo_servico_principal"
                        )
                        or turno_conv
                        or "Integral"
                    )

                    if (
                        periodo_principal_atual
                        not in periodos_servico
                    ):
                        periodo_principal_atual = "Outro"

                    adicionais_atuais = [
                        x
                        for x in _normalizar_servicos_adicionais(
                            meta_atual
                        )
                        if x.get("servico")
                        in mapa_obras
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

                    with st.container(border=True):
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

                        status_sel = st.selectbox(
                            "Status",
                            OPCOES_STATUS_PRESENCA,
                            index=idx_status,
                            key=f"engm_st_{c_id}",
                        )

                        obra_sel = st.selectbox(
                            "Obra / Serviço",
                            opcoes_obras,
                            index=idx_obra,
                            key=f"engm_obra_{c_id}",
                        )

                        periodo_principal = st.selectbox(
                            "Período no serviço",
                            periodos_servico,
                            index=periodos_servico.index(
                                periodo_principal_atual
                            ),
                            key=f"engm_periodo_{c_id}",
                        )

                        segundo_servico = "— Nenhum —"
                        segundo_periodo = "Tarde"

                        with st.expander(
                            "Mais opções",
                            expanded=False,
                        ):
                            val_extra = st.number_input(
                                "Extra (R$)",
                                min_value=0.0,
                                value=float(
                                    conv.get("valor_extra")
                                    or 0.0
                                ),
                                step=10.0,
                                key=f"engm_extra_{c_id}",
                                help=(
                                    "Se o status for falta ou atestado, "
                                    "o extra será salvo como zero."
                                ),
                            )

                            obs_nova = st.text_input(
                                "Observação / justificativa",
                                value=obs_livre,
                                key=f"engm_obs_{c_id}",
                            )

                            if not tem_conv_separada:
                                opcoes_adic = [
                                    "— Nenhum —"
                                ] + list(
                                    mapa_obras.keys()
                                )
                                adic_atual = (
                                    adicionais_atuais[0].get(
                                        "servico"
                                    )
                                    if adicionais_atuais
                                    else "— Nenhum —"
                                )
                                idx_adic = (
                                    opcoes_adic.index(
                                        adic_atual
                                    )
                                    if adic_atual
                                    in opcoes_adic
                                    else 0
                                )

                                segundo_servico = st.selectbox(
                                    "2º serviço na mesma unidade",
                                    opcoes_adic,
                                    index=idx_adic,
                                    key=f"engm_seg_serv_{c_id}",
                                )

                                periodo_adic_atual = (
                                    adicionais_atuais[0].get(
                                        "periodo",
                                        "Tarde",
                                    )
                                    if adicionais_atuais
                                    else "Tarde"
                                )

                                if (
                                    periodo_adic_atual
                                    not in periodos_servico
                                ):
                                    periodo_adic_atual = "Outro"

                                segundo_periodo = st.selectbox(
                                    "Período do 2º serviço",
                                    periodos_servico,
                                    index=periodos_servico.index(
                                        periodo_adic_atual
                                    ),
                                    key=f"engm_seg_periodo_{c_id}",
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
                        "segundo_servico": segundo_servico,
                        "segundo_periodo": segundo_periodo,
                        "tem_conv_separada": tem_conv_separada,
                        "val_extra": val_extra,
                        "obs_nova": obs_nova,
                        "turno_conv": turno_conv,
                    }

                salvar_todos = st.form_submit_button(
                    "Salvar equipe",
                    type="primary",
                    use_container_width=True,
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

                    if (
                        item["segundo_servico"]
                        == item["obra_sel"]
                        and item["segundo_servico"]
                        != "— Nenhum —"
                    ):
                        erros_validacao.append(
                            f"{nome_pessoa}: o 2º serviço deve ser diferente do principal."
                        )

                if erros_validacao:
                    for msg in erros_validacao:
                        st.warning(msg)

                else:
                    salvos = 0
                    falhas = []

                    for item in dados_form.values():
                        conv = item["conv"]
                        c_id = conv.get("id")
                        nome_pessoa = str(
                            item["colab"].get("nome")
                            or "Colaborador"
                        )

                        adicionais = []

                        if (
                            not item["tem_conv_separada"]
                            and item["segundo_servico"]
                            in item["mapa_obras"]
                        ):
                            adicionais.append(
                                {
                                    "servico": item[
                                        "segundo_servico"
                                    ],
                                    "periodo": item[
                                        "segundo_periodo"
                                    ],
                                }
                            )

                        meta = registrar_metadata_apontamento(
                            conv,
                            data_apont,
                            apontado_por=engenheiro_campo,
                            periodo_principal=item[
                                "periodo_principal"
                            ],
                            servicos_adicionais=adicionais,
                        )

                        nova_obs = montar_observacao_operacional(
                            item["turno_conv"],
                            item["obs_nova"],
                            meta,
                        )

                        valor_extra_final = (
                            float(item["val_extra"])
                            if status_eh_presenca(
                                item["status_sel"]
                            )
                            else 0.0
                        )

                        try:
                            obra_id_final = item[
                                "mapa_obras"
                            ][item["obra_sel"]]

                            supabase.table(
                                "convocacoes"
                            ).update(
                                {
                                    "obra_id": obra_id_final,
                                    "status": item[
                                        "status_sel"
                                    ],
                                    "valor_extra": (
                                        valor_extra_final
                                    ),
                                    "observacao": nova_obs,
                                }
                            ).eq(
                                "id",
                                c_id,
                            ).execute()

                            salvar_apontamento_estruturado(
                                conv,
                                data_apont,
                                engenheiro_campo,
                                item["status_sel"],
                                valor_extra_final,
                                item["obs_nova"],
                                obra_id_final,
                                item[
                                    "periodo_principal"
                                ],
                                adicionais,
                            )

                            salvos += 1

                        except Exception as e:
                            falhas.append(
                                f"{nome_pessoa}: {str(e)[:110]}"
                            )

                    limpar_cache_operacional()

                    for msg in falhas:
                        st.error(msg)

                    if salvos and not falhas:
                        _feedback_salvo_mobile(
                            f"Apontamento salvo · {salvos} registro(s)."
                        )
                        st.rerun()
                    elif salvos:
                        st.caption(
                            f"✓ {salvos} apontamento(s) foram salvos, mas houve pendências abaixo."
                        )

    # =====================================================================
    # AMANHÃ — CONVOCADOS + NOVA CONVOCAÇÃO NA MESMA TELA
    # =====================================================================
    elif area_campo == "Amanhã":
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
                    supabase.table("convocacoes")
                    .select("*")
                    .eq(
                        "data",
                        data_conv_auto.isoformat(),
                    )
                    .execute()
                    .data
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

            nome_manual = ""
            tipo_manual = "Profissional"
            funcao_manual = ""
            avulso_manual = False

            with st.expander(
                "Adicionar nome que não está na lista",
                expanded=False,
            ):
                nome_manual = st.text_input(
                    "Nome",
                    key="engm_manual_nome",
                    placeholder="Nome completo",
                )

                avulso_manual = st.checkbox(
                    "É avulso?",
                    key="engm_manual_avulso",
                )

                tipo_manual = st.selectbox(
                    "Categoria da diária",
                    [
                        "Profissional",
                        "Ajudante",
                    ],
                    key="engm_manual_tipo",
                )

                funcao_manual = st.text_input(
                    "Função (opcional)",
                    key="engm_manual_funcao",
                )

            if st.button(
                "Confirmar convocação",
                type="primary",
                use_container_width=True,
                key="engm_confirm_conv",
            ):
                if (
                    not equipe_selecionada
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

                                if nome_manual.strip():
                                    c_id_manual, colab_manual, msg_manual = (
                                        criar_ou_obter_colaborador_manual(
                                            nome_manual,
                                            tipo_manual,
                                            funcao_manual,
                                            avulso=avulso_manual,
                                        )
                                    )

                                    if c_id_manual:
                                        pessoas.append(
                                            (
                                                c_id_manual,
                                                str(
                                                    colab_manual.get("nome")
                                                    or nome_manual
                                                ),
                                            )
                                        )
                                    else:
                                        avisos.append(
                                            msg_manual
                                            or f"{nome_manual}: não foi possível cadastrar."
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
                                    limpar_cache_operacional()

                                    # Só os avisos precisam sobreviver ao rerun.
                                    if avisos:
                                        st.session_state["_engm_conv_feedback"] = {
                                            "avisos": avisos,
                                        }

                                    st.session_state["_engm_reset_convocacao"] = True

                                    _feedback_salvo_mobile(
                                        f"Convocação salva · {sucessos} pessoa(s)."
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
    st.markdown("### 💰 ACESSO FINANCEIRO")
    st.caption("Conferência semanal de extras, faltas e atestados. As extras são fechadas em ciclos de terça-feira a segunda-feira.")

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

    extras_fin, ausencias_fin = carregar_dados_financeiro(data_ini_fin, data_fim_fin)
    total_extra_fin = sum(float(x.get("Valor Extra (R$)") or 0.0) for x in extras_fin)
    nomes_extra_fin = {normalizar(x.get("Colaborador", "")) for x in extras_fin}
    total_faltas_fin = sum(1 for x in ausencias_fin if x.get("Status") == "Falta")
    total_atest_fin = sum(1 for x in ausencias_fin if x.get("Status") == "Atestado")

    tab_fin_extra, tab_fin_aus, tab_fin_rel = st.tabs([
        "💸 EXTRAS", "🚫 FALTAS / ATESTADOS", "📄 RELATÓRIO"
    ])

    with tab_fin_extra:
        fm1, fm2, fm3 = st.columns(3)
        fm1.metric("TOTAL A PAGAR", formatar_reais(total_extra_fin))
        fm2.metric("COLABORADORES", len(nomes_extra_fin))
        fm3.metric("LANÇAMENTOS", len(extras_fin))

        st.markdown("### Consolidado por colaborador")
        resumo_fin = resumir_extras_financeiro(extras_fin)
        if resumo_fin.empty:
            st.info("Nenhuma extra foi lançada neste ciclo.")
        else:
            resumo_view = resumo_fin.copy()
            resumo_view["Total Extra"] = resumo_view["Total Extra (R$)"].apply(formatar_reais)
            resumo_view = resumo_view.drop(columns=["Total Extra (R$)"])
            tabela_aproar(resumo_view, key="tbl_fin_resumo")

            st.markdown("### Detalhamento por dia")
            detalhe_extra_view = pd.DataFrame(extras_fin)[[
                "Data", "Colaborador", "Função", "Unidade", "Engenheiro", "Valor Extra (R$)"
            ]].copy()
            detalhe_extra_view["Valor Extra"] = detalhe_extra_view["Valor Extra (R$)"].apply(formatar_reais)
            detalhe_extra_view = detalhe_extra_view.drop(columns=["Valor Extra (R$)"])
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
            f"Pagamento das extras em **{data_pag_fin.strftime('%d/%m/%Y')}**."
        )
        st.info(
            f"Total de extras: {formatar_reais(total_extra_fin)} • "
            f"Faltas: {total_faltas_fin} • Atestados: {total_atest_fin}"
        )

        excel_fin = gerar_excel_financeiro(extras_fin, ausencias_fin, data_ini_fin, data_fim_fin, data_pag_fin)
        pdf_fin = gerar_pdf_financeiro(extras_fin, ausencias_fin, data_ini_fin, data_fim_fin, data_pag_fin)

        fr1, fr2 = st.columns(2)
        with fr1:
            st.download_button(
                "📊 BAIXAR RELATÓRIO EXCEL",
                data=excel_fin,
                file_name=f"financeiro_extras_{data_ini_fin.strftime('%d-%m-%Y')}_a_{data_fim_fin.strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_fin_excel"
            )
        with fr2:
            st.download_button(
                "📄 BAIXAR RELATÓRIO PDF",
                data=pdf_fin,
                file_name=f"financeiro_extras_{data_ini_fin.strftime('%d-%m-%Y')}_a_{data_fim_fin.strftime('%d-%m-%Y')}.pdf",
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
        st.caption("Modo de edição ativo")
        if st.button("Bloquear edição", key="bloquear_edicao_sidebar_ui4", use_container_width=True):
            st.session_state["edicao_liberada"] = False
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
                    <div class="ap-kpi-label">Pendentes</div>
                    <div class="ap-kpi-row"><div class="ap-kpi-value">{len(pendentes)}</div><div class="ap-kpi-badge">{int(pct_pendente)}%</div></div>
                    <div class="ap-kpi-note">apontamento(s) a concluir</div>
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
                '<span>Há colaboradores ainda sem Obra/Serviço definida no dia selecionado.</span></div>'
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
            "Fechamento de custos, apontamentos e exportações por período.",
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
            obras_rel_lista = sorted(list(set([o['nome'] for o in obras]))) if obras else []
            obra_relatorio = st.selectbox("Filtro por Obra:", ["TODAS AS OBRAS"] + obras_rel_lista, key="obra_rel")

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
                                    "APROAR - RELATÓRIO DE CUSTOS"
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

                            cabecalhos = [
                                ("Data", 22, "C"),
                                ("Colaborador", 53, "L"),
                                ("Função", 36, "L"),
                                ("Engenheiro", 30, "C"),
                                ("Status", 37, "C"),
                                ("Turno/Período", 27, "C"),
                                ("Diária", 24, "C"),
                                ("Extra", 22, "C"),
                                ("Observação", 27, "L"),
                            ]

                            pdf.set_font(
                                "Arial",
                                "B",
                                8,
                            )
                            for idx, (
                                titulo,
                                largura,
                                alinhamento,
                            ) in enumerate(cabecalhos):
                                pdf.cell(
                                    largura,
                                    6,
                                    to_latin(titulo),
                                    border=1,
                                    align=alinhamento,
                                    ln=(
                                        idx
                                        == len(cabecalhos) - 1
                                    ),
                                )

                            pdf.set_font(
                                "Arial",
                                "",
                                7.5,
                            )

                            for _, row in df_obra.iterrows():
                                valores = [
                                    (
                                        str(row["Data"]),
                                        22,
                                        "C",
                                    ),
                                    (
                                        str(row["Colaborador"])[:26],
                                        53,
                                        "L",
                                    ),
                                    (
                                        str(row["Função"])[:18],
                                        36,
                                        "L",
                                    ),
                                    (
                                        str(row["Engenheiro"])[:14],
                                        30,
                                        "C",
                                    ),
                                    (
                                        str(row["Status"])[:18],
                                        37,
                                        "C",
                                    ),
                                    (
                                        str(
                                            row[
                                                "Período do serviço"
                                            ]
                                        )[:14],
                                        27,
                                        "C",
                                    ),
                                    (
                                        f"R$ {float(row['Diária (R$)']):.2f}",
                                        24,
                                        "C",
                                    ),
                                    (
                                        f"R$ {float(row['Extra (R$)']):.2f}",
                                        22,
                                        "C",
                                    ),
                                    (
                                        str(
                                            row.get(
                                                "Observação",
                                                "",
                                            )
                                        )[:18],
                                        27,
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
                                227,
                                7,
                                to_latin("TOTAL DA OBRA:"),
                                border=0,
                                align="R",
                            )
                            pdf.cell(
                                44,
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
                                f"relatorio_custos_"
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
                            "GUSTAVO": "FEF9C3",
                            "JOEL": "F3E8FF",
                            "NETO": "FFEDD5",
                            "SOARES": "FFE4E6",
                            "GABRIEL": "CCFBF1",
                            "PAULO": "F1F5F9",
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

                                for c_idx in range(1, 10):
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
                                    "Turno / Período",
                                    "Diária Rateada (R$)",
                                    "Extra (R$)",
                                    "Custo Total (R$)",
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
                                        f"=F{current_row}+G{current_row}"
                                    )

                                    linha_dados = [
                                        r["Colaborador"],
                                        r["Função"],
                                        r["Engenheiro"],
                                        r["Status"],
                                        r["Período do serviço"],
                                        float(r["Diária (R$)"]),
                                        float(r["Extra (R$)"]),
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

                                        if c_idx in [6, 7, 8]:
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
                                    column=7,
                                    value="TOTAL DA OBRA:",
                                ).font = Font(
                                    name="Arial",
                                    size=10,
                                    bold=True,
                                )
                                ws.cell(
                                    row=current_row,
                                    column=7,
                                ).alignment = Alignment(
                                    horizontal="right"
                                )

                                celula_subtotal = ws.cell(
                                    row=current_row,
                                    column=8,
                                    value=(
                                        f"=SUM(H{inicio_dados_obra}:"
                                        f"H{fim_dados_obra})"
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
                                f"apontamentos_rateados_"
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
        tab_cad_obra, tab_cad_colab, tab_import_colab, tab_limpeza = st.tabs(["🏗️ Obras", "👷 Colaboradores", "📤 Importar Colaboradores", "🗑️ Limpeza de Dados"])
        
        with tab_cad_obra:
            st.markdown("**Cadastrar nova obra**")
            with st.form("form_cad_obra"):
                nome_obra = st.text_input("Nome da Obra (Ex: 1863, 1383...):")
                unidade_obra = st.text_input("Unidade (Ex: CENTRO, MUSEU, FIEC...):")
                submit_obra = st.form_submit_button("Cadastrar Obra")
                if submit_obra:
                    if nome_obra and unidade_obra:
                        supabase.table("obras").insert({"nome": nome_obra, "unidade": unidade_obra.upper()}).execute()
                        limpar_cache_operacional()
                        st.success("Obra cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha todos os campos.")

        with tab_cad_colab:
            st.markdown("**Cadastrar novo colaborador**")
            with st.form("form_cad_colab"):
                nome_colab = st.text_input("Nome Completo:")
                tipo_colab = st.selectbox("Categoria da diária:", ["Profissional", "Ajudante"], key="tipo_cad_colab")
                funcao_colab = st.text_input("Função / Cargo:")
                diaria_colab = valor_diaria_por_tipo(tipo_colab)
                st.caption(f"Valor aplicado automaticamente: {formatar_reais(diaria_colab)}")
                submit_colab = st.form_submit_button("Cadastrar Colaborador")
                if submit_colab:
                    if nome_colab:
                        funcao_salva = limpar_funcao(funcao_colab) if funcao_colab.strip() else tipo_colab.upper()
                        try:
                            supabase.table("colaboradores").insert({
                                "nome": nome_colab.strip().upper(),
                                "funcao": funcao_salva,
                                "valor_diaria": diaria_colab
                            }).execute()
                            limpar_cache_operacional()
                            st.success("Colaborador cadastrado com sucesso!")
                            st.rerun()
                        except Exception:
                            st.error("Não foi possível cadastrar. Verifique se esse nome já existe.")
                    else:
                        st.warning("Informe o nome do colaborador.")

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

                    opcoes_valor = ["(selecione)"] + colunas
                    idx_valor = (
                        opcoes_valor.index(col_valor_auto)
                        if col_valor_auto in colunas
                        else 0
                    )
                    col_valor_import = st.selectbox(
                        "Coluna VALOR DO COLABORADOR (obrigatória):",
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
                            "avulso": avulso_val,
                        }

                    registros_import = list(registros_por_nome.values())

                    if registros_import:
                        preview_import = pd.DataFrame([
                            {
                                "Nome": r["nome"],
                                "Função": r["funcao"],
                                "Categoria": r["tipo"],
                                "Valor do colaborador": formatar_reais(r["valor_diaria"]),
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
                                    }
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

            if st.session_state.get("msg_limpeza_prod_v1"):
                st.success(
                    st.session_state.pop("msg_limpeza_prod_v1")
                )

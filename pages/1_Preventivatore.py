import streamlit as st
import json
import os
import requests
import base64

# Configurazione della chiave API tramite i Secrets di Streamlit o fallback locale sicuro
if "GEMINI_API_KEY" in st.secrets:
    API_KEY_LOCALE = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY_LOCALE = "AQ.Ab8RN6JMjOFaJq3n0991ViyP2Xt4WDeXjpwiXHX3mMOzr7HYFw"

# ==========================================
# 1. INIZIALIZZAZIONE DEI LISTINI MENSILI E INDICI
# ==========================================
if "listino" not in st.session_state:
    st.session_state.listino = {
        # LUCE DOMESTICO
        "luce_fix_dom_f1": 0.1485, "luce_fix_dom_f2": 0.1485, "luce_fix_dom_f3": 0.1485,
        "pun_dom_unico": 0.1091,
        "luce_var_dom_f1": 0.0165, "luce_var_dom_f2": 0.0165, "luce_var_dom_f3": 0.0165,
        "luce_pcv_dom": 20.00,
        
        # LUCE ALTRI USI
        "luce_fix_au_f1": 0.1298, "luce_fix_au_f2": 0.1148, "luce_fix_au_f3": 0.1058,
        "pun_au_unico": 0.1091,
        "luce_var_au_f1": 0.0150, "luce_var_au_f2": 0.0150, "luce_var_au_f3": 0.0150,
        "luce_pcv_au": 15.00,
        
        # GAS DOMESTICO
        "gas_fix_dom": 0.5100, "psbil_dom_unico": 0.4499, "gas_var_dom_spread": 0.0700, "gas_qvd_dom": 18.00,
        
        # GAS ALTRI USI
        "gas_fix_au": 0.5500, "psbil_au_unico": 0.4499, "gas_var_au_spread": 0.0650, "gas_qvd_au": 26.00
    }

if "prompt_ai" not in st.session_state:
    st.session_state.prompt_ai = (
        "Sei un analista esperto di bollette energetiche italiane per lo Studio Lauri e Tirrenia Energia. "
        "Analizza il documento ed estrai con cura sia i consumi sia tutte le componenti di spesa fisse passanti.\n\n"
        "DEVI RESTITUIRMI UN OUTPUT FORMATTATO IN DUE PARTI PRECISE:\n\n"
        "PARTE 1: Un blocco JSON racchiuso tra tag [JSON_START] e [JSON_END] con questa struttura:\n"
        "[JSON_START]\n"
        "{\n"
        "  \"fornitura\": \"LUCE\" o \"GAS\",\n"
        "  \"destinazione\": \"Usi Domestici\" o \"Altri Usi\",\n"
        "  \"spesa_attuale\": 0.00,\n"
        "  \"f1\": 0,\n"
        "  \"f2\": 0,\n"
        "  \"f3\": 0,\n"
        "  \"spesa_trasporto\": 0.00,\n"
        "  \"oneri_sistema\": 0.00,\n"
        "  \"altre_partite\": 0.00,\n"
        "  \"canone_rai\": 0.00,\n"
        "  \"bonus_sociale\": 0.00\n"
        "}\n"
        "[JSON_END]\n\n"
        "PARTE 2: Una descrizione testuale dettagliata (Report) che riassuma:\n"
        "- Nome del vecchio gestore e periodo di riferimento.\n"
        "- Come hai individuato le singole voci di spesa fisse passanti e i consumi."
    )

if "report_testuale" not in st.session_state:
    st.session_state.report_testuale = ""

if "dati_bolletta" not in st.session_state:
    st.session_state.dati_bolletta = {
        "fornitura": "LUCE", "destinazione": "Usi Domestici", "spesa_attuale": 0.0, 
        "f1": 0, "f2": 0, "f3": 0, "spesa_trasporto": 0.0, "oneri_sistema": 0.0, 
        "altre_partite": 0.0, "canone_rai": 0.0, "bonus_sociale": 0.0
    }

st.sidebar.markdown("## 🔐 Area Riservata Studio Lauri")
admin_pass = st.sidebar.text_input("Inserisci Password:", type="password")

if admin_pass == "lauri2026":
    st.sidebar.success("Accesso Consentito!")
    st.session_state.prompt_ai = st.sidebar.text_area("Modifica le regole dell'AI:", value=st.session_state.prompt_ai, height=200)

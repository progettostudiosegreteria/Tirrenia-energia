import streamlit as st
import json
import os
import requests
import base64

# ==========================================
# CHIAVE API CORRETTA E DIRETTA
# ==========================================
API_KEY_LOCALE = "AQ.Ab8RN6JMjOFaJq3n0991ViyP2Xt4WDeXjpwiXHX3mMOzr7HYFw"

# ==========================================
# INIZIALIZZAZIONE STATO E LISTINI
# ==========================================
if "listino" not in st.session_state:
    st.session_state.listino = {
        "luce_fix_dom_f1": 0.1485, "luce_fix_dom_f2": 0.1485, "luce_fix_dom_f3": 0.1485,
        "pun_dom_unico": 0.1091,
        "luce_var_dom_f1": 0.0165, "luce_var_dom_f2": 0.0165, "luce_var_dom_f3": 0.0165,
        "luce_pcv_dom": 20.00,
        "luce_fix_au_f1": 0.1298, "luce_fix_au_f2": 0.1148, "luce_fix_au_f3": 0.1058,
        "pun_au_unico": 0.1091,
        "luce_var_au_f1": 0.0150, "luce_var_au_f2": 0.0150, "luce_var_au_f3": 0.0150,
        "luce_pcv_au": 15.00,
        "gas_fix_dom": 0.5100, "psbil_dom_unico": 0.4499, "gas_var_dom_spread": 0.0700, "gas_qvd_dom": 18.00,
        "gas_fix_au": 0.5500, "psbil_au_unico": 0.4499, "gas_var_au_spread": 0.0650, "gas_qvd_au": 26.00
    }

if "prompt_ai" not in st.session_state:
    st.session_state.prompt_ai = (
        "Sei un analista esperto di bollette energetiche italiane per lo Studio Lauri e Tirrenia Energia. "
        "Analizza il documento ed estrai con cura sia i consumi sia tutte le componenti di spesa fisse passanti. "
        "DEVI RESTITUIRMI UN OUTPUT FORMATTATO IN DUE PARTI PRECISE: "
        "PARTE 1: Un blocco JSON racchiuso tra tag [JSON_START] e [JSON_END] con questa struttura: "
        "[JSON_START] "
        "{"
        "  'fornitura': 'LUCE' o 'GAS',"
        "  'destinazione': 'Usi Domestici' o 'Altri Usi',"
        "  'spesa_attuale': 0.00,"
        "  'f1': 0,"
        "  'f2': 0,"
        "  'f3': 0,"
        "  'spesa_trasporto': 0.00,"
        "  'oneri_sistema': 0.00,"
        "  'altre_partite': 0.00,"
        "  'canone_rai': 0.00,"
        "  'bonus_sociale': 0.00"
        "} "
        "[JSON_END] "
        "PARTE 2: Una descrizione testuale dettagliata (Report) che riassuma: "
        "- Nome del vecchio gestore e periodo di riferimento. "
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
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 MODIFICA LISTINI")
    st.session_state.listino["luce_fix_dom_f1"] = st.sidebar.number_input("Luce Dom. Fisso F

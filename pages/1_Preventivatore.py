import streamlit as st
import json
import os
import requests
import base64

# ==========================================
# CHIAVE API - RECUPERO SICURO
# ==========================================
# Proviamo a prenderla dai Secrets di Streamlit (scelta consigliata online)
if "GEMINI_API_KEY" in st.secrets:
    API_KEY_LOCALE = st.secrets["GEMINI_API_KEY"]
else:
    # Se non è nei secrets, usiamo la stringa scritta qui sotto.
    # NOTA: Sostituisci questa stringa con una chiave valida che inizia con AIzaSy...
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
        "PARTE 2: Una descrizione testuale dettagliata (Report)

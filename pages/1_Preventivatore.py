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
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 MODIFICA LISTINI")
    st.session_state.listino["luce_fix_dom_f1"] = st.sidebar.number_input("Luce Dom. Fisso F1", value=st.session_state.listino["luce_fix_dom_f1"], format="%.4f")
    st.session_state.listino["pun_dom_unico"] = st.sidebar.number_input("PUN Default Dom.", value=st.session_state.listino["pun_dom_unico"], format="%.5f")
    st.session_state.listino["gas_fix_dom"] = st.sidebar.number_input("Gas Dom. Fisso", value=st.session_state.listino["gas_fix_dom"], format="%.4f")
    st.session_state.listino["psbil_dom_unico"] = st.sidebar.number_input("PSBIL Default Dom.", value=st.session_state.listino["psbil_dom_unico"], format="%.4f")
else:
    if admin_pass != "":
        st.sidebar.error("Password Errata.")

st.title("⚡ Tirrenia Energia & Studio Lauri")
st.subheader("Preventivatore Automatico Certificato con Analisi AI")

uploaded_file = st.file_uploader("📂 Carica la bolletta attuale del cliente (PDF o Foto)", type=["pdf", "png", "jpg", "jpeg"])

f1_consumo = 0
f2_consumo = 0
f3_consumo = 0
consumo_totale = 0
spesa_attuale = 0.0
c_trasporto = 0.0
c_oneri = 0.0
c_altre = 0.0
c_rai = 0.0
c_bonus = 0.0
pun_valore = 0.0
psbil_valore = 0.0
iva_aliquota = 0.22

if uploaded_file is not None:
    st.info(f"Documento '{uploaded_file.name}' pronto per la lettura.")
    
    if st.button("🧠 Avvia Lettura Automatica con AI"):
        with st.spinner("L'AI sta analizzando i testi..."):
            try:
                bytes_data = uploaded_file.getvalue()
                base64_file = base64.b64encode(bytes_data).decode("utf-8")
                
                # SINTASSI DI CHIAMATA HTTP CERTIFICATA DA GOOGLE PER LA VERSIONE V1BETA CON DATI INLINE
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
                headers = {"Content-Type": "application/json"}
                params = {"key": API_KEY_LOCALE}
                
                payload = {
                    "contents": [{
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": uploaded_file.type,
                                    "data": base64_file
                                }
                            },
                            {
                                "text": st.session_state.prompt_ai
                            }
                        ]

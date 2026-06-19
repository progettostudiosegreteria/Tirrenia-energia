import streamlit as st
import json
import os
import requests
import base64

# Chiave API inserita direttamente nel codice per l'ambiente online
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
                
                # CORREZIONE PUNTO CRITICO: Cambiato l'endpoint del modello in gemini-1.5-flash-latest come richiesto da v1beta
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY_LOCALE}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{
                        "parts": [
                            {"inlineData": {"mimeType": uploaded_file.type, "data": base64_file}},
                            {"text": st.session_state.prompt_ai}
                        ]
                    }]
                }
                
                req_response = requests.post(url, headers=headers, json=payload)
                res_json = req_response.json()
                
                if "error" in res_json:
                    st.error(f"Errore diretto da Google API: {res_json['error']['message']}")
                    st.json(res_json["error"])
                else:
                    full_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    
                    if "[JSON_START]" in full_text and "[JSON_END]" in full_text:
                        json_part = full_text.split("[JSON_START]")[-1].split("[JSON_END]")[0].strip()
                        report_part = full_text.split("[JSON_END]")[-1].strip()
                    else:
                        json_part = full_text
                        report_part = "Report generato direttamente."
                    
                    risultato_json = json.loads(json_part)
                    st.session_state.dati_bolletta.update(risultato_json)
                    st.session_state.report_testuale = full_text if report_part == "" else report_part
                    st.success("Scansione completata!")
                
            except Exception as e:
                st.error(f"Errore interno del codice o JSON: {e}")

    if st.session_state.report_testuale != "":
        with st.expander("📝 Visualizza l'Analisi Dettagliata dell'AI", expanded=True):
            st.write(st.session_state.report_testuale)

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Dati Acquisiti per la Preventivazione")
        idx_forn = 0 if st.session_state.dati_bolletta["fornitura"] == "LUCE" else 1
        idx_uso = 0 if st.session_state.dati_bolletta["destinazione"] == "Usi Domestici" else 1
        tipo_fornitura = st.radio("Tipologia Fornitura:", ["LUCE", "GAS"], index=idx_forn)
        tipo_uso = st.radio("Destinazione d'Uso:", ["Usi Domestici", "Altri Usi"], index=idx_uso)
        st.markdown("---")
        
        if tipo_fornitura == "LUCE":
            st.markdown("**Consumi Rilevati nel Periodo (kWh):**")
            f1_consumo = st.number_input("Fascia F1:", value=int(st.session_state.dati_bolletta["f1"]))
            f2_consumo = st.number_input("Fascia F2:", value=int(st.session_state.dati_bolletta["f2"]))
            f3_consumo = st.number_input("Fascia F3:", value=int(st.session_state.dati_bolletta["f3"]))
            consumo_totale = f1_consumo + f2_consumo + f3_consumo
            st.code(f"Consumo Totale: {consumo_totale} kWh")
            spesa_attuale = st.number_input("Spesa Attuale Vecchio Gestore (€):", value=float(st.session_state.dati_bolletta["spesa_attuale"]))
            st.markdown("---")
            st.markdown("**🛠️ Spese Passanti e Imposte:**")
            c_trasporto = st.number_input("Spesa per il Trasporto (€):", value=float(st.session_state.dati_bolletta.get("spesa_trasporto", 0.0)))
            c_oneri = st.number_input("Spesa per Oneri di Sistema (€):", value=float(st.session_state.dati_bolletta.get("oneri_sistema", 0.0)))
            c_altre = st.number_input("Altre Partite / Ricalcoli (€):", value=float(st.session_state.dati_bolletta.get("altre_partite", 0.0)))
            c_rai = st.number_input("Canone RAI (€):", value=float(st.session_state.dati_bolletta.get("canone_rai", 0.0)))
            c_bonus = st.number_input("Bonus Sociale (Valore NEGATIVO) (€):", value=float(st.session_state.dati_bolletta.get("bonus_sociale", 0.0)))
            st.markdown("---")
            st.markdown("**📈 Indice di Mercato Unico:**")
            default_pun = st.session_state.listino["pun_au_unico"] if tipo_uso == "Altri Usi" else st.session_state.listino["pun_dom_unico"]
            pun_valore = st.number_input("PUN (€/kWh):", value=default_pun, format="%.5f")
            iva_aliquota = 0.22 if tipo_uso == "Altri Usi" else 0.10
        else:
            st.markdown("**Consumo Gas Rilevato (Smc):**")
            consumo_totale = st.number_input("Volume Totale Gas (Smc):", value=int(st.session_state.dati_bolletta["f1"]))
            f1_consumo = consumo_totale
            spesa_attuale = st.number_input("Spesa Attuale Vecchio Gestore (€):", value=float(st.session_state.dati_bolletta["spesa_attuale"]))
            st.markdown("---")
            st.markdown("**🛠️ Spese Passanti e Imposte:**")
            c_trasporto = st.number_input("Spesa per il Trasporto (€):", value=float(st.session_state.dati_bolletta.get("spesa_trasporto", 0.0)))
            c_oneri = st.number_input("Spesa per Oneri di Sistema (€):", value=float(st.session_state.dati_bolletta.get("oneri_sistema", 0.0)))
            c_altre = st.number_input("Altre Partite / Ricalcoli (€):", value=float(st.session_state.dati_bolletta.get("altre_partite", 0.0)))
            c_bonus = st.number_input("Bonus Sociale (Valore NEGATIVO) (€):", value=float(st.session_state.dati_bolletta.get("bonus_sociale", 0.0)))
            c_rai = 0.0
            st.markdown("---")
            st.markdown("**📈 Indice di Mercato Unico:**")
            default_psbil = st.session_state.listino["psbil_au_unico"] if tipo_uso == "Altri Usi" else st.session_state.listino["psbil_dom_unico"]
            psbil_valore = st.number_input("PSBIL (€/Smc):", value=default_psbil, format="%.4f")
            iva_aliquota = 0.22

    with col2:
        st.markdown("### 📊 Risultato della Comparazione Finita")
        coeff_perdite = 1.102 if tipo_fornitura == "LUCE" else 1.0
        totale_costi_passanti_invariabili = c_trasporto + c_oneri + c_altre
        totale_fissa = 0.0
        totale_variabile = 0.0
        
        if tipo_fornitura == "LUCE":
            if tipo_uso == "Altri Usi":
                spesa_energia_fix = (f1_consumo * st.session_state.listino["luce_fix_au_f1"] * coeff_perdite) + (f2_consumo * st.session_state.listino["luce_fix_au_f2"] * coeff_perdite) + (f3_consumo * st.session_state.listino["luce_fix_au_f3"] * coeff_perdite)
                imponibile_fix = spesa_energia_fix + (st.session_state.listino["luce_pcv_au"] * 2) + totale_costi_passanti_invariabili
                totale_fissa = (imponibile_fix * (1 + iva_aliquota)) + c_rai + c_bonus
                
                spesa_energia_var = (f1_consumo * (pun_valore + st.session_state.listino["luce_var_au_f1"]) * coeff_perdite) + (f2_consumo * (pun_valore + st.session_state.listino["luce_var_au_f2"]) * coeff_perdite) + (f3_consumo * (pun_valore + st.session_state.listino["luce_var_au_f3"]) * coeff_perdite)
                imponibile_var = spesa_energia_var + (st.session_state.listino["luce_pcv_au"] * 2) + totale_costi_passanti_invariabili
                totale_variabile = (imponibile_var * (1 + iva_aliquota)) + c_rai + c_bonus
            else:
                spesa_energia_fix = (f1_consumo * st.session_state.listino["luce_fix_dom_f1"] * coeff_perdite) + (f2_consumo * st.session_state.listino["luce_fix_dom_f2"] * coeff_perdite) + (f3_consumo * st.session_state.listino["luce_fix_dom_f3"] * coeff_perdite)
                imponibile_fix = spesa_energia_fix + st.session_state.listino["luce_pcv_dom"] + totale_costi_passanti_invariabili
                totale_fissa = (imponibile_fix * (1 + iva_aliquota)) + c_rai + c_bonus
                
                spesa_energia_var = (f1_consumo * (pun_valore + st.session_state.listino["luce_var_dom_f1"]) * coeff_perdite) + (f2_consumo * (pun_valore + st.session_state.listino["luce_var_dom_f2"]) * coeff_perdite) + (f3_consumo * (pun_valore + st.session_state.listino["luce_var_dom_f3"]) * coeff_perdite)
                imponibile_var = spesa_energia_var + st.session_state.listino["luce_pcv_dom"] + totale_costi_passanti_invariabili
                totale_variabile = (imponibile_var * (1 + iva_aliquota)) + c_rai + c_bonus
        else:
            if tipo_uso == "Altri Usi":
                spesa_gas_fix = consumo_totale * st.session_state.listino["gas_fix_au"]
                imponibile_fix = spesa_gas_fix + st.session_state.listino["gas_qvd_au"] + totale_costi_passanti_invariabili
                totale_fissa = (imponibile_fix * (1 + iva_aliquota)) + c_bonus
                
                spesa_gas_var = consumo_totale * (psbil_valore + st.session_state.listino["gas_var_au_spread"])
                imponibile_var = spesa_gas_var + st.session_state.listino["gas_qvd_au"] + totale_costi_passanti_invariabili
                totale_variabile = (imponibile_var * (1 + iva_aliquota)) + c_bonus
            else:
                spesa_gas_fix = consumo_totale * st.session_state.listino["gas_fix_dom"]
                imponibile_fix = spesa_gas_fix + st.session_state.listino["gas_qvd_dom"] + totale_costi_passanti_invariabili
                totale_fissa = (imponibile_fix * (1 + iva_aliquota)) + c_bonus
                
                spesa_gas_var = consumo_totale * (psbil_valore + st.session_state.listino["gas_var_dom_spread"])
                imponibile_var = spesa_gas_var + st.session_state.listino["gas_qvd_dom"] + totale_costi_passanti_invariabili
                totale_variabile = (imponibile_var * (1 + iva_aliquota)) + c_bonus

        st.markdown(f"<div style='background-color: #111827; padding: 15px; border-radius: 12px; margin-bottom: 15px; border-left: 5px solid #ef4444;'><span style='color: #9ca3af; font-size: 12px;'>VECCHIO GESTORE IN BOLLETTA</span><br><span style='color: #ef4444; font-size: 24px; font-weight: bold;'>€ {spesa_attuale:.2f}</span></div>", unsafe_allow_html=True)
        
        b1, b2 = st.columns(2)
        with b1:
            st.markdown(f"<div style='background-color: #111827; padding: 15px; border-radius: 12px; border-left: 5px solid #f28e2b;'><span style='color: #9ca3af; font-size: 11px;'>TIRRENIA PREZZO FISFO</span><br><span style='color: #ffffff; font-size: 20px; font-weight: bold;'>€ {totale_fissa:.2f}</span></div>", unsafe_allow_html=True)
            st.metric("Risparmio Fisfo", f"€ {spesa_attuale - totale_fissa:.2f}")
        with b2:
            st.markdown(f"<div style='background-color: #111827; padding: 15px; border-radius: 12px; border-left: 5px solid #10b981;'><span style='color: #9ca3af; font-size: 11px;'>TIRRENIA PREZZO VARIABILE</span><br><span style='color: #ffffff; font-size: 20px; font-weight: bold;'>€ {totale_variabile:.2f}</span></div>", unsafe_allow_html=True)
            st.metric("Risparmio Variabile", f"€ {spesa_attuale - totale_variabile:.2f}")

        miglior_risparmio = max(spesa_attuale - totale_fissa, spesa_attuale - totale_variabile)
        tipo_migliore = "VARIABILE" if (spesa_attuale - totale_variabile) > (spesa_attuale - totale_fissa) else "FISSO"
        
        st.markdown(f"<div style='background-color: #064e3b; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #10b981; margin-top: 25px;'><span style='color: #a7f3d0; font-size: 13px; font-weight: bold;'>MIGLIOR OPZIONE CONVENIENZA (TIRRENIA {tipo_migliore})</span><br><span style='color: #34d399; font-size: 34px; font-weight: 900;'>€ {miglior_risparmio:.2f} Totali di Risparmio</span></div>", unsafe_allow_html=True)
else:
    st.info("📂 Carica una bolletta per attivare l'estrazione intelligente e il motore di calcolo.")

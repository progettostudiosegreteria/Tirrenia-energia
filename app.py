import streamlit as st

# 1. CONFIGURAZIONE DELLA PAGINA
st.set_page_config(
    page_title="Tirrenia Energia - Risparmia sulla tua bolletta", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Iniezione globale CSS per lo sfondo scuro
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b0f19 !important;
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] {
            display: none !important;
        }
        footer {visibility: hidden !important;}
        .block-container {
            padding-top: 2rem !important; 
            padding-bottom: 0rem !important;
            max-width: 95% !important;
        }
        div.stButton > button {
            background-color: #f28e2b !important;
            color: #ffffff !important;
            border: none !important;
            padding: 12px 30px !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            height: 48px !important;
            cursor: pointer !important;
            box-shadow: 0 4px 15px rgba(242, 142, 43, 0.4) !important;
        }
        div.stButton > button:hover {
            background-color: #e07d1b !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. BARRA DI NAVIGAZIONE SUPERIORE
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 4%; background-color: #0d1527; border: 1px solid #1e293b; border-radius: 12px; margin-bottom: 45px;">
        <div style="font-size: 22px; font-weight: 900; color: #ffffff; font-family: 'Arial', sans-serif;">
            TIRRENIA<span style="color: #f28e2b;">ENERGIA</span>
        </div>
        <div style="display: flex; gap: 30px; font-size: 14px; font-weight: 500; font-family: 'Arial', sans-serif;">
            <a href="#" style="color: #ffffff; text-decoration: none;">Home</a>
            <a href="#" style="color: #9ca3af; text-decoration: none;">Offerte</a>
            <a href="#" style="color: #9ca3af; text-decoration: none;">Preventivatore AI</a>
            <a href="#" style="color: #9ca3af; text-decoration: none;">Chi Siamo</a>
            <a href="#" style="color: #9ca3af; text-decoration: none;">Contatti</a>
        </div>
        <div style="color: #ffffff; font-size: 14px; font-weight: bold; font-family: 'Arial', sans-serif;">
            <span style="color: #f28e2b;">📞</span> 081 8242528
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. INTERFACCIA A DUE COLONNE
col1, col2 = st.columns([1.2, 1.0], gap="large")

with col1:
    st.markdown("""
        <div style="display: inline-block; background-color: #1a233a; border: 1px solid #2e3d5e; color: #9ca3af; font-size: 12px; padding: 6px 16px; border-radius: 20px; font-weight: 500; margin-bottom: 25px; font-family: 'Arial', sans-serif;">
            <span style="color: #f28e2b; margin-right: 5px;">●</span> Mercato Libero Energia Elettrica
        </div>
        <h1 style="font-size: 54px; font-weight: 900; line-height: 1.15; margin-bottom: 25px; color: #ffffff; font-family: 'Arial', sans-serif;">
            Risparmia sulla tua<br><span style="color: #f28e2b;">bolletta luce e gas</span>
        </h1>
        <p style="color: #9ca3af; font-size: 17px; line-height: 1.6; margin-bottom: 40px; max-width: 520px; font-family: 'Arial', sans-serif;">
            Carica la tua bolletta, la nostra AI estrae automaticamente tutti i dati e calcola quanto puoi risparmiare passando a Tirrenia Energia.
        </p>
    """, unsafe_allow_html=True)
    
    c_btn1, c_btn2 = st.columns([1.1, 1.0])
    with c_btn1:
        if st.button("Calcola il tuo risparmio →", key="home_action_redirect", use_container_width=True):
            st.switch_page("pages/1_Preventivatore.py")
            
    with c_btn2:
        st.markdown("""
            <a href="#" style="display: flex; justify-content: center; align-items: center; background-color: transparent; color: #ffffff; border: 1px solid #2e3d5e; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-size: 15px; font-weight: bold; height: 48px; font-family: 'Arial', sans-serif;">
                Scopri le offerte
            </a>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <div style="display: flex; gap: 25px; margin-top: 60px; font-size: 13px; color: #9ca3af; font-family: 'Arial', sans-serif;">
            <div><span style="color: #10b981; margin-right: 4px;">✔️</span> Nessun costo di attivazione</div>
            <div><span style="color: #10b981; margin-right: 4px;">✔️</span> Preventivo gratuito in 2 minuti</div>
            <div><span style="color: #10b981; margin-right: 4px;">✔️</span> Cambio fornitore senza interruzioni</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #0d1527; border: 1px solid #1e293b; padding: 35px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-family: 'Arial', sans-serif;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px;">
            <div style="background-color: #d97706; color: #ffffff; width: 26px; height: 26px; display: flex; justify-content: center; align-items: center; border-radius: 50%; font-weight: bold; font-size: 13px;">i</div>
            <h3 style="color: #ffffff; margin: 0; font-size: 18px; font-weight: bold; letter-spacing: 0.3px;">Chi Siamo & Partnership</h3>
        </div>
        <p style="color: #ffffff; font-size: 14px; line-height: 1.6; margin-bottom: 22px;">
            <b>Tirrenia Energia</b> opera nel settore della vendita di <span style="color: #3b82f6; font-weight: bold;">gas naturale</span> e di <span style="color: #3b82f6; font-weight: bold;">energia elettrica</span> in ambito nazionale.
        </p>
        <p style="color: #ffffff; font-size: 14px; line-height: 1.6; margin-bottom: 22px;">
            L'impegno di Tirrenia Energia è porre <b>"le persone"</b> e non <b>"i numeri"</b> al centro del proprio business garantendo <span style="color: #f28e2b; font-weight: bold;">assistenza, consulenza e gestione delle forniture</span>.
        </p>
        <p style="color: #9ca3af; font-size: 14px; line-height: 1.6; margin-bottom: 35px;">
            Per Tirrenia Energia sei importante, la nostra passione è al tuo servizio per offrirti le migliori soluzioni per la tua casa e il tuo lavoro.
        </p>
        <div style="background-color: #111a2e; border: 1px solid rgba(242, 142, 43, 0.2); border-left: 4px solid #f28e2b; padding: 18px; border-radius: 6px; margin-bottom: 35px;">
            <h4 style="color: #f28e2b; font-size: 12px; font-weight: 900; margin-top: 0; margin-bottom: 8px; letter-spacing: 0.6px;">PRESIDIO TERRITORIALE CAMPANIA</h4>
            <p style="color: #ffffff; font-size: 13px; line-height: 1.5; margin: 0;">
                Tirrenia Energia è partner dello <b>Studio Lauri</b> con sede in Palma Campania, Via Circumvallazione 170, Palma Campania (NA) 80036.
            </p>
        </div>
        <p style="color: #9ca3af; font-size: 12px; margin-bottom: 12px; font-weight: 500;">Per maggiori informazioni e contrattualizzazione chiamaci:</p>
        <div style="display: flex; gap: 15px;">
            <div style="flex: 1; background-color: #0b111e; border: 1px solid #1e293b; padding: 12px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="color: #f28e2b; font-size: 18px;">📞</div>
                <div>
                    <span style="color: #737373; font-size: 10px; display: block; font-weight: bold; letter-spacing: 0.3px;">FISSO</span>
                    <span style="color: #ffffff; font-size: 13px; font-weight: bold;">081 8242528</span>
                </div>
            </div>
            <div style="flex: 1; background-color: #0b111e; border: 1px solid #1e293b; padding: 12px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <div style="color: #10b981; font-size: 18px;">🟢</div>
                <div>
                    <span style="color: #737373; font-size: 10px; display: block; font-weight: bold; letter-spacing: 0.3px;">CELLULARE</span>
                    <span style="color: #ffffff; font-size: 13px; font-weight: bold;">351 764 9350</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
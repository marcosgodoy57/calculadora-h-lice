import streamlit as st

# --- CONFIGURAÇÃO INDUSTRIAL ---
st.set_page_config(page_title="Helix DoseExata - OPERACIONAL", layout="centered")

# Estilos visuais
st.markdown("""
    <style>
    .big-font { font-size:22px !important; font-weight: bold; color: #1E3A8A; }
    .recipe-card { background-color: #ECFDF5; padding: 20px; border-radius: 15px; border: 2px solid #10B981; }
    .warning-card { background-color: #FEF2F2; padding: 20px; border-radius: 15px; border: 2px solid #EF4444; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS TÉCNICO (Ajuste aqui os preços e doses se necessário) ---
PENEIRAS = {'L1': 29.0, 'L2': 28.0, 'R1': 26.9, 'R2': 25.5, 'C1': 24.2, 'C2': 23.0, 'R3': 19.4, 'C3': 19.2, 'C4': 13.5}
PRODUTOS = {
    'Fortenza 600FS': {'dose_ref': 20.0, 'dens_ref': 1.26, 'preco': 1313.83},
    'Poncho 600FS': {'dose_ref': 70.0, 'dens_ref': 1.26, 'preco': 434.50},
    'Cruiser 600FS': {'dose_ref': 70.0, 'dens_ref': 1.26, 'preco': 490.00},
    'Dermacor': {'dose_ref': 12.0, 'dens_ref': 1.20, 'preco': 1850.00},
    'Maxim Advanced': {'dose_ref': 50.0, 'dens_ref': 1.10, 'preco': 620.00}
}

st.title("Painel do Operador CBT - Helix")
st.markdown("---")

# --- PASSO 1: CONFIGURAÇÃO ---
st.header("1️⃣ Configuração do Lote")
col1, col2 = st.columns(2)
with col1:
    peneira = st.selectbox("Qual a PENEIRA?", options=list(PENEIRAS.keys()), index=2)
with col2:
    batelada_kg = st.number_input("Tamanho da Batelada (kg)", value=160, step=10)

# --- PASSO 2: PRODUTOS ---
st.header("2️⃣ Seleção de Produtos")
selecionados = st.multiselect("Selecione os produtos da receita:", options=list(PRODUTOS.keys()))

# --- PASSO 3: AFERIÇÃO ---
st.header("3️⃣ Aferição de Densidade (Copo 100ml)")
densidades_reais = {}
for p in selecionados:
    massa = st.number_input(f"Peso do Copo (100ml) de {p}:", value=float(PRODUTOS[p]['dens_ref']*100), step=0.1)
    densidades_reais[p] = massa / 100

# --- PASSO 4: RESULTADO ---
st.markdown("---")
st.header("4️⃣ INSTRUÇÃO DE CARGA")

if not selecionados:
    st.info("Selecione os produtos acima para gerar a receita.")
else:
    peso_sc = PENEIRAS[peneira]
    sacos_por_batelada = batelada_kg / peso_sc
    total_ml_produtos = 0
    detalhes_produtos = []
    
    for p in selecionados:
        dose_aj_sc = PRODUTOS[p]['dose_ref'] * (peso_sc / 26.9)
        dose_batelada = dose_aj_sc * sacos_por_batelada
        total_ml_produtos += dose_batelada
        detalhes_produtos.append(f"🔹 **{p}:** {dose_batelada:.1f} ml")

    calda_alvo_batelada = 600 * sacos_por_batelada # Meta industrial de 600ml/saco
    agua_complemento = calda_alvo_batelada - total_ml_produtos

    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">PARA CADA BATELADA DE {batelada_kg} KG:</p>', unsafe_allow_html=True)
    for d in detalhes_produtos:
        st.markdown(d)
    if agua_complemento > 0:
        st.markdown(f"🔹 **Água + Polímero + Corante:** {agua_complemento:.1f} ml")
    st.markdown("---")
    st.markdown(f"✅ **VOLUME TOTAL NO TANQUE:** {calda_alvo_batelada:.1f} ml")
    st.markdown('</div>', unsafe_allow_html=True)

    # Cálculo financeiro simplificado (expansível)
    with st.expander("Ver Economia Industrial"):
        custo_cheio = sum([PRODUTOS[p]['dose_ref']/1000 * PRODUTOS[p]['preco'] for p in selecionados]) * sacos_por_batelada
        custo_aj_sc = sum([(PRODUTOS[p]['dose_ref'] * (peso_sc/26.9))/1000 * PRODUTOS[p]['preco'] for p in selecionados])
        economia_batelada = custo_cheio - (custo_aj_sc * sacos_por_batelada)
        st.write(f"Economia nesta batelada: R$ {economia_batelada:.2f}")
        st.write(f"Economia para 1 milhão de sacos: R$ { (economia_batelada/sacos_por_batelada) * 1000000:,.2f}")

st.caption("Helix Sementes | Patos de Minas - MG")

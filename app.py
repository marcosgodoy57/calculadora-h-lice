import streamlit as st

# --- CONFIGURAÇÃO INDUSTRIAL ---
st.set_page_config(page_title="Helix DoseExata - OPERACIONAL", layout="centered")

# Estilos visuais para galpão
st.markdown("""
    <style>
    .big-font { font-size:22px !important; font-weight: bold; color: #1E3A8A; }
    .recipe-card { background-color: #ECFDF5; padding: 20px; border-radius: 15px; border: 2px solid #10B981; }
    .warning-card { background-color: #FEF2F2; padding: 20px; border-radius: 15px; border: 2px solid #EF4444; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS TÉCNICO ---
# Pesos de referência (médios) do catálogo
PENEIRAS_PADRAO = {'L1': 29.0, 'L2': 28.0, 'R1': 26.9, 'R2': 25.5, 'C1': 24.2, 'C2': 23.0, 'R3': 19.4, 'C3': 19.2, 'C4': 13.5}
PRODUTOS = {
    'Fortenza 600FS': {'dose_ref': 20.0, 'dens_ref': 1.26, 'preco': 1313.83},
    'Poncho 600FS': {'dose_ref': 70.0, 'dens_ref': 1.26, 'preco': 434.50},
    'Cruiser 600FS': {'dose_ref': 70.0, 'dens_ref': 1.26, 'preco': 490.00},
    'Dermacor': {'dose_ref': 12.0, 'dens_ref': 1.20, 'preco': 1850.00},
    'Maxim Advanced': {'dose_ref': 50.0, 'dens_ref': 1.10, 'preco': 620.00}
}

st.title("Painel do Operador CBT - Helix")
st.caption("Foco em Precisão: Ajuste por Biomassa Real do Lote")
st.markdown("---")

# --- PASSO 1: CONFIGURAÇÃO DO LOTE ---
st.header("1️⃣ Configuração da Semente")
col1, col2 = st.columns(2)
with col1:
    peneira_sel = st.selectbox("Selecione a PENEIRA:", options=list(PENEIRAS_PADRAO.keys()), index=2)
    peso_sugerido = PENEIRAS_PADRAO[peneira_sel]

with col2:
    # AQUI ESTÁ A MELHORIA: O operador vê o padrão, mas digita o real
    peso_real_sc = st.number_input(f"PESO REAL da sacaria (kg):", value=float(peso_sugerido), step=0.1, help="Peso real aferido na balança para este lote específico.")

batelada_kg = st.number_input("Tamanho da Batelada na Máquina (kg)", value=160, step=10)

# --- PASSO 2: PRODUTOS ---
st.header("2️⃣ Seleção de Produtos")
selecionados = st.multiselect("Selecione os produtos da receita:", options=list(PRODUTOS.keys()))

# --- PASSO 3: AFERIÇÃO DE DENSIDADE ---
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
    # A base de cálculo agora é o peso_real_sc (partida) e não mais o fixo do catálogo
    sacos_por_batelada = batelada_kg / peso_real_sc
    total_ml_produtos = 0
    detalhes_produtos = []
    
    for p in selecionados:
        # Cálculo da dose ajustada: DoseRef * (PesoReal / 26.9)
        dose_aj_sc = PRODUTOS[p]['dose_ref'] * (peso_real_sc / 26.9)
        dose_batelada = dose_aj_sc * sacos_por_batelada
        total_ml_produtos += dose_batelada
        detalhes_produtos.append(f"🔹 **{p}:** {dose_batelada:.1f} ml")

    calda_alvo_batelada = 600 * sacos_por_batelada # Meta industrial de 600ml/saco
    agua_complemento = calda_alvo_batelada - total_ml_produtos

    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="big-font">PARA BATELADA DE {batelada_kg} KG (Peneira {peneira_sel}):</p>', unsafe_allow_html=True)
    st.write(f"Configurado para peso real de **{peso_real_sc} kg** por sacaria.")
    st.markdown("---")
    for d in detalhes_produtos:
        st.markdown(d)
    if agua_complemento > 0:
        st.markdown(f"🔹 **Água + Polímero + Corante:** {agua_complemento:.1f} ml")
    else:
        st.markdown(f"⚠️ **Atenção:** Volume de produtos ({total_ml_produtos:.1f}ml) excede o alvo!")
        
    st.markdown("---")
    st.markdown(f"✅ **VOLUME TOTAL NO TANQUE:** {max(calda_alvo_batelada, total_ml_produtos):.1f} ml")
    st.markdown('</div>', unsafe_allow_html=True)

    # Cálculo financeiro simplificado
    with st.expander("📊 Relatório de Eficiência e Economia"):
        custo_padrao_sc = sum([PRODUTOS[p]['dose_ref']/1000 * PRODUTOS[p]['preco'] for p in selecionados])
        custo_ajustado_sc = sum([(PRODUTOS[p]['dose_ref'] * (peso_real_sc/26.9))/1000 * PRODUTOS[p]['preco'] for p in selecionados])
        economia_por_saco = custo_padrao_sc - custo_ajustado_sc
        
        st.write(f"Economia real neste lote: **R$ {economia_por_saco:.4f} por saco**")
        st.write(f"Em 1 milhão de sacos: **R$ {economia_por_saco * 1000000:,.2f}**")
        
        # Auditoria técnica de IA
        total_g_ia_kg = 0
        for p in selecionados:
            dose_aj_sc = PRODUTOS[p]['dose_ref'] * (peso_real_sc / 26.9)
            g_ia = (dose_aj_sc * 0.6) / peso_real_sc 
            total_g_ia_kg += g_ia
        
        st.write(f"Concentração IA Final: {total_g_ia_kg:.2f} g/kg")
        if total_g_ia_kg > 3.0:
            st.error("Risco de Fitotoxicidade detectado!")

st.caption("Helix Sementes | Unidade Patos de Minas - MG")

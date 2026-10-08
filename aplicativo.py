

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

# ==========================================
# CONFIGURAÇÕES E DADOS BASE
# ==========================================
st.set_page_config(page_title="KN Alta Performance", page_icon="⚡", layout="wide")

ARQUIVO_DADOS = "dados_treinos.json"

MODALIDADES_EXERCICIOS = {
    "Futebol": ["Passe curto", "Passe longo", "Finalização", "Controle de bola", "Drible", "Trabalho de pés", "Condicionamento físico"],
    "Futevôlei": ["Saque", "Recepção de peito", "Recepção de coxa", "Levantamento", "Ataque (Pingada)", "Ataque (Forte)", "Defesa"],
    "Beach Tênis": ["Saque", "Voleio de Forehand", "Voleio de Backhand", "Smash", "Lob", "Devolução", "Movimentação em areia"],
    "Tênis": ["Saque", "Forehand", "Backhand", "Voleio", "Smash", "Slice", "Footwork"],
    "Basquete": ["Arremesso (Jump)", "Lance Livre", "Bandeja", "Drible", "Passe de peito", "Passe picado", "Rebote"]
}

# ==========================================
# FUNÇÕES DE BANCO DE DADOS (JSON)
# ==========================================
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Inicializa os dados na sessão
if "db" not in st.session_state:
    st.session_state.db = carregar_dados()

def atualizar_db():
    salvar_dados(st.session_state.db)

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
# --- ADICIONANDO O LOGO AQUI ---
caminho_logo = "1000317530.jpg"
if os.path.exists(caminho_logo):
    st.sidebar.image(caminho_logo, use_container_width=True)
else:
    st.sidebar.warning("Logo não encontrado. Salve a imagem como '1000317530.jpg' na mesma pasta do app.")
# -------------------------------

st.sidebar.title("⚡ Gerenciamento de Alunos")

# 1. Seleção / Criação de Aluno
alunos_existentes = list(st.session_state.db.keys())
opcao_aluno = st.sidebar.selectbox("Selecione o Aluno", ["+ Novo Aluno"] + alunos_existentes)

if opcao_aluno == "+ Novo Aluno":
    st.sidebar.subheader("Cadastrar Novo Aluno")
    novo_nome = st.sidebar.text_input("Nome do Aluno")
    nova_modalidade = st.sidebar.selectbox("Modalidade Principal", list(MODALIDADES_EXERCICIOS.keys()))
    
    if st.sidebar.button("Cadastrar Aluno", use_container_width=True):
        if novo_nome and novo_nome not in st.session_state.db:
            st.session_state.db[novo_nome] = {
                "modalidade": nova_modalidade,
                "treinos": []
            }
            atualizar_db()
            st.sidebar.success(f"Aluno {novo_nome} cadastrado!")
            st.rerun()
        elif novo_nome in st.session_state.db:
            st.sidebar.error("Aluno já existe!")
    
    aluno_atual = None
else:
    aluno_atual = opcao_aluno

# 2. Adição de Treinos (Se um aluno estiver selecionado)
if aluno_atual:
    st.sidebar.divider()
    st.sidebar.subheader(f"Adicionar Exercício para {aluno_atual}")
    
    modalidade_aluno = st.session_state.db[aluno_atual]["modalidade"]
    st.sidebar.caption(f"Modalidade: **{modalidade_aluno}**")
    
    # Dropdown dinâmico baseado na modalidade
    lista_exercicios = MODALIDADES_EXERCICIOS.get(modalidade_aluno, [])
    exercicio_selecionado = st.sidebar.selectbox("Exercício", lista_exercicios)
    
    col_sets, col_reps = st.sidebar.columns(2)
    series = col_sets.number_input("Séries", min_value=1, value=3, step=1)
    reps = col_reps.text_input("Repetições/Tempo", value="10 a 12")
    
    url_video = st.sidebar.text_input("URL do Vídeo (Opcional)", placeholder="Ex: https://youtube.com/...")
    observacoes = st.sidebar.text_area("Observações (Opcional)")
    
    if st.sidebar.button("Adicionar ao Treino", type="primary", use_container_width=True):
        novo_treino = {
            "exercicio": exercicio_selecionado,
            "series": series,
            "reps": reps,
            "url_video": url_video,
            "observacoes": observacoes
        }
        st.session_state.db[aluno_atual]["treinos"].append(novo_treino)
        atualizar_db()
        st.sidebar.success("Exercício adicionado!")
        st.rerun()

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
if not aluno_atual:
    st.title("Bem-vindo ao Sistema KN Alta Performance")
    st.info("👈 Selecione ou cadastre um aluno na barra lateral para começar.")
else:
    dados_aluno = st.session_state.db[aluno_atual]
    treinos = dados_aluno["treinos"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Ficha de Treino: {aluno_atual}")
    with col2:
        st.metric(label="Modalidade", value=dados_aluno["modalidade"])
    
    tab_treino, tab_analise = st.tabs(["📋 Planilha de Treino", "📊 Análise de Desempenho"])
    
    # --- TAB 1: PLANILHA DE TREINO ---
    with tab_treino:
        if not treinos:
            st.warning("Nenhum exercício cadastrado para este aluno ainda.")
        else:
            for i, treino in enumerate(treinos):
                with st.expander(f"⚡ {treino['exercicio']} - {treino['series']}x {treino['reps']}", expanded=True):
                    col_info, col_video, col_acao = st.columns([2, 2, 1])
                    
                    with col_info:
                        st.markdown(f"**Séries:** {treino['series']}")
                        st.markdown(f"**Repetições:** {treino['reps']}")
                        if treino['observacoes']:
                            st.markdown(f"**Obs:** {treino['observacoes']}")
                    
                    with col_video:
                        if treino['url_video']:
                            try:
                                st.video(treino['url_video'])
                            except:
                                st.error("Erro ao carregar vídeo. Verifique a URL.")
                        else:
                            st.write("*(Sem vídeo associado)*")
                    
                    with col_acao:
                        if st.button("Remover Exercício", key=f"del_{aluno_atual}_{i}", help="Excluir este exercício do treino"):
                            st.session_state.db[aluno_atual]["treinos"].pop(i)
                            atualizar_db()
                            st.rerun()

    # --- TAB 2: ANÁLISE COM MATPLOTLIB ---
    with tab_analise:
        if not treinos:
            st.info("Adicione exercícios para visualizar os gráficos de análise.")
        else:
            df_treinos = pd.DataFrame(treinos)
            
            col_grafico1, col_grafico2 = st.columns(2)
            
            with col_grafico1:
                st.subheader("Distribuição de Exercícios")
                # Conta a frequência de cada exercício
                contagem_exercicios = df_treinos['exercicio'].value_counts()
                
                # Ajustando as cores para combinar com o logo (Amarelo/Preto/Azul)
                cores_logo = ['#FFD700', '#00BFFF', '#1E90FF', '#4682B4', '#FFA500', '#FF8C00']
                
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                ax1.pie(contagem_exercicios, labels=contagem_exercicios.index, autopct='%1.1f%%', 
                        startangle=90, colors=cores_logo)
                ax1.axis('equal') 
                st.pyplot(fig1)
                
            with col_grafico2:
                st.subheader("Volume de Treino (Total de Séries)")
                # Agrupa por exercício e soma as séries
                volume_series = df_treinos.groupby('exercicio')['series'].sum().sort_values()
                
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                volume_series.plot(kind='barh', ax=ax2, color='#FFD700') # Cor amarela do logo
                ax2.set_xlabel("Número de Séries")
                ax2.set_ylabel("")
                ax2.grid(axis='x', linestyle='--', alpha=0.7)
                
                # Deixando o fundo do gráfico transparente para integrar melhor
                fig2.patch.set_alpha(0.0)
                ax2.patch.set_alpha(0.0)
                
                plt.tight_layout()
                st.pyplot(fig2)


import streamlit as st
import os

# 1. Configuração da página integrada com visual Mobile-First
st.set_page_config(
    page_title="Louvor App",
    page_icon="🎵",
    layout="centered"
)

# Injeção de CSS customizado
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            background-color: #2e3b4e;
            color: white;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #4a5d78;
            color: #4dfd9f;
        }
        
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 450px;
        }
        
        code {
            color: #4dfd9f !important;
            background-color: #1e1e1e !important;
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 14px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Estrutura de pastas
BASE_DIR = "arquivos"
CATEGORIAS = ["cifras", "audios", "videos", "partituras"]
for cat in CATEGORIAS:
    os.makedirs(os.path.join(BASE_DIR, cat), exist_ok=True)

# =========================================================
# 📸 INSERÇÃO DA IMAGEM DE CABEÇALHO (BANNER DO APP)
# =========================================================
NOME_IMAGEM = "louvor.jpg"  # Mude para "banner.png" se sua imagem for PNG
if os.path.exists(NOME_IMAGEM):
    # Força o Streamlit a renderizar a imagem como um elemento HTML responsivo nativo
    st.image(NOME_IMAGEM, use_container_width=True, output_format="JPEG")
else:
    st.markdown("<h1 style='text-align: center;'>🎶</h1>", unsafe_allow_html=True)

# Texto de identificação da igreja abaixo do banner
st.markdown("<h2 style='text-align: center; color: #2e3b4e; font-family: sans-serif; margin-top: 10px;'>Ministério de Música</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>IPI Cohab 1 • Repositório Oficial</p>", unsafe_allow_html=True)
st.divider()
# =========================================================

# --- PAINEL DO ADMINISTRADOR (Menu Gaveta) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    senha = st.text_input("Senha de Administrador:", type="password")
    if senha == "louvor123":
        st.success("Acesso Liberado!")
        cat_upload = st.selectbox("Categoria do Envio:", CATEGORIAS)
        arquivo = st.file_uploader("Escolha o arquivo:")
        if arquivo is not None:
            with open(os.path.join(BASE_DIR, cat_upload, arquivo.name), "wb") as f:
                f.write(arquivo.getbuffer())
            st.success(f"'{arquivo.name}' enviado!")
            st.toast("Arquivo atualizado com sucesso!")
    elif senha != "":
        st.error("Senha inválida.")

def listar_arquivos(categoria):
    caminho = os.path.join(BASE_DIR, categoria)
    if os.path.exists(caminho):
        return [f for f in os.listdir(caminho) if not f.startswith(".")]
    return []

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📄\nCifras", key="btn_cifras"): st.session_state.tela_atual = "Cifras"
with col2:
    if st.button("🔊\nÁudios", key="btn_audios"): st.session_state.tela_atual = "Áudios"
with col3:
    if st.button("📺\nVídeos", key="btn_videos"): st.session_state.tela_atual = "Vídeos"
with col4:
    if st.button("🎼\nPartit.", key="btn_partituras"): st.session_state.tela_atual = "Partituras"

st.write("")

# --- CONTROLE DAS TELAS DO APLICATIVO ---
if st.session_state.tela_atual == "Cifras":
    st.subheader("📄 Acervo de Cifras")
    lista = listar_arquivos("cifras")
    busca = st.text_input("🔍 Buscar louvor pelo nome:")
    if busca:
        lista = [f for f in lista if busca.lower() in f.lower()]
    if lista:
        sel = st.selectbox("Selecione a música:", lista, key="nav_cifra")
        cam = os.path.join(BASE_DIR, "cifras", sel)
        if sel.endswith(".txt"):
            with open(cam, "r", encoding="utf-8") as f:
                st.code(f.read(), language="text")
        else:
            with open(cam, "rb") as f:
                st.download_button("📥 Baixar Arquivo de Cifra", f, file_name=sel)
    else: st.info("Nenhum louvor encontrado.")

elif st.session_state.tela_atual == "Áudios":
    st.subheader("🔊 Áudios de Referência / VS")
    lista = listar_arquivos("audios")
    busca = st.text_input("🔍 Buscar áudio pelo nome:")
    if busca:
        lista = [f for f in lista if busca.lower() in f.lower()]
    if lista:
        sel = st.selectbox("Selecione o áudio:", lista, key="nav_audio")
        cam = os.path.join(BASE_DIR, "audios", sel)
        with open(cam, "rb") as f:
            bytes_audio = f.read()
        st.audio(bytes_audio, format="audio/mp3")
    else: st.info("Nenhum áudio encontrado.")

elif st.session_state.tela_atual == "Vídeos":
    st.subheader("📺 Vídeos de Ensaios e Tutoriais")
    lista = listar_arquivos("videos")
    if lista:
        sel = st.selectbox("Selecione o vídeo:", lista, key="nav_video")
        cam = os.path.join(BASE_DIR, "videos", sel)
        st.video(cam)
    else: st.info("Nenhum vídeo disponível.")

elif st.session_state.tela_atual == "Partituras":
    st.subheader("🎼 Partituras Oficiais")
    lista = listar_arquivos("partituras")
    if lista:
        sel = st.selectbox("Selecione o louvor:", lista, key="nav_partitura")
        cam = os.path.join(BASE_DIR, "partituras", sel)
        with open(cam, "rb") as f:
            st.download_button("📥 Baixar Partitura (PDF)", f, file_name=sel)
    else: st.info("Nenhuma partitura disponível.")

else:
    st.info("👋 Toque em um dos botões acima para navegar pelas cifras, áudios e partituras do nosso ministério!")

import streamlit as st
import os

# 1. Configuração da página para PC e Celular
st.set_page_config(
    page_title="Repositório - Ministério de Louvor",
    page_icon="🎵",
    layout="wide"
)

# 2. Criação automática das pastas de mídia
BASE_DIR = "arquivos"
CATEGORIAS = ["cifras", "audios", "videos", "partituras"]

for cat in CATEGORIAS:
    os.makedirs(os.path.join(BASE_DIR, cat), exist_ok=True)

st.title("🎵 Repositório Online de Louvor")
st.write("Acesse cifras, áudios, vídeos e partituras diretamente do PC ou celular.")

# 3. Painel de upload na barra lateral (Protegido por senha)
st.sidebar.header("⚙️ Painel do Administrador")
senha = st.sidebar.text_input("Senha para enviar arquivos:", type="password")

if senha == "louvor123":
    st.sidebar.success("Acesso liberado!")
    cat_upload = st.sidebar.selectbox("Categoria:", CATEGORIAS)
    arquivo = st.sidebar.file_uploader("Escolha o arquivo:")
    if arquivo is not None:
        with open(os.path.join(BASE_DIR, cat_upload, arquivo.name), "wb") as f:
            f.write(arquivo.getbuffer())
        st.sidebar.success(f"'{arquivo.name}' adicionado com sucesso!")
        st.toast("Novo arquivo adicionado! Atualize a página.")
elif senha != "":
    st.sidebar.error("Senha incorreta.")

# 4. Criação das Abas na Interface do Usuário
aba_cifras, aba_audios, aba_videos, aba_partituras = st.tabs([
    "📄 Cifras", "🔊 Áudios", "📺 Vídeos", "🎼 Partituras"
])

# FUNÇÃO PADRONIZADA (Garante que não dê NameError)
def listar_arquivos(categoria):
    caminho = os.path.join(BASE_DIR, categoria)
    if os.path.exists(caminho):
        return [f for f in os.listdir(caminho) if not f.startswith(".")]
    return []

# --- ABA DE CIFRAS ---
with aba_cifras:
    st.header("Cifras dos Louvores")
    lista = listar_arquivos("cifras")
    if lista:
        sel = st.selectbox("Escolha o louvor (Cifra):", lista, key="sel_cifra")
        cam = os.path.join(BASE_DIR, "cifras", sel)
        if sel.endswith(".txt"):
            with open(cam, "r", encoding="utf-8") as f:
                st.code(f.read(), language="text")
        else:
            with open(cam, "rb") as f:
                st.download_button("Baixar Cifra", f, file_name=sel)
    else:
        st.info("Nenhuma cifra adicionada ainda.")

# --- ABA DE ÁUDIOS ---
with aba_audios:
    st.header("Áudios de Referência")
    lista = listar_arquivos("audios")
    if lista:
        sel = st.selectbox("Escolha o áudio:", lista, key="sel_audio")
        cam = os.path.join(BASE_DIR, "audios", sel)
        
        # Lê o arquivo MP3 de forma binária para o player funcionar na nuvem
        with open(cam, "rb") as f:
            bytes_audio = f.read()
        st.audio(bytes_audio, format="audio/mp3")
    else:
        st.info("Nenhum áudio adicionado ainda.")

# --- ABA DE VÍDEOS ---
with aba_videos:
    st.header("Vídeos de Ensaios / Tutoriais")
    lista = listar_arquivos("videos")
    if lista:
        sel = st.selectbox("Escolha o vídeo:", lista, key="sel_video")
        cam = os.path.join(BASE_DIR, "videos", sel)
        st.video(cam)
    else:
        st.info("Nenhum vídeo adicionado ainda.")

# --- ABA DE PARTITURAS ---
with aba_partituras:
    st.header("Partituras Disponíveis")
    lista = listar_arquivos("partituras")
    if lista:
        sel = st.selectbox("Escolha a partitura:", lista, key="sel_partitura")
        cam = os.path.join(BASE_DIR, "partituras", sel)
        with open(cam, "rb") as f:
            st.download_button("Baixar Partitura (PDF)", f, file_name=sel)
    else:
        st.info("Nenhuma partitura adicionada ainda.")

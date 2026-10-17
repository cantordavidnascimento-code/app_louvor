import streamlit as st
import os

# Configuração da página para PC e Celular
st.set_page_config(
    page_title="Repositório - Ministério de Louvor",
    page_icon="🎵",
    layout="wide"
)

# Criação automática das pastas de mídia
BASE_DIR = "arquivos"
CATEGORIAS = ["cifras", "audios", "videos", "partituras"]

for cat in CATEGORIAS:
    os.makedirs(os.path.join(BASE_DIR, cat), exist_ok=True)

st.title("🎵 Repositório Online de Louvor")
st.write("Acesse cifras, áudios, vídeos e partituras.")

# Painel de upload na barra lateral
st.sidebar.header("⚙️ Painel do Administrador")
senha = st.sidebar.text_input("Senha para enviar arquivos:", type="password")

if senha == "louvor123":
    st.sidebar.success("Acesso liberado!")
    cat_upload = st.sidebar.selectbox("Categoria:", CATEGORIAS)
    arquivo = st.sidebar.file_uploader("Escolha o arquivo:")
    if arquivo is not None:
        with open(os.path.join(BASE_DIR, cat_upload, arquivo.name), "wb") as f:
            f.write(arquivo.getbuffer())
        st.sidebar.success(f"'{arquivo.name}' adicionado!")

# Abas do aplicativo
aba_cifras, aba_audios, aba_videos, aba_partituras = st.tabs([
    "📄 Cifras", "🔊 Áudios", "📺 Vídeos", "🎼 Partituras"
])

def listar(categoria):
    caminho = os.path.join(BASE_DIR, categoria)
    return [f for f in os.listdir(caminho) if not f.startswith(".")] if os.path.exists(caminho) else []

with aba_cifras:
    lista = listar("cifras")
    if lista:
        sel = st.selectbox("Escolha o louvor:", lista, key="cifra")
        cam = os.path.join(BASE_DIR, "cifras", sel)
        if sel.endswith(".txt"):
            with open(cam, "r", encoding="utf-8") as f:
                st.code(f.read(), language="text")
        else:
            with open(cam, "rb") as f:
                st.download_button("Baixar Cifra", f, file_name=sel)
    else: st.info("Nenhuma cifra adicionada.")

# --- ABA DE ÁUDIOS ---
with aba_audios:
    st.header("Áudios de Referência")
    def lista = listar_arquivos("audios")
    if lista:
        sel = st.selectbox("Escolha o áudio:", lista, key="audio")
        caminho_audio = os.path.join(BASE_DIR, "audios", sel)
        
        # CORREÇÃO: Abre e lê o arquivo MP3 de forma binária antes de mandar para o player
        with open(caminho_audio, "rb") as f:
            bytes_audio = f.read()
        
        # O player agora recebe os dados prontos para tocar instantaneamente
        st.audio(bytes_audio, format="audio/mp3")
    else:
        st.info("Nenhum áudio adicionado ainda.")


with aba_videos:
    lista = listar("videos")
    if lista:
        sel = st.selectbox("Escolha o vídeo:", lista, key="video")
        st.video(os.path.join(BASE_DIR, "videos", sel))
    else: st.info("Nenhum vídeo adicionado.")

with aba_partituras:
    lista = listar("partituras")
    if lista:
        sel = st.selectbox("Escolha a partitura:", lista, key="partitura")
        with open(os.path.join(BASE_DIR, "partituras", sel), "rb") as f:
            st.download_button("Baixar Partitura", f, file_name=sel)
    else: st.info("Nenhuma partitura adicionada.")

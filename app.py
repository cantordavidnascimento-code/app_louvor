import streamlit as st
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

# 1. Configuração da página integrada com visual Mobile-First
st.set_page_config(
    page_title="Louvor App",
    page_icon="🎵",
    layout="centered"
)

# Conexão automática com as credenciais do Google salvas nos Secrets do Streamlit
@st.cache_resource
def conectar_drive():
    try:
        info_chaves = st.secrets["gcp_service_account"]
        credenciais = service_account.Credentials.from_service_account_info(info_chaves)
        return build('drive', 'v3', credentials=credenciais)
    except Exception as e:
        st.error("Erro ao carregar as credenciais do Google Drive. Verifique os Secrets.")
        return None

drive_service = conectar_drive()
ID_PASTA_RAIZ = st.secrets["google_drive"]["id_pasta_raiz"]

# FUNÇÃO DE SEGURANÇA: Força o robô a compartilhar as pastas criadas com o seu e-mail pessoal
def forcar_permissao_usuario(file_id, email_usuario):
    if not drive_service: return
    try:
        permissao = {
            'type': 'user',
            'role': 'editor',
            'emailAddress': email_usuario
        }
        drive_service.permissions().create(fileId=file_id, body=permissao).execute()
    except Exception:
        pass

# Dicionário mapeando as categorias do app para os IDs das subpastas do Drive
@st.cache_data
def buscar_ou_criar_subpastas():
    if not drive_service: return {}
    
    categorias = ["cifras", "audios", "videos", "partituras"]
    pastas_mapeadas = {}
    
    query = f"'{ID_PASTA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resultados = drive_service.files().list(q=query, fields="files(id, name)").execute()
    pastas_existentes = {f['name']: f['id'] for f in resultados.get('files', [])}
    
    # Pega o e-mail do administrador configurado nos secrets para dar acesso
    email_admin = st.secrets["gcp_service_account"]["client_email"]
    
    for cat in categorias:
        if cat in pastas_existentes:
            pastas_mapeadas[cat] = pastas_existentes[cat]
        else:
            # Cria a pasta
            meta_pasta = {
                'name': cat,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [ID_PASTA_RAIZ]
            }
            nova_pasta = drive_service.files().create(body=meta_pasta, fields='id').execute()
            id_nova_pasta = nova_pasta.get('id')
            pastas_mapeadas[cat] = id_nova_pasta
            
            # BLINDAGEM: Força o compartilhamento da nova subpasta na hora
            forcar_permissao_usuario(id_nova_pasta, email_admin)
            
    return pastas_mapeadas

MAPA_PASTAS = buscar_ou_criar_subpastas()

# Injeção de CSS para o visual Mobile
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .stButton>button {
            width: 100%; border-radius: 20px; background-color: #2e3b4e; color: white;
            border: none; padding: 10px 20px; font-weight: bold; transition: 0.3s;
        }
        .stButton>button:hover { background-color: #4a5d78; color: #4dfd9f; }
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 450px; }
        code { color: #4dfd9f !important; background-color: #1e1e1e !important; font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

NOME_IMAGEM = "louvor.jpg"
if os.path.exists(NOME_IMAGEM):
    st.image(NOME_IMAGEM, use_container_width=True, output_format="JPEG")
else:
    st.markdown("<h1 style='text-align: center;'>🎶</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #2e3b4e; margin-top: 10px;'>Ministério de Música</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>IPI Cohab 1 • Repositório Permanente</p>", unsafe_allow_html=True)
st.divider()

# --- PAINEL DO ADMINISTRADOR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    senha = st.text_input("Senha de Administrador:", type="password")
    if senha == "louvor123":
        st.success("Acesso Liberado!")
        cat_upload = st.selectbox("Categoria do Envio:", ["cifras", "audios", "videos", "partituras"])
        arquivo = st.file_uploader("Escolha o arquivo para o Google Drive:")
        
        if arquivo is not None and drive_service:
            id_pasta_destino = MAPA_PASTAS.get(cat_upload)
            meta_arquivo = {'name': arquivo.name, 'parents': [id_pasta_destino]}
            media = MediaIoBaseUpload(io.BytesIO(arquivo.read()), mimetype=arquivo.type, resumable=True)
            
            with st.spinner("Enviando arquivo para o Google Drive de forma permanente..."):
                novo_arquivo = drive_service.files().create(body=meta_arquivo, media_body=media, fields='id').execute()
                id_arquivo_criado = novo_arquivo.get('id')
                
                # BLINDAGEM: Força o arquivo enviado a dar permissão para o seu e-mail pessoal vê-lo
                email_admin = st.secrets["gcp_service_account"]["client_email"]
                forcar_permissao_usuario(id_arquivo_criado, email_admin)
                
            st.success(f"'{arquivo.name}' salvo permanentemente no Drive!")
            st.cache_data.clear()
            st.toast("Arquivo atualizado!")
    elif senha != "":
        st.error("Senha inválida.")

def listar_arquivos_drive(categoria):
    if not drive_service or categoria not in MAPA_PASTAS: return []
    id_pasta = MAPA_PASTAS[categoria]
    query = f"'{id_pasta}' in parents and trashed = false"
    resultados = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return resultados.get('files', [])

def baixar_arquivo_drive(id_arquivo):
    if not drive_service: return b""
    requisicao = drive_service.files().get_media(fileId=id_arquivo)
    fh = io.BytesIO()
    baixador = MediaIoBaseDownload(fh, requisicao)
    concluido = False
    while not concluido:
        status, concluido = baixador.next_chunk()
    return fh.getvalue()

if "tela_atual" not in st.session_state: st.session_state.tela_atual = "Home"

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

# --- TELAS DO APP CONECTADAS AO DRIVE ---
if st.session_state.tela_atual == "Cifras":
    st.subheader("📄 Acervo de Cifras (Google Drive)")
    lista = listar_arquivos_drive("cifras")
    busca = st.text_input("🔍 Buscar louvor pelo nome:")
    if busca:
        lista = [f for f in lista if busca.lower() in f['name'].lower()]
    if lista:
        nomes = [f['name'] for f in lista]
        sel_nome = st.selectbox("Selecione a música:", nomes, key="nav_cifra")
        id_sel = next(f['id'] for f in lista if f['name'] == sel_nome)
        
        if sel_nome.endswith(".txt"):
            bytes_cifra = baixar_arquivo_drive(id_sel)
            st.code(bytes_cifra.decode("utf-8"), language="text")
        else:
            bytes_cifra = baixar_arquivo_drive(id_sel)
            st.download_button("📥 Baixar Arquivo de Cifra", bytes_cifra, file_name=sel_nome)
    else: st.info("Nenhum louvor encontrado no Drive.")

elif st.session_state.tela_atual == "Áudios":
    st.subheader("🔊 Áudios de Referência (Google Drive)")
    lista = listar_arquivos_drive("audios")
    busca = st.text_input("🔍 Buscar áudio pelo nome:")
    if busca:
        lista = [f for f in lista if busca.lower() in f['name'].lower()]
    if lista:
        nomes = [f['name'] for f in lista]
        sel_nome = st.selectbox("Selecione o áudio:", nomes, key="nav_audio")
        id_sel = next(f['id'] for f in lista if f['name'] == sel_nome)
        
        with st.spinner("Carregando player de áudio permanente..."):
            bytes_audio = baixar_arquivo_drive(id_sel)
        st.audio(bytes_audio, format="audio/mp3")
    else: st.info("Nenhum áudio encontrado no Drive.")

elif st.session_state.tela_atual == "Vídeos":
    st.subheader("📺 Vídeos de Ensaios (Google Drive)")
    lista = listar_arquivos_drive("videos")
    if lista:
        nomes = [f['name'] for f in lista]
        sel_nome = st.selectbox("Selecione o vídeo:", nomes, key="nav_video")
        id_sel = next(f['id'] for f in lista if f['name'] == sel_nome)
        bytes_video = baixar_arquivo_drive(id_sel)
        st.video(bytes_video)
    else: st.info("Nenhum vídeo disponível no Drive.")

elif st.session_state.tela_atual == "Partituras":
    st.subheader("🎼 Partituras Oficiais (Google Drive)")
    lista = listar_arquivos_drive("partituras")
    if lista:
        nomes = [f['name'] for f in lista]
        sel_nome = st.selectbox("Selecione o louvor:", nomes, key="nav_partitura")
        id_sel = next(f['id'] for f in lista if f['name'] == sel_nome)
        bytes_partitura = baixar_arquivo_drive(id_sel)
        st.download_button("📥 Baixar Partitura (PDF)", bytes_partitura, file_name=sel_nome)
    else: st.info("Nenhuma partitura disponível no Drive.")

else:
    st.info("👋 Toque em um dos botões acima para navegar pelas músicas conectadas ao nosso Google Drive!")

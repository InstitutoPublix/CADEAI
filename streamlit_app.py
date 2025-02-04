import streamlit as st
import openai
import os
import time
import json
import speech_recognition as sr
from PIL import Image

# Configurações iniciais
st.set_page_config(
    page_title="CADE IA",
    page_icon="💛",
    layout="wide",
)

# CSS personalizado para estilizar o balão de upload e o aviso
st.markdown(
    """
    <style>
    /* Estilo para o texto na sidebar */
    .stSidebar .stMarkdown, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stExpander {
        color: white !important;  
    }
    /* Estilo para o texto na parte principal */
    .stMarkdown, .stTextInput, .stTextArea, .stButton, .stExpander {
        color: black !important;  
    }
    /* Estilo para o container de upload de arquivos */
    .stFileUploader > div > div {
        background-color: white;  
        color: black;  
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;  
    }
    /* Estilo para o texto dentro do balão de upload */
    .stFileUploader label {
        color: black !important;  
    }
    /* Estilo para o botão de upload */
    .stFileUploader button {
        background-color: #8dc50b;  
        color: white;  
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
    }
    /* Estilo para o texto de drag and drop */
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {
        color: black !important;  
    }
    /* Estilo para o container de avisos (st.warning) */
    div[data-testid="stNotification"] > div > div {
        background-color: white !important;  
        color: black !important;  
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #ccc !important;  
    }
    /* Estilo para o ícone de aviso */
    div[data-testid="stNotification"] > div > div > div:first-child {
        color: #8dc50b !important;  
    }
    /* Estilo para o subtítulo */
    .subtitulo {
        font-size: 16px !important;  
        color: black !important;  
    }
    /* Estilo para o rótulo do campo de entrada na sidebar */
    .stSidebar label {
        color: white !important;  
    }
    /* Estilo para o texto na caixa de entrada do chat */
    .stChatInput input {
        color: white !important;  
    }
    /* Estilo para o placeholder na caixa de entrada do chat */
    .stChatInput input::placeholder {
        color: white !important;  
    }
    /* Estilo para o texto na caixa de entrada do chat */
    div.stChatInput textarea {
        color: white !important;  
    }
    /* Estilo para o placeholder na caixa de entrada do chat */
    div.stChatInput textarea::placeholder {
        color: white !important;  
        opacity: 1;  
    }
    /* Estilo para o ícone */
    .stImage > img {
        filter: drop-shadow(0 0 0 #8dc50b);  
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Caminho para a logo do bot
LOGO_BOT_PATH = "assets/Logo_bot.png"

# Verificar se o arquivo da logo existe
if os.path.exists(LOGO_BOT_PATH):
    try:
        LOGO_BOT = Image.open(LOGO_BOT_PATH)
    except Exception as e:
        st.error(f"Erro ao carregar a logo: {e}")
        LOGO_BOT = None
else:
    LOGO_BOT = None

# Caminho para o ícone personalizado
ICON_PATH = "assets/icon_cade.png"

# Verificar se o arquivo do ícone existe
if os.path.exists(ICON_PATH):
    try:
        col1, col2 = st.columns([1.5, 4])
        with col1:
            st.image(ICON_PATH, width=100)
        with col2:
            st.title("CADE IA")
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("CADE IA")

# Subtítulo
st.markdown('<p class="subtitulo">Sou uma IA especialista em Administração Pública desenvolvida pelo Instituto Publix em parceria com o Conselho Administrativo de Defesa Econômica CADE.</p>', unsafe_allow_html=True)

# Inicialização segura das variáveis de estado
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []

# Função para salvar o estado
def salvar_estado():
    estado = {"mensagens_chat": st.session_state.mensagens_chat}
    with open("estado_bot.json", "w") as f:
        json.dump(estado, f)

# Função para carregar o estado
def carregar_estado():
    if os.path.exists("estado_bot.json"):
        with open("estado_bot.json", "r") as f:
            estado = json.load(f)
            st.session_state.mensagens_chat = estado.get("mensagens_chat", [])

# Carregar o estado ao iniciar o aplicativo
carregar_estado()

# Função para limpar o histórico do chat
def limpar_historico():
    st.session_state.mensagens_chat = []
    salvar_estado()

# Configuração da API OpenAI
api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
if api_key:
    openai.api_key = api_key
    if st.sidebar.button("🧹 Limpar Histórico do Chat"):
        limpar_historico()
        st.sidebar.success("Histórico do chat limpo com sucesso!")
else:
    st.warning("Por favor, insira sua chave de API para continuar.")

# **Função de Reconhecimento de Voz**
def reconhecer_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Fale agora... (Aguarde o processamento)")
        try:
            audio = recognizer.listen(source, timeout=5)
            texto_transcrito = recognizer.recognize_google(audio, language="pt-BR")
            return texto_transcrito
        except sr.WaitTimeoutError:
            return "Tempo limite excedido. Tente novamente."
        except sr.UnknownValueError:
            return "Não foi possível entender o áudio. Tente novamente."
        except sr.RequestError:
            return "Erro na conexão com o serviço de reconhecimento de voz."

# Botão para ativar o reconhecimento de voz
if st.button("🎤 Gravar Áudio e Converter para Texto"):
    texto_audio = reconhecer_audio()
    if texto_audio:
        st.write(f"**Texto reconhecido:** {texto_audio}")

# Entrada para perguntas no chat
user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    st.session_state.mensagens_chat.append({"user": user_input, "bot": None})
    st.session_state.mensagens_chat[-1]["bot"] = f"Simulação de resposta para: {user_input}"
    salvar_estado()

# Exibição do histórico do chat
with st.container():
    for mensagem in st.session_state.mensagens_chat:
        if mensagem["user"]:
            with st.chat_message("user"):
                st.write(f"*Você:* {mensagem['user']}")
        if mensagem["bot"]:
            with st.chat_message("assistant"):
                st.write(f"*CADE IA:* {mensagem['bot']}")

import streamlit as st
import openai
import os
from PIL import Image
import time
import json

# Configurações iniciais da página
st.set_page_config(
    page_title="CADE IA",  # Personaliza o título da aba
    page_icon="💛",  # Personaliza o favicon
    layout="wide",
)

# CSS para tornar o site "White Label"
st.markdown(
    """
    <style>
    /* Remover barra superior do Streamlit */
    header {visibility: hidden;}

    /* Remover botão de configurações */
    [data-testid="stToolbar"] {visibility: hidden !important;}

    /* Remover rodapé do Streamlit */
    footer {visibility: hidden;}

    /* Remover botão de compartilhamento */
    [data-testid="stActionButtonIcon"] {display: none !important;}

    /* Ajustar margem para evitar espaços vazios */
    .block-container {padding-top: 1rem;}

    /* Estilização personalizada */
    .stSidebar .stMarkdown, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stExpander {
        color: white !important;
    }
    .stMarkdown, .stTextInput, .stTextArea, .stButton, .stExpander {
        color: black !important;
    }
    .stFileUploader > div > div {
        background-color: white;
        color: black;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;
    }
    .stFileUploader label {
        color: black !important;
    }
    .stFileUploader button {
        background-color: #8dc50b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
    }
    .stChatInput input, div.stChatInput textarea {
        color: white !important;
    }
    .stChatInput input::placeholder, div.stChatInput textarea::placeholder {
        color: white !important;
        opacity: 1;
    }
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
            st.image(ICON_PATH, width=10000000)
        with col2:
            st.title("CADE IA")
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("CADE IA")

# Subtítulo com fonte reduzida e texto preto
st.markdown(
    '<p class="subtitulo">Sou uma IA especialista em Administração Pública desenvolvida pelo Instituto Publix em parceria com o Conselho Administrativo de Defesa Econômica CADE, estou aqui para ajudar.</p>',
    unsafe_allow_html=True
)

# Inicialização segura das variáveis de estado
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []

# Função para salvar o estado em um arquivo JSON
def salvar_estado():
    estado = {"mensagens_chat": st.session_state.mensagens_chat}
    with open("estado_bot.json", "w") as f:
        json.dump(estado, f)

# Função para carregar o estado de um arquivo JSON
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

# Carregar arquivos de texto nativos como contexto
def carregar_contexto():
    contexto = ""
    arquivos_contexto = ["contexto1.txt", "contexto2.txt", "contexto3.txt", "contexto4.txt", "contexto5.txt"]
    for arquivo in arquivos_contexto:
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                contexto += f.read() + "\n\n"
        else:
            st.error(f"Arquivo de contexto não encontrado: {arquivo}")
    return contexto

# Carregar o contexto ao iniciar o aplicativo
contexto = carregar_contexto()

# Função para dividir o texto em chunks
def dividir_texto(texto, max_tokens=800):
    palavras = texto.split()
    chunks, chunk_atual = [], ""
    for palavra in palavras:
        if len(chunk_atual.split()) + len(palavra.split()) <= max_tokens:
            chunk_atual += palavra + " "
        else:
            chunks.append(chunk_atual.strip())
            chunk_atual = palavra + " "
    if chunk_atual:
        chunks.append(chunk_atual.strip())
    return chunks

# Função para selecionar chunks relevantes com base na pergunta
def selecionar_chunks_relevantes(pergunta, chunks):
    palavras_chave = pergunta.lower().split()
    return [chunk for chunk in chunks if any(palavra in chunk.lower() for palavra in palavras_chave)][:4]

# Função para gerar resposta com OpenAI usando GPT-4
def gerar_resposta(texto_usuario):
    if not contexto:
        return "Erro: Nenhum contexto carregado."
    
    chunks = dividir_texto(contexto)
    chunks_relevantes = selecionar_chunks_relevantes(texto_usuario, chunks)

    contexto_pergunta = "Você é uma IA feita pelo Publix em parceria com o CADE, que busca dar respostas especializadas sobre a Administração Pública e a instituição CADE. Responda com base no seguinte contexto:\n\n"
    for i, chunk in enumerate(chunks_relevantes):
        contexto_pergunta += f"--- Parte {i+1} do Contexto ---\n{chunk}\n\n"

    mensagens = [{"role": "system", "content": contexto_pergunta}, {"role": "user", "content": texto_usuario}]

    for _ in range(3):
        try:
            time.sleep(1)
            resposta = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=mensagens,
                temperature=0.3,
                max_tokens=800
            )
            return resposta["choices"][0]["message"]["content"]
        except Exception as e:
            time.sleep(2)
            continue
    return "Erro ao gerar a resposta."

# Adicionar a logo na sidebar
if LOGO_BOT:
    st.sidebar.image(LOGO_BOT, width=300)
else:
    st.sidebar.markdown("**Logo não encontrada**")

# Interface do Streamlit
api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
if api_key:
    openai.api_key = api_key
    if st.sidebar.button("🧹 Limpar Histórico do Chat"):
        limpar_historico()
        st.sidebar.success("Histórico do chat limpo com sucesso!")
else:
    st.warning("Por favor, insira sua chave de API para continuar.")

user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    st.session_state.mensagens_chat.append({"user": user_input, "bot": None})
    resposta = gerar_resposta(user_input)
    st.session_state.mensagens_chat[-1]["bot"] = resposta
    salvar_estado()

with st.container():
    for mensagem in st.session_state.mensagens_chat:
        with st.chat_message("user"):
            st.write(f"*Você:* {mensagem['user']}")
        with st.chat_message("assistant"):
            st.write(f"*CADE IA:* {mensagem['bot']}")

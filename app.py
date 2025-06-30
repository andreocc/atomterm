import streamlit as st
import requests
import json
import time

# Configuracao da pagina
st.set_page_config(
    page_title="AtomTerm Streamlit",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo CSS para um visual retro aprimorado
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

        :root {
            --retro-green: #00FF41; /* Fluorescent Green */
            --retro-dark: #0A0A0A;
            --retro-black: #000000;
        }

        body {
            font-family: 'VT323', monospace; /* Retro monospace font */
            color: var(--retro-green);
            background-color: var(--retro-black);
            overflow: hidden; /* Hide scrollbars for a cleaner look */
        }

        .stApp {
            background: var(--retro-black);
            border: 2px solid var(--retro-green); /* Retro border */
            box-shadow: 0 0 15px var(--retro-green); /* Subtle glow for the border */
            padding: 10px;
            position: relative;
            overflow: hidden; /* For scanlines and noise */
            min-height: 100vh; /* Ensure app takes full viewport height */
            display: flex;
            flex-direction: column;
        }

        /* CRT Scanline Effect */
        .stApp::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 2px, 3px 100%;
            pointer-events: none;
            z-index: 1;
        }

        /* Digital Noise/Interference Effect */
        .stApp::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(0deg, transparent 0%, transparent 1px, rgba(0, 255, 0, 0.05) 1px, rgba(0, 255, 0, 0.05) 2px);
            opacity: 0.1;
            pointer-events: none;
            z-index: 2;
            animation: noise 1s steps(10) infinite;
        }

        @keyframes noise {
            0% { background-position: 0 0; }
            100% { background-position: 0 100%; }
        }

        /* Text Glow Effect and subtle color distortion */
        .stMarkdown, h1, h2, h3, h4, h5, h6, .stTextInput > div > div > input, .stButton > button, .stSelectbox > div > div {
            text-shadow: 0 0 7px var(--retro-green), 0 0 10px var(--retro-green), 0 0 15px var(--retro-green); /* Stronger glow */
            filter: hue-rotate(5deg) saturate(1.1); /* Subtle color distortion */
        }

        /* Title with shadow/reflection */
        .st-emotion-cache-10trblm.e1nzilvr1 h1 {
            color: var(--retro-green);
            font-family: 'VT323', monospace;
            font-size: 3em; /* Larger title */
            text-shadow: 0 0 10px var(--retro-green), 0 0 20px var(--retro-green), 0 0 30px var(--retro-green); /* Stronger glow */
            margin-bottom: 0;
        }
        .st-emotion-cache-10trblm.e1nzilvr1 h1::after {
            content: attr(data-testid); /* This is a hack, Streamlit doesn't expose element content easily */
            display: block;
            font-size: 0.5em;
            opacity: 0.3;
            transform: scaleY(-1);
            filter: blur(2px); /* Reflection effect */
            text-shadow: none;
        }

        .stTextInput > div > div > input {
            background-color: var(--retro-dark);
            color: var(--retro-green);
            border: 1px solid var(--retro-green);
            font-family: 'VT323', monospace;
            font-size: 1.5em; /* Larger text */
            padding: 10px;
        }

        .stButton > button {
            background-color: var(--retro-dark);
            color: var(--retro-green);
            border: 1px solid var(--retro-green);
            font-family: 'VT323', monospace;
            font-size: 1.5em; /* Larger text */
            padding: 10px;
        }

        .stSelectbox > div > div {
            background-color: var(--retro-dark);
            color: var(--retro-green);
            border: 1px solid var(--retro-green);
            font-family: 'VT323', monospace;
            font-size: 1.5em; /* Larger text */
            padding: 10px;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--retro-green);
            font-family: 'VT323', monospace;
            font-size: 2.5em; /* Larger headings */
        }

        .stMarkdown {
            color: var(--retro-green);
            font-family: 'VT323', monospace; /* Ensure markdown also uses VT323 */
            font-size: 1.3em; /* Larger markdown text */
        }

        /* Chat messages */
        .stChatMessage {
            background-color: var(--retro-dark);
            border: 1px solid var(--retro-green);
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: 0 0 5px var(--retro-green); /* Glow for chat messages */
        }
        .stChatMessage p {
            color: var(--retro-green);
            font-family: 'VT323', monospace;
            font-size: 1.2em;
        }

        /* Ensure chat input is visible and styled */
        .st-chat-input {
            position: sticky; /* Changed from fixed to sticky */
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: var(--retro-black); /* Match app background */
            padding: 10px;
            border-top: 2px solid var(--retro-green);
            box-shadow: 0 0 15px var(--retro-green);
            z-index: 100;
            margin-top: auto; /* Push to bottom */
        }
        .st-chat-input input {
            width: calc(100% - 20px); /* Adjust width for padding */
            margin: 0 auto; /* Center the input */
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

OLLAMA_BASE_URL = "http://localhost:11434"

# Funcoes para interagir com a API do Ollama
def get_available_models():
    """Busca os modelos disponiveis no Ollama."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Erro ao conectar com Ollama: {e}")
        return []

def chat_with_ollama(model, messages):
    """Envia uma mensagem para o modelo Ollama e retorna a resposta."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro ao comunicar com o modelo: {e}"

# Inicializacao do estado da sessao
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# --- Barra Lateral ---
st.sidebar.title("AtomTerm Controle")

# Selecao de modelo
available_models = get_available_models()
if available_models:
    st.session_state.selected_model = st.sidebar.selectbox(
        "Selecione o Modelo:",
        options=available_models,
        index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
    )
else:
    st.sidebar.warning("Nenhum modelo do Ollama encontrado.")

# Botao para limpar historico
if st.sidebar.button("Limpar Historico"):
    st.session_state.messages = []
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Status do Sistema")
if available_models:
    st.sidebar.success(f"Ollama: ONLINE")
    st.sidebar.info(f"Modelo Atual: {st.session_state.selected_model}")
else:
    st.sidebar.error("Ollama: OFFLINE")


# --- Interface Principal ---
st.title("🤖 AtomTerm - Interface para Ollama")
st.markdown("---")

# Exibicao do historico de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuario
if prompt := st.chat_input("Digite sua mensagem..."):
    if not st.session_state.selected_model:
        st.warning("Por favor, selecione um modelo na barra lateral.")
    else:
        # Adiciona a mensagem do usuario ao historico e exibe
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gera e exibe a resposta do assistente com efeito de digitação
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("O agente esta pensando..."):
                response_text = chat_with_ollama(
                    st.session_state.selected_model,
                    st.session_state.messages
                )
            for char in response_text:
                full_response += char
                message_placeholder.markdown(full_response + "▌") # Add blinking cursor
                time.sleep(0.02) # Adjust typing speed here
            message_placeholder.markdown(full_response) # Remove cursor after typing

        # Adiciona a resposta do assistente ao historico
        st.session_state.messages.append({"role": "assistant", "content": full_response})

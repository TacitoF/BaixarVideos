import streamlit as st
import yt_dlp
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Downloader Universal",
    page_icon="⚫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS MODERNO (VISUAL DARK & ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* 1. Fundo Geral */
    .stApp {
        background-color: #0e0e0e;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 2. Textos Gerais */
    h1, h2, h3, p, label, .stMarkdown, .stInfo {
        color: #e0e0e0 !important;
    }
    
    /* 3. Inputs de Texto */
    .stTextInput > div > div > input {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #888888 !important;
        opacity: 1;
    }
    .stTextInput > div > div > input:focus {
        border-color: #555555 !important;
    }

    /* 4. Input Numérico */
    .stNumberInput > div > div > input {
        background-color: #1c1c1c !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 12px;
    }
    button[kind="secondary"] {
        background-color: #1c1c1c !important;
        border: 1px solid #333333 !important;
        color: #e0e0e0 !important;
    }

    /* 5. Botão Principal */
    .stButton > button {
        width: 100%;
        background-color: #e0e0e0 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
    }
    /* Força texto preto no botão */
    .stButton > button, .stButton > button p {
        color: #000000 !important;
    }
    .stButton > button:hover {
        background-color: #ffffff !important;
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }

    /* 6. Remove elementos padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("⚫ Downloader Pro")
st.markdown(
    """
    Suporte total para: **Instagram, TikTok, Facebook, X (Twitter), Pinterest**, entre outros.
    \n⚠️ *Este site não suporta downloads do YouTube.*
    """
)

# --- GERENCIAMENTO DE COOKIES ---
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

# --- LÓGICA DE INTERFACE ---
with st.container():
    url = st.text_input("Link da Mídia", placeholder="Cole o link do Instagram, TikTok ou Facebook...", label_visibility="collapsed")

    is_story = False
    story_index = 1
    button_label = "BAIXAR MÍDIA" # Texto padrão do botão

    # Detecção de Stories do Instagram
    if url and "instagram.com/stories/" in url:
        is_story = True
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📸 **Story detectado!** Selecione o número ao lado:")
        with col2:
            # O input numérico atualiza o script, mudando o texto do botão abaixo
            story_index = st.number_input("Nº", min_value=1, value=1, step=1, label_visibility="collapsed")
        
        # O botão muda de texto para confirmar a seleção do usuário
        button_label = f"BAIXAR STORY Nº {story_index}"

    # Verificação de YouTube (Bloqueio Visual)
    is_youtube = url and ("youtube.com" in url or "youtu.be" in url)

    if is_youtube:
        st.error("🚫 Downloads do YouTube não são permitidos. Tente outra plataforma.")
    else:
        # O botão só aparece se não for YouTube
        if st.button(button_label):
            if not url:
                st.toast("⚠️ Por favor, cole um link primeiro.")
            else:
                output_path = os.path.join(tmp_dir, f"media_final_{int(time.time())}.mp4")
                if os.path.exists(output_path): os.remove(output_path)
                
                status_text = st.empty()
                progress_bar = st.progress(0)
                
                try:
                    status_text.markdown("🔄 **Iniciando conexão...**")
                    progress_bar.progress(20)
                    
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_path,
                        'cookiefile': cookie_file,
                        'nocheckcertificate': True,
                        'quiet': True,
                        'no_warnings': True,
                        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    }

                    if is_story:
                        ydl_opts['playlist_items'] = str(story_index)
                        status_text.markdown(f"🔄 **Baixando Story nº {story_index}...**")
                    else:
                        status_text.markdown("🔄 **Processando mídia...**")

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    progress_bar.progress(80)

                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        progress_bar.progress(100)
                        status_text.success("✅ **Sucesso!**")
                        time.sleep(0.5)
                        progress_bar.empty()
                        
                        st.video(output_path)
                        
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="SALVAR NA GALERIA",
                                data=f,
                                file_name=f"media_download.mp4",
                                mime="video/mp4"
                            )
                    else:
                        status_text.error("❌ Erro: Arquivo vazio ou mídia não encontrada.")
                        progress_bar.empty()

                except Exception as e:
                    status_text.error(f"Erro: {e}")
                    progress_bar.empty()
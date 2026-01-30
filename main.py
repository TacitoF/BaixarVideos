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

# --- CSS DARK MODERNO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; font-family: 'Helvetica Neue', Arial, sans-serif; }
    h1, h2, p, label, .stMarkdown, .stInfo { color: #e0e0e0 !important; }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    .stTextInput > div > div > input::placeholder { color: #888888 !important; }
    
    /* Input Numérico */
    .stNumberInput > div > div > input {
        background-color: #1c1c1c !important;
        color: white !important;
        border: 1px solid #333333 !important;
    }
    button[kind="secondary"] {
        background-color: #1c1c1c !important;
        border: 1px solid #333333 !important;
        color: #e0e0e0 !important;
    }

    /* Botão Principal */
    .stButton > button {
        width: 100%;
        background-color: #e0e0e0 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
        color: #000000 !important;
    }
    .stButton > button p { color: #000000 !important; }
    .stButton > button:hover {
        background-color: #ffffff !important;
        transform: scale(1.01);
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE RESET ---
def reset_interface():
    """Limpa o vídeo anterior ao mudar o link."""
    if 'current_video_path' in st.session_state:
        del st.session_state['current_video_path']
    if 'download_success' in st.session_state:
        del st.session_state['download_success']

st.title("⚫ Downloader Pro")
st.markdown("Suporte: **Instagram (Stories, Reels, Posts)**, TikTok, X (Twitter).\n⚠️ *YouTube não suportado.*")

# --- COOKIES ---
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "cookies.txt")

# Garante a escrita correta dos cookies da conta nova
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

# --- INTERFACE ---
with st.container():
    url = st.text_input(
        "Link da Mídia", 
        placeholder="Cole o link aqui...", 
        label_visibility="collapsed",
        on_change=reset_interface
    )

    is_story = False
    story_index = 1
    button_label = "BAIXAR MÍDIA"

    # Detecção de Stories
    if url and "instagram.com/stories/" in url:
        is_story = True
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📸 **Story detectado!** Selecione qual baixar:")
        with col2:
            story_index = st.number_input("Nº", min_value=1, value=1, step=1, label_visibility="collapsed")
        
        button_label = f"BAIXAR STORY Nº {story_index}"

    # Bloqueio YouTube
    if url and ("youtube.com" in url or "youtu.be" in url):
        st.error("🚫 Downloads do YouTube não são permitidos.")
        reset_interface()
    else:
        if st.button(button_label):
            reset_interface()
            
            if not url:
                st.toast("⚠️ Cole um link primeiro.")
            else:
                output_path = os.path.join(tmp_dir, f"media_{int(time.time())}.mp4")
                if os.path.exists(output_path): os.remove(output_path)
                
                status = st.empty()
                prog = st.progress(0)
                
                try:
                    status.markdown("🔄 **Conectando com conta segura...**")
                    prog.progress(20)
                    
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_path,
                        'cookiefile': cookie_file,
                        'nocheckcertificate': True,
                        'quiet': True,
                        'no_warnings': True,
                        # User Agent de iPhone recente para evitar bloqueios na conta nova
                        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                    }

                    if is_story:
                        ydl_opts['playlist_items'] = str(story_index)
                        status.markdown(f"🔄 **Baixando Story nº {story_index}...**")
                    else:
                        status.markdown("🔄 **Processando mídia...**")

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    prog.progress(100)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.session_state['current_video_path'] = output_path
                        st.session_state['download_success'] = True
                        status.success("✅ **Sucesso!**")
                        time.sleep(0.5)
                        prog.empty()
                        st.rerun()
                    else:
                        status.error("❌ Erro: Arquivo vazio. Verifique se o story ainda existe.")
                        prog.empty()

                except Exception as e:
                    if "403" in str(e):
                        status.error("Erro 403: O Instagram pediu verificação na conta nova. Tente acessar o link no navegador primeiro.")
                    else:
                        status.error(f"Erro: {e}")
                    prog.empty()

    # Exibição do Resultado
    if 'download_success' in st.session_state and st.session_state['download_success']:
        path = st.session_state['current_video_path']
        st.markdown("---")
        st.video(path)
        with open(path, "rb") as f:
            st.download_button("SALVAR NA GALERIA", f, "video_download.mp4", "video/mp4")
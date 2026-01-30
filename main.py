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
    
    /* Botões Pequenos (Check) */
    div[data-testid="column"] button {
        background-color: #333333 !important;
        border: 1px solid #555555 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 48px; 
    }

    /* Botão Principal (Download) */
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
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO AUXILIAR ---
def get_stories_count(url, cookie_file):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'cookiefile': cookie_file,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                return len(list(info['entries']))
            return 1
    except Exception:
        return 0

# --- INÍCIO DO APP ---
st.title("⚫ Downloader Pro")
st.markdown("Suporte: **Instagram, TikTok, X.**\n⚠️ *YouTube não suportado.*")

tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "cookies.txt")

if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

# --- CONTROLE DE ESTADO (LÓGICA BLINDADA) ---
if 'last_url' not in st.session_state:
    st.session_state.last_url = ""

# --- INTERFACE DE ENTRADA ---
with st.container():
    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        # Input simples, sem callbacks complexos
        url = st.text_input(
            "Link da Mídia", 
            placeholder="Cole o link e clique na lupa...", 
            label_visibility="collapsed",
            key="url_input"
        )
    
    with col_btn:
        # Botão para FORÇAR a atualização se o Enter não funcionar
        check_click = st.button("🔎", help="Clique aqui para processar o link")

    # --- LÓGICA DE DETECÇÃO DE MUDANÇA ---
    # Se o URL mudou (via Enter) OU se o botão de lupa foi clicado
    if url != st.session_state.last_url or check_click:
        # Limpa tudo
        keys = ['current_video_path', 'download_success', 'story_count_cache']
        for k in keys:
            if k in st.session_state:
                del st.session_state[k]
        
        # Atualiza o último URL conhecido
        st.session_state.last_url = url
        
        # Se foi clique no botão, força rerun para renderizar a nova interface imediatamente
        if check_click:
            st.rerun()

    # --- RENDERIZAÇÃO DA INTERFACE ---
    is_story = False
    story_index = 1
    max_stories = 1
    button_label = "BAIXAR MÍDIA"

    if url:
        # 1. Instagram Story
        if "instagram.com/stories/" in url:
            is_story = True
            st.markdown("---")
            
            if 'story_count_cache' not in st.session_state:
                with st.spinner("🔍 Lendo link..."):
                    count = get_stories_count(url, cookie_file)
                    st.session_state['story_count_cache'] = count
            
            max_stories = st.session_state.get('story_count_cache', 1)
            
            if max_stories > 0:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"📸 **Story detectado!** {max_stories} disponíveis.")
                with col2:
                    story_index = st.number_input("Nº", min_value=1, max_value=max_stories, value=1, step=1, label_visibility="collapsed")
                button_label = f"BAIXAR STORY Nº {story_index}"
            else:
                st.error("⚠️ Erro ao ler stories. Verifique login/cookies.")

        # 2. X / Twitter
        elif "x.com" in url or "twitter.com" in url:
            st.markdown("---")
            st.info("🐦 **Link do X (Twitter) detectado!**")
            button_label = "BAIXAR DO X"

        # 3. TikTok
        elif "tiktok.com" in url:
            st.markdown("---")
            st.info("🎵 **Link do TikTok detectado!**")
            button_label = "BAIXAR TIKTOK"
        
        # 4. YouTube (Bloqueio)
        elif "youtube.com" in url or "youtu.be" in url:
            st.error("🚫 YouTube não suportado.")
            button_label = None # Esconde o botão

        # --- BOTÃO DE AÇÃO ---
        if button_label and st.button(button_label):
            if is_story and max_stories == 0:
                st.error("Sem stories para baixar.")
            else:
                output_path = os.path.join(tmp_dir, f"media_{int(time.time())}.mp4")
                if os.path.exists(output_path): os.remove(output_path)
                
                status = st.empty()
                prog = st.progress(0)
                
                try:
                    status.markdown("🔄 **Baixando...**")
                    prog.progress(20)
                    
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_path,
                        'cookiefile': cookie_file,
                        'nocheckcertificate': True,
                        'quiet': True,
                        'no_warnings': True,
                        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                    }

                    if is_story:
                        ydl_opts['playlist_items'] = str(story_index)

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    prog.progress(100)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.session_state['current_video_path'] = output_path
                        st.session_state['download_success'] = True
                        status.success("✅ **Pronto!**")
                        time.sleep(0.5)
                        prog.empty()
                        st.rerun()
                    else:
                        status.error("❌ Falha: Arquivo vazio.")
                        prog.empty()

                except Exception as e:
                    status.error(f"Erro: {e}")
                    prog.empty()

    # --- EXIBIÇÃO FINAL ---
    if 'download_success' in st.session_state and st.session_state['download_success']:
        path = st.session_state['current_video_path']
        st.markdown("---")
        st.video(path)
        with open(path, "rb") as f:
            st.download_button("SALVAR NA GALERIA", f, "video_download.mp4", "video/mp4")
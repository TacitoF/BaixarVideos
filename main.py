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

# --- FUNÇÕES AUXILIARES ---

def get_stories_count(url, cookie_file):
    """Verifica quantos stories existem no link sem baixar o vídeo."""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True, # Apenas extrai metadados, muito rápido
            'cookiefile': cookie_file,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                # Retorna a quantidade de itens na playlist (stories)
                return len(list(info['entries']))
            return 1 # Se não for playlist, assume que é 1
    except Exception:
        return 0

def reset_interface():
    """Limpa estados ao mudar o link."""
    keys_to_reset = ['current_video_path', 'download_success', 'story_count_cache']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

# --- APP START ---
st.title("⚫ Downloader Pro")
st.markdown("Suporte: **Instagram (Stories, Reels)**, TikTok, X.\n⚠️ *YouTube não suportado.*")

# --- COOKIES ---
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "cookies.txt")

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
    max_stories = 1
    button_label = "BAIXAR MÍDIA"

    # Lógica de Stories Inteligente
    if url and "instagram.com/stories/" in url:
        is_story = True
        st.markdown("---")
        
        # Verifica a contagem (com cache para não rodar toda hora)
        if 'story_count_cache' not in st.session_state:
            with st.spinner("🔍 Analisando quantos stories existem..."):
                count = get_stories_count(url, cookie_file)
                st.session_state['story_count_cache'] = count
        
        max_stories = st.session_state.get('story_count_cache', 1)
        
        if max_stories > 0:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📸 **Story detectado!** Encontramos **{max_stories}** stories disponíveis.")
            with col2:
                # O input agora tem limite máximo baseado na contagem real
                story_index = st.number_input(
                    "Nº", 
                    min_value=1, 
                    max_value=max_stories, 
                    value=1, 
                    step=1, 
                    label_visibility="collapsed"
                )
            button_label = f"BAIXAR STORY Nº {story_index}"
        else:
            st.error("⚠️ Não foi possível ler os stories. Verifique se a conta é privada ou se os stories expiraram.")

    # Bloqueio YouTube
    if url and ("youtube.com" in url or "youtu.be" in url):
        st.error("🚫 Downloads do YouTube não são permitidos.")
        reset_interface()
    else:
        if st.button(button_label):
            # Limpa vídeo anterior se houver
            if 'current_video_path' in st.session_state:
                 del st.session_state['current_video_path']
            
            if not url:
                st.toast("⚠️ Cole um link primeiro.")
            elif is_story and max_stories == 0:
                st.error("Erro: Nenhum story encontrado para baixar.")
            else:
                output_path = os.path.join(tmp_dir, f"media_{int(time.time())}.mp4")
                if os.path.exists(output_path): os.remove(output_path)
                
                status = st.empty()
                prog = st.progress(0)
                
                try:
                    status.markdown("🔄 **Conectando...**")
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
                        status.markdown(f"🔄 **Baixando Story {story_index} de {max_stories}...**")
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
                        status.error("❌ Erro: Arquivo vazio. O story pode ter expirado durante o processo.")
                        prog.empty()

                except Exception as e:
                    if "403" in str(e):
                        status.error("Erro 403: Acesso negado. Tente gerar novos cookies.")
                    else:
                        status.error(f"Erro: {e}")
                    prog.empty()

    # Exibição Persistente
    if 'download_success' in st.session_state and st.session_state['download_success']:
        path = st.session_state['current_video_path']
        st.markdown("---")
        st.video(path)
        with open(path, "rb") as f:
            st.download_button("SALVAR NA GALERIA", f, "video_download.mp4", "video/mp4")
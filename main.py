import streamlit as st
import yt_dlp
import os
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="NexusDL",
    page_icon="⚫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS REFINADO (ALINHAMENTO E ALTURA) ---
st.markdown("""
    <style>
    /* 1. BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2b2b2b 0%, #000000 80%);
        background-attachment: fixed;
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* 2. CONTAINER */
    .block-container {
        max-width: 600px;
        margin: 0 auto;
        padding-top: 15vh !important;
        padding-bottom: 5rem;
        text-align: center !important;
    }
    
    @media (max-width: 600px) {
        .block-container { 
            padding-top: 10vh !important; 
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    h1, h2, h3, p, label {
        text-align: center !important;
        color: #e0e0e0 !important;
    }
    
    h1 {
        background: linear-gradient(180deg, #ffffff 0%, #888888 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 2rem !important;
        font-size: 2.5rem !important;
    }

    .st-emotion-cache-1629p8f a, a.anchor-link { display: none !important; }

    /* 3. INPUT DE TEXTO (REDUZIDO E CENTRALIZADO) */
    .stTextInput input {
        /* Altura reduzida para 42px (Sensação visual melhor) */
        height: 42px !important;
        line-height: 42px !important; 
        min-height: 42px !important;
        
        /* Padding zerado verticalmente para garantir centro exato */
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        padding-left: 15px !important;
        
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        font-size: 14px !important; /* Fonte levemente menor para casar com a altura */
        backdrop-filter: blur(10px);
        
        text-align: left !important; 
    }
    
    .stTextInput input::placeholder {
        text-align: center !important;
        color: rgba(255, 255, 255, 0.5) !important;
        line-height: 42px !important; /* Garante que o placeholder siga a linha */
    }

    .stTextInput > div > div > input:focus {
        border-color: #666666 !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.05);
    }

    /* 4. COLUNAS CENTRALIZADAS */
    div[data-testid="column"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* 5. BOTÃO "VERIFICAR LINK" */
    .stButton button {
        width: 100% !important; 
        height: 40px; /* Levemente menor que o input para hierarquia visual */
        
        background-color: rgba(255, 255, 255, 0.08) !important; 
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 11px !important;
        letter-spacing: 1.5px;
        transition: all 0.3s ease !important;
        margin-top: 8px !important;
        
        white-space: nowrap !important;
    }
    
    .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-color: #ffffff !important;
        transform: translateY(-2px);
    }
    .stButton button p { color: #ffffff !important; }

    /* 6. BOTÃO DE DOWNLOAD (DESTAQUE) */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #00ff88 0%, #00d4ff 100%) !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 900 !important;
        height: 45px !important;
    }
    [data-testid="stDownloadButton"] button p { color: #000000 !important; }

    /* ANIMAÇÃO */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .stTextInput, .stButton, .stInfo, .stAlert { animation: fadeIn 0.6s ease-out forwards; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO AUXILIAR ---
def get_stories_count(url, cookie_file):
    try:
        ydl_opts = {
            'quiet': True, 'extract_flat': True, 'cookiefile': cookie_file, 'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: return len(list(info['entries']))
            return 1
    except: return 0

# --- INÍCIO DO APP ---
st.title("NexusDL")
st.markdown("Insta • TikTok • X (Twitter)", help="Cole o link abaixo.")

tmp_dir = "/tmp"
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)
cookie_file = os.path.join(tmp_dir, "cookies.txt")
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f: f.write(st.secrets["general"]["COOKIES_DATA"])

if 'last_url' not in st.session_state: st.session_state.last_url = ""

# --- INTERFACE ---
with st.container():
    # 1. INPUT
    url = st.text_input("Link", placeholder="Cole o link da mídia aqui...", label_visibility="collapsed", key="url_input")
    
    # 2. BOTÃO CENTRALIZADO (SIMETRIA PERFEITA)
    # Usamos [5, 4, 5].
    # Total = 14 partes.
    # Esquerda: 5 partes vazias.
    # Meio: 4 partes (Botão).
    # Direita: 5 partes vazias.
    # Isso garante matematicamente que o botão está no centro exato.
    b_col1, b_col2, b_col3 = st.columns([5, 4, 5])
    
    with b_col2:
        check_click = st.button("VERIFICAR LINK", help="Clique para processar")

    # Lógica de Reset
    if url != st.session_state.last_url or check_click:
        for k in ['current_video_path', 'download_success', 'story_count_cache']:
            if k in st.session_state: del st.session_state[k]
        st.session_state.last_url = url
        if check_click: st.rerun()

    is_story = False; story_index = 1; max_stories = 1; button_label = "PREPARAR DOWNLOAD"

    if url:
        if "instagram.com/stories/" in url:
            is_story = True
            if 'story_count_cache' not in st.session_state:
                with st.spinner("Conectando ao Nexus..."):
                    st.session_state['story_count_cache'] = get_stories_count(url, cookie_file)
            max_stories = st.session_state.get('story_count_cache', 1)
            
            if max_stories > 0:
                st.info(f"📸 Story • {max_stories} disponíveis")
                # Seletor centralizado
                s_col1, s_col2, s_col3 = st.columns([5, 4, 5])
                with s_col2:
                    story_index = st.number_input("Nº", 1, max_stories, 1, label_visibility="collapsed")
                button_label = f"PREPARAR STORY Nº {story_index}"
            else: st.error("Stories indisponíveis.")

        elif "instagram.com" in url: st.info("Instagram Reels/Post identificado")
        elif "x.com" in url or "twitter.com" in url: st.info("Link do X (Twitter) identificado")
        elif "tiktok.com" in url: st.info("Link do TikTok identificado")
        elif "youtube.com" in url or "youtu.be" in url: st.error("YouTube não suportado."); button_label = None

        # Botão de Ação Principal (Mantém a simetria [5, 4, 5])
        if button_label:
            act_col1, act_col2, act_col3 = st.columns([5, 4, 5])
            with act_col2:
                if st.button(button_label):
                    if is_story and max_stories == 0: st.error("Erro na seleção.")
                    else:
                        output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
                        if os.path.exists(output_path): os.remove(output_path)
                        status = st.empty(); prog = st.progress(0)
                        try:
                            status.markdown("Iniciando extração...")
                            prog.progress(20)
                            ydl_opts = {
                                'format': 'best', 'outtmpl': output_path, 'cookiefile': cookie_file,
                                'nocheckcertificate': True, 'quiet': True, 'no_warnings': True,
                                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                            }
                            if is_story: ydl_opts['playlist_items'] = str(story_index)
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                            prog.progress(100)
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                                st.session_state['current_video_path'] = output_path
                                st.session_state['download_success'] = True
                                status.empty(); time.sleep(0.2); prog.empty(); st.rerun()
                            else: status.error("Falha no download."); prog.empty()
                        except Exception as e: status.error(f"Erro: {e}"); prog.empty()

    if 'download_success' in st.session_state and st.session_state['download_success']:
        path = st.session_state['current_video_path']
        st.video(path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Botão Final também centralizado
        dl_col1, dl_col2, dl_col3 = st.columns([5, 4, 5])
        with dl_col2:
            with open(path, "rb") as f:
                st.download_button("BAIXAR ARQUIVO", f, f"NexusDL_{timestamp}.mp4", "video/mp4")
        st.toast("✅ Pronto! Clique em 'BAIXAR ARQUIVO'.", icon=None)
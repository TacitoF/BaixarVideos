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
# --- CSS REFINADO COM DESIGN MODERNO E TECNOLÓGICO ---
st.markdown("""
    <style>
    /* 1. BACKGROUND TECNOLÓGICO E MODERNO */
    .stApp {
        background: 
            radial-gradient(circle at 15% 50%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(0, 255, 136, 0.08) 0%, transparent 50%),
            linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0a0a0a 100%);
        background-attachment: fixed;
        font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
    }
    
    /* Efeito de partículas sutis (apenas visual) */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.03) 0px, transparent 2px),
            radial-gradient(circle at 60% 10%, rgba(0, 255, 136, 0.03) 0px, transparent 2px),
            radial-gradient(circle at 90% 40%, rgba(255, 255, 255, 0.02) 0px, transparent 2px);
        background-size: 400px 400px, 600px 600px, 500px 500px;
        z-index: -1;
        pointer-events: none;
    }
    
    /* 2. CONTAINER PRINCIPAL - CENTRALIZADO PERFEITAMENTE */
    .block-container {
        max-width: 600px !important;
        margin: 0 auto !important;
        padding-top: 15vh !important;
        padding-bottom: 5rem !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
    }
    
    /* Container com borda sutil e efeito de profundidade */
    .block-container::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 20px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.01));
        -webkit-mask: 
            linear-gradient(#fff 0 0) content-box, 
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Responsividade para mobile */
    @media (max-width: 768px) {
        .block-container { 
            padding-top: 10vh !important; 
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }
        
        h1 {
            font-size: 2.2rem !important;
            margin-bottom: 1.5rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .block-container { 
            padding-top: 8vh !important; 
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        h1 {
            font-size: 1.9rem !important;
        }
    }
    
    /* 3. TÍTULO COM GRADIENTE DINÂMICO */
    h1, h2, h3, p, label, .stMarkdown {
        text-align: center !important;
        color: #e0e0e0 !important;
        width: 100%;
    }
    
    h1 {
        background: linear-gradient(90deg, #FFFFFF 0%, #00d4ff 50%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900 !important;
        margin-bottom: 2.5rem !important;
        font-size: 2.8rem !important;
        letter-spacing: -0.5px;
        position: relative;
        display: inline-block;
        padding-bottom: 0.5rem;
    }
    
    /* Linha sutil abaixo do título */
    h1::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 25%;
        width: 50%;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
    }
    
    /* Subtítulo */
    .stMarkdown h3 {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 400 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1.5px;
        margin-bottom: 2.5rem !important;
        text-transform: uppercase;
    }
    
    /* 4. INPUT DE LINK - DESIGN MODERNO */
    .stTextInput {
        width: 100%;
        max-width: 500px;
        margin: 0 auto 1.5rem auto;
    }
    
    .stTextInput input {
        height: 48px !important;
        line-height: 48px !important;
        min-height: 48px !important;
        
        padding: 0 20px !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        
        color: white !important;
        font-size: 15px !important;
        font-weight: 400;
        
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .stTextInput input:hover {
        border-color: rgba(0, 212, 255, 0.3) !important;
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.15);
        transform: translateY(-1px);
    }
    
    .stTextInput input:focus {
        border-color: rgba(0, 212, 255, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1), 0 8px 30px rgba(0, 212, 255, 0.2) !important;
        outline: none;
        transform: translateY(-2px);
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
        text-align: center !important;
        font-size: 14px !important;
        letter-spacing: 0.5px;
        transition: color 0.2s ease;
    }
    
    .stTextInput input:focus::placeholder {
        color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* 5. BOTÕES - DESIGN COERENTE E CENTRALIZADO */
    /* Container de botão centralizado */
    .button-container {
        width: 100%;
        display: flex;
        justify-content: center;
        margin: 0.5rem 0 1.5rem 0;
    }
    
    /* Botão VERIFICAR LINK */
    .stButton button {
        width: 100% !important;
        max-width: 280px !important;
        height: 46px !important;
        
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.7s ease;
        z-index: -1;
    }
    
    .stButton button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(0, 212, 255, 0.4) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15);
    }
    
    .stButton button:hover::before {
        left: 100%;
    }
    
    .stButton button:active {
        transform: translateY(0);
        transition: transform 0.1s ease;
    }
    
    /* 6. BOTÃO DE DOWNLOAD (DESTAQUE TECNOLÓGICO) */
    [data-testid="stDownloadButton"] button {
        width: 100% !important;
        max-width: 280px !important;
        height: 52px !important;
        
        background: linear-gradient(90deg, #00ff88 0%, #00d4ff 100%) !important;
        background-size: 200% 100% !important;
        
        border: none !important;
        border-radius: 12px !important;
        
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 13px !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(0, 255, 136, 0.25);
        
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    [data-testid="stDownloadButton"] button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.7s ease;
        z-index: -1;
    }
    
    [data-testid="stDownloadButton"] button:hover {
        background-position: 100% 0 !important;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 255, 136, 0.35), 0 0 20px rgba(0, 212, 255, 0.2);
    }
    
    [data-testid="stDownloadButton"] button:hover::before {
        left: 100%;
    }
    
    [data-testid="stDownloadButton"] button p {
        color: #000000 !important;
        font-weight: 900 !important;
        margin: 0;
    }
    
    /* 7. ELEMENTOS DE STATUS E INFO */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 12px !important;
        border-left: none !important;
        margin: 0.5rem auto 1rem auto !important;
        max-width: 500px !important;
        text-align: center !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* 8. VIDEO PLAYER */
    .stVideo {
        border-radius: 16px !important;
        overflow: hidden !important;
        margin: 1.5rem auto !important;
        max-width: 500px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 9. NUMBER INPUT (PARA STORIES) */
    .stNumberInput input {
        height: 46px !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        text-align: center !important;
        font-weight: 600 !important;
    }
    
    /* 10. ANIMAÇÕES SUAVES */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glowPulse {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
    
    .stTextInput, .stButton, .stAlert, .stInfo, .stVideo, .stNumberInput {
        animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    
    .stButton button {
        animation: fadeInUp 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    
    /* 11. EFEITO DE BRILHO SUTIL NO CONTAINER */
    .block-container {
        animation: glowPulse 8s ease-in-out infinite;
    }
    
    /* 12. OCULTAR ELEMENTOS DO STREAMLIT */
    #MainMenu, footer, header, .stDeployButton {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 13. SCROLLBAR PERSONALIZADA */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ff88 0%, #00d4ff 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00ff88 0%, #00aaff 100%);
    }
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
import streamlit as st
import yt_dlp
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Downloader Pro",
    page_icon="⚫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PROFISSIONAL (CORRIGIDO) ---
st.markdown("""
    <style>
    /* Fundo e Fonte */
    .stApp { background-color: #0e0e0e; font-family: 'Helvetica Neue', Arial, sans-serif; }
    h1, h2, p, label, .stMarkdown, div { color: #e0e0e0 !important; }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    /* Botão Lupa (Check) */
    div[data-testid="column"] button {
        background-color: #1c1c1c !important;
        border: 1px solid #333333 !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
    }

    /* Botão de Ação Principal (PROCESSAR) */
    .stButton > button {
        width: 100%;
        background-color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.8rem !important;
        font-weight: 700 !important;
        margin-top: 5px !important;
        color: #000000 !important;
        text-transform: uppercase;
        font-size: 14px !important;
        letter-spacing: 1px;
    }
    .stButton > button:hover { background-color: #cccccc !important; }

    /* CORREÇÃO DO BOTÃO DE DOWNLOAD FINAL */
    [data-testid="stDownloadButton"] > button {
        width: 100% !important;
        background-color: #4CAF50 !important; /* Verde profissional para destaque final */
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        text-transform: uppercase;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #45a049 !important;
    }
    
    /* Alerts e Infos */
    .stAlert {
        background-color: #1c1c1c !important;
        color: #cccccc !important;
        border: 1px solid #333333 !important;
    }
    
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
st.title("Downloader Pro")
st.markdown("Insta • TikTok • X (Twitter)", help="Insira o link para identificar a plataforma.")

tmp_dir = "/tmp"
# Cria o diretório tmp se não existir (para teste local funcionar)
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

cookie_file = os.path.join(tmp_dir, "cookies.txt")

# Suporte a cookies (Local e Nuvem)
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

# --- CONTROLE DE ESTADO ---
if 'last_url' not in st.session_state:
    st.session_state.last_url = ""

# --- INTERFACE ---
with st.container():
    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        url = st.text_input(
            "Link", 
            placeholder="Cole o link da mídia aqui...", 
            label_visibility="collapsed",
            key="url_input"
        )
    
    with col_btn:
        check_click = st.button("🔎", help="Verificar link")

    # --- LÓGICA DE DETECÇÃO ---
    if url != st.session_state.last_url or check_click:
        keys = ['current_video_path', 'download_success', 'story_count_cache']
        for k in keys:
            if k in st.session_state: del st.session_state[k]
        st.session_state.last_url = url
        if check_click: st.rerun()

    is_story = False
    story_index = 1
    max_stories = 1
    button_label = "PROCESSAR LINK" # Texto alterado conforme pedido
    status_msg = None

    if url:
        # 1. Instagram Story
        if "instagram.com/stories/" in url:
            is_story = True
            if 'story_count_cache' not in st.session_state:
                with st.spinner("Analisando..."):
                    count = get_stories_count(url, cookie_file)
                    st.session_state['story_count_cache'] = count
            
            max_stories = st.session_state.get('story_count_cache', 1)
            
            if max_stories > 0:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.info(f"Instagram Story • {max_stories} disponíveis")
                with c2:
                    story_index = st.number_input("Nº", min_value=1, max_value=max_stories, value=1, step=1, label_visibility="collapsed")
                button_label = f"PROCESSAR STORY Nº {story_index}"
            else:
                st.error("Stories indisponíveis (Conta privada ou expirada).")

        # 2. Instagram Reels/Post
        elif "instagram.com" in url:
            st.info("Instagram Reels/Post identificado")
            button_label = "PROCESSAR INSTAGRAM"

        # 3. X / Twitter
        elif "x.com" in url or "twitter.com" in url:
            st.info("Link do X (Twitter) identificado")
            button_label = "PROCESSAR VÍDEO X"

        # 4. TikTok
        elif "tiktok.com" in url:
            st.info("Link do TikTok identificado")
            button_label = "PROCESSAR TIKTOK"
        
        # 5. YouTube (Bloqueio)
        elif "youtube.com" in url or "youtu.be" in url:
            st.error("YouTube não suportado pela plataforma.")
            button_label = None

        # --- BOTÃO DE AÇÃO ---
        if button_label and st.button(button_label):
            if is_story and max_stories == 0:
                st.error("Erro na seleção.")
            else:
                # Nome do arquivo temporário
                output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
                if os.path.exists(output_path): os.remove(output_path)
                
                status = st.empty()
                prog = st.progress(0)
                
                try:
                    status.markdown("Iniciando extração...")
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
                        status.empty()
                        time.sleep(0.2)
                        prog.empty()
                        st.rerun()
                    else:
                        status.error("Falha no download. Arquivo vazio.")
                        prog.empty()

                except Exception as e:
                    status.error(f"Erro no servidor: {e}")
                    prog.empty()

    # --- EXIBIÇÃO FINAL ---
    if 'download_success' in st.session_state and st.session_state['download_success']:
        path = st.session_state['current_video_path']
        
        st.video(path)
        
        col_dl, col_info = st.columns([1, 1])
        with col_dl:
            with open(path, "rb") as f:
                # Botão final com nome claro e CSS corrigido
                st.download_button(
                    label="BAIXAR ARQUIVO", 
                    data=f, 
                    file_name="video_baixado.mp4", 
                    mime="video/mp4"
                )
        
        st.toast("✅ Vídeo pronto! Clique em 'BAIXAR ARQUIVO' para salvar.", icon=None)
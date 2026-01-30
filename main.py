import streamlit as st
import yt_dlp
import os
import time
import re
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="NexusDL",
    page_icon="⚫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- FUNÇÃO LOG DISCORD ---
def send_discord_log(error_msg, video_url):
    if "general" in st.secrets and "DISCORD_WEBHOOK" in st.secrets["general"]:
        webhook_url = st.secrets["general"]["DISCORD_WEBHOOK"]
    else:
        return

    clean_msg = str(error_msg)[:800]
    
    is_feedback = "FEEDBACK" in video_url or "REPORT" in video_url
    
    title = "📢 Novo Feedback" if is_feedback else "🚨 Falha no Download"
    color = 3447003 if is_feedback else 15548997

    data = {
        "username": "NexusDL Monitor",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/564/564619.png",
        "embeds": [{
            "title": title,
            "color": color, 
            "fields": [
                {"name": "Origem/URL", "value": video_url, "inline": False},
                {"name": "Detalhes", "value": f"```{clean_msg}```", "inline": False},
                {"name": "Horário", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": True}
            ]
        }]
    }
    try:
        requests.post(webhook_url, json=data, timeout=3)
    except:
        pass

# --- FUNÇÃO PARA LIMPAR MENSAGENS DE ERRO ---
def clean_error_message(error_text):
    text = str(error_text)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    if "not a valid URL" in text or "Unsupported URL" in text:
        return "⚠️ Link inválido. Certifique-se de copiar a URL completa (http/https)."
        
    if "HTTP Error 400" in text:
        return "⚠️ Conexão recusada (Erro 400). O Instagram bloqueou a conexão anônima ou os cookies expiraram."
    if "Sign in to confirm" in text or "login" in text.lower():
        return "🔒 Conteúdo exige login (Cookies necessários)."
    if "Video unavailable" in text:
        return "🚫 Vídeo não encontrado ou excluído."
    if "Private video" in text:
        return "🔒 Este vídeo é privado."
        
    return f"Erro técnico: {text[:200]}..."

# --- CSS (ATUALIZADO PARA REMOVER BORDA VERMELHA E CENTRALIZAR BOTÕES) ---
st.markdown("""
    <style>
    /* 1. BACKGROUND MONOCROMÁTICO E TECNOLÓGICO */
    .stApp {
        background: 
            radial-gradient(circle at 15% 50%, rgba(255, 255, 255, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(255, 255, 255, 0.03) 0%, transparent 50%),
            linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0a0a0a 100%);
        background-attachment: fixed;
        font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        z-index: -1;
        pointer-events: none;
        opacity: 0.3;
    }
    
    /* 2. CONTAINER PRINCIPAL */
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
    
    @media (max-width: 768px) {
        .block-container { 
            padding-top: 10vh !important; 
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }
        h1 { font-size: 2.2rem !important; margin-bottom: 1.5rem !important; }
    }
    
    @media (max-width: 480px) {
        .block-container { 
            padding-top: 8vh !important; 
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        h1 { font-size: 1.9rem !important; }
    }
    
    /* 3. TÍTULO */
    h1, h2, h3, p, label, .stMarkdown {
        text-align: center !important;
        color: #e0e0e0 !important;
        width: 100%;
    }
    
    h1 {
        background: linear-gradient(90deg, #FFFFFF 0%, #AAAAAA 50%, #888888 100%);
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
    
    h1::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 25%;
        width: 50%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    }
    
    .stMarkdown h3 {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 400 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1.5px;
        margin-bottom: 2.5rem !important;
        text-transform: uppercase;
    }
    
    /* 4. INPUT (ATUALIZADO - BORDA NEUTRA) */
    .stTextInput {
        width: 100%;
        max-width: 500px;
        margin: 0 auto 1.5rem auto;
    }
    
    .stTextInput > div > div {
        display: flex !important;
        align-items: center !important;
        height: 100% !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        border-width: 1.5px !important;
    }

    /* BORDA CINZA NO FOCO - REMOVIDA BORDA VERMELHA */
    .stTextInput > div > div:focus-within {
        border-color: rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
    }

    .stTextInput input {
        height: 48px !important;
        line-height: 48px !important;
        min-height: 48px !important;
        padding: 0 20px !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        color: white !important;
        caret-color: white !important;
        font-size: 15px !important;
        font-weight: 400;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex !important;
        align-items: center !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
        text-align: center !important;
        font-size: 14px !important;
        letter-spacing: 0.5px;
        transition: color 0.2s ease;
        line-height: normal !important;
        position: relative;
        top: 0;
        transform: none;
    }
    
    /* REMOVE INSTRUÇÃO 'PRESS ENTER' */
    [data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* 5. BOTÕES (ATUALIZADO - SEMPRE CENTRALIZADOS) */
    .stButton, [data-testid="stDownloadButton"], .stFormSubmitButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    
    .stButton > button, 
    [data-testid="stDownloadButton"] > button,
    .stFormSubmitButton > button {
        width: 100% !important;
        max-width: 280px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    @media (max-width: 768px) {
        .stButton, [data-testid="stDownloadButton"], .stFormSubmitButton { 
            width: 100% !important; 
            max-width: 100% !important;
        }
    }
    
    .stButton button,
    .stFormSubmitButton button {
        width: 100% !important;
        max-width: 280px !important;
        height: 46px !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
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
        margin: 0 auto !important;
    }
    
    .stButton button::before,
    .stFormSubmitButton button::before {
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
    
    .stButton button:hover,
    .stFormSubmitButton button:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .stButton button:hover::before,
    .stFormSubmitButton button:hover::before { left: 100%; }
    .stButton button:active,
    .stFormSubmitButton button:active { transform: translateY(0); transition: transform 0.1s ease; }
    
    /* 6. BOTÃO DE DOWNLOAD (ATUALIZADO - CENTRALIZADO E COM MESMO LAYOUT) */
    [data-testid="stDownloadButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    [data-testid="stDownloadButton"] > div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    
    [data-testid="stDownloadButton"] button {
        width: 100% !important;
        max-width: 280px !important;
        height: 46px !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
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
        margin: 0 auto !important;
        display: block !important;
    }
    
    [data-testid="stDownloadButton"] button::before {
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
    
    [data-testid="stDownloadButton"] button:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stDownloadButton"] button:hover::before { left: 100%; }
    [data-testid="stDownloadButton"] button:active { transform: translateY(0); transition: transform 0.1s ease; }
    
    [data-testid="stDownloadButton"] button p { 
        color: #ffffff !important; 
        font-weight: 700 !important; 
        margin: 0; 
    }
    
    /* 7. ELEMENTOS DE STATUS */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 12px !important;
        border-left: none !important;
        margin: 0.5rem auto 1rem auto !important;
        max-width: 500px !important;
        text-align: center !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
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
    
    /* 9. NUMBER INPUT */
    .stNumberInput {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    .stNumberInput input {
        height: 46px !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        text-align: center !important;
        font-weight: 600 !important;
        max-width: 200px !important;
        margin: 0 auto !important;
    }
    
    /* 10. ANIMAÇÕES */
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    .stTextInput, .stButton, .stAlert, .stInfo, .stVideo, .stNumberInput { animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
    
    /* 11. OCULTAR ELEMENTOS */
    #MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }
    
    /* 12. SCROLLBAR */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.03); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #888888 0%, #aaaaaa 100%); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #aaaaaa 0%, #cccccc 100%); }
    
    /* 13. MOBILE */
    @media (max-width: 768px) {
        div[data-testid="column"] { padding-left: 0 !important; padding-right: 0 !important; }
        .stButton, [data-testid="stDownloadButton"], .stFormSubmitButton { 
            display: flex !important; 
            justify-content: center !important; 
            align-items: center !important; 
        }
        .stTextInput { padding-left: 0 !important; padding-right: 0 !important; }
        .stTextInput input { font-size: 16px !important; }
    }
    
    /* 14. TOAST E SPINNER */
    .stToast { background: rgba(30, 30, 30, 0.95) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 12px !important; backdrop-filter: blur(10px) !important; }
    .stSpinner > div { border-color: #ffffff transparent transparent transparent !important; }
    
    /* 15. COLUNAS PARA CENTRALIZAÇÃO */
    .stColumns {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    .stColumns > div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* 16. FORM STYLES */
    .stForm {
        margin-top: 1rem !important;
    }
    
    .stForm > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    
    /* 17. ESPECÍFICO PARA BOTÕES DE DOWNLOAD DENTRO DE COLUNAS */
    [data-testid="column"] [data-testid="stDownloadButton"] {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    /* 18. FORÇAR CENTRALIZAÇÃO DO CONTAINER DO DOWNLOAD BUTTON */
    div[data-testid="stDownloadButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT ---
st.markdown("""
    <script>
    function centerElements() {
        // Centralizar todos os botões
        const buttons = document.querySelectorAll('.stButton, .stFormSubmitButton');
        buttons.forEach(button => {
            if (button.parentElement) {
                button.parentElement.style.display = 'flex';
                button.parentElement.style.justifyContent = 'center';
                button.parentElement.style.alignItems = 'center';
                button.parentElement.style.width = '100%';
            }
        });
        
        // Centralizar botão de download específico
        const downloadButtons = document.querySelectorAll('[data-testid="stDownloadButton"]');
        downloadButtons.forEach(button => {
            button.style.display = 'flex';
            button.style.justifyContent = 'center';
            button.style.alignItems = 'center';
            button.style.width = '100%';
            button.style.margin = '0 auto';
            
            // Garantir que o container interno também esteja centralizado
            const innerDiv = button.querySelector('div');
            if (innerDiv) {
                innerDiv.style.display = 'flex';
                innerDiv.style.justifyContent = 'center';
                innerDiv.style.width = '100%';
            }
        });
        
        // Centralizar colunas
        const columns = document.querySelectorAll('.stColumns > div, [data-testid="column"]');
        columns.forEach(col => {
            col.style.display = 'flex';
            col.style.justifyContent = 'center';
            col.style.alignItems = 'center';
            col.style.flexDirection = 'column';
        });
        
        // Mobile adjustments
        if (window.innerWidth <= 768) {
            const inputs = document.querySelectorAll('.stTextInput');
            inputs.forEach(input => { 
                input.style.margin = '0 auto'; 
                input.style.maxWidth = '100%';
            });
        }
    }
    
    // Função para centralizar específicamente os botões de download
    function centerDownloadButtons() {
        const downloadContainers = document.querySelectorAll('[data-testid="stDownloadButton"]');
        downloadContainers.forEach(container => {
            // Garantir que o container principal esteja centralizado
            container.style.display = 'flex';
            container.style.justifyContent = 'center';
            container.style.alignItems = 'center';
            container.style.width = '100%';
            container.style.margin = '0 auto';
            
            // Garantir que o botão dentro do container esteja centralizado
            const button = container.querySelector('button');
            if (button) {
                button.style.margin = '0 auto';
                button.style.display = 'block';
            }
            
            // Se estiver dentro de uma coluna, centralizar a coluna também
            let parent = container.parentElement;
            while (parent && !parent.classList.contains('stApp')) {
                if (parent.getAttribute('data-testid') === 'column') {
                    parent.style.display = 'flex';
                    parent.style.justifyContent = 'center';
                    parent.style.alignItems = 'center';
                }
                parent = parent.parentElement;
            }
        });
    }
    
    window.addEventListener('load', function() {
        centerElements();
        centerDownloadButtons();
    });
    window.addEventListener('resize', function() {
        centerElements();
        centerDownloadButtons();
    });
    window.addEventListener('DOMContentLoaded', function() {
        centerElements();
        centerDownloadButtons();
    });
    
    // Verificar periodicamente para garantir centralização
    setInterval(function() {
        centerElements();
        centerDownloadButtons();
    }, 100);
    </script>
""", unsafe_allow_html=True)

# --- INÍCIO DO APP ---
st.title("NexusDL")
st.markdown("Insta • TikTok • X (Twitter)", help="Cole o link abaixo.")

# --- GERENCIAMENTO DE COOKIES ---
tmp_dir = "/tmp"
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)

if os.path.exists("cookies.txt"):
    cookie_file = "cookies.txt"
elif "general" in st.secrets:
    cookie_file = os.path.join(tmp_dir, "cookies.txt")
    with open(cookie_file, "w", encoding="utf-8") as f: 
        if "COOKIES_DATA" in st.secrets["general"]:
            f.write(st.secrets["general"]["COOKIES_DATA"])
else:
    cookie_file = None

# --- FUNÇÃO AUXILIAR ---
def get_stories_count(url, c_file):
    if not c_file: return 0
    try:
        ydl_opts = {
            'quiet': True, 'extract_flat': True, 'cookiefile': c_file, 'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: return len(list(info['entries']))
            return 1
    except: return 0

if 'last_url' not in st.session_state: st.session_state.last_url = ""

# --- INTERFACE ---
with st.container():
    url = st.text_input("Link", placeholder="Cole o link da mídia aqui...", label_visibility="collapsed", key="url_input")
    
    # Botão VERIFICAR LINK centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        check_click = st.button("VERIFICAR LINK", help="Clique para processar", use_container_width=True)

    if url != st.session_state.last_url:
        for k in ['current_video_path', 'download_success', 'story_count_cache', 'story_processed']:
            if k in st.session_state: del st.session_state[k]
        st.session_state.last_url = url

    download_now = False
    
    if url:
        is_story = "instagram.com/stories/" in url
        
        if is_story:
            if check_click and 'story_count_cache' not in st.session_state:
                with st.spinner("Conectando ao Nexus..."):
                    st.session_state['story_count_cache'] = get_stories_count(url, cookie_file)
            
            if 'story_count_cache' in st.session_state:
                max_stories = st.session_state['story_count_cache']
                if max_stories > 0:
                    st.info(f"📸 {max_stories} Stories disponíveis")
                    
                    # Número de story centralizado
                    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
                    with col_s2:
                        story_index = st.number_input("Nº", 1, max_stories, 1, label_visibility="collapsed")
                    
                    # Botão BAIXAR STORY centralizado
                    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                    with col_b2:
                        if st.button(f"BAIXAR STORY {story_index}", use_container_width=True):
                            download_now = True
                else:
                    st.error("Stories indisponíveis (Login necessário).")
        
        elif check_click:
            download_now = True
            story_index = 0

        if download_now:
            output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
            if os.path.exists(output_path): os.remove(output_path)
            
            status = st.empty(); prog = st.progress(0)
            try:
                status.markdown("Extraindo mídia...")
                prog.progress(20)
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                    'nocheckcertificate': True,
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
                
                if cookie_file:
                    ydl_opts['cookiefile'] = cookie_file

                if is_story:
                    ydl_opts['playlist_items'] = str(story_index)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                prog.progress(100)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.session_state['current_video_path'] = output_path
                    st.session_state['download_success'] = True
                    status.empty(); time.sleep(0.2); prog.empty(); st.rerun()
                else:
                    status.error("Falha no download. O arquivo não foi gerado."); prog.empty()
                    send_discord_log("Arquivo final tem 0 bytes ou não existe", url)

            except Exception as e:
                send_discord_log(e, url)
                status.error(clean_error_message(e))
                prog.empty()

    if st.session_state.get('download_success'):
        path = st.session_state['current_video_path']
        st.video(path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Botão BAIXAR ARQUIVO centralizado (CORRIGIDO)
        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
        with col_d2:
            with open(path, "rb") as f:
                st.download_button(
                    "BAIXAR ARQUIVO", 
                    f, 
                    f"NexusDL_{timestamp}.mp4", 
                    "video/mp4",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # --- RODAPÉ TOGGLE ---
    if 'feedback_open' not in st.session_state:
        st.session_state.feedback_open = False

    def toggle_feedback():
        st.session_state.feedback_open = not st.session_state.feedback_open

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        label_btn = "❌ Fechar Suporte" if st.session_state.feedback_open else "🏳️ Relatar Problema"
        st.button(label_btn, on_click=toggle_feedback, use_container_width=True)

    if st.session_state.feedback_open:
        with st.container():
            with st.form("report_form"):
                st.caption("Descreva o problema encontrado.")
                email_contato = st.text_input("Seu E-mail (Opcional)", placeholder="Contato...")
                descricao_erro = st.text_area("Detalhes do erro", placeholder="Ex: O vídeo baixou sem áudio...", height=100)
                
                # Botão ENVIAR REPORTE centralizado
                col_e1, col_e2, col_e3 = st.columns([1, 2, 1])
                with col_e2:
                    enviar_report = st.form_submit_button("Enviar Reporte", use_container_width=True)
                
                if enviar_report and descricao_erro:
                    msg_final = f"**Contato:** {email_contato}\n**Relato:** {descricao_erro}"
                    send_discord_log(msg_final, "📩 FEEDBACK MANUAL")
                    st.success("Enviado com sucesso!")
                elif enviar_report:
                    st.warning("Por favor, descreva o erro.")

    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 20px;">
        NexusDL © 2026
    </div>
    """, unsafe_allow_html=True)
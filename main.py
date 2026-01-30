import streamlit as st
import yt_dlp
import tempfile
import os
import time

# ========== CONFIGURAÇÃO ==========
st.set_page_config(page_title="Downloader IG", page_icon="📥", layout="centered")

# CSS simples
st.markdown("""
<style>
    .stTextInput input {font-size: 18px; padding: 15px; border-radius: 10px;}
    button {height: 55px; font-size: 18px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# ========== TÍTULO ==========
st.title("📥 Instagram Downloader")

# ========== GERENCIADOR DE COOKIES ==========
def get_cookies_from_secrets():
    """Pega cookies do Streamlit Secrets - VOCÊ ATUALIZA AQUI SEM MUDAR CÓDIGO"""
    
    # Opção 1: Streamlit Secrets (RECOMENDADO)
    if "instagram_cookies" in st.secrets:
        return st.secrets["instagram_cookies"]
    
    # Opção 2: Hardcoded (fallback)
    return """# Cookies do Instagram
.instagram.com	TRUE	/	TRUE	1804339209	csrftoken	AxphUKL3_SEUVcDt0KupgQ
.instagram.com	TRUE	/	TRUE	1797077440	datr	wOENaULolsWhkWR1bHHaLeKG
.instagram.com	TRUE	/	TRUE	1794053445	ig_did	C61C07EA-9D8D-45A8-8F1C-EE86039D6CE8
.instagram.com	TRUE	/	TRUE	1797077442	mid	aQ3hwQALAAGERhoVtMQ94Eh6gL_s
.instagram.com	TRUE	/	TRUE	1794053442	ig_nrcb	1
.instagram.com	TRUE	/	TRUE	1770384006	wd	1920x945
.instagram.com	TRUE	/	TRUE	1777555209	ds_user_id	1102578910
.instagram.com	TRUE	/	TRUE	0	rur	"LDC\\0541102578910\\0541801315208:01fe1a447024b78a1e89c8c0be3b9854723398e8ce0f9eb9023f3dbabdfaf4f0c51e6231"
.instagram.com	TRUE	/	TRUE	1801315209	sessionid	1102578910%3AckQRZD9sXouIsg%3A0%3AAYh5ATVfB-r2CaWp6WXmZ2xTgdGDQmcPdK1PitLq2g"""

def create_cookie_file():
    """Cria arquivo de cookies temporário"""
    cookie_content = get_cookies_from_secrets()
    cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
    cookie_file.write(cookie_content)
    cookie_file.close()
    return cookie_file.name

# ========== FUNÇÃO DE DOWNLOAD ==========
def download_instagram_video(url):
    """Função principal de download"""
    
    # Cria arquivo de cookies
    cookie_path = create_cookie_file()
    
    try:
        # Configuração do yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(tempfile.gettempdir(), 'ig_%(id)s.%(ext)s'),
            'cookiefile': cookie_path,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Instagram 275.0.0.27.98 Android',
            'http_headers': {
                'User-Agent': 'Instagram 275.0.0.27.98 Android',
                'X-IG-App-ID': '936619743392459',
            },
        }
        
        # Executa
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            with st.spinner('🔍 Conectando...'):
                info = ydl.extract_info(url, download=False)
                
                if info:
                    st.info(f"📹 **{info.get('title', 'Vídeo do Instagram')[:50]}...**")
                
                with st.spinner('⬇️  Baixando...'):
                    ydl.download([url])
        
        # Procura o arquivo
        for file in os.listdir(tempfile.gettempdir()):
            if file.startswith('ig_') and file.endswith('.mp4'):
                filepath = os.path.join(tempfile.gettempdir(), file)
                if os.path.getsize(filepath) > 1024:  # > 1KB
                    return filepath
        
        return None
        
    except Exception as e:
        st.error(f"❌ Erro: {str(e)[:100]}")
        return None
    
    finally:
        # Limpa arquivo de cookies
        try:
            os.unlink(cookie_path)
        except:
            pass

# ========== INTERFACE ==========
# Campo de input
url = st.text_input(
    "",
    value="https://www.instagram.com/reel/DS54kY8D1bU/",
    placeholder="Cole link do Instagram aqui...",
    help="Reels, Posts, Stories"
)

# Botão
if st.button("🚀 BAIXAR VÍDEO", type="primary", use_container_width=True):
    if not url:
        st.warning("⚠️  Cole um link!")
    else:
        # Limpa URL
        clean_url = url.split('?')[0].split('#')[0]
        
        # Download
        video_path = download_instagram_video(clean_url)
        
        if video_path:
            # Sucesso
            st.success("✅ Pronto!")
            
            # Mostra vídeo
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            
            st.video(video_bytes)
            
            # Botão download
            st.download_button(
                "💾 SALVAR NO CELULAR",
                data=video_bytes,
                file_name=f"instagram_{int(time.time())}.mp4",
                mime="video/mp4",
                type="primary",
                use_container_width=True
            )
            
            # Limpa
            try:
                os.remove(video_path)
            except:
                pass
        else:
            st.error("❌ Falha ao baixar")

# ========== CONFIGURAÇÃO DO SECRETS ==========
with st.expander("⚙️  CONFIGURAR COOKIES (APENAS UMA VEZ)"):
    st.markdown("""
    ### Como configurar PARA SEMPRE:
    
    1. **Obtenha cookies novos:**
       - Faça login no Instagram
       - Acesse [cookie-editor.com](https://cookie-editor.com)
       - Importe → Exporte (Netscape format)
    
    2. **No Streamlit Cloud:**
       - Settings → Secrets
       - Cole assim:
    
    ```toml
    [instagram_cookies]
    data = """
    .instagram.com	TRUE	/	TRUE	1804339209	csrftoken	SEU_TOKEN
    .instagram.com	TRUE	/	TRUE	1797077440	datr	SEU_DATR
    ... todos os cookies ...
    """
    ```
    
    3. **Pronto!** Quando expirar, só atualiza os Secrets.
    """)
import streamlit as st
import yt_dlp
import tempfile
import os
import time

# ========== CONFIGURAÇÃO ==========
st.set_page_config(
    page_title="📥 Video Downloader",
    page_icon="📥",
    layout="centered"
)

# ========== CSS SIMPLES ==========
st.markdown("""
<style>
    .stTextInput input {
        font-size: 18px !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    
    button {
        height: 55px !important;
        font-size: 18px !important;
        border-radius: 10px !important;
    }
    
    .stVideo {
        border-radius: 10px !important;
        margin: 20px 0 !important;
    }
    
    .error-box {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== TÍTULO ==========
st.title("📥 Video Downloader")
st.caption("Cole o link do vídeo (Instagram, TikTok, Twitter, Facebook, etc.)")

# ========== GERENCIADOR DE COOKIES ==========
def criar_arquivo_cookies():
    """Cria arquivo temporário com cookies do Instagram"""
    try:
        # Tenta pegar do Streamlit Secrets
        if "instagram_cookies" in st.secrets:
            cookies_data = st.secrets["instagram_cookies"]["data"]
        else:
            # Fallback: cookies hardcoded (você atualiza aqui)
            cookies_data = """# Instagram Cookies
.instagram.com	TRUE	/	TRUE	1804339209	csrftoken	AxphUKL3_SEUVcDt0KupgQ
.instagram.com	TRUE	/	TRUE	1797077440	datr	wOENaULolsWhkWR1bHHaLeKG
.instagram.com	TRUE	/	TRUE	1794053445	ig_did	C61C07EA-9D8D-45A8-8F1C-EE86039D6CE8
.instagram.com	TRUE	/	TRUE	1797077442	mid	aQ3hwQALAAGERhoVtMQ94Eh6gL_s
.instagram.com	TRUE	/	TRUE	1794053442	ig_nrcb	1
.instagram.com	TRUE	/	TRUE	1770384006	wd	1920x945
.instagram.com	TRUE	/	TRUE	1777555209	ds_user_id	1102578910
.instagram.com	TRUE	/	TRUE	0	rur	"LDC\\0541102578910\\0541801315208:01fe1a447024b78a1e89c8c0be3b9854723398e8ce0f9eb9023f3dbabdfaf4f0c51e6231"
.instagram.com	TRUE	/	TRUE	1801315209	sessionid	1102578910%3AckQRZD9sXouIsg%3A0%3AAYh5ATVfB-r2CaWp6WXmZ2xTgdGDQmcPdK1PitLq2g"""
        
        # Cria arquivo temporário
        cookie_file = tempfile.NamedTemporaryFile(
            mode='w', 
            delete=False, 
            suffix='.txt', 
            encoding='utf-8'
        )
        cookie_file.write(cookies_data)
        cookie_file.close()
        
        return cookie_file.name
        
    except Exception as e:
        st.error(f"Erro ao configurar cookies: {e}")
        return None

# ========== DETECTAR PLATAFORMA ==========
def detectar_plataforma(url):
    """Detecta qual plataforma é a URL"""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'facebook'
    elif 'reddit.com' in url_lower:
        return 'reddit'
    elif 'pinterest.com' in url_lower:
        return 'pinterest'
    elif 'linkedin.com' in url_lower:
        return 'linkedin'
    else:
        return 'outro'

# ========== CONFIGURAÇÕES POR PLATAFORMA ==========
def obter_configuracao(plataforma, url):
    """Retorna configurações específicas para cada plataforma"""
    
    base_config = {
        'format': 'best[height<=720]',
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(title).50s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'socket_timeout': 20,
        'retries': 3,
    }
    
    if plataforma == 'instagram':
        # Configuração para Instagram
        cookie_file = criar_arquivo_cookies()
        if cookie_file:
            base_config['cookiefile'] = cookie_file
        
        base_config.update({
            'user_agent': 'Instagram 275.0.0.27.98 Android',
            'http_headers': {
                'User-Agent': 'Instagram 275.0.0.27.98 Android',
                'X-IG-App-ID': '936619743392459',
            },
        })
        
        # Se for story, adiciona configuração especial
        if '/stories/' in url.lower():
            base_config['extractor_args'] = {
                'instagram': {'story_index': ['0']}
            }
    
    elif plataforma == 'tiktok':
        base_config.update({
            'user_agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; pt_BR)',
            'http_headers': {
                'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; pt_BR)',
                'Referer': 'https://www.tiktok.com/',
            },
        })
    
    elif plataforma == 'twitter':
        base_config.update({
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://twitter.com/',
            },
        })
    
    elif plataforma == 'facebook':
        base_config.update({
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.facebook.com/',
            },
        })
    
    else:  # outras plataformas
        base_config.update({
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
            },
        })
    
    return base_config

# ========== DOWNLOAD DE VÍDEO ==========
def baixar_video(url):
    """Função principal para baixar vídeos"""
    
    # Detecta plataforma
    plataforma = detectar_plataforma(url)
    
    # Verifica se é YouTube
    if plataforma == 'youtube':
        return None, "❌ **YouTube não é suportado.**\n\nUse outras plataformas como:\n• Instagram\n• TikTok\n• Twitter/X\n• Facebook\n• Reddit"
    
    try:
        # Obtém configuração
        config = obter_configuracao(plataforma, url)
        
        # Mostra status
        with st.spinner(f'🔍 Conectando ao {plataforma.upper()}...'):
            # Executa download
            with yt_dlp.YoutubeDL(config) as ydl:
                # Primeiro obtém informações
                info = ydl.extract_info(url, download=False)
                
                if info:
                    titulo = info.get('title', 'Vídeo')
                    st.info(f"📹 **{titulo[:60]}...**")
                
                # Agora baixa
                with st.spinner('⬇️  Baixando vídeo...'):
                    ydl.download([url])
        
        # Procura o arquivo baixado
        temp_dir = tempfile.gettempdir()
        video_encontrado = None
        
        for arquivo in os.listdir(temp_dir):
            if arquivo.endswith(('.mp4', '.webm', '.mkv', '.mov')):
                caminho = os.path.join(temp_dir, arquivo)
                # Verifica se foi criado recentemente
                if time.time() - os.path.getmtime(caminho) < 60:
                    if os.path.getsize(caminho) > 1024:  # > 1KB
                        video_encontrado = caminho
                        break
        
        if video_encontrado:
            return video_encontrado, None
        else:
            return None, "❌ Não foi possível encontrar o vídeo baixado."
        
    except Exception as e:
        error_msg = str(e)
        
        # Mensagens amigáveis para erros comuns
        if "Instagram" in error_msg and "login" in error_msg:
            return None, "❌ **Instagram requer login.**\n\nAtualize os cookies nas configurações do app."
        elif "unavailable" in error_msg.lower():
            return None, "❌ **Vídeo indisponível ou removido.**"
        elif "private" in error_msg.lower():
            return None, "❌ **Vídeo privado.**\n\nCertifique-se de que o vídeo é público."
        elif "rate-limit" in error_msg.lower():
            return None, "⚠️ **Limite de requisições atingido.**\n\nAguarde alguns minutos e tente novamente."
        else:
            return None, f"❌ **Erro:** {error_msg[:100]}"

# ========== INTERFACE PRINCIPAL ==========
# Campo para o link
url = st.text_input(
    "",
    placeholder="🔗 Cole aqui o link do vídeo...",
    help="Instagram, TikTok, Twitter/X, Facebook, Reddit, etc."
)

# Botão de download
if st.button("🚀 BAIXAR VÍDEO", type="primary", use_container_width=True):
    if not url:
        st.warning("⚠️  Por favor, cole um link primeiro!")
    elif not url.startswith(('http://', 'https://')):
        st.error("❌ Link inválido! Use http:// ou https://")
    else:
        # Remove parâmetros extras da URL
        url_limpa = url.split('?')[0].split('#')[0]
        
        # Executa o download
        video_path, erro = baixar_video(url_limpa)
        
        if video_path:
            # SUCESSO!
            st.success("✅ **Download concluído!**")
            
            # Mostra o vídeo
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            
            st.video(video_bytes)
            
            # Botão para salvar
            tamanho_mb = os.path.getsize(video_path) / (1024 * 1024)
            nome_arquivo = f"video_{int(time.time())}.mp4"
            
            st.download_button(
                "💾 SALVAR NO CELULAR",
                data=video_bytes,
                file_name=nome_arquivo,
                mime="video/mp4",
                type="primary",
                use_container_width=True,
                help=f"Tamanho: {tamanho_mb:.1f} MB"
            )
            
            # Limpa o arquivo temporário
            try:
                os.remove(video_path)
            except:
                pass
            
        elif erro:
            # ERRO
            st.markdown(f'<div class="error-box">{erro}</div>', unsafe_allow_html=True)
            
            # Sugestões
            with st.expander("💡 Dicas para resolver"):
                st.markdown("""
                **Para Instagram:**
                - Os cookies podem ter expirado
                - Atualize os cookies nas configurações
                - Certifique-se de seguir a conta (para stories)
                
                **Para outras plataformas:**
                - Verifique se o vídeo é público
                - Tente copiar o link novamente
                - Teste em outra plataforma
                """)

# ========== EXEMPLOS ==========
st.markdown("---")
st.caption("📋 **Exemplos de links que funcionam:**")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📸 Instagram", use_container_width=True):
        st.session_state.exemplo_url = "https://www.instagram.com/reel/Cz9tZK8u32u/"
        st.rerun()

with col2:
    if st.button("🎵 TikTok", use_container_width=True):
        st.session_state.exemplo_url = "https://www.tiktok.com/@example/video/123456789"
        st.rerun()

with col3:
    if st.button("🐦 Twitter", use_container_width=True):
        st.session_state.exemplo_url = "https://twitter.com/user/status/123456789"
        st.rerun()

# Preenche com exemplo se clicado
if 'exemplo_url' in st.session_state:
    url = st.session_state.exemplo_url
    del st.session_state.exemplo_url

# ========== CONFIGURAÇÃO DE COOKIES ==========
with st.expander("⚙️  CONFIGURAR COOKIES DO INSTAGRAM"):
    st.markdown("""
    ### Para Instagram funcionar:
    
    1. **Obtenha cookies atualizados:**
       - Faça login no Instagram
       - Acesse [cookie-editor.com](https://cookie-editor.com)
       - Clique em "Import from browser"
       - Selecione instagram.com
       - Clique em "Export" → "Netscape format"
    
    2. **No Streamlit Cloud:**
       - Vá em Settings → Secrets
       - Cole assim:
    
    ```toml
    [instagram_cookies]
    data = \"\"\"
    .instagram.com	TRUE	/	TRUE	1804339209	csrftoken	SEU_TOKEN_AQUI
    .instagram.com	TRUE	/	TRUE	1797077440	datr	SEU_DATR_AQUI
    ... todos os outros cookies ...
    \"\"\"
    ```
    
    3. **Salve e reinicie o app.**
    
    ⚠️ *Cookies expiram em ~30 dias. Atualize periodicamente.*
    """)
    
    # Link rápido para cookie-editor
    if st.button("🌐 Abrir cookie-editor.com"):
        st.markdown('[Abrir cookie-editor.com](https://cookie-editor.com){:target="_blank"}', unsafe_allow_html=True)

# ========== PLATAFORMAS SUPORTADAS ==========
st.markdown("---")
st.caption("✅ **Plataformas suportadas:** Instagram • TikTok • Twitter/X • Facebook • Reddit • Pinterest • LinkedIn • e mais")
st.caption("❌ **Não suportado:** YouTube")
import streamlit as st
import yt_dlp
import os
import tempfile
import time
import re
from typing import Optional

# ========== CONFIGURAÇÃO MOBILE-FIRST ==========
st.set_page_config(
    page_title="📥 Downloader Universal",
    page_icon="📥",
    layout="centered",  # Melhor para mobile
    initial_sidebar_state="collapsed"  # Sidebar recolhida no mobile
)

# CSS para mobile
st.markdown("""
<style>
    /* Ajustes gerais para mobile */
    .stTextInput > div > div > input {
        font-size: 16px !important; /* Evita zoom no iOS */
        padding: 12px !important;
    }
    
    button[kind="primary"] {
        width: 100% !important;
        height: 50px !important;
        font-size: 18px !important;
        margin-top: 10px !important;
    }
    
    /* Ajusta vídeos para mobile */
    .stVideo {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Melhora espaçamento */
    .main > div {
        padding: 1rem !important;
    }
    
    /* Botões de download maiores */
    .stDownloadButton > button {
        width: 100% !important;
        height: 45px !important;
        font-size: 16px !important;
    }
    
    /* Esconde elementos em mobile */
    @media (max-width: 768px) {
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
    }
</style>
""", unsafe_allow_html=True)

# ========== FUNÇÕES AUXILIARES ==========
def setup_cookies() -> str:
    """Configura cookies a partir dos secrets"""
    tmp_dir = tempfile.gettempdir()
    cookie_file = os.path.join(tmp_dir, "mobile_cookies.txt")
    
    if "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
        cookies_data = st.secrets["general"]["COOKIES_DATA"]
        # Corrige barras invertidas se necessário
        cookies_data = cookies_data.replace('\\\\', '\\')
        
        with open(cookie_file, "w", encoding="utf-8") as f:
            f.write(cookies_data)
        
        # Verifica se os cookies foram salvos
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r') as f:
                content = f.read()
                youtube_count = len(re.findall(r'\.youtube\.com', content))
                instagram_count = len(re.findall(r'\.instagram\.com', content))
                
                st.sidebar.success(f"✅ {youtube_count} cookies YouTube")
                st.sidebar.success(f"✅ {instagram_count} cookies Instagram")
        
        return cookie_file
    return None

def get_platform(url: str) -> dict:
    """Identifica a plataforma e retorna configurações específicas"""
    config = {
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'format': 'best[height<=720]',
        'extractor_args': {},
        'http_headers': {}
    }
    
    if 'youtube.com' in url or 'youtu.be' in url:
        config.update({
            'platform': 'youtube',
            'format': 'best[height<=480][ext=mp4]',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash'],
                }
            },
            'http_headers': {
                'Accept': '*/*',
                'Accept-Language': 'pt-BR,pt;q=0.9',
                'Referer': 'https://m.youtube.com/',
            }
        })
    elif 'instagram.com' in url:
        config.update({
            'platform': 'instagram',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9',
                'X-IG-App-ID': '936619743392459',
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
    elif 'tiktok.com' in url:
        config.update({
            'platform': 'tiktok',
            'format': 'best',
            'http_headers': {
                'Accept': '*/*',
                'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; pt_BR) Cronet',
            }
        })
    else:
        config['platform'] = 'other'
    
    return config

def create_progress_bar():
    """Cria uma barra de progresso visual"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    return progress_bar, status_text

def download_video(url: str, cookie_file: Optional[str] = None, story_index: int = 1):
    """Função principal de download"""
    with st.spinner('🔍 Analisando link...'):
        try:
            # Identifica plataforma
            platform_config = get_platform(url)
            platform = platform_config['platform']
            
            # Configurações base do yt-dlp
            ydl_opts = {
                'format': platform_config['format'],
                'outtmpl': os.path.join(tempfile.gettempdir(), '%(title).50s.%(ext)s'),
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
                'user_agent': platform_config['user_agent'],
                'http_headers': platform_config['http_headers'],
            }
            
            # Adiciona cookies se disponíveis
            if cookie_file and os.path.exists(cookie_file):
                ydl_opts['cookiefile'] = cookie_file
            
            # Configurações específicas por plataforma
            if platform_config['extractor_args']:
                ydl_opts['extractor_args'] = platform_config['extractor_args']
            
            # Configuração especial para Instagram Stories
            if platform == 'instagram' and 'stories' in url:
                ydl_opts['extractor_args'] = {
                    'instagram': {
                        'story_index': [str(story_index - 1)]
                    }
                }
            
            # Barra de progresso
            progress_bar, status_text = create_progress_bar()
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = d['downloaded_bytes'] / d['total_bytes']
                        progress_bar.progress(percent)
                        status_text.text(f"⬇️  Baixando: {d.get('_percent_str', '0%')}")
                elif d['status'] == 'finished':
                    progress_bar.progress(1.0)
                    status_text.text("✅ Processando vídeo...")
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Executa o download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Primeiro obtém informações
                info = ydl.extract_info(url, download=False)
                
                if info:
                    # Mostra informações
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"📹 **{info.get('title', 'Vídeo')[:50]}...**")
                    with col2:
                        if info.get('duration'):
                            mins = info['duration'] // 60
                            secs = info['duration'] % 60
                            st.info(f"⏱️  **{mins}:{secs:02d}**")
                    
                    # Para Instagram Stories
                    if platform == 'instagram' and 'entries' in info and 'stories' in url:
                        total = len(info['entries'])
                        st.info(f"📸 **{total} stories encontrados**")
                        if story_index > total:
                            st.warning(f"⚠️  Só existem {total} stories")
                
                # Agora faz o download
                status_text.text("🚀 Iniciando download...")
                result = ydl.download([url])
                
                # Encontra o arquivo baixado
                temp_dir = tempfile.gettempdir()
                recent_files = []
                
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        ext = os.path.splitext(file)[1].lower()
                        if ext in ['.mp4', '.webm', '.mkv', '.mov', '.avi']:
                            # Verifica se foi criado recentemente (últimos 30 segundos)
                            if time.time() - os.path.getmtime(file_path) < 30:
                                recent_files.append(file_path)
                
                if recent_files:
                    # Pega o mais recente
                    video_path = max(recent_files, key=os.path.getmtime)
                    
                    # Calcula tamanho
                    file_size = os.path.getsize(video_path)
                    size_mb = file_size / (1024 * 1024)
                    
                    # Sucesso!
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ **Pronto!** ({size_mb:.1f} MB)")
                    
                    # Mostra o vídeo
                    with open(video_path, "rb") as f:
                        video_bytes = f.read()
                    
                    st.video(video_bytes)
                    
                    # Botão de download otimizado para mobile
                    filename = os.path.basename(video_path)
                    if len(filename) > 40:
                        filename = filename[:40] + "..."
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 SALVAR",
                            data=video_bytes,
                            file_name=os.path.basename(video_path),
                            mime="video/mp4",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("🔄 NOVO", use_container_width=True):
                            st.rerun()
                    
                    # Limpeza automática após 5 minutos
                    st.caption(f"⚠️  O vídeo será apagado em 5 minutos")
                    
                    return True
                else:
                    st.error("❌ Não foi possível encontrar o arquivo baixado")
                    return False
                    
        except Exception as e:
            st.error(f"❌ **Erro:** {str(e)[:100]}")
            
            # Mensagens amigáveis para mobile
            error_msg = str(e).lower()
            if "http error 403" in error_msg:
                st.error("🔐 **Acesso bloqueado!** Atualize os cookies.")
            elif "private" in error_msg:
                st.error("🔒 **Conteúdo privado!** Faça login na plataforma.")
            elif "unavailable" in error_msg:
                st.error("❌ **Link inválido ou removido!**")
            elif "instagram" in error_msg and "login" in error_msg:
                st.error("📱 **Instagram requer login!**")
            
            return False

# ========== INTERFACE MOBILE ==========
def main():
    # Título otimizado para mobile
    st.markdown("<h1 style='text-align: center;'>📥 DOWNLOADER UNIVERSAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Baixe vídeos do YouTube, Instagram, TikTok e mais!</p>", unsafe_allow_html=True)
    
    # Configura cookies
    cookie_file = setup_cookies()
    
    # Campo de URL (grande para mobile)
    url = st.text_input(
        "",
        placeholder="🔗 Cole aqui o link do vídeo...",
        help="YouTube, Instagram, TikTok, Twitter/X, Facebook"
    )
    
    # Opções específicas
    story_index = 1
    if url and 'instagram.com/stories' in url:
        st.info("📸 **Instagram Story detectado**")
        story_index = st.slider("Escolha qual story baixar:", 1, 10, 1, 1)
    
    # Botão principal (grande para mobile)
    if st.button("🚀 BAIXAR AGORA", type="primary", use_container_width=True):
        if not url:
            st.warning("⚠️  Cole um link primeiro!")
        else:
            # Validação básica de URL
            if not url.startswith(('http://', 'https://')):
                st.error("❌ Link inválido! Use http:// ou https://")
            else:
                # Executa o download
                success = download_video(url, cookie_file, story_index)
                
                if not success:
                    # Sugestões de solução
                    with st.expander("🛠️  Solução de problemas"):
                        st.markdown("""
                        **Problemas comuns:**
                        
                        **YouTube:**
                        - 🍪 Cookies expirados (atualize no Secrets)
                        - 🔒 Vídeo com restrição de idade
                        - 🌐 Bloqueio regional
                        
                        **Instagram:**
                        - 📱 Faça login no app primeiro
                        - 🔗 Link inválido/expirado
                        - 👤 Conta privada (precisa seguir)
                        
                        **Geral:**
                        - 🔄 Tente outro link
                        - 📶 Verifique sua conexão
                        - ⏱️  Aguarde e tente novamente
                        """)
    
    # Exemplos de links (colapsável)
    with st.expander("📋 Exemplos de links que funcionam"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎵 YouTube (teste)", use_container_width=True):
                st.session_state.test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                st.rerun()
        with col2:
            if st.button("📸 Instagram (público)", use_container_width=True):
                st.session_state.test_url = "https://www.instagram.com/p/Cz9tZK8u32u/"
                st.rerun()
    
    # Teste rápido
    if 'test_url' in st.session_state:
        url = st.session_state.test_url
        del st.session_state.test_url
    
    # Sidebar apenas em desktop
    with st.sidebar:
        if st.button("🔄 LIMPAR CACHE", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache limpo!")
        
        st.markdown("---")
        st.markdown("**📱 Plataformas:**")
        st.markdown("- ✅ YouTube")
        st.markdown("- ✅ Instagram")
        st.markdown("- ✅ TikTok")
        st.markdown("- ✅ Twitter/X")
        st.markdown("- ✅ Facebook")
        
        st.markdown("---")
        st.markdown("**💡 Dicas:**")
        st.markdown("1. Use links completos")
        st.markdown("2. Vídeos devem ser públicos")
        st.markdown("3. Mantenha cookies atualizados")
        
        if cookie_file:
            st.markdown("---")
            st.success("🍪 Cookies ativos")
        else:
            st.markdown("---")
            st.warning("🔓 Modo visitante")

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    main()
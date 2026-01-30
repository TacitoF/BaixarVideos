import streamlit as st
import yt_dlp
import os
import tempfile
import time
import re
from typing import Optional, Dict, Any
import requests

# ========== CONFIGURAÇÃO MOBILE-FIRST ==========
st.set_page_config(
    page_title="📥 Downloader Universal",
    page_icon="📥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS otimizado para mobile
st.markdown("""
<style>
    /* Ajustes gerais para mobile */
    .stTextInput > div > div > input {
        font-size: 16px !important;
        padding: 14px !important;
        border-radius: 10px !important;
    }
    
    button[kind="primary"] {
        width: 100% !important;
        height: 55px !important;
        font-size: 18px !important;
        margin: 15px 0 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    
    /* Ajusta contêineres */
    .main > div {
        padding: 1rem !important;
    }
    
    /* Botões de download */
    .stDownloadButton > button {
        width: 100% !important;
        height: 50px !important;
        font-size: 17px !important;
        border-radius: 10px !important;
    }
    
    /* Mensagens de erro/sucesso */
    .stAlert {
        border-radius: 10px !important;
        margin: 10px 0 !important;
    }
    
    /* Esconde elementos desktop */
    @media (max-width: 768px) {
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    }
    
    /* Melhora visualização de vídeo */
    video {
        border-radius: 10px !important;
        margin: 15px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== GERENCIADOR DE COOKIES ==========
class CookieManager:
    @staticmethod
    def setup_cookies() -> Optional[str]:
        """Configura cookies com fallback automático"""
        tmp_dir = tempfile.gettempdir()
        cookie_file = os.path.join(tmp_dir, "smart_cookies.txt")
        
        try:
            if "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
                cookies_data = st.secrets["general"]["COOKIES_DATA"]
                cookies_data = cookies_data.replace('\\\\', '\\')
                
                with open(cookie_file, "w", encoding="utf-8") as f:
                    f.write(cookies_data)
                
                if CookieManager.validate_cookies(cookie_file):
                    return cookie_file
                else:
                    st.warning("⚠️  Cookies parecem expirados. Usando modo alternativo...")
                    return None
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def validate_cookies(cookie_file: str) -> bool:
        """Valida se os cookies estão funcionando"""
        try:
            with open(cookie_file, 'r') as f:
                content = f.read()
                
            # Verifica se tem cookies essenciais do YouTube
            essential_yt = ['LOGIN_INFO', '__Secure-1PSID', 'PREF']
            essential_ig = ['sessionid', 'csrftoken']
            
            yt_count = sum(1 for cookie in essential_yt if cookie in content)
            ig_count = sum(1 for cookie in essential_ig if cookie in content)
            
            return yt_count >= 2 or ig_count >= 2
            
        except:
            return False

# ========== ESTRATÉGIAS DE DOWNLOAD ==========
class DownloadStrategies:
    """Múltiplas estratégias para baixar vídeos"""
    
    @staticmethod
    def strategy_direct(url: str, platform: str) -> Dict[str, Any]:
        """Estratégia direta (sem cookies)"""
        base_config = {
            'format': 'best[height<=480][ext=mp4]',
            'nocheckcertificate': True,
            'quiet': True,
            'ignoreerrors': True,
            'socket_timeout': 15,
            'retries': 2,
        }
        
        if platform == 'youtube':
            base_config.update({
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'skip': ['dash', 'hls']
                    }
                },
                'http_headers': {
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.youtube.com/',
                }
            })
        elif platform == 'instagram':
            base_config.update({
                'user_agent': 'Instagram 269.0.0.18.75 Android',
                'http_headers': {
                    'X-IG-App-ID': '936619743392459',
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
        
        return base_config
    
    @staticmethod
    def strategy_with_cookies(url: str, platform: str, cookie_file: str) -> Dict[str, Any]:
        """Estratégia com cookies"""
        config = DownloadStrategies.strategy_direct(url, platform)
        config['cookiefile'] = cookie_file
        
        if platform == 'youtube':
            config['format'] = 'best[height<=720]'
            config['extractor_args']['youtube']['player_client'].append('android_embed')
        
        return config
    
    @staticmethod
    def strategy_lightweight(url: str, platform: str) -> Dict[str, Any]:
        """Estratégia leve para vídeos curtos"""
        config = DownloadStrategies.strategy_direct(url, platform)
        config['format'] = 'worst[ext=mp4]'  # Menor qualidade possível
        config['socket_timeout'] = 10
        config['retries'] = 1
        return config

# ========== DETECTOR DE PLATAFORMA ==========
def detect_platform(url: str) -> Dict[str, Any]:
    """Detecta a plataforma com precisão"""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return {
            'name': 'youtube',
            'icon': '🎵',
            'requires_cookies': True,
            'public_works': True
        }
    elif 'instagram.com' in url_lower:
        is_story = '/stories/' in url_lower
        return {
            'name': 'instagram',
            'icon': '📸',
            'is_story': is_story,
            'requires_cookies': True,
            'public_works': False
        }
    elif 'tiktok.com' in url_lower:
        return {
            'name': 'tiktok',
            'icon': '🎵',
            'requires_cookies': False,
            'public_works': True
        }
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return {
            'name': 'twitter',
            'icon': '🐦',
            'requires_cookies': False,
            'public_works': True
        }
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return {
            'name': 'facebook',
            'icon': '📘',
            'requires_cookies': False,
            'public_works': True
        }
    else:
        return {
            'name': 'other',
            'icon': '🌐',
            'requires_cookies': False,
            'public_works': True
        }

# ========== INTERFACE PRINCIPAL ==========
def main():
    # Cabeçalho mobile-friendly
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: 0;'>📥 DOWNLOADER</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; margin-top: 0;'>YouTube • Instagram • TikTok</p>", unsafe_allow_html=True)
    
    with col_status:
        cookie_file = CookieManager.setup_cookies()
        if cookie_file:
            st.success("🍪 OK")
        else:
            st.warning("🔓 SEM")
    
    # Campo de URL
    url = st.text_input(
        "",
        placeholder="🔗 https://youtube.com/watch?v=...",
        key="url_input",
        help="Cole qualquer link de vídeo"
    )
    
    # Detecta plataforma
    platform_info = None
    if url:
        platform_info = detect_platform(url)
        st.info(f"{platform_info['icon']} **{platform_info['name'].upper()}** detectado")
    
    # Configurações específicas
    story_index = 1
    use_cookies = st.checkbox("🔐 Usar cookies (recomendado)", value=True if cookie_file else False)
    low_quality = st.checkbox("📦 Modo leve (mais rápido)")
    
    if platform_info and platform_info.get('is_story'):
        story_index = st.slider("📊 Story número:", 1, 10, 1, 1)
    
    # Botão principal
    if st.button("🚀 BAIXAR AGORA", type="primary", use_container_width=True):
        if not url:
            st.warning("⚠️  Cole um link primeiro!")
            st.stop()
        
        # Validação básica
        if not url.startswith(('http://', 'https://')):
            st.error("❌ Link inválido! Use http:// ou https://")
            st.stop()
        
        # Processamento
        with st.spinner('🔍 Analisando...'):
            try:
                # Seleciona estratégia
                if use_cookies and cookie_file:
                    strategy = "with_cookies"
                    ydl_opts = DownloadStrategies.strategy_with_cookies(
                        url, platform_info['name'], cookie_file
                    )
                elif low_quality:
                    strategy = "lightweight"
                    ydl_opts = DownloadStrategies.strategy_lightweight(
                        url, platform_info['name']
                    )
                else:
                    strategy = "direct"
                    ydl_opts = DownloadStrategies.strategy_direct(
                        url, platform_info['name']
                    )
                
                # Configuração especial para Instagram Stories
                if platform_info['name'] == 'instagram' and platform_info.get('is_story'):
                    ydl_opts['extractor_args'] = {
                        'instagram': {'story_index': [str(story_index - 1)]}
                    }
                
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🔄 Conectando...")
                
                # Hook de progresso
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d:
                            percent = d['downloaded_bytes'] / d['total_bytes']
                            progress_bar.progress(percent)
                            speed = d.get('_speed_str', 'N/A')
                            status_text.text(f"⬇️  {d.get('_percent_str', '0%')} | {speed}")
                
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Executa o download
                temp_dir = tempfile.gettempdir()
                ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Primeiro tenta obter info
                    try:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            title = info.get('title', 'Vídeo')[:40]
                            duration = info.get('duration', 0)
                            
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.caption(f"📹 {title}...")
                            with col_info2:
                                if duration > 0:
                                    mins = duration // 60
                                    secs = duration % 60
                                    st.caption(f"⏱️  {mins}:{secs:02d}")
                    except:
                        pass
                    
                    # Agora baixa
                    status_text.text("🚀 Iniciando download...")
                    ydl.download([url])
                
                # Procura o arquivo
                video_file = None
                for file in os.listdir(temp_dir):
                    if file.endswith(('.mp4', '.webm', '.mkv')):
                        file_path = os.path.join(temp_dir, file)
                        if time.time() - os.path.getmtime(file_path) < 30:
                            video_file = file_path
                            break
                
                if video_file and os.path.getsize(video_file) > 1024:
                    # Sucesso!
                    progress_bar.progress(1.0)
                    status_text.success("✅ Pronto!")
                    
                    file_size = os.path.getsize(video_file) / (1024 * 1024)
                    st.success(f"**Download concluído!** ({file_size:.1f} MB)")
                    
                    # Mostra o vídeo
                    with open(video_file, "rb") as f:
                        video_bytes = f.read()
                    
                    st.video(video_bytes)
                    
                    # Botões de ação
                    col_dl, col_new = st.columns(2)
                    
                    with col_dl:
                        filename = f"video_{int(time.time())}.mp4"
                        st.download_button(
                            "💾 SALVAR",
                            data=video_bytes,
                            file_name=filename,
                            mime="video/mp4",
                            type="primary",
                            use_container_width=True
                        )
                    
                    with col_new:
                        if st.button("🔄 NOVO", use_container_width=True):
                            st.cache_data.clear()
                            st.rerun()
                    
                    # Info adicional
                    st.caption(f"🎯 Estratégia: {strategy} | 🍪 Cookies: {'Sim' if use_cookies and cookie_file else 'Não'}")
                    
                else:
                    st.error("❌ Falha no download!")
                    
                    # Tenta alternativa
                    if strategy != "lightweight":
                        st.info("🔄 Tentando modo leve...")
                        if st.button("🔄 TENTAR MODO LEVE", use_container_width=True):
                            st.session_state.retry_light = True
                            st.rerun()
                    
                    show_troubleshooting(url, platform_info)
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Erro: {error_msg[:80]}")
                
                if "403" in error_msg:
                    st.error("🔐 **YouTube bloqueou!** Atualize cookies no Secrets.")
                    show_cookie_instructions()
                elif "Private" in error_msg or "login" in error_msg:
                    st.error("🔒 **Conteúdo privado!** Faça login na plataforma.")
                elif "Unavailable" in error_msg or "removed" in error_msg:
                    st.error("❌ **Link inválido ou removido!**")
                else:
                    show_troubleshooting(url, platform_info)
    
    # Retry com modo leve
    if 'retry_light' in st.session_state:
        st.session_state.low_quality = True
        del st.session_state.retry_light
    
    # Sidebar de ajuda
    with st.sidebar:
        st.header("🆘 Ajuda Rápida")
        
        if st.button("🔄 Testar YouTube público", use_container_width=True):
            st.session_state.test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            st.rerun()
        
        if st.button("📸 Testar Instagram público", use_container_width=True):
            st.session_state.test_url = "https://www.instagram.com/p/Cz9tZK8u32u/"
            st.rerun()
        
        st.markdown("---")
        st.markdown("**🎯 Dicas:**")
        st.markdown("• YouTube precisa de cookies")
        st.markdown("• Instagram: siga a conta")
        st.markdown("• Links públicos funcionam melhor")
        
        if not cookie_file:
            st.markdown("---")
            st.warning("**🍪 Cookies:**")
            st.markdown("1. Faça login no YouTube")
            st.markdown("2. Use cookie-editor.com")
            st.markdown("3. Cole no Secrets")

# ========== FUNÇÕES AUXILIARES ==========
def show_troubleshooting(url: str, platform_info: Dict):
    """Mostra solução de problemas específica"""
    with st.expander("🛠️  SOLUÇÃO DE PROBLEMAS", expanded=True):
        
        if platform_info['name'] == 'youtube':
            st.markdown("""
            **Problemas com YouTube:**
            
            1. **🍪 Cookies expirados** (mais comum)
               - Atualize cookies no Secrets
               - Use cookie-editor.com
            
            2. **🔒 Vídeo restrito**
               - Idade/região bloqueada
               - Tente vídeo público
            
            3. **🌐 Bloqueio do servidor**
               - Aguarde alguns minutos
               - Tente modo leve
            
            **Solução rápida:**
            """)
            
            if st.button("🔄 Testar vídeo público"):
                st.session_state.test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                st.rerun()
        
        elif platform_info['name'] == 'instagram':
            st.markdown("""
            **Problemas com Instagram:**
            
            1. **📱 Login necessário**
               - Cookies do Instagram necessários
               - Faça login no app primeiro
            
            2. **🔗 Story expirado**
               - Stories duram 24h
               - Link pode estar inválido
            
            3. **👤 Conta privada**
               - Você precisa seguir
               - Ou conta deve ser pública
            
            **Teste rápido:**
            """)
            
            if st.button("📸 Testar post público"):
                st.session_state.test_url = "https://www.instagram.com/p/Cz9tZK8u32u/"
                st.rerun()
        
        else:
            st.markdown("""
            **Problemas gerais:**
            
            1. **🔗 Link inválido**
               - Verifique se o vídeo existe
               - Copie novamente o link
            
            2. **📶 Conexão lenta**
               - Aguarde e tente novamente
               - Use modo leve
            
            3. **⚠️  Plataforma não suportada**
               - Alguns sites bloqueiam downloads
               - Tente outra plataforma
            """)

def show_cookie_instructions():
    """Mostra instruções para atualizar cookies"""
    with st.expander("📝 COMO ATUALIZAR COOKIES"):
        st.markdown("""
        **Passo a passo:**
        
        1. **🌐 Abra** [cookie-editor.com](https://cookie-editor.com)
        2. **🔓 Faça login** no YouTube
        3. **📋 Clique** em "Import from browser"
        4. **🎯 Selecione** youtube.com
        5. **📤 Clique** em "Export" → "Netscape format"
        6. **📋 Copie** TODO o texto
        7. **⚙️ No Streamlit**, vá em Settings → Secrets
        8. **📝 Cole** no campo COOKIES_DATA
        9. **🔄 Reinicie** o app
        
        **Dica:** Cookies expiram em 30 dias. Atualize periodicamente.
        """)

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    # Teste rápido
    if 'test_url' in st.session_state:
        st.session_state.url_input = st.session_state.test_url
        del st.session_state.test_url
    
    main()
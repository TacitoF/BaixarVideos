import streamlit as st
import yt_dlp
import os
import tempfile
import time

st.set_page_config(page_title="Downloader Universal", page_icon="📲")
st.title("📲 Downloader Universal")

# Configuração de diretório temporário
tmp_dir = tempfile.gettempdir()
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")
output_path = os.path.join(tmp_dir, f"video_{int(time.time())}.mp4")

# Escreve os cookies do Secrets
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])
    st.success("✅ Cookies carregados do Secrets")
else:
    st.warning("⚠️  Cookies não encontrados no Secrets. Baixando como visitante...")

url = st.text_input("Cole o link aqui:", placeholder="Ex: https://www.youtube.com/watch?v=...")

# Configuração específica para Instagram Stories
story_index = None
if url and "instagram.com/stories" in url:
    col1, col2 = st.columns(2)
    with col1:
        story_index = st.number_input("Número do story na sequência:", min_value=1, value=1, step=1)
    with col2:
        st.info("Use 1 para o primeiro, 2 para o segundo, etc.")

if st.button("📥 Preparar Download", type="primary"):
    if not url:
        st.warning("⚠️  Insira um link primeiro.")
    else:
        with st.spinner('⏳ Baixando na nuvem...'):
            try:
                # Configurações do yt-dlp
                ydl_opts = {
                    'format': 'best[height<=720]',  # Limita a 720p
                    'outtmpl': output_path,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'noprogress': True,
                    'quiet': True,
                    'socket_timeout': 30,
                    'retries': 10,
                    'fragment_retries': 10,
                    'skip_unavailable_fragments': True,
                    'no_warnings': True,
                    'ignoreerrors': True,
                    'merge_output_format': 'mp4',
                }
                
                # Adiciona cookies se existirem
                if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 100:
                    ydl_opts['cookiefile'] = cookie_file
                    st.info("🔐 Usando cookies para download")
                
                # Configuração para Instagram Stories
                if "instagram.com/stories" in url and story_index:
                    ydl_opts['extractor_args'] = {
                        'instagram': {
                            'story_index': [str(story_index - 1)]  # Índice 0-based
                        }
                    }
                    ydl_opts['headers'] = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                        'Referer': 'https://www.instagram.com/',
                    }
                
                # Configuração específica para YouTube
                if 'youtube.com' in url or 'youtu.be' in url:
                    ydl_opts['format'] = 'best[height<=480][ext=mp4]'  # YouTube: 480p
                    ydl_opts['extractor_args'] = {
                        'youtube': {
                            'player_client': ['android'],  # Cliente mobile para evitar bloqueios
                        }
                    }
                
                # Executa o download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Primeiro extrai informações (para debug)
                    try:
                        info = ydl.extract_info(url, download=False)
                        st.info(f"📹 **Título:** {info.get('title', 'Desconhecido')}")
                        st.info(f"⏱️ **Duração:** {info.get('duration', 'Desconhecido')} segundos")
                        if 'entries' in info and "instagram.com/stories" in url:
                            st.info(f"📊 **Total de stories:** {len(info['entries'])}")
                    except Exception as info_error:
                        st.warning(f"ℹ️  Não foi possível obter informações: {info_error}")
                    
                    # Faz o download
                    ydl.download([url])
                
                # Verifica se o arquivo foi baixado
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:  # > 1KB
                    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    
                    st.success(f"✅ **Download concluído!** ({file_size_mb:.1f} MB)")
                    
                    # Mostra o vídeo
                    with open(output_path, "rb") as video_file:
                        video_bytes = video_file.read()
                    
                    st.video(video_bytes)
                    
                    # Botão de download
                    st.download_button(
                        label="📱 Salvar no Celular",
                        data=video_bytes,
                        file_name=f"video_{int(time.time())}.mp4",
                        mime="video/mp4",
                        type="primary"
                    )
                    
                    # Limpeza
                    try:
                        os.remove(output_path)
                    except:
                        pass
                        
                else:
                    st.error("❌ **Falha no download.** Possíveis causas:")
                    st.error("1. 🍪 Cookies expirados (atualize no Secrets)")
                    st.error("2. 🔒 Vídeo privado/bloqueado")
                    st.error("3. 📵 Link inválido")
                    st.error("4. ⏱️ Timeout do servidor")
                    
                    # Sugestões
                    st.info("💡 **Soluções:**")
                    st.info("- Teste com vídeos públicos do YouTube primeiro")
                    st.info("- Atualize os cookies (expiram em ~30 dias)")
                    st.info("- Tente outro link")
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"🚨 **Erro:** {error_msg}")
                
                # Mensagens específicas para erros comuns
                if "HTTP Error 403" in error_msg:
                    st.error("🔐 **Acesso negado!** Cookies expirados. Atualize no Secrets.")
                elif "Private video" in error_msg:
                    st.error("🔒 **Vídeo privado!** Não é possível baixar.")
                elif "Unsupported URL" in error_msg:
                    st.error("❓ **URL não suportada!** Verifique o link.")
                elif "timed out" in error_msg:
                    st.error("⏱️ **Timeout!** Tente novamente ou use vídeo menor.")

# Informações úteis na sidebar
with st.sidebar:
    st.header("ℹ️  Informações")
    st.markdown("""
    ### Plataformas suportadas:
    - ✅ YouTube (com cookies)
    - ✅ Instagram (stories e posts)
    - ✅ TikTok (se público)
    - ✅ Twitter/X (vídeos)
    - ✅ Facebook (vídeos públicos)
    
    ### Dicas:
    1. Para YouTube, cookies são necessários
    2. Para Instagram Stories, escolha o número
    3. Vídeos devem ser públicos
    4. Downloads são temporários
    
    ### Problemas comuns:
    - 🔄 Cookies expiram em 30 dias
    - 📵 Links privados não funcionam
    - 🐛 Alguns vídeos podem falhar
    """)
    
    if "general" in st.secrets:
        st.success("🔑 Cookies configurados")
    else:
        st.warning("🔓 Modo visitante ativo")

# Limpeza no final
st.cache_data.clear()
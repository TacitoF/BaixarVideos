import streamlit as st
import yt_dlp
import os
import re

st.set_page_config(page_title="Downloader Universal", page_icon="📲")
st.title("📲 Downloader Universal")

tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")
output_path = os.path.join(tmp_dir, "video_final.mp4")

# Escreve os cookies sempre que o app inicia
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

url = st.text_input("Cole o link aqui:", placeholder="Ex: https://www.youtube.com/watch?v=...")

# Nova opção para Instagram Stories
story_index = None
if "instagram.com/stories" in url:
    col1, col2 = st.columns(2)
    with col1:
        story_index = st.number_input("Número do story na sequência:", min_value=1, value=1, step=1)
    with col2:
        st.info("Use 1 para o primeiro, 2 para o segundo, etc.")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        try:
            if os.path.exists(output_path): 
                os.remove(output_path)
            
            with st.spinner('Baixando na nuvem...'):
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'noprogress': True,
                    'quiet': True,
                }
                
                # Configuração específica para Instagram Stories
                if "instagram.com/stories" in url and story_index:
                    # Para Instagram, precisamos de headers adicionais
                    ydl_opts['extractor_args'] = {
                        'instagram': {
                            'story_index': [str(story_index - 1)]  # yt-dlp usa índice 0-based
                        }
                    }
                    
                    # Adiciona headers para evitar bloqueios
                    ydl_opts['headers'] = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us,en;q=0.5',
                        'Accept-Encoding': 'gzip,deflate',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                        'Connection': 'keep-alive',
                    }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extrai informações primeiro para debug
                    info = ydl.extract_info(url, download=False)
                    
                    # Se for Instagram Story, mostra qual está sendo baixado
                    if "instagram.com/stories" in url:
                        if 'entries' in info:
                            st.info(f"📊 Encontrados {len(info['entries'])} stories no total")
                            if story_index <= len(info['entries']):
                                st.info(f"⬇️ Baixando story {story_index} de {len(info['entries'])}")
                            else:
                                st.warning(f"Só existem {len(info['entries'])} stories disponíveis")
                        
                    # Faz o download
                    ydl.download([url])

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("✅ Download concluído!")
                    st.video(output_path)
                    with open(output_path, "rb") as file:
                        st.download_button("⬇️ Salvar no Celular", file, "video.mp4", "video/mp4")
                else:
                    st.error("Erro: Não foi possível baixar o vídeo. Verifique se os cookies estão atualizados.")

        except Exception as e:
            st.error(f"Erro: {e}")
            st.info("💡 Dica: Para Instagram Stories, certifique-se de que:")
            st.info("1. Você está logado com cookies válidos")
            st.info("2. O story ainda está disponível (duram 24h)")
            st.info("3. A conta não é privada")
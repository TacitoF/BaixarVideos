import streamlit as st
import yt_dlp
import os

# Configurações de Interface
st.set_page_config(page_title="Downloader do Tácito", page_icon="📲")
st.title("📲 Downloader Pro")

url = st.text_input("Cole o link aqui:", placeholder="https://...")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        output_name = "video_final.mp4"
        cookie_file = "temp_cookies.txt"

        try:
            with st.spinner('Processando... Isso pode demorar para vídeos longos.'):
                # 1. Gerenciamento de Cookies via Secrets
                if "general" in st.secrets:
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    # Fallback para teste local (certifique-se de que o cookies.txt está na pasta)
                    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

                # 2. Configurações otimizadas para evitar o Erro 403 e "Format not available"
                ydl_opts = {
                    # '18' é o formato MP4 que já vem com áudio e vídeo juntos (360p/640p)
                    # Essencial para rodar em servidores sem FFmpeg como o Streamlit
                    'format': '18/best[ext=mp4]', 
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    # User-agent atualizado para simular Chrome recente no Windows
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                    'quiet': True,
                    'no_warnings': True,
                }

                # Limpeza de resíduos de downloads anteriores
                if os.path.exists(output_name):
                    os.remove(output_name)
                
                # Execução do download usando o motor yt-dlp
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 3. Entrega do arquivo para o navegador
                if os.path.exists(output_name):
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo pronto!")
                        st.video(output_name) # Preview para conferência
                        
                        st.download_button(
                            label="⬇️ Baixar para o Dispositivo",
                            data=file,
                            file_name="video_baixado.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Erro: O formato solicitado não está disponível ou o servidor bloqueou o acesso.")

        except Exception as e:
            st.error(f"Erro: {e}")
            if "403" in str(e):
                st.info("💡 Dica: O YouTube bloqueou o IP. Tente atualizar seu conteúdo de cookies nos Secrets.")

st.markdown("---")
st.caption("Personal Downloader - v1.2")
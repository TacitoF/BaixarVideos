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
            with st.spinner('Processando... Isso pode demorar um pouco.'):
                # 1. Gerenciamento de Cookies via Secrets
                if "general" in st.secrets:
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

                # 2. Configurações para burlar bloqueios e gerenciar formatos
                ydl_opts = {
                    # Tenta baixar o melhor MP4 pronto para evitar erro de formato no servidor
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    # Disfarce de Navegador para o YouTube
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                    'quiet': True,
                    'no_warnings': True,
                }

                if os.path.exists(output_name):
                    os.remove(output_name)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 3. Entrega do arquivo para o seu celular
                if os.path.exists(output_name):
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo pronto!")
                        st.video(output_name) # Preview
                        st.download_button(
                            label="⬇️ Baixar para o Celular",
                            data=file,
                            file_name="video_baixado.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Erro: O formato solicitado não está disponível. Tente outro link.")

        except Exception as e:
            st.error(f"Erro: {e}")
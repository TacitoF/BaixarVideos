import streamlit as st
import yt_dlp
import os

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
            with st.spinner('Processando...'):
                # 1. Gerenciamento de Cookies
                if "general" in st.secrets:
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

                # 2. Configurações para Servidores sem FFmpeg (O pulo do gato)
                ydl_opts = {
                    # Busca o melhor MP4 único que já vem com áudio e vídeo juntos
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    # Disfarce de Navegador Humano
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                }

                if os.path.exists(output_name):
                    os.remove(output_name)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 3. Verificação e Entrega
                if os.path.exists(output_name) and os.path.getsize(output_name) > 0:
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo pronto!")
                        st.video(output_name)
                        st.download_button(
                            label="⬇️ Baixar para o Celular",
                            data=file,
                            file_name="video_tácito.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Erro: O arquivo gerado está vazio. Tente outro link ou atualize os cookies.")

        except Exception as e:
            st.error(f"Erro: {e}")
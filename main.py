import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Downloader do Tácito", page_icon="📲")
st.title("Downloader Pro")

url = st.text_input("Cole o link aqui:")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        output_name = "video_temp.mp4"
        cookie_file = "temp_cookies.txt"

        try:
            with st.spinner('Processando...'):
                # Lógica de Cookies Segura
                if "general" in st.secrets:
                    # Se estiver no Streamlit Cloud, cria o arquivo a partir dos Secrets
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    # Se estiver no seu PC, usa o seu arquivo local
                    cookie_file = "cookies.txt"

                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                }

                if os.path.exists(output_name):
                    os.remove(output_name)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                with open(output_name, "rb") as file:
                    st.success("Vídeo pronto!")
                    st.video(output_name) # Preview
                    st.download_button(
                        label="Baixar para o Dispositivo",
                        data=file,
                        file_name="video_tácito.mp4",
                        mime="video/mp4"
                    )
        except Exception as e:
            st.error(f"Erro: {e}")
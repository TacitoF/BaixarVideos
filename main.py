import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Downloader Pro", page_icon="📲")
st.title("📲 Downloader Universal")

# 1. Carregar os Cookies do Secret do Streamlit
cookie_file = "temp_cookies.txt"
if "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])
else:
    cookie_file = None

url = st.text_input("Cole o link do YouTube ou Instagram:")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        output_name = "video_downloaded.mp4"
        try:
            with st.spinner('Baixando...'):
                ydl_opts = {
                    # No Streamlit Cloud sem Docker, 'best' é mais seguro para evitar erros de merge
                    'format': 'best[ext=mp4]/best', 
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'quiet': True,
                }

                if os.path.exists(output_name):
                    os.remove(output_name)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_name):
                    with open(output_name, "rb") as f:
                        st.video(f)
                        st.download_button("Baixar para o Celular", f, "video.mp4")
        except Exception as e:
            st.error(f"Erro: {e}")
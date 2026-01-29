import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Downloader Universal", page_icon="📲")
st.title("📲 Downloader Universal")

# 1. Carregar Cookies do Secrets (Streamlit Cloud format)
cookie_file = "temp_cookies.txt"
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

url = st.text_input("Cole o link do YouTube ou Instagram:")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        output_name = "video_final.mp4"
        try:
            with st.spinner('Baixando e processando na nuvem...'):
                ydl_opts = {
                    # Busca o melhor MP4 já pronto para evitar processamento pesado
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'socket_timeout': 60,
                }

                if os.path.exists(output_name):
                    os.remove(output_name)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_name) and os.path.getsize(output_name) > 0:
                    st.success("✅ Vídeo pronto!")
                    st.video(output_name)
                    with open(output_name, "rb") as f:
                        st.download_button("Salvar no Celular", f, "video.mp4")
                else:
                    st.error("Erro: O arquivo não foi gerado. Verifique se o packages.txt com ffmpeg está no GitHub.")
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
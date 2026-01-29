import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Downloader Universal", page_icon="📲")
st.title("📲 Downloader Universal")

# 1. Carregar Cookies do Secrets
cookie_file = os.path.join(os.getcwd(), "temp_cookies.txt")
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

url = st.text_input("Cole o link aqui:")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link.")
    else:
        output_name = "video_final.mp4"
        try:
            with st.spinner('Baixando... Se o packages.txt estiver ok, será rápido!'):
                ydl_opts = {
                    # '18' é o formato MP4 360p padrão que NÃO precisa de FFmpeg
                    # 'best' tentará a melhor qualidade se o FFmpeg for detectado
                    'format': '18/best[ext=mp4]/best', 
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }

                if os.path.exists(output_name): os.remove(output_name)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_name) and os.path.getsize(output_name) > 0:
                    st.success("✅ Download concluído!")
                    st.video(output_name)
                    with open(output_name, "rb") as f:
                        st.download_button("Salvar no Celular", f, "video.mp4")
                else:
                    st.error("O arquivo saiu vazio. Aguarde 1 minuto para o Streamlit instalar o ffmpeg via packages.txt.")
        except Exception as e:
            st.error(f"Erro: {e}")
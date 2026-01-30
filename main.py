import streamlit as st
import yt_dlp
import os

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

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        try:
            if os.path.exists(output_path): os.remove(output_path)
            
            with st.spinner('Baixando na nuvem...'):
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    # Reduz a carga no servidor para evitar bloqueios
                    'noprogress': True,
                    'quiet': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("✅ Download concluído!")
                    st.video(output_path)
                    with open(output_path, "rb") as file:
                        st.download_button("⬇️ Salvar no Celular", file, "video.mp4", "video/mp4")
                else:
                    st.error("Erro 403: O YouTube bloqueou estes cookies. Por favor, gere novos cookies e atualize o Secrets.")

        except Exception as e:
            st.error(f"Erro: {e}")
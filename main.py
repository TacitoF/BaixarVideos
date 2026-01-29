import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Downloader Universal", page_icon="📲")
st.title("📲 Downloader Universal")

# 1. Caminhos e Cookies na pasta temporária do servidor
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")
output_path = os.path.join(tmp_dir, "video_final.mp4")

if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

url = st.text_input("Cole o link aqui:", placeholder="YouTube ou Instagram")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link.")
    else:
        try:
            if os.path.exists(output_path): os.remove(output_path)
            
            with st.spinner('Baixando na nuvem...'):
                ydl_opts = {
                    # '18' é o MP4 360p (funciona sem erro 403 na maioria dos casos)
                    # 'best' tentará a melhor qualidade se a rede permitir
                    'format': '18/best[ext=mp4]/best',
                    'outtmpl': output_path,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'rm_cachedir': True, # Limpa o cache para evitar o erro de arquivo vazio
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'socket_timeout': 150,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("✅ Download concluído!")
                    st.video(output_path)
                    with open(output_path, "rb") as file:
                        st.download_button("⬇️ Salvar no Celular", file, "video.mp4", "video/mp4")
                else:
                    st.error("O YouTube cortou a conexão. Aguarde 30 segundos e tente novamente.")

        except Exception as e:
            st.error(f"Erro detectado: {e}")
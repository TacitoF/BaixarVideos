import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Downloader Universal", page_icon="📲")
st.title("📲 Downloader Universal")

# 1. Gerenciamento Robusto de Cookies
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "cookies_master.txt")

def setup_cookies():
    if "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
        # Sobrescreve sempre para garantir que o cookie mais novo seja usado
        with open(cookie_file, "w", encoding="utf-8") as f:
            f.write(st.secrets["general"]["COOKIES_DATA"])
        return cookie_file
    return None

url = st.text_input("Cole o link aqui:", placeholder="YouTube ou Instagram")

if st.button("Preparar Download"):
    current_cookies = setup_cookies()
    if not url:
        st.warning("Insira um link primeiro.")
    elif not current_cookies:
        st.error("Erro: COOKIES_DATA não encontrado nos Secrets do Streamlit.")
    else:
        output_path = os.path.join(tmp_dir, "video_final.mp4")
        try:
            if os.path.exists(output_path): os.remove(output_path)
            
            with st.spinner('Furando o bloqueio e baixando...'):
                ydl_opts = {
                    # Força MP4 para evitar erros de merge no servidor
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_path,
                    'cookiefile': current_cookies,
                    'nocheckcertificate': True,
                    # User-agent atualizado para parecer um navegador real
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                    'socket_timeout': 120,
                    'quiet': True,
                    'no_warnings': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("✅ Download realizado com sucesso!")
                    st.video(output_path)
                    with open(output_path, "rb") as file:
                        st.download_button("⬇️ Salvar no Celular", file, "video.mp4", "video/mp4")
                else:
                    st.error("Erro: O YouTube ainda está bloqueando. Tente atualizar seus cookies no navegador e colar o novo valor nos Secrets.")

        except Exception as e:
            st.error(f"Erro detectado: {e}")
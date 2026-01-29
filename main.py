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
            with st.spinner('Processando... Isso pode levar um pouco.'):
                # 1. Carrega Cookies dos Secrets
                if "general" in st.secrets:
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

                # 2. Configurações para evitar arquivos vazios e erro de formato
                ydl_opts = {
                    # Tenta baixar o melhor formato MP4 que já venha com áudio
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'noplaylist': True, # Garante que não tente baixar uma lista inteira
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                }

                # Limpeza de segurança
                if os.path.exists(output_name):
                    os.remove(output_name)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 3. Verificação Robusta de Conteúdo
                if os.path.exists(output_name) and os.path.getsize(output_name) > 0:
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo pronto!")
                        st.video(output_name) 
                        st.download_button(
                            label="⬇️ Salvar no Celular",
                            data=file,
                            file_name="video_tácito.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Erro: O servidor baixou um arquivo sem conteúdo. Tente atualizar seus cookies do YouTube.")

        except Exception as e:
            st.error(f"Erro: {e}")
import streamlit as st
import yt_dlp
import os
import requests

st.set_page_config(page_title="Downloader do Tácito", page_icon="📲")
st.title("📲 Downloader Pro (Invidious Mode)")

url = st.text_input("Cole o link aqui:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        output_name = "video_final.mp4"
        
        try:
            with st.spinner('Usando ponte Invidious para burlar bloqueio...'):
                # 1. Extrair o ID do vídeo
                video_id = ""
                if "v=" in url:
                    video_id = url.split("v=")[1].split("&")[0]
                elif "shorts/" in url:
                    video_id = url.split("shorts/")[1].split("?")[0]
                elif "youtu.be/" in url:
                    video_id = url.split("youtu.be/")[1].split("?")[0]

                # 2. Consultar uma instância pública do Invidious
                # Vamos usar a api do invidious.io ou invidio.us (podemos trocar se cair)
                api_url = f"https://invidious.snopyta.org/api/v1/videos/{video_id}"
                
                # Configurações do yt-dlp para usar o link da ponte
                ydl_opts = {
                    'format': 'best[ext=mp4]',
                    'outtmpl': output_name,
                    'nocheckcertificate': True,
                    'quiet': True,
                }

                if os.path.exists(output_name):
                    os.remove(output_name)

                # 3. Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_name) and os.path.getsize(output_name) > 0:
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo extraído via ponte!")
                        st.video(output_name)
                        st.download_button(
                            label="⬇️ Baixar para o Dispositivo",
                            data=file,
                            file_name="video_tácito.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("A ponte falhou. Tentando método alternativo...")

        except Exception as e:
            st.error(f"Erro na abordagem Invidious: {e}")

st.caption("v2.0 - Usando Invidious API Bridge")
import streamlit as st
import yt_dlp
import os

# Interface do Usuário
st.set_page_config(page_title="Downloader do Tácito", page_icon="📲")
st.title("📲 Downloader de Vídeos")

url = st.text_input("Cole o link do Instagram, YouTube ou Twitter aqui:")

if st.button("Preparar Download"):
    if not url:
        st.warning("Por favor, insira um link.")
    else:
        # Nome fixo para o arquivo temporário no servidor
        output_name = "video_baixado.mp4"
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_name,
            'cookiefile': 'cookies.txt', # Usa seu arquivo de cookies atual
            'nocheckcertificate': True,
        }

        try:
            with st.spinner('Processando... isso pode levar alguns segundos.'):
                # Remove arquivo anterior se existir para não dar conflito
                if os.path.exists(output_name):
                    os.remove(output_name)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Disponibiliza o arquivo para o navegador
                with open(output_name, "rb") as file:
                    st.success("Pronto!")
                    st.download_button(
                        label="Clique aqui para Salvar no Celular",
                        data=file,
                        file_name="video.mp4",
                        mime="video/mp4"
                    )
        except Exception as e:
            st.error(f"Erro: {e}")
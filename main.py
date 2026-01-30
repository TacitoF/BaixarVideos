import streamlit as st
import yt_dlp
import tempfile
import os

st.set_page_config(page_title="Downloader", layout="centered")
st.title("📥 Download Simples")

# Input
url = st.text_input("", placeholder="🔗 Cole link do vídeo aqui...")

# Botão único
if st.button("⬇️  BAIXAR", type="primary", use_container_width=True) and url:
    with st.spinner("Processando..."):
        try:
            # Config simples
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(tempfile.gettempdir(), 'video.mp4'),
                'quiet': True,
            }
            
            # Baixa
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Encontra arquivo
            video_file = os.path.join(tempfile.gettempdir(), 'video.mp4')
            
            if os.path.exists(video_file):
                with open(video_file, "rb") as f:
                    video_bytes = f.read()
                
                st.video(video_bytes)
                st.download_button("💾 Salvar", video_bytes, "video.mp4", "video/mp4")
                
                # Limpa
                os.remove(video_file)
            else:
                st.error("❌ Erro ao baixar")
                
        except Exception as e:
            st.error(f"Erro: {e}")
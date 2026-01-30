import streamlit as st
import yt_dlp
import os
import base64

# Configuração da página para design moderno
st.set_page_config(
    page_title="Downloader Pro", 
    page_icon="📥", 
    layout="centered"
)

# --- CSS PERSONALIZADO (Dark Mode & Mobile Friendly) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #4B4B4B;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3d3f4b;
        border-color: #00ff88;
    }
    .stTextInput>div>div>input {
        background-color: #1a1c24;
        color: white;
        border-radius: 10px;
    }
    .status-box {
        padding: 20px;
        border-radius: 15px;
        background-color: #1a1c24;
        border: 1px solid #2e313d;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📥 Downloader Pro")
st.markdown("Download inteligente de YouTube e Instagram (incluindo Stories).")

tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")

# Escreve os novos cookies (Instagram Atualizado)
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

url = st.text_input("Cole o link aqui:", placeholder="Link do Vídeo ou Perfil (Stories)")

# Opção para escolher o número do Story (Resolve seu problema do 4º story)
story_index = st.number_input("Se for Story, qual a posição? (Ex: 1 para o primeiro, 4 para o quarto)", min_value=1, value=1)

if st.button("Preparar Download"):
    if not url:
        st.warning("Insira um link primeiro.")
    else:
        output_path = os.path.join(tmp_dir, f"video_index_{story_index}.mp4")
        try:
            if os.path.exists(output_path): os.remove(output_path)
            
            with st.spinner('Acessando mídia na nuvem...'):
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
                    'quiet': True,
                    # Lógica para pegar um item específico de uma playlist/Stories
                    'playlist_items': str(story_index),
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success(f"✅ Mídia {story_index} pronta!")
                    st.video(output_path)
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Baixar para Galeria", 
                            data=file, 
                            file_name=f"media_{story_index}.mp4", 
                            mime="video/mp4"
                        )
                else:
                    st.error("Erro: Não foi possível capturar este story específico. Verifique se ele ainda está no ar.")

        except Exception as e:
            st.error(f"Erro: {e}")
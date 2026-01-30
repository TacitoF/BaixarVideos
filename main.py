import streamlit as st
import yt_dlp
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Downloader Pro", page_icon="⚫", layout="centered")

# --- CSS DARK MINIMALISTA (CORRIGIDO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; font-family: 'Helvetica Neue', Arial, sans-serif; }
    h1, p, label { color: #e0e0e0 !important; }
    
    .stTextInput > div > div > input {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    .stTextInput > div > div > input::placeholder { color: #888888 !important; }

    .stButton > button {
        width: 100%;
        background-color: #e0e0e0 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3.5rem !important;
        transition: 0.3s;
        border: none !important;
    }
    .stButton > button p { color: #000000 !important; } /* Texto do botão sempre preto */
    .stButton > button:hover { background-color: #ffffff !important; transform: scale(1.01); }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚫ Downloader Pro")
st.markdown("Download de Reels e Posts (Mídias Públicas). \n\n⚠️ *Stories e YouTube não são suportados nesta versão sem login.*")

# Limpeza automática ao mudar o link
def reset():
    if 'video' in st.session_state: del st.session_state['video']

url = st.text_input("", placeholder="Cole o link do Instagram aqui...", on_change=reset)

if url:
    if "stories" in url:
        st.warning("📥 **Atenção:** Stories exigem login privado. Esta versão 'Sem Cookies' não consegue acessá-los para proteger sua conta.")
    elif "youtube.com" in url or "youtu.be" in url:
        st.error("🚫 O YouTube não é suportado nesta plataforma.")
    else:
        if st.button("BAIXAR AGORA"):
            output_path = f"/tmp/video_{int(time.time())}.mp4"
            status = st.empty()
            
            try:
                status.markdown("🔄 **Conectando...**")
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                    'nocheckcertificate': True,
                    'quiet': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.session_state['video'] = output_path
                    status.success("✅ **Sucesso!**")
                    st.video(output_path)
                    with open(output_path, "rb") as f:
                        st.download_button("SALVAR NA GALERIA", f, "video.mp4", "video/mp4")
                else:
                    status.error("❌ O Instagram bloqueou o servidor. Sem cookies, o download em nuvem é instável.")
            except Exception as e:
                status.error(f"Erro: O Instagram exige autenticação para este link.")
import streamlit as st
import yt_dlp
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Downloader Pro",
    page_icon="⚫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS MODERNO E CORRIGIDO (CONTRASTE ALTO) ---
st.markdown("""
    <style>
    /* 1. Fundo Geral */
    .stApp {
        background-color: #0e0e0e;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 2. Textos Gerais */
    h1, h2, h3, p, label, .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    /* 3. Inputs de Texto (Correção do Placeholder) */
    .stTextInput > div > div > input {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    /* Cor do texto de dica (placeholder) */
    .stTextInput > div > div > input::placeholder {
        color: #888888 !important; /* Cinza claro visível */
        opacity: 1;
    }
    .stTextInput > div > div > input:focus {
        border-color: #555555 !important;
    }

    /* 4. Input Numérico (Story Selector) */
    .stNumberInput > div > div > input {
        background-color: #1c1c1c !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 12px;
    }
    button[kind="secondary"] {
        background-color: #1c1c1c !important;
        border: 1px solid #333333 !important;
        color: #e0e0e0 !important;
    }

    /* 5. Botão Principal (CORREÇÃO DE TEXTO APAGADO) */
    .stButton > button {
        width: 100%;
        background-color: #e0e0e0 !important; /* Fundo Claro */
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    /* Força a cor do texto DENTRO do botão para PRETO */
    .stButton > button, 
    .stButton > button p, 
    .stButton > button div {
        color: #000000 !important; 
    }

    .stButton > button:hover {
        background-color: #ffffff !important;
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }
    .stButton > button:active {
        background-color: #cccccc !important;
    }

    /* 6. Esconder elementos padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("⚫ Downloader Pro")
st.markdown("Cole seu link abaixo. A interface se adapta automaticamente.", help="Suporta Instagram e YouTube.")

# --- GERENCIAMENTO DE COOKIES ---
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

# --- LÓGICA DE INTERFACE ---
with st.container():
    # Placeholder agora configurado via CSS
    url = st.text_input("Link da Mídia", placeholder="Cole o link do Instagram ou YouTube aqui...", label_visibility="collapsed")

    is_story = False
    story_index = 1
    
    if url and "instagram.com/stories/" in url:
        is_story = True
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("📸 **Link de Story detectado!**")
        with col2:
            story_index = st.number_input("Qual baixar?", min_value=1, value=1, step=1)

    # --- BOTÃO ---
    if st.button("BAIXAR MÍDIA"):
        if not url:
            st.toast("⚠️ Por favor, cole um link primeiro.")
        else:
            output_path = os.path.join(tmp_dir, f"media_final_{int(time.time())}.mp4")
            if os.path.exists(output_path): os.remove(output_path)
            
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            try:
                status_text.markdown("🔄 **Iniciando conexão segura...**")
                progress_bar.progress(20)
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': output_path,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'quiet': True,
                    'no_warnings': True,
                    # User Agent Mobile do iPhone (Melhor para Instagram)
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                }

                if is_story:
                    ydl_opts['playlist_items'] = str(story_index)
                    status_text.markdown(f"🔄 **Baixando Story nº {story_index}...**")
                else:
                    status_text.markdown("🔄 **Processando vídeo...**")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                progress_bar.progress(80)

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    progress_bar.progress(100)
                    status_text.success("✅ **Download Concluído!**")
                    time.sleep(0.5)
                    progress_bar.empty()
                    
                    st.video(output_path)
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="SALVAR NA GALERIA",
                            data=f,
                            file_name=f"story_{story_index}.mp4" if is_story else "video_download.mp4",
                            mime="video/mp4"
                        )
                else:
                    status_text.error("❌ Erro: Arquivo vazio. Verifique se o story ainda está disponível.")
                    progress_bar.empty()

            except Exception as e:
                status_text.error(f"Erro: {e}")
                progress_bar.empty()
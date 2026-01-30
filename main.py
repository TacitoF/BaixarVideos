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

# --- CSS MODERNO E MINIMALISTA (VISUAL DARK) ---
st.markdown("""
    <style>
    /* Fundo Geral e Fonte */
    .stApp {
        background-color: #0e0e0e; /* Preto Quase Absoluto */
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Títulos e Textos */
    h1, h2, h3, p, label {
        color: #e0e0e0 !important;
    }
    
    /* Inputs de Texto (Visual Card) */
    .stTextInput > div > div > input {
        background-color: #1c1c1c;
        color: #ffffff;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 12px;
        font-size: 16px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #555555;
        box-shadow: none;
    }

    /* Input Numérico (Story Selector) */
    .stNumberInput > div > div > input {
        background-color: #1c1c1c;
        color: white;
        border: 1px solid #333333;
        border-radius: 12px;
    }
    /* Botões de + e - do number input */
    button[kind="secondary"] {
        background-color: #1c1c1c;
        border: 1px solid #333333;
        color: #e0e0e0;
    }

    /* Botão Principal (Download) */
    .stButton > button {
        width: 100%;
        background-color: #e0e0e0; /* Contraste alto: Botão claro em fundo escuro */
        color: #000000;
        border: none;
        border-radius: 12px;
        padding: 0.75rem;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background-color: #ffffff;
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }
    .stButton > button:active {
        background-color: #cccccc;
    }

    /* Mensagens de Sucesso/Erro */
    .stAlert {
        background-color: #1c1c1c;
        color: #e0e0e0;
        border: 1px solid #333333;
        border-radius: 10px;
    }
    
    /* Remove decorações padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("⚫ Downloader Pro")
st.markdown("Cole seu link abaixo. A interface se adapta automaticamente.", help="Suporta Instagram (Reels, Stories, Posts) e YouTube.")

# --- GERENCIAMENTO DE COOKIES (BACKEND) ---
tmp_dir = "/tmp"
cookie_file = os.path.join(tmp_dir, "master_cookies.txt")
if "general" in st.secrets:
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])

# --- LÓGICA DE INTERFACE DINÂMICA ---
# Container principal para centralizar visualmente
with st.container():
    url = st.text_input("Link da Mídia", placeholder="Cole o link do Instagram ou YouTube aqui...", label_visibility="collapsed")

    # DETECÇÃO AUTOMÁTICA DE STORIES
    is_story = False
    story_index = 1
    
    # Se o usuário colou algo e tem 'stories' no link
    if url and "instagram.com/stories/" in url:
        is_story = True
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("Detectamos um link de Story!")
        with col2:
            # Melhoria de Usabilidade: Seletor Numérico Claro
            story_index = st.number_input(
                "Qual baixar?", 
                min_value=1, 
                value=1, 
                step=1,
                help="1 = O story mais recente (ou o exato do link). Aumente para pegar os próximos."
            )

    # --- BOTÃO DE AÇÃO ---
    if st.button("BAIXAR MÍDIA"):
        if not url:
            st.toast("⚠️ Por favor, cole um link primeiro.")
        else:
            output_path = os.path.join(tmp_dir, f"media_final_{int(time.time())}.mp4")
            
            # Limpeza prévia
            if os.path.exists(output_path): os.remove(output_path)
            
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            try:
                status_text.markdown("🔄 **Conectando aos servidores...**")
                progress_bar.progress(20)
                
                ydl_opts = {
                    'format': 'best', # Tenta a melhor qualidade
                    'outtmpl': output_path,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'quiet': True,
                    'no_warnings': True,
                    # User Agent Mobile para evitar bloqueios do Instagram
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                }

                # Lógica Específica para Stories
                if is_story:
                    # 'playlist_items' define qual item da lista baixar
                    ydl_opts['playlist_items'] = str(story_index)
                    status_text.markdown(f"🔄 **Baixando Story nº {story_index}...**")
                else:
                    status_text.markdown("🔄 **Processando vídeo...**")

                # Execução do Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                progress_bar.progress(80)

                # Verificação e Entrega
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    progress_bar.progress(100)
                    status_text.success("✅ **Download Concluído!**")
                    time.sleep(0.5)
                    progress_bar.empty()
                    
                    # Exibe o vídeo
                    st.video(output_path)
                    
                    # Botão de Download do Arquivo
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="SALVAR NA GALERIA",
                            data=f,
                            file_name=f"story_{story_index}.mp4" if is_story else "video_download.mp4",
                            mime="video/mp4"
                        )
                else:
                    status_text.error("❌ Erro: Arquivo vazio. Verifique se o story ainda está disponível (24h).")
                    progress_bar.empty()

            except Exception as e:
                status_text.error(f"Erro no processamento: {e}")
                progress_bar.empty()
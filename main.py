import streamlit as st
import yt_dlp
import os

# Interface e Configurações
st.set_page_config(page_title="Downloader do Tácito", page_icon="📲")
st.title("📲 Downloader Pro")

url = st.text_input("Cole o link aqui:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Preparar Download"):
    if not url:
        st.warning("Por favor, insira um link primeiro.")
    else:
        output_name = "video_temp.mp4"
        cookie_file = "temp_cookies.txt"

        try:
            with st.spinner('Processando vídeo... Isso pode levar alguns segundos.'):
                
                # 1. Gerenciamento de Cookies (Segurança para o Streamlit Cloud)
                if "general" in st.secrets:
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    # Se rodar localmente, tenta usar o seu cookies.txt
                    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

                # 2. Configurações para Burlar o Erro 403 (Disguise)
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    # Força o servidor a parecer um navegador Chrome real
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                    'quiet': True,
                    'no_warnings': True,
                    # Tenta baixar o conteúdo sem fragmentação excessiva
                    'http_chunk_size': 10485760, # 10MB
                }

                # Limpa restos de downloads anteriores
                if os.path.exists(output_name):
                    os.remove(output_name)
                
                # 3. Download via yt-dlp
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 4. Exibição e Botão de Download para o Dispositivo
                if os.path.exists(output_name):
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo processado com sucesso!")
                        st.video(output_name) # Preview
                        
                        st.download_button(
                            label="⬇️ Clique aqui para Salvar no Dispositivo",
                            data=file,
                            file_name="video_baixado.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Erro interno: Arquivo não gerado.")

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
            st.info("💡 Dica: Se o erro for 403, atualize seus cookies do YouTube no painel do Streamlit.")

st.markdown("---")
st.caption("Criado por Tácito - Uso Pessoal")
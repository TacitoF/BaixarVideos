import streamlit as st
import yt_dlp
import os

# Configuração da página
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
                
                # 1. Gerenciamento de Cookies (Local vs Cloud)
                if "general" in st.secrets:
                    with open(cookie_file, "w") as f:
                        f.write(st.secrets["general"]["COOKIES_DATA"])
                else:
                    # Verifica se o arquivo físico existe no seu PC
                    if os.path.exists("cookies.txt"):
                        cookie_file = "cookies.txt"
                    else:
                        cookie_file = None # Tenta baixar sem cookies se não achar

                # 2. Configurações Avançadas para evitar Erro 403
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': output_name,
                    'cookiefile': cookie_file,
                    'nocheckcertificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.google.com/',
                    'quiet': True,
                    'no_warnings': True,
                    # Adiciona retentativas automáticas em caso de erro de rede
                    'retries': 5,
                    'fragment_retries': 5,
                }

                # Limpa arquivos temporários de tentativas anteriores
                if os.path.exists(output_name):
                    os.remove(output_name)
                
                # 3. Execução do Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 4. Interface de entrega do arquivo
                if os.path.exists(output_name):
                    with open(output_name, "rb") as file:
                        st.success("✅ Vídeo processado com sucesso!")
                        st.video(output_name) # Exibe o player para conferência
                        
                        st.download_button(
                            label="⬇️ Clique aqui para Baixar",
                            data=file,
                            file_name="video_baixado.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("O arquivo não foi gerado. Tente outro link.")

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
            st.info("Dica: Se o erro for 403, tente atualizar seu arquivo cookies.txt no painel do Streamlit.")

# Rodapé simples
st.markdown("---")
st.caption("Criado para uso pessoal. Lembre-se de respeitar os direitos autorais.")
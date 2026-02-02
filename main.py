import streamlit as st
import yt_dlp
import os
import time
import re
import requests
from datetime import datetime
from urllib.parse import urlparse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="NexusDL",
    page_icon="⚫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- FUNÇÃO PARA VERIFICAR SE É LINK DO YOUTUBE ---
def is_youtube_url(url):
    """Verifica se a URL é do YouTube"""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        return any(youtube_domain in domain for youtube_domain in ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com'])
    except:
        return False

# --- FUNÇÃO PARA DOWNLOAD DO YOUTUBE COM PROGRESSO ---
def download_youtube_with_progress(url, output_path, res, progress_bar, status_placeholder):
    """
    Processa via API externa e, ao finalizar (1000), baixa o arquivo
    fisicamente para o output_path local.
    """
    try:
        api_key = st.secrets["general"]["YOUTUBE_API_KEY"]
    except KeyError:
        error_msg = "Erro: Chave 'YOUTUBE_API_KEY' não encontrada nos Secrets."
        # Enviar para o Discord e retornar o erro
        raise Exception(error_msg)

    init_url = f"https://p.savenow.to/ajax/download.php?format={res}&url={url}&apikey={api_key}"

    try:
        response = requests.get(init_url)
        response.raise_for_status()
        data = response.json()
        job_id = data.get("id")

        if not job_id:
            error_msg = "API do YouTube não retornou ID do job"
            raise Exception(error_msg)

        while True:
            time.sleep(1.5)
            progress_endpoint = f"https://p.savenow.to/ajax/progress?id={job_id}"

            p_resp = requests.get(progress_endpoint)
            p_resp.raise_for_status()
            p_data = p_resp.json()

            curr = int(p_data.get("progress", 0))
            norm = min(max(curr / 1000, 0.0), 1.0)
            if progress_bar:
                progress_bar.progress(norm)

            if curr == 1000:
                final_url = p_data.get("download_url")
                
                if not final_url:
                    error_msg = "API do YouTube não retornou URL de download"
                    raise Exception(error_msg)

                if status_placeholder:
                    status_placeholder.markdown("⬇️ Baixando vídeo para o servidor...")

                with requests.get(final_url, stream=True) as r:
                    r.raise_for_status()
                    with open(output_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                if status_placeholder:
                    status_placeholder.empty()
                if progress_bar:
                    progress_bar.empty()

                return output_path

            if p_data.get("status") == "error":
                error_msg = f"API do YouTube retornou erro: {p_data.get('message', 'Erro desconhecido')}"
                raise Exception(error_msg)

    except requests.exceptions.RequestException as e:
        error_msg = f"Erro de conexão com API do YouTube: {str(e)}"
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erro na API SaveNow: {str(e)}"
        raise Exception(error_msg)

# --- FUNÇÃO LOG DISCORD (ATUALIZADA COM FORMATAÇÃO MELHOR) ---
def send_discord_log(error_msg, video_url):
    clean_msg = str(error_msg)[:800]
    
    # Determinar se é feedback baseado no conteúdo
    is_feedback = "FEEDBACK" in str(video_url) or "REPORT" in str(video_url) or "feedback" in str(error_msg).lower()
    
    # Escolher o webhook correto baseado no tipo
    if is_feedback:
        webhook_key = "DISCORD_WEBHOOK_FEEDBACK"
        color = 3447003  # Azul para feedback
        username = "NexusDL Feedback"
        
        # Processar mensagem de feedback
        if "**Contato:**" in clean_msg and "**Relato:**" in clean_msg:
            # Extrair contato e relato do feedback
            parts = clean_msg.split("**Contato:**")[1].split("**Relato:**")
            contato = parts[0].strip() if len(parts) > 0 else "Não informado"
            relato = parts[1].strip() if len(parts) > 1 else clean_msg
            
            if contato == " " or contato == "":
                contato = "Não informado"
            
            title = "📢 NOVO FEEDBACK"
            fields = [
                {"name": "📧 Contato", "value": f"```{contato}```", "inline": False},
                {"name": "📝 Relato", "value": f"```{relato[:1000]}```", "inline": False},
                {"name": "🕐 Horário", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": True}
            ]
        else:
            title = "📢 NOVO FEEDBACK"
            fields = [
                {"name": "📝 Mensagem", "value": f"```{clean_msg}```", "inline": False},
                {"name": "🕐 Horário", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": True}
            ]
    else:
        webhook_key = "DISCORD_WEBHOOK_ERROR"
        color = 15548997  # Vermelho para erro
        username = "NexusDL Monitor"
        
        # Limpar a mensagem de erro
        error_display = clean_msg
        # Remover códigos ANSI e formatação estranha
        error_display = re.sub(r'❌\[0;31m', '', error_display)
        error_display = re.sub(r'❌\[0m', '', error_display)
        error_display = re.sub(r'\[0;31m', '', error_display)
        error_display = re.sub(r'\[0m', '', error_display)
        error_display = re.sub(r'ERROR:', 'ERRO:', error_display)
        
        # Formatar URL para exibição
        url_display = str(video_url)[:200]
        if len(str(video_url)) > 200:
            url_display = url_display + "..."
        
        title = "🚨 FALHA NO DOWNLOAD"
        fields = [
            {"name": "🔗 URL", "value": f"```{url_display}```", "inline": False},
            {"name": "📋 Detalhes do Erro", "value": f"```{error_display}```", "inline": False},
            {"name": "🕐 Horário", "value": datetime.now().strftime("%d/%m/Y %H:%M:%S"), "inline": True}
        ]
    
    # Verificar se o segredo existe
    if "general" in st.secrets and webhook_key in st.secrets["general"]:
        webhook_url = st.secrets["general"][webhook_key]
    else:
        return  # Se não tiver webhook configurado, não faz nada

    data = {
        "username": username,
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/564/564619.png",
        "embeds": [{
            "title": title,
            "color": color,
            "thumbnail": {
                "url": "https://cdn-icons-png.flaticon.com/512/564/564619.png"
            },
            "fields": fields,
            "footer": {
                "text": "NexusDL Monitor System",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/564/564619.png"
            },
            "timestamp": datetime.now().isoformat()
        }]
    }
    try:
        response = requests.post(webhook_url, json=data, timeout=3)
        if response.status_code != 204:
            print(f"Erro ao enviar para Discord: {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar para Discord: {e}")
        pass  # Falha silenciosa no log

# --- FUNÇÃO PARA LIMPAR MENSAGENS DE ERRO ---
def clean_error_message(error_text, url=""):
    text = str(error_text)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # Limpar formatações específicas
    text = re.sub(r'❌\[0;31m', '', text)
    text = re.sub(r'❌\[0m', '', text)
    text = re.sub(r'\[0;31m', '', text)
    text = re.sub(r'\[0m', '', text)
    
    # Verificação específica para erros da API do YouTube
    if "YouTube" in text or "SaveNow" in text or "API" in text:
        return "🚫 Erro na API do YouTube. Tente novamente mais tarde."
    
    if "not a valid URL" in text or "Unsupported URL" in text:
        return "⚠️ Link inválido. Certifique-se de copiar a URL completa."
        
    if "HTTP Error 400" in text:
        return "⚠️ Conexão recusada (Erro 400). O Instagram bloqueou a conexão anônima ou os cookies expiraram."
    if "Sign in to confirm" in text or "login" in text.lower():
        return "🔒 Conteúdo exige login (Cookies necessários)."
    if "Video unavailable" in text:
        return "🚫 Vídeo não encontrado ou excluído."
    if "Private video" in text:
        return "🔒 Este vídeo é privado."
        
    return f"Erro técnico: {text[:200]}..."

# --- CARREGAR CSS E JS ---
def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS padrão como fallback
        st.markdown("""
        <style>
        .stApp { background: #0a0a0a; }
        </style>
        """, unsafe_allow_html=True)

def load_js():
    try:
        with open("script.js", "r", encoding="utf-8") as f:
            js = f.read()
            st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)
    except FileNotFoundError:
        # JavaScript padrão como fallback
        st.markdown("""
        <script>
        console.log("JS não carregado");
        </script>
        """, unsafe_allow_html=True)

# --- CARREGAR ESTILOS E SCRIPTS ---
load_css()
load_js()

# --- INÍCIO DO APP ---
st.title("NexusDL")
st.markdown("Insta • TikTok • X (Twitter) • YouTube", help="Cole o link abaixo.")

# --- GERENCIAMENTO DE COOKIES ---
tmp_dir = "/tmp"
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)

if os.path.exists("cookies.txt"):
    cookie_file = "cookies.txt"
elif "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
    cookie_file = os.path.join(tmp_dir, "cookies.txt")
    with open(cookie_file, "w", encoding="utf-8") as f: 
        f.write(st.secrets["general"]["COOKIES_DATA"])
else:
    cookie_file = None

# --- FUNÇÃO AUXILIAR ---
def get_stories_count(url, c_file):
    if not c_file: return 0
    try:
        ydl_opts = {
            'quiet': True, 'extract_flat': True, 'cookiefile': c_file, 'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: return len(list(info['entries']))
            return 1
    except: return 0

if 'last_url' not in st.session_state: st.session_state.last_url = ""
if 'link_verificado' not in st.session_state: st.session_state.link_verificado = False

# --- INTERFACE ---
with st.container():
    # Criar um formulário para a URL para suporte nativo a Enter
    with st.form(key="url_form"):
        url = st.text_input("Link", placeholder="Cole o link da mídia aqui...", label_visibility="collapsed", key="url_input")
        
        # Botão VERIFICAR LINK centralizado
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            check_click = st.form_submit_button("VERIFICAR LINK", help="Clique para processar (ou pressione Enter)", use_container_width=True)

    # Atualizar estado da URL
    if url != st.session_state.last_url:
        st.session_state.link_verificado = False
        st.session_state.last_url = url
        for k in ['current_video_path', 'download_success', 'story_count_cache', 'story_processed']:
            if k in st.session_state: del st.session_state[k]

    if check_click:
        st.session_state.link_verificado = True

    download_now = False
    
    if url and st.session_state.link_verificado:
        # VERIFICAÇÃO PARA YOUTUBE
        if is_youtube_url(url):
            formats = ["360", "480", "720", "1080"]
            col_yt1, col_yt2, col_yt3 = st.columns([1, 2, 1])
            with col_yt2:
                res = st.selectbox("Resolução:", [f"{f}p" for f in formats])
                if st.button("PROCESSAR VÍDEO", use_container_width=True):
                    output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
                    
                    status = st.empty()
                    prog = st.progress(0)
                    
                    try:
                        status.markdown("Extraindo mídia...")
                        # Chama a função de download do YouTube
                        result_path = download_youtube_with_progress(
                            url, output_path, int(res.replace("p", "")), prog, status
                        )
                        
                        if result_path and os.path.exists(result_path) and os.path.getsize(result_path) > 0:
                            st.session_state['current_video_path'] = result_path
                            st.session_state['download_success'] = True
                            st.rerun()
                        else:
                            error_msg = "API do YouTube retornou resultado vazio"
                            st.error("Falha: O vídeo não pôde ser processado.")
                            send_discord_log(error_msg, url)
                            
                    except Exception as e:
                        send_discord_log(e, url)
                        st.error(clean_error_message(e, url))
                    finally:
                        prog.empty()
                        status.empty()
        
        else:
            is_story = "instagram.com/stories/" in url
            
            if is_story:
                if 'story_count_cache' not in st.session_state:
                    with st.spinner("Conectando ao Nexus..."):
                        st.session_state['story_count_cache'] = get_stories_count(url, cookie_file)
                
                if 'story_count_cache' in st.session_state:
                    max_stories = st.session_state['story_count_cache']
                    if max_stories > 0:
                        st.info(f"📸 {max_stories} Stories disponíveis")
                        
                        # Número de story centralizado
                        col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
                        with col_s2:
                            story_index = st.number_input("Nº", 1, max_stories, 1, label_visibility="collapsed")
                        
                        # Botão BAIXAR STORY centralizado
                        col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                        with col_b2:
                            if st.button(f"BAIXAR STORY {story_index}", use_container_width=True):
                                download_now = True
                    else:
                        st.error("Stories indisponíveis (Login necessário).")
            
            else:
                col_bt1, col_bt2, col_bt3 = st.columns([1, 2, 1])
                with col_bt2:
                    if st.button("PROCESSAR VÍDEO", use_container_width=True):
                        download_now = True
                story_index = 0

            if download_now:
                output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
                if os.path.exists(output_path): os.remove(output_path)
                
                status = st.empty(); prog = st.progress(0)
                try:
                    status.markdown("Extraindo mídia...")
                    prog.progress(20)
                    
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_path,
                        'nocheckcertificate': True,
                        'quiet': True,
                        'no_warnings': True,
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    }
                    
                    if cookie_file:
                        ydl_opts['cookiefile'] = cookie_file

                    if is_story:
                        ydl_opts['playlist_items'] = str(story_index)
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                    prog.progress(100)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.session_state['current_video_path'] = output_path
                        st.session_state['download_success'] = True
                        status.empty(); time.sleep(0.2); prog.empty(); st.rerun()
                    else:
                        error_msg = "Arquivo final tem 0 bytes ou não existe"
                        status.error("Falha no download. O arquivo não foi gerado."); prog.empty()
                        send_discord_log(error_msg, url)

                except Exception as e:
                    send_discord_log(e, url)
                    status.error(clean_error_message(e, url))
                    prog.empty()

    if st.session_state.get('download_success'):
        path = st.session_state['current_video_path']
        st.video(path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Botão BAIXAR ARQUIVO centralizado (CORRIGIDO)
        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
        with col_d2:
            with open(path, "rb") as f:
                st.download_button(
                    "BAIXAR ARQUIVO", 
                    f, 
                    f"NexusDL_{timestamp}.mp4", 
                    "video/mp4",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # --- RODAPÉ TOGGLE ---
    if 'feedback_open' not in st.session_state:
        st.session_state.feedback_open = False

    def toggle_feedback():
        st.session_state.feedback_open = not st.session_state.feedback_open

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        label_btn = "❌ Fechar Suporte" if st.session_state.feedback_open else "🏳️ Relatar Problema"
        st.button(label_btn, on_click=toggle_feedback, use_container_width=True)

    if st.session_state.feedback_open:
        with st.container():
            with st.form("report_form"):
                st.caption("Descreva o problema encontrado.")
                email_contato = st.text_input("Seu E-mail (Opcional)", placeholder="Contato...", key="email_input")
                descricao_erro = st.text_area("Detalhes do erro", placeholder="Ex: O vídeo baixou sem áudio...", height=100, key="descricao_input")
                
                # Botão ENVIAR REPORTE centralizado
                col_e1, col_e2, col_e3 = st.columns([1, 2, 1])
                with col_e2:
                    enviar_report = st.form_submit_button("Enviar Reporte", use_container_width=True)
                
                if enviar_report and descricao_erro:
                    msg_final = f"**Contato:** {email_contato}\n**Relato:** {descricao_erro}"
                    send_discord_log(msg_final, "📩 FEEDBACK MANUAL")
                    st.success("Enviado com sucesso!")
                elif enviar_report:
                    st.warning("Por favor, descreva o erro.")

    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 20px;">
        NexusDL © 2026<br>
        Desenvolvido por Tácito e Gabriel
    </div>
    """, unsafe_allow_html=True)
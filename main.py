import streamlit as st
import yt_dlp
import os
import time
import re
import requests
import threading
from datetime import datetime
from urllib.parse import urlparse

# Configuração inicial do Streamlit (Sem emoji no ícone)
st.set_page_config(
    page_title="NexusDL",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mensagens de carregamento rotativas
LOADING_MESSAGES = [
    "Analisando URL...",
    "Verificando disponibilidade do conteudo...",
    "Preparando download...",
    "Processando dados de midia...",
    "Otimizando formato de saida...",
    "Estabelecendo conexao...",
    "Extraindo metadados...",
    "Inicializando processo de download..."
]

def rotate_loading_message(start_time, current_message_index):
    """Alterna mensagens de carregamento a cada 3 segundos"""
    elapsed = time.time() - start_time
    new_index = int(elapsed // 3) % len(LOADING_MESSAGES)
    if new_index != current_message_index:
        return new_index, LOADING_MESSAGES[new_index]
    return current_message_index, None

def is_youtube_url(url):
    """Verifica se a URL é do YouTube"""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
        return any(yt_domain in domain for yt_domain in youtube_domains)
    except:
        return False

def is_instagram_story(url):
    """Verifica se é um link de story do Instagram"""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if 'instagram.com' in domain:
            path = parsed_url.path.lower()
            return '/stories/' in path or '/story/' in path
        return False
    except:
        return False

def validate_url(url):
    """Valida formato da URL e verifica plataformas suportadas"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "URL invalida. Certifique-se de incluir 'http://' ou 'https://'"
        
        domain = parsed.netloc.lower()
        supported_domains = [
            'youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com',
            'instagram.com', 'www.instagram.com',
            'tiktok.com', 'www.tiktok.com',
            'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com'
        ]
        
        for supported in supported_domains:
            if supported in domain:
                return True, ""
        
        return False, "URL nao suportada. Use links do YouTube, Instagram, TikTok ou X (Twitter)."
    except Exception as e:
        return False, f"URL invalida: {str(e)}"

def check_video_exists(url):
    """Verifica disponibilidade do conteúdo"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'no_warnings': True,
            'skip_download': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        # Adiciona cookies para Instagram se existirem
        if "instagram.com" in url and os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = "cookies.txt"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return True, info
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if "unable to download webpage" in error_msg or "video unavailable" in error_msg:
            return False, "Video nao encontrado ou indisponivel"
        elif "private video" in error_msg:
            return False, "Este video e privado"
        elif "sign in to confirm" in error_msg or "login" in error_msg:
            return False, "Login necessario para acessar este conteudo"
        else:
            return False, f"Erro ao verificar video: {str(e)[:100]}"
    except Exception as e:
        return False, f"Erro inesperado: {str(e)[:100]}"

def download_youtube_with_progress(url, output_path, res, progress_bar, status_placeholder):
    """Download de vídeos do YouTube usando API externa com barra de progresso"""
    try:
        api_key = st.secrets["general"]["YOUTUBE_API_KEY"]
    except KeyError:
        error_msg = "Erro: Chave 'YOUTUBE_API_KEY' nao encontrada nos Secrets."
        raise Exception(error_msg)

    init_url = f"https://p.savenow.to/ajax/download.php?format={res}&url={url}&apikey={api_key}"
    
    # Inicializa variáveis de controle de progresso
    start_time = time.time()
    last_message_time = start_time
    message_index = 0
    status_placeholder.markdown(LOADING_MESSAGES[0])

    try:
        response = requests.get(init_url)
        response.raise_for_status()
        data = response.json()
        job_id = data.get("id")

        if not job_id:
            raise Exception("API do YouTube nao retornou ID do job")

        while True:
            time.sleep(1.5)
            
            # Atualiza mensagem a cada 3 segundos
            current_time = time.time()
            if current_time - last_message_time >= 3:
                message_index, new_message = rotate_loading_message(start_time, message_index)
                if new_message and status_placeholder:
                    status_placeholder.markdown(new_message)
                last_message_time = current_time
            
            # Verifica progresso
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
                    raise Exception("API do YouTube nao retornou URL de download")

                status_placeholder.markdown("Baixando video para o servidor...")

                # Download final do arquivo
                with requests.get(final_url, stream=True) as r:
                    r.raise_for_status()
                    with open(output_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                status_placeholder.empty()
                progress_bar.empty()
                return output_path

            if p_data.get("status") == "error":
                raise Exception(f"API do YouTube retornou erro: {p_data.get('message', 'Erro desconhecido')}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro de conexao com API do YouTube: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro na API SaveNow: {str(e)}")

def send_discord_log(error_msg, video_url="", error_type="download"):
    """Envia logs de erro para Discord com categorização - Mantém Emojis APENAS aqui"""
    clean_msg = str(error_msg)[:800]
    
    # Determina tipo de erro para formatação adequada
    is_feedback = "FEEDBACK" in str(video_url) or "REPORT" in str(video_url) or "feedback" in str(error_msg).lower()
    is_validation = error_type == "validation"
    
    # Configurações baseadas no tipo
    if is_feedback:
        webhook_key = "DISCORD_WEBHOOK_FEEDBACK"
        color = 3447003  # Azul
        username = "NexusDL Feedback"
        
        # Formata mensagem de feedback
        if "**Contato:**" in clean_msg and "**Relato:**" in clean_msg:
            parts = clean_msg.split("**Contato:**")[1].split("**Relato:**")
            contato = parts[0].strip() if parts[0].strip() else "Não informado"
            relato = parts[1].strip() if len(parts) > 1 else clean_msg
            
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
    
    elif is_validation:
        webhook_key = "DISCORD_WEBHOOK_ERROR"
        color = 16753920  # Laranja para erros de validação
        username = "NexusDL Monitor"
        
        # Formata URL para exibição
        url_display = str(video_url)[:200]
        if len(str(video_url)) > 200:
            url_display = url_display + "..."
        
        title = "⚠️ ERRO DE VALIDAÇÃO"
        fields = [
            {"name": "🔗 URL", "value": f"```{url_display}```", "inline": False},
            {"name": "📋 Detalhes do Erro", "value": f"```{clean_msg}```", "inline": False},
            {"name": "🕐 Horário", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": True}
        ]
    
    else:  # Erro de download padrão
        webhook_key = "DISCORD_WEBHOOK_ERROR"
        color = 15548997  # Vermelho
        username = "NexusDL Monitor"
        
        # Limpa formatações da mensagem
        error_display = clean_msg
        error_display = re.sub(r'❌\[0;31m', '', error_display)
        error_display = re.sub(r'❌\[0m', '', error_display)
        error_display = re.sub(r'\[0;31m', '', error_display)
        error_display = re.sub(r'\[0m', '', error_display)
        error_display = re.sub(r'ERROR:', 'ERRO:', error_display)
        
        url_display = str(video_url)[:200]
        if len(str(video_url)) > 200:
            url_display = url_display + "..."
        
        title = "🚨 FALHA NO DOWNLOAD"
        fields = [
            {"name": "🔗 URL", "value": f"```{url_display}```", "inline": False},
            {"name": "📋 Detalhes do Erro", "value": f"```{error_display}```", "inline": False},
            {"name": "🕐 Horário", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": True}
        ]
    
    # Envia para Discord se webhook configurado
    if "general" in st.secrets and webhook_key in st.secrets["general"]:
        webhook_url = st.secrets["general"][webhook_key]
        data = {
            "username": username,
            "embeds": [{
                "title": title,
                "color": color,
                "fields": fields,
                "timestamp": datetime.now().isoformat()
            }]
        }
        try:
            requests.post(webhook_url, json=data, timeout=3)
        except Exception:
            pass  # Falha silenciosa no log

def clean_error_message(error_text, url=""):
    """Limpa e formata mensagens de erro para exibição ao usuário"""
    text = str(error_text)
    
    # Remove códigos de formatação ANSI
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # Remove formatações específicas e Emojis
    text = re.sub(r'❌\[0;31m', '', text)
    text = re.sub(r'❌\[0m', '', text)
    text = re.sub(r'\[0;31m', '', text)
    text = re.sub(r'\[0m', '', text)
    
    # Traduz mensagens comuns
    if "YouTube" in text or "SaveNow" in text or "API" in text:
        return "Erro na API do YouTube. Tente novamente mais tarde."
    if "not a valid URL" in text or "Unsupported URL" in text:
        return "Link invalido. Certifique-se de copiar a URL completa."
    if "HTTP Error 400" in text:
        return "Conexao recusada (Erro 400). O Instagram bloqueou a conexao anonima ou os cookies expiraram."
    if "Sign in to confirm" in text or "login" in text.lower():
        return "Conteudo exige login (Cookies necessarios)."
    if "Video unavailable" in text:
        return "Video nao encontrado ou excluido."
    if "Private video" in text:
        return "Este video e privado."
        
    return f"Erro tecnico: {text[:200]}..."

def download_with_loading(url, output_path, cookie_file, is_story=False, story_index=0, progress_bar=None, status_placeholder=None):
    """Download para outras plataformas com sistema de progresso"""
    
    def download_thread():
        try:
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
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            download_result['success'] = True
        except Exception as e:
            download_result['error'] = e
    
    # Inicializa resultado
    download_result = {'success': False, 'error': None}
    
    # Inicia thread de download
    thread = threading.Thread(target=download_thread)
    thread.start()
    
    # Sistema de mensagens rotativas
    start_time = time.time()
    message_index = 0
    
    if status_placeholder:
        status_placeholder.markdown(LOADING_MESSAGES[0])
    
    # Loop de progresso enquanto download ocorre
    while thread.is_alive():
        message_index, new_message = rotate_loading_message(start_time, message_index)
        if new_message and status_placeholder:
            status_placeholder.markdown(new_message)
        
        # Progresso simulado baseado no tempo
        if progress_bar:
            elapsed = time.time() - start_time
            progress = min(elapsed * 5, 90)
            progress_bar.progress(int(progress))
        
        time.sleep(0.5)
    
    thread.join()
    
    # Verifica resultado
    if download_result['success']:
        if progress_bar:
            progress_bar.progress(100)
        return True
    else:
        if download_result['error']:
            raise download_result['error']
        return False

def get_stories_count(url, c_file):
    """Conta número de stories disponíveis"""
    if not c_file: 
        return 0
    try:
        ydl_opts = {
            'quiet': True, 
            'extract_flat': True, 
            'cookiefile': c_file, 
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: 
                return len(list(info['entries']))
            return 1
    except Exception:
        return 0

def determine_content_type(url):
    """Determina tipo de conteúdo e se requer interação do usuário"""
    if is_youtube_url(url):
        return "youtube"  # Requer escolha de qualidade
    elif is_instagram_story(url):
        return "instagram_story"  # Pode requerer escolha de story
    else:
        return "direct"  # Download direto sem escolhas

def process_content_automatically(url, content_type, cookie_file, story_index=1):
    """Processa automaticamente conteúdos que não requerem escolhas"""
    output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
    if os.path.exists(output_path): 
        os.remove(output_path)
    
    status = st.empty()
    prog = st.progress(0)
    
    try:
        if content_type == "direct":
            success = download_with_loading(url, output_path, cookie_file, False, 0, prog, status)
        elif content_type == "instagram_story":
            success = download_with_loading(url, output_path, cookie_file, True, story_index, prog, status)
        else:
            return None
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            error_msg = "Arquivo final tem 0 bytes ou nao existe"
            status.error("Falha no download. O arquivo nao foi gerado.")
            prog.empty()
            send_discord_log(error_msg, url)
            return None

    except Exception as e:
        send_discord_log(e, url)
        status.error(clean_error_message(e, url))
        prog.empty()
        return None

# Carrega estilos CSS
def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
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
        pass

# Inicializa interface
load_css()
load_js()

# Interface principal
st.title("NexusDL")
st.markdown("Instagram - TikTok - X (Twitter) - YouTube", help="Cole o link abaixo.")

# Configura diretório temporário
tmp_dir = "/tmp"
if not os.path.exists(tmp_dir): 
    os.makedirs(tmp_dir)

# Gerenciamento de cookies
if os.path.exists("cookies.txt"):
    cookie_file = "cookies.txt"
elif "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
    cookie_file = os.path.join(tmp_dir, "cookies.txt")
    with open(cookie_file, "w", encoding="utf-8") as f: 
        f.write(st.secrets["general"]["COOKIES_DATA"])
else:
    cookie_file = None

# Inicializa estados da sessão
if 'last_url' not in st.session_state: 
    st.session_state.last_url = ""
if 'link_verificado' not in st.session_state: 
    st.session_state.link_verificado = False
if 'video_exists' not in st.session_state: 
    st.session_state.video_exists = False
if 'video_info' not in st.session_state: 
    st.session_state.video_info = None
if 'content_type' not in st.session_state:
    st.session_state.content_type = None
if 'stories_count' not in st.session_state:
    st.session_state.stories_count = 0
if 'show_quality_selector' not in st.session_state:
    st.session_state.show_quality_selector = False
if 'quality_selector_created' not in st.session_state:
    st.session_state.quality_selector_created = False
if 'auto_processing' not in st.session_state:
    st.session_state.auto_processing = False
if 'youtube_processing' not in st.session_state:
    st.session_state.youtube_processing = False

# Formulário principal
with st.container():
    with st.form(key="url_form"):
        url = st.text_input("Link", placeholder="Cole o link da midia aqui...", label_visibility="collapsed", key="url_input")
        
        # Layout Mobile-Friendly para o botão principal
        col1, col2, col3 = st.columns([1, 15, 1])
        with col2:
            check_click = st.form_submit_button("VERIFICAR LINK", help="Clique para processar (ou pressione Enter)", use_container_width=True)

    # Reseta estado se URL mudou
    if url != st.session_state.last_url:
        st.session_state.link_verificado = False
        st.session_state.video_exists = False
        st.session_state.video_info = None
        st.session_state.last_url = url
        st.session_state.content_type = None
        st.session_state.show_quality_selector = False
        st.session_state.quality_selector_created = False
        st.session_state.auto_processing = False
        st.session_state.youtube_processing = False
        st.session_state.stories_count = 0
        
        # Remove estados de download
        for k in ['current_video_path', 'download_success', 'story_count_cache', 'story_processed']:
            if k in st.session_state: 
                del st.session_state[k]

    # Processa verificação de link
    if check_click:
        if not url:
            st.error("Por favor, cole uma URL no campo acima.")
            send_discord_log("Campo de URL vazio", "", "validation")
        else:
            # Valida URL
            is_valid, validation_msg = validate_url(url)
            if not is_valid:
                st.error(validation_msg)
                st.session_state.link_verificado = False
                st.session_state.video_exists = False
                # Envia erro de validação para Discord
                send_discord_log(validation_msg, url, "validation")
            else:
                # Verifica disponibilidade do conteúdo
                with st.spinner("Verificando URL..."):
                    video_exists, video_result = check_video_exists(url)
                    
                    if video_exists:
                        st.session_state.link_verificado = True
                        st.session_state.video_exists = True
                        st.session_state.video_info = video_result
                        
                        # Determina tipo de conteúdo
                        st.session_state.content_type = determine_content_type(url)
                        
                        # Conta stories se for Instagram
                        if st.session_state.content_type == "instagram_story":
                            with st.spinner("Contando stories..."):
                                st.session_state.stories_count = get_stories_count(url, cookie_file)
                        
                        # Define fluxo baseado no tipo
                        if st.session_state.content_type == "youtube":
                            st.session_state.show_quality_selector = True
                            st.session_state.auto_processing = False
                        elif st.session_state.content_type == "instagram_story" and st.session_state.stories_count > 1:
                            st.session_state.show_quality_selector = False
                            st.session_state.auto_processing = False
                        else:
                            # Processamento automático para conteúdos diretos
                            st.session_state.show_quality_selector = False
                            st.session_state.auto_processing = True
                        
                        st.success("URL verificada com sucesso!")
                        
                        # Inicia processamento automático se necessário
                        if st.session_state.auto_processing and not st.session_state.get('download_success'):
                            st.rerun()
                        
                    else:
                        st.session_state.link_verificado = True
                        st.session_state.video_exists = False
                        error_msg = video_result if isinstance(video_result, str) else "Nao foi possivel verificar o video"
                        st.error(error_msg)
                        # Envia erro de verificação para Discord
                        send_discord_log(error_msg, url, "download")

    # Processamento automático para conteúdos diretos
    if (st.session_state.get('auto_processing') and 
        st.session_state.link_verificado and 
        st.session_state.video_exists and
        not st.session_state.get('download_success')):
        
        story_index = 1
        if st.session_state.content_type == "instagram_story" and st.session_state.stories_count == 1:
            story_index = 1
        
        with st.spinner("Processando automaticamente..."):
            output_path = process_content_automatically(
                url, 
                st.session_state.content_type, 
                cookie_file,
                story_index
            )
            
            if output_path and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                st.session_state['current_video_path'] = output_path
                st.session_state['download_success'] = True
                st.session_state.auto_processing = False
                st.rerun()

    # Mostra interfaces de seleção quando necessário
    if url and st.session_state.link_verificado and st.session_state.video_exists:
        
        # YouTube - Seletor de qualidade
        # MODIFICADO: Só mostra se NÃO tiver feito download com sucesso ainda
        if (st.session_state.content_type == "youtube" and 
            st.session_state.show_quality_selector and 
            not st.session_state.get('download_success')):
            
            # Se NÃO estiver processando, mostra os botões
            if not st.session_state.get('youtube_processing'):
                formats = ["360p", "480p", "720p", "1080p"]
                
                # Layout Mobile-Friendly
                col_yt1, col_yt2, col_yt3 = st.columns([1, 15, 1])
                with col_yt2:
                    res = st.radio("Resolucao:", formats, horizontal=True, key="quality_selector")
                    
                    # Botão de processamento
                    if st.button("PROCESSAR VIDEO", use_container_width=True, key="youtube_process_button"):
                        st.session_state.youtube_selected_res = int(res.replace("p", ""))
                        st.session_state.youtube_processing = True
                        st.rerun()

            # Se ESTIVER processando, esconde botões e roda a lógica
            else:
                output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
                status = st.empty()
                prog = st.progress(0)
                
                try:
                    res_value = st.session_state.get('youtube_selected_res', 360)
                    result_path = download_youtube_with_progress(
                        url, output_path, res_value, prog, status
                    )
                    
                    if result_path and os.path.exists(result_path) and os.path.getsize(result_path) > 0:
                        st.session_state['current_video_path'] = result_path
                        st.session_state['download_success'] = True
                        st.session_state.youtube_processing = False
                        st.rerun()
                    else:
                        error_msg = "API do YouTube retornou resultado vazio"
                        st.error("Falha: O video nao pode ser processado.")
                        send_discord_log(error_msg, url)
                        st.session_state.youtube_processing = False
                        
                except Exception as e:
                    send_discord_log(e, url)
                    st.error(clean_error_message(e, url))
                    st.session_state.youtube_processing = False
                finally:
                    prog.empty()
                    status.empty()
                    if st.session_state.youtube_processing == False:
                        st.rerun()
        
        # Instagram com múltiplos stories
        elif (st.session_state.content_type == "instagram_story" and 
              st.session_state.stories_count > 1):
            
            st.info(f"{st.session_state.stories_count} Stories disponiveis")
            
            # Layout Mobile-Friendly
            col_s1, col_s2, col_s3 = st.columns([1, 15, 1])
            with col_s2:
                story_index = st.number_input("N", 1, st.session_state.stories_count, 1, 
                                            label_visibility="collapsed", key="story_index_selector")
            
            col_b1, col_b2, col_b3 = st.columns([1, 15, 1])
            with col_b2:
                if st.button(f"BAIXAR STORY {story_index}", use_container_width=True, key="story_download_button"):
                    output_path = os.path.join(tmp_dir, f"download_{int(time.time())}.mp4")
                    if os.path.exists(output_path): 
                        os.remove(output_path)
                    
                    status = st.empty()
                    prog = st.progress(0)
                    
                    try:
                        success = download_with_loading(
                            url, output_path, cookie_file, True, story_index, prog, status
                        )
                        
                        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            st.session_state['current_video_path'] = output_path
                            st.session_state['download_success'] = True
                            status.empty()
                            time.sleep(0.2)
                            prog.empty()
                            st.rerun()
                        else:
                            error_msg = "Arquivo final tem 0 bytes ou nao existe"
                            status.error("Falha no download. O arquivo nao foi gerado.")
                            prog.empty()
                            send_discord_log(error_msg, url)

                    except Exception as e:
                        send_discord_log(e, url)
                        status.error(clean_error_message(e, url))
                        prog.empty()

    # Exibe resultado do download - SEMPRE visível quando houver download
    if st.session_state.get('download_success') and st.session_state.get('current_video_path'):
        path = st.session_state['current_video_path']
        if os.path.exists(path) and os.path.getsize(path) > 0:
            st.markdown("---")
            st.subheader("Video Processado com Sucesso")
            st.video(path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Layout Mobile-Friendly
            col_d1, col_d2, col_d3 = st.columns([1, 15, 1])
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
    
    # Sistema de feedback
    if 'feedback_open' not in st.session_state:
        st.session_state.feedback_open = False

    def toggle_feedback():
        st.session_state.feedback_open = not st.session_state.feedback_open

    # Layout Mobile-Friendly
    col_f1, col_f2, col_f3 = st.columns([1, 15, 1])
    with col_f2:
        label_btn = "Fechar Suporte" if st.session_state.feedback_open else "Relatar Problema"
        st.button(label_btn, on_click=toggle_feedback, use_container_width=True)

    if st.session_state.feedback_open:
        with st.container():
            with st.form("report_form"):
                st.caption("Descreva o problema encontrado.")
                email_contato = st.text_input("Seu E-mail (Opcional)", placeholder="Contato...", key="email_input")
                descricao_erro = st.text_area("Detalhes do erro", placeholder="Ex: O video baixou sem audio...", height=100, key="descricao_input")
                
                col_e1, col_e2, col_e3 = st.columns([1, 15, 1])
                with col_e2:
                    enviar_report = st.form_submit_button("Enviar Reporte", use_container_width=True)
                
                if enviar_report and descricao_erro:
                    msg_final = f"**Contato:** {email_contato}\n**Relato:** {descricao_erro}"
                    send_discord_log(msg_final, "FEEDBACK MANUAL")
                    st.success("Enviado com sucesso!")
                elif enviar_report:
                    st.warning("Por favor, descreva o erro.")

    # Rodapé
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 20px;">
        NexusDL 2026<br>
        Desenvolvido por Tacito e Gabriel
    </div>
    """, unsafe_allow_html=True)
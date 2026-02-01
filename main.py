import os
import time
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st
import yt_dlp

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NexusDL", page_icon="⚫", layout="centered", initial_sidebar_state="collapsed")


# --- FUNÇÕES DE VERIFICAÇÃO E AUXÍLIO ---
def is_youtube_url(url):
    """Verifica se a URL é do YouTube"""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        return any(
            youtube_domain in domain
            for youtube_domain in ["youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com"]
        )
    except:
        return False


def process_youtube_download_api(video_url, format_res):
    """Lógica de download via API externa para YouTube com chave via Secrets"""

    try:
        api_key = st.secrets["general"]["YOUTUBE_API_KEY"]
    except KeyError:
        st.error("Erro: Chave 'YOUTUBE_API_KEY' não encontrada nos Secrets.")
        return None

    init_url = f"https://p.savenow.to/ajax/download.php?format={format_res}&url={video_url}&apikey={api_key}"

    try:
        response = requests.get(init_url)
        response.raise_for_status()
        data = response.json()
        job_id = data.get("id")

        if not job_id:
            return None

        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        while True:
            time.sleep(1.5)
            progress_endpoint = f"https://p.savenow.to/ajax/progress?id={job_id}"

            p_resp = requests.get(progress_endpoint)
            p_data = p_resp.json()

            curr = int(p_data.get("progress", 0))
            norm = min(max(curr / 1000, 0.0), 1.0)

            progress_bar.progress(norm)
            status_placeholder.markdown(
                f"<p style='text-align:center'>Processando no Servidor Nexus: {norm * 100:.1f}%</p>",
                unsafe_allow_html=True,
            )

            if curr == 1000:
                final_url = p_data.get("download_url")
                status_placeholder.empty()
                progress_bar.empty()
                return final_url

            if p_data.get("status") == "error":
                status_placeholder.empty()
                progress_bar.empty()
                return None

    except Exception:
        return None


def send_discord_log(error_msg, video_url):
    clean_msg = str(error_msg)[:800]
    is_feedback = "FEEDBACK" in str(video_url) or "REPORT" in str(video_url) or "feedback" in str(error_msg).lower()

    if is_feedback:
        webhook_key = "DISCORD_WEBHOOK_FEEDBACK"
        color = 3447003
        username = "NexusDL Feedback"
        title = "📢 NOVO FEEDBACK"
        fields = [{"name": "📝 Mensagem", "value": f"```{clean_msg}```", "inline": False}]
    else:
        webhook_key = "DISCORD_WEBHOOK_ERROR"
        color = 15548997
        username = "NexusDL Monitor"
        title = "🚨 FALHA NO DOWNLOAD"
        fields = [
            {"name": "🔗 URL", "value": f"```{str(video_url)[:200]}```", "inline": False},
            {"name": "📋 Detalhes", "value": f"```{clean_msg}```", "inline": False},
        ]

    if "general" in st.secrets and webhook_key in st.secrets["general"]:
        webhook_url = st.secrets["general"][webhook_key]
        data = {
            "username": username,
            "embeds": [{"title": title, "color": color, "fields": fields, "timestamp": datetime.now().isoformat()}],
        }
        try:
            requests.post(webhook_url, json=data, timeout=3)
        except:
            pass


def clean_error_message(error_text, url=""):
    text = str(error_text)
    if "not a valid URL" in text or "Unsupported URL" in text:
        return "⚠️ Link inválido. Certifique-se de copiar a URL completa."
    if "HTTP Error 400" in text:
        return "⚠️ Erro 400: O Instagram bloqueou a conexão ou os cookies expiraram."
    if "Video unavailable" in text:
        return "🚫 Vídeo não encontrado ou excluído."
    return f"Erro técnico: {text[:100]}..."


try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("NexusDL")
st.markdown("YouTube • Insta • TikTok • X", help="Cole o link abaixo.")

tmp_dir = "/tmp"
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

cookie_file = None
if os.path.exists("cookies.txt"):
    cookie_file = "cookies.txt"
elif "general" in st.secrets and "COOKIES_DATA" in st.secrets["general"]:
    cookie_file = os.path.join(tmp_dir, "cookies.txt")
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(st.secrets["general"]["COOKIES_DATA"])


def get_stories_count(url, c_file):
    try:
        ydl_opts = {"quiet": True, "extract_flat": True, "cookiefile": c_file}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return len(list(info["entries"])) if "entries" in info else 1
    except:
        return 0


if "last_url" not in st.session_state:
    st.session_state.last_url = ""
if "link_verificado" not in st.session_state:
    st.session_state.link_verificado = False

with st.container():
    with st.form(key="url_form"):
        url_input = st.text_input("Link", placeholder="Cole o link da mídia aqui...", label_visibility="collapsed")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            check_click = st.form_submit_button("VERIFICAR LINK", use_container_width=True)

    if url_input != st.session_state.last_url:
        st.session_state.link_verificado = False
        st.session_state.last_url = url_input
        for k in ["current_video_path", "download_success", "story_count_cache"]:
            if k in st.session_state:
                del st.session_state[k]

    if check_click:
        st.session_state.link_verificado = True

    if url_input and st.session_state.link_verificado:
        # CASO 1: YOUTUBE
        if is_youtube_url(url_input):
            st.info("📺 YouTube detectado.")
            formats = ["360", "480", "720", "1080"]
            col_yt1, col_yt2, col_yt3 = st.columns([1, 2, 1])
            with col_yt2:
                selected_res = st.selectbox("Resolução:", [f"{f}p" for f in formats], key="yt_res")
                if st.button("GERAR DOWNLOAD", use_container_width=True):
                    res_val = selected_res.replace("p", "")
                    with st.spinner("Conectando ao Nexus..."):
                        final_link = process_youtube_download_api(url_input, res_val)
                    if final_link:
                        st.success("✅ Link pronto!")
                        st.link_button("BAIXAR MP4", final_link, type="primary", use_container_width=True)
                    else:
                        st.error("Erro ao processar. Tente outra resolução.")

        # CASO 2: OUTRAS REDES
        else:
            download_now = False
            is_story = "instagram.com/stories/" in url_input

            if is_story:
                if "story_count_cache" not in st.session_state:
                    with st.spinner("Lendo Stories..."):
                        st.session_state["story_count_cache"] = get_stories_count(url_input, cookie_file)

                max_stories = st.session_state.get("story_count_cache", 0)
                if max_stories > 0:
                    st.info(f"📸 {max_stories} Stories encontrados")
                    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
                    with col_s2:
                        story_idx = st.number_input("Nº", 1, max_stories, 1)
                        if st.button(f"BAIXAR STORY {story_idx}", use_container_width=True):
                            download_now = True
                else:
                    st.error("Stories indisponíveis.")
            else:
                col_bt1, col_bt2, col_bt3 = st.columns([1, 2, 1])
                with col_bt2:
                    if st.button("PROCESSAR VÍDEO", use_container_width=True):
                        download_now = True
                story_idx = 0

            if download_now:
                output_path = os.path.join(tmp_dir, f"nexus_{int(time.time())}.mp4")
                status = st.empty()
                prog = st.progress(0)
                try:
                    status.markdown("Extraindo mídia...")
                    prog.progress(30)
                    opts = {
                        "format": "best",
                        "outtmpl": output_path,
                        "quiet": True,
                        "no_warnings": True,
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
                    }
                    if cookie_file:
                        opts["cookiefile"] = cookie_file
                    if is_story:
                        opts["playlist_items"] = str(story_idx)

                    with yt_dlp.YoutubeDL(opts) as ydl:
                        ydl.download([url_input])

                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.session_state["current_video_path"] = output_path
                        st.session_state["download_success"] = True
                        status.empty()
                        prog.empty()
                        st.rerun()
                    else:
                        status.error("Falha ao gerar arquivo.")
                        prog.empty()
                except Exception as e:
                    send_discord_log(e, url_input)
                    status.error(clean_error_message(e, url_input))
                    prog.empty()

    # Exibição do resultado local (Insta/TikTok)
    if st.session_state.get("download_success"):
        path = st.session_state["current_video_path"]
        st.video(path)
        with open(path, "rb") as f:
            st.download_button(
                "BAIXAR ARQUIVO", f, f"NexusDL_{int(time.time())}.mp4", "video/mp4", use_container_width=True
            )

st.markdown("---")
if "feedback_open" not in st.session_state:
    st.session_state.feedback_open = False

col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    if st.button("❌ Fechar" if st.session_state.feedback_open else "🏳️ Relatar Problema", use_container_width=True):
        st.session_state.feedback_open = not st.session_state.feedback_open
        st.rerun()

if st.session_state.feedback_open:
    with st.form("report"):
        email = st.text_input("E-mail (Opcional)")
        msg = st.text_area("O que aconteceu?")
        if st.form_submit_button("Enviar") and msg:
            send_discord_log(f"Feedback: {msg} | Contato: {email}", "📩 FEEDBACK")
            st.success("Enviado!")

st.markdown(
    '<div style="text-align:center;color:gray;font-size:12px">NexusDL © 2026 | Tácito</div>', unsafe_allow_html=True
)

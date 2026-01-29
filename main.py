import yt_dlp
import os

def baixar_video(url):
    # Cria a pasta de downloads se não existir
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        # 'best' baixa um arquivo único já pronto em mp4, evitando erro de FFmpeg
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        
        # --- ESSENCIAL PARA STORIES ---
        # O arquivo 'cookies.txt' deve estar na pasta C:\Users\tacito.tinoco\Documents\BaixarVideos
        'cookiefile': 'cookies.txt', 
        
        # Opções de estabilidade
        'hls_prefer_native': True,
        'retries': 10,
        'fragment_retries': 10,
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n--- Iniciando download de: {url} ---")
            ydl.download([url])
            print("\n✅ Sucesso! O arquivo está na pasta 'downloads'.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\nDICA: Para Stories, certifique-se de que o 'cookies.txt' foi gerado com você logado no Instagram.")

if __name__ == "__main__":
    print("=== Downloader Pro (YouTube, Instagram, Twitter) ===")
    link = input("Cole o link aqui: ").strip()
    if link:
        baixar_video(link)
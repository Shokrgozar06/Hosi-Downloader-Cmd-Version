import json
import os
import yt_dlp

CONFIG_FILE = 'config.json'

def load_config():
    """Load settings from JSON file if available."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(config):
    """Save settings to JSON file."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print("Settings saved successfully!")

def ask_quality_preference():
    """Prompt user to select a default video/audio quality."""
    print("\n--- Select Default Quality ---")
    print("1. Best available quality")
    print("2. 1080p (or lower)")
    print("3. 720p (or lower)")
    print("4. 480p (or lower)")
    print("5. Audio only (MP3 / Separate Folders)")
    
    choice = input("Enter your choice (1-5) [Default: 1]: ").strip()
    
    quality_map = {
        '1': 'bestvideo+bestaudio/best',
        '2': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
        '3': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
        '4': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
        '5': 'bestaudio/best'
    }
    
    selected_format = quality_map.get(choice, 'bestvideo+bestaudio/best')
    config = {
        'format': selected_format, 
        'choice_code': choice if choice in quality_map else '1',
        'is_audio_only': (choice == '5')
    }
    save_config(config)
    return config

def download_media(url, config):
    is_audio = config.get('is_audio_only', False)
    
    if is_audio:
        outtmpl = 'Downloads/%(playlist_title,uploader,artist)s/%(playlist_index,1)s - %(title)s.%(ext)s'
    else:
        outtmpl = '%(title)s.%(ext)s'
        
    ydl_opts = {
        'format': config['format'],
        'outtmpl': outtmpl,
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'ignoreerrors': True,
    }
    
    if is_audio:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        print("\nAnalyzing link and starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n[SUCCESS] Download completed!")
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
if __name__ == "__main__":
    config = load_config()
    
    if config:
        print(f"Loaded existing quality configuration (Option {config.get('choice_code')}).")
        change = input("Do you want to change the default quality? (y/N): ").strip().lower()
        if change == 'y':
            config = ask_quality_preference()
    else:
        config = ask_quality_preference()

    while True:
        print("\n" + "=" * 50)
        media_url = input("Enter URL (or type 'q' / 'exit' to quit): ").strip()
        
        if media_url.lower() in ['q', 'exit', 'quit']:
            print("Exiting program. Goodbye!")
            break
            
        if not media_url:
            print("URL cannot be empty. Please try again.")
            continue

        download_media(media_url, config)
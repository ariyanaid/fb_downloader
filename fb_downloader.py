import requests
import json
import subprocess
import os
import time

def print_banner():
    banner = r"""
   _____ ____        _                     _                 _           
  |  ___| __ )    __| | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
  | |_  |  _ \   / _` |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
  |  _| | |_) | | (_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
  |_|   |____/   \__,_|\___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   

                                    by ariyanaid
"""
    print(banner)

def downloadFile(link, file_name, output_folder):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    try:
        resp = requests.get(link, headers=headers).content
    except:
        print("[X] Gagal download:", link)
        return False
    with open(os.path.join(output_folder, file_name), 'wb') as f:
        f.write(resp)
    return True

def downloadVideo(link, output_folder, quality):
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Dnt': '1',
    'Dpr': '1.3125',
    'Priority': 'u=0, i',
    'Sec-Ch-Prefers-Color-Scheme': 'dark',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="124.0.6367.156", "Google Chrome";v="124.0.6367.156", "Not-A.Brand";v="99.0.0.0"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Viewport-Width': '1463'
}

    print("[*] Memuat halaman...")
    try:
        resp = requests.get(link, headers=headers)
    except:
        print("[X] Gagal akses URL:", link)
        return

    page = resp.text
    link = resp.url.split('?')[0]
    splits = link.split('/')
    video_id = splits[-1]

    print("[*] Parsing metadata...")
    try:
        target_video_audio_id = page.split('"id":"{}"'.format(video_id))[1].split('"dash_prefetch_experimental":[')[1].split(']')[0].strip()
    except:
        try:
            target_video_audio_id = page.split('"video_id":"{}"'.format(video_id))[1].split('"dash_prefetch_experimental":[')[1].split(']')[0].strip()
        except:
            print("[X] Gagal parsing dari:", link)
            return

    sources = json.loads("[" + target_video_audio_id + "]")

    if len(sources) == 1:
        print("[!] Deteksi 1 stream - kemungkinan video+audio sudah gabung.")
        try:
            video_link = page.split('"representation_id":"{}"'.format(sources[0]))[1].split('"base_url":"')[1].split('"')[0]
            video_link = video_link.replace('\\', '')
            print("[OK] URL video+audio:", video_link)
        except:
            print("[X] Gagal ambil URL gabungan.")
            return

        print("[*] Mendownload file tunggal...")
        if downloadFile(video_link, f'{video_id}.mp4', output_folder):
            print("[OK] Selesai tanpa merge:", f'{video_id}.mp4')
        return

    try:
        if quality == 'HD':
            video_link = page.split('"representation_id":"{}"'.format(sources[0]))[1].split('"base_url":"')[1].split('"')[0]
        else:
            video_link = page.split('"representation_id":"{}"'.format(sources[-1]))[1].split('"base_url":"')[1].split('"')[0]
        video_link = video_link.replace('\\', '')
        print("[OK] URL video:", video_link)
    except:
        print("[X] Gagal ambil URL video.")
        return

    try:
        audio_link = page.split('"representation_id":"{}"'.format(sources[1]))[1].split('"base_url":"')[1].split('"')[0]
        audio_link = audio_link.replace('\\', '')
        print("[OK] URL audio:", audio_link)
    except:
        print("[X] Gagal ambil URL audio.")
        return

    print("[*] Mendownload video...")
    if not downloadFile(video_link, 'video.mp4', output_folder): return
    print("[*] Mendownload audio...")
    if not downloadFile(audio_link, 'audio.mp4', output_folder): return

    print("[*] Menggabungkan file dengan ffmpeg lokal...")
    video_path = os.path.join(output_folder, 'video.mp4')
    audio_path = os.path.join(output_folder, 'audio.mp4')
    output_path = os.path.join(output_folder, f'{video_id}.mp4')

    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe')
    if not os.path.isfile(ffmpeg_path):
        print("[X] ffmpeg.exe tidak ditemukan di:", ffmpeg_path)
        return

    cmd = f'"{ffmpeg_path}" -hide_banner -loglevel error -y -i "{video_path}" -i "{audio_path}" -c copy "{output_path}"'
    subprocess.call(cmd, shell=True)

    os.remove(video_path)
    os.remove(audio_path)
    print("[OK] Merge selesai:", output_path)

def main():
    print_banner()
    output_folder = os.path.join(os.getcwd(), 'hasil_download_fb')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    mode = input("Pilih mode (1: URL tunggal, 2: File TXT): ").strip()
    quality = input("Pilih kualitas video (HD/SD): ").strip().upper()

    if mode == '1':
        link = input("Masukkan URL video: ").strip()
        print("== Memulai download tunggal ==")
        downloadVideo(link, output_folder, quality)
    elif mode == '2':
        txt_path = input("Masukkan path file .txt (misal: url.txt): ").strip()
        if not os.path.exists(txt_path):
            print("File tidak ditemukan:", txt_path)
            return
        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            urls = [line.strip() for line in f if line.strip()]
        total = len(urls)
        for i, url in enumerate(urls, 1):
            print(f"\n== [{i}/{total}] Memulai:", url)
            downloadVideo(url, output_folder, quality)
            print("[*] Menunggu 2 detik...\n")
            time.sleep(2)
    else:
        print("Mode tidak valid.")

    print("\n[OK] Semua selesai. Cek folder:", output_folder)

if __name__ == "__main__":
    main()

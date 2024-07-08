import os
from googleapiclient.discovery import build

def get_youtube_links(api_key, queries, max_results=50, existing_videos=set()):
    youtube = build('youtube', 'v3', developerKey=api_key)

    all_videos = []
    found_video_ids = existing_videos.copy()

    for query in queries:
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )

            response = request.execute()

            for item in response['items']:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                if video_id not in found_video_ids and video_title not in (title for title, _ in all_videos):
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    videos.append((video_title, video_url))
                    found_video_ids.add(video_id)

                if len(videos) >= max_results:
                    break

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        all_videos.extend(videos)

    return all_videos, found_video_ids

def save_links_to_file(videos, filename='youtube_links.txt'):
    # Mengecek apakah file sudah ada dan membaca jumlah baris yang ada
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_lines = file.readlines()
        start_index = sum(1 for line in existing_lines if line.strip()) // 2 + 1
    else:
        start_index = 1

    # Menambahkan video baru dengan penomoran yang berlanjut
    with open(filename, 'a') as file:
        for index, (title, link) in enumerate(videos, start=start_index):
            file.write(f'{index}. {title}\n{link}\n\n')
    
    print(f'Links and titles saved to {filename}')

def load_existing_videos(filename='youtube_links.txt'):
    existing_videos = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('https://www.youtube.com/watch?v='):
                    video_id = line.split('=')[1].strip()
                    existing_videos.add(video_id)
    return existing_videos

if __name__ == '__main__':
    api_key = 'YOUR_YOUTUBE_API_KEY'  # Ganti dengan API key Anda
    queries = input('Masukkan keywords (pisahkan dengan koma): ').split(',')
    max_results = int(input('Masukkan jumlah maksimal hasil pencarian per keyword (maksimal 50): '))

    if max_results > 50:
        print('Jumlah maksimal hasil pencarian adalah 50. Menggunakan nilai maksimal 50.')
        max_results = 50

    queries = [query.strip() for query in queries]  # Menghilangkan spasi di sekitar keywords

    # Memuat video yang sudah ada dari file sebelumnya
    existing_videos = load_existing_videos()

    # Mengambil video baru yang berbeda dari yang sudah ada
    videos, new_existing_videos = get_youtube_links(api_key, queries, max_results, existing_videos)

    # Menyimpan hasil pencarian baru ke dalam file
    save_links_to_file(videos)

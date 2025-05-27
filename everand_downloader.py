import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime


"""
Everand Podcast Downloader – universelles Python-Skript für beliebige Everand-Podcast-Reihen

Dieses Skript lädt automatisch alle verfügbaren Folgen eines Podcasts von der Plattform Everand herunter,
sofern diese über die eingebetteten MP3-Links von ZEIT ONLINE bereitgestellt werden.

🔧 Funktionen:
- Durchsucht alle Seiten eines Everand-Podcasts (paginierte Listenansicht)
- Extrahiert:
    - die Detail-Links jeder Folge (/listen/podcast/<ID>)
    - das Veröffentlichungsdatum
    - den Titel
- Öffnet jede Detailseite, um den eingebetteten MP3-Link von ZEIT ONLINE zu extrahieren
- Lädt die MP3-Datei herunter
- Speichert die Datei zunächst mit der Original-ID im Dateinamen
- Merkt sich bereits heruntergeladene Episoden (downloaded_ids.txt)
- Sortiert am Ende alle neu geladenen Folgen nach Datum und benennt sie um zu:
    001_<Titel>.mp3, 002_<Titel>.mp3, ...

📁 Zielordner:
- Die Dateien werden im Unterordner "downloads_<Podcast-Name>" gespeichert

🧾 Verwendung:
1. Führe das Skript aus
2. Gib die Podcast-ID und den Slug aus der Everand-URL ein (Beispiel: 463298684 + Die-Erschaffung-der-Welt)
3. Der Download erfolgt automatisch für alle neuen Folgen

💡 Voraussetzungen:
- Python 3.x
- Pakete: requests, beautifulsoup4
  → Installieren mit: pip install requests beautifulsoup4

Autor: [Dein Name]
Stand: Mai 2025
"""


# Zielordner
DOWNLOAD_FOLDER = "downloads_zeit_verbrechen"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
DOWNLOADED_IDS_FILE = os.path.join(DOWNLOAD_FOLDER, "downloaded_ids.txt")

# Bereits heruntergeladene IDs einlesen
if os.path.exists(DOWNLOADED_IDS_FILE):
    with open(DOWNLOADED_IDS_FILE, "r") as f:
        downloaded_ids = set(line.strip() for line in f)
else:
    downloaded_ids = set()

def extract_episode_data_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    episodes = []

    for row in soup.select("tr._1nfXuX"):
        player_link_tag = row.select_one("a[href*='/listen/podcast/']")
        date_tag = row.select_one("td.CQO7ZI")
        title_tag = row.select_one("h3._1qKON5")
        if not (player_link_tag and date_tag and title_tag):
            continue
        href = player_link_tag['href']
        match = re.search(r'/listen/podcast/(\d+)', href)
        if not match:
            continue
        podcast_id = match.group(1)
        try:
            date = datetime.strptime(date_tag.text.strip(), '%b %d, %Y').date()
        except ValueError:
            continue
        episodes.append({
            'id': podcast_id,
            'link': href if href.startswith("http") else f"https://de.everand.com{href}",
            'date': date,
            'title': title_tag.text.strip()
        })
    return episodes

def extract_mp3_link_from_detail(html):
    match = re.search(r'https:\/\/zeitonline[^"]+\.mp3', html)
    return match.group(0) if match else None

def clean_title(title):
    title = title.replace('anhören', '').strip()
    title = re.sub(r'[^\w\s\-]', '', title)
    title = re.sub(r'\s+', '_', title)
    return title

def download_file(url, filename):
    try:
        response = requests.get(url, stream=True, timeout=15,verify=False)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ Downloadfehler bei {filename}: {e}")
        return False

# Alle Seiten durchsuchen
all_episodes = []
for page in range(1, 50):
    url = f"https://de.everand.com/podcast-show/463292094/Verbrechen?page={page}&sort=desc"
    try:
        print(f"🔎 Lade Seite {page}...")
        res = requests.get(url, timeout=10,verify=False)
        if not res.ok:
            break
        episodes = extract_episode_data_from_page(res.text)
        if not episodes:
            print("✅ Keine weiteren Folgen gefunden.")
            break
        all_episodes.extend(episodes)
    except Exception as e:
        print(f"❌ Fehler auf Seite {page}: {e}")
        break

# Nur neue Episoden
episodes_to_download = [ep for ep in all_episodes if ep['id'] not in downloaded_ids]
print(f"🔽 Neue Folgen gefunden: {len(episodes_to_download)}")

# MP3-Links laden und temporär speichern
downloads = []
for ep in sorted(episodes_to_download, key=lambda e: e['date']):
    print(f"⬇️ Lade Detailseite für {ep['id']} ...")
    try:
        res = requests.get(ep['link'], timeout=10,verify=False)
        if not res.ok:
            print("❌ Fehler beim Laden der Detailseite.")
            continue
        mp3_url = extract_mp3_link_from_detail(res.text)
        if not mp3_url:
            print("⚠️ Kein MP3-Link gefunden.")
            continue
        cleaned_title = clean_title(ep['title'])
        temp_filename = f"{ep['id']}_{cleaned_title}.mp3"
        filepath = os.path.join(DOWNLOAD_FOLDER, temp_filename)
        if download_file(mp3_url, filepath):
            downloads.append((ep['id'], ep['date'], cleaned_title, filepath))
            with open(DOWNLOADED_IDS_FILE, "a") as f:
                f.write(ep['id'] + "\n")
    except Exception as e:
        print(f"⚠️ Fehler bei Folge {ep['id']}: {e}")

# Nach Datum sortieren und final umbenennen
downloads.sort(key=lambda x: x[1])  # sort by date

for index, (_, _, title, filepath) in enumerate(downloads, start=1):
    final_name = f"{index:03d}_{title}.mp3"
    final_path = os.path.join(DOWNLOAD_FOLDER, final_name)
    os.rename(filepath, final_path)
    print(f"✅ Umbenannt: {final_name}")

import requests
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime



"""
Simplecast Podcast Downloader (RSS-Feed)

Dieses Python-Skript lädt automatisch alle Episoden eines Podcasts herunter,
die über einen standardkonformen RSS-Feed bereitgestellt werden (z. B. Simplecast, Podigee, etc.).

🔧 Was das Skript tut:
- Lädt und analysiert einen RSS-Feed im XML-Format (z. B. https://feeds.simplecast.com/b1Qn2k9W)
- Extrahiert aus jedem <item>:
    - Titel der Episode
    - Veröffentlichungsdatum (pubDate)
    - Direktlink zur MP3-Datei (aus <enclosure>)
    - Eindeutige ID (guid) zur Wiedererkennung
- Speichert jede MP3-Datei lokal im Ordner downloads_<PODCAST_NAME>
- Vergibt fortlaufende Dateinamen nach Veröffentlichungsdatum:
      001_Titel.mp3, 002_Titel.mp3, ...
- Merkt sich heruntergeladene Folgen dauerhaft in der Datei downloaded_ids.txt,
  um doppelte Downloads bei erneutem Ausführen zu vermeiden

🛠 Voraussetzungen:
- Python 3.x
- Module: requests, xml.etree.ElementTree (Standard), email.utils (Standard)

📁 Ergebnis:
- MP3-Dateien werden in einem individuellen Unterordner gespeichert
- Bereits heruntergeladene Episoden werden übersprungen

🔁 Ideal geeignet für automatische Podcast-Archivierung über RSS

Autor: [Dein Name]
Stand: Mai 2025
"""



# 🔧 Konfiguration
RSS_FEED_URL = "https://feeds.simplecast.com/b1Qn2k9W"
PODCAST_NAME = "Augen_Zu"
DOWNLOAD_FOLDER = f"downloads_{PODCAST_NAME}"
DOWNLOADED_FILE = os.path.join(DOWNLOAD_FOLDER, "downloaded_ids.txt")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 📄 Bereits geladene GUIDs einlesen
if os.path.exists(DOWNLOADED_FILE):
    with open(DOWNLOADED_FILE, "r") as f:
        downloaded_guids = set(line.strip() for line in f)
else:
    downloaded_guids = set()

def clean_title(title):
    title = re.sub(r'[^\w\s\-]', '', title)
    title = re.sub(r'\s+', '_', title.strip())
    return title

# 📥 RSS abrufen und parsen
resp = requests.get(RSS_FEED_URL,verify=False)
root = ET.fromstring(resp.content)

# 🔍 Alle Episoden sammeln
episodes = []
for item in root.findall(".//item"):
    title = item.findtext("title")
    pubDate = item.findtext("pubDate")
    enclosure = item.find("enclosure")
    guid = item.findtext("guid") or (enclosure.attrib.get("url") if enclosure is not None else None)

    if enclosure is None or "url" not in enclosure.attrib or not title or not pubDate:
        continue

    if guid in downloaded_guids:
        continue

    mp3_url = enclosure.attrib["url"]
    date_obj = parsedate_to_datetime(pubDate)

    episodes.append({
        "guid": guid,
        "title": title,
        "date": date_obj,
        "mp3_url": mp3_url
    })


# Nach Datum sortieren
episodes.sort(key=lambda x: x["date"])

# 🔽 Dateien herunterladen
for idx, ep in enumerate(episodes, start=1 + len(downloaded_guids)):
    safe_title = clean_title(ep["title"])
    filename = f"{idx:03d}_{safe_title}.mp3"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    print(f"⬇️ Lade {filename} ...")

    try:
        res = requests.get(ep["mp3_url"], stream=True, timeout=15,verify=False)
        res.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in res.iter_content(8192):
                f.write(chunk)
        print(f"✅ Gespeichert: {filename}")
        with open(DOWNLOADED_FILE, "a") as f:
            f.write(ep["guid"] + "\n")
    except Exception as e:
        print(f"❌ Fehler bei {ep['title']}: {e}")

🎧 Podcast Downloader für Everand & RSS (Simplecast)
Dieses Repository enthält zwei leistungsfähige Python-Skripte zum automatisierten Herunterladen kompletter Podcast-Reihen:

📥 1. everand_downloader.py
Ein spezialisiertes Skript zum Herunterladen aller Folgen eines Podcasts von der Plattform Everand (ehemals Scribd).

🔧 Funktionen:
Ruft alle paginierten Podcast-Seiten von Everand ab

Extrahiert aus jeder Folge:

Titel

Veröffentlichungsdatum

interne Podcast-ID

den echten MP3-Link von ZEIT ONLINE

Lädt neue Folgen herunter und speichert sie im Unterordner downloads_<Podcast-Name>

Benennt Dateien chronologisch um: 001_<Titel>.mp3, 002_<Titel>.mp3 usw.

Erkennt bereits heruntergeladene Episoden durch downloaded_ids.txt

🧪 Verwendung:
Führe das Skript aus

Gib bei Aufforderung die Podcast-ID und den URL-Slug ein (aus Everand-URL entnehmbar)

Das Skript lädt alle verfügbaren Folgen herunter und speichert sie lokal

🔁 2. simplecast_downloader.py
Ein universeller RSS-Podcast-Downloader – ideal für alle Feeds im Format RSS 2.0, z. B. von Simplecast, Podigee, Anchor, etc.

🔧 Funktionen:
Liest RSS-Feed und extrahiert:

Titel

Veröffentlichungsdatum

MP3-Link (<enclosure url=...>)

Lädt alle MP3-Dateien herunter in downloads_<PODCAST_NAME>

Benennt Folgen automatisch durch: 001_<Titel>.mp3, 002_<Titel>.mp3 …

Erkennt bereits heruntergeladene Episoden durch downloaded_ids.txt

🧪 Verwendung:
Passe RSS_FEED_URL im Skript an deinen gewünschten Feed an

Führe das Skript aus – es lädt nur neue Folgen herunter


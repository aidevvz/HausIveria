# Ratgeber: Artikel anlegen

Jeder Artikel ist **eine Markdown-Datei** in diesem Ordner. Beim Push auf `main` baut Netlify die Website neu
und der Artikel ist nach ca. 1–2 Minuten live unter `https://iveria.at/ratgeber/<dateiname>.html`.

Übersicht, Navigation („Ratgeber“ erscheint automatisch ab dem ersten Artikel), Sitemap, RSS-Feed,
llms.txt, Schema (BlogPosting, BreadcrumbList, FAQPage), Open Graph und „Weiterlesen“ werden automatisch erzeugt.
Nichts davon von Hand anfassen.

## Dateiname = URL

- nur `a-z`, `0-9` und `-`, keine Umlaute: `ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`
- kurz und mit dem Hauptsuchbegriff: `maklerprovision-oesterreich.md`, nicht `artikel-3.md`
- **Nach dem Veröffentlichen nie umbenennen** (die URL ändert sich sonst und Rankings gehen verloren)

## Aufbau

Vorlage: [`_vorlage.md`](_vorlage.md) (Dateien mit `_` am Anfang werden ignoriert).

```markdown
---
title: "Maklerprovision in Österreich: Wer zahlt was?"
seo_title: "Maklerprovision Österreich: Wer zahlt?"   # optional, max. 60 Zeichen
description: "Wie hoch ist die Maklerprovision beim Kauf, Verkauf und bei Miete in Österreich? Höchstsätze, Bestellerprinzip und Beispiele."
date: 2026-11-05
updated: 2026-11-20          # optional, nur bei inhaltlicher Überarbeitung
category: Recht & Steuern
image: /Images/ratgeber/maklerprovision-oesterreich.webp     # optional, empfohlen
image_alt: "Beschreibung dessen, was auf dem Bild zu sehen ist"
cta: verkaufen               # verkaufen | bewertung | kaufen | bautraeger | kontakt (Standard: kontakt)
related: [immobilie-verkaufen-unterlagen]   # optional, Dateinamen ohne .md
faq:                         # optional, wird sichtbar am Artikelende angezeigt + FAQPage-Schema
  - q: "Wer zahlt die Maklerprovision bei einer Mietwohnung?"
    a: "Seit 1. Juli 2023 gilt das Bestellerprinzip: ..."
draft: false                 # true = wird nicht veröffentlicht
---
Einleitung (2–4 Sätze, Hauptsuchbegriff kommt vor) ...

## Erste Zwischenüberschrift
...
```

### Pflichtfelder und Regeln (der Build prüft sie)

| Feld | Regel |
|---|---|
| `title` | Pflicht. Ist die H1. Über 60 Zeichen nur mit `seo_title` (max. 60) |
| `description` | Pflicht, 70–160 Zeichen, für jeden Artikel einzigartig |
| `date` | Pflicht, `JJJJ-MM-TT`. Liegt es in der Zukunft, erscheint der Artikel erst beim ersten Build ab diesem Tag |
| `category` | Pflicht. Bitte einheitlich: `Verkaufen`, `Kaufen`, `Vermieten`, `Bewertung`, `Bauträger`, `Recht & Steuern`, `Markt Wien` |
| `image` | optional, muss unter `/Images/ratgeber/` liegen, dann ist `image_alt` Pflicht |
| Text | **keine H1** (`#`). Mit `##` gliedern, `###` für Unterpunkte. Ab 3 `##` entsteht automatisch ein Inhaltsverzeichnis |
| Bilder im Text | `![Alternativtext](/Images/ratgeber/datei.webp)`, Alternativtext ist Pflicht |

Unbekannte Felder, fehlende Bilder oder Formfehler **brechen den Build ab**. Dann bleibt die bisherige Version
online und Netlify zeigt die Fehlerliste im Deploy-Log. Vor dem Push lokal prüfen:

```bash
pip install -r requirements.txt
python3 _build/build.py /tmp/iveria-check   # baut in einen Testordner, Exit-Code 1 + Fehlerliste bei Problemen
```

## Bilder

- Ablage: `Images/ratgeber/<dateiname-des-artikels>.webp` (weitere: `...-2.webp` usw.)
- Format WebP, Titelbild mindestens 1200 px breit (für Google Discover und Social-Vorschau), Seitenverhältnis 16:10
- Dateigröße möglichst unter 250 KB
- Nur Bilder mit geklärten Rechten (eigene Fotos, lizenzierte Stockfotos, KI-generiert). Keine Bilder von fremden Websites

## Inhaltliche Regeln

- Sprache: Österreichisches Deutsch (de-AT), Leser mit **„Sie“** ansprechen. „Jänner“, „heuer“ wo es natürlich passt
- **Keine erfundenen Fakten, Zahlen, Fälle oder Kundenstimmen.** Gesetzliche und steuerliche Angaben (Prozentsätze, Fristen,
  Gesetzesstellen) nur mit aktueller Quelle (RIS, oesterreich.gv.at, BMF, WKO) und Quelle im Text verlinken
- Keine Personennamen, Telefonnummern, Adressen oder Kennzahlen von Iveria erfinden, die nicht auf der Website stehen
- Ein Hauptsuchbegriff pro Artikel: im `title`, in der Einleitung, in mindestens einer `##`-Überschrift. Kein Keyword-Stuffing
- Zwei Artikel dürfen nicht dasselbe Suchthema bedienen (sonst konkurrieren sie gegeneinander). Bestehendes lieber mit `updated` überarbeiten
- Mindestens 2 interne Links: auf eine passende Leistungsseite (`/verkaufen.html`, `/bewertung.html`, `/kaufen.html`,
  `/bautraeger.html`, `/kontakt.html`) und auf einen anderen Ratgeber-Artikel (`/ratgeber/<dateiname>.html`)
- `faq` nur mit Fragen, die zum Artikel gehören. Antworten kurz (1–3 Sätze), dürfen nichts enthalten, was dem Text widerspricht
- Länge nach Thema: lieber vollständig und präzise als lang. Typisch 900–1.800 Wörter

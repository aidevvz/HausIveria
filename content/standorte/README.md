# Standortseiten (Ortsseiten und Hubs)

Eine Markdown-Datei pro Seite. Beim Push auf `main` baut Netlify die Website neu.
Ausgabe im Root: `content/standorte/immobilienmakler-moedling.md` → `https://iveria.at/immobilienmakler-moedling.html`.

Automatisch erzeugt (nicht von Hand anfassen): Inhaltsverzeichnis, Preistabelle, Listen für Objektarten und Lagen,
FAQ-Block, Bewertungs-Aufruf, „Weiterlesen“, Schema (RealEstateAgent mit `areaServed`, Service, FAQPage, BreadcrumbList,
bei Hubs ItemList), Sitemap, llms.txt, Menüpunkt „Standorte“ und Footer-Spalte „Standorte“.

## Status: Entwurf, noindex, live

| `draft` | `noindex` | Ergebnis |
|---|---|---|
| `true` | egal | wird **nicht** gebaut, nicht erreichbar |
| `false` | `true` | gebaut und per URL erreichbar, aber `noindex`, nicht in Sitemap, Menü, Footer, Hub-Listen |
| `false` | `false` | **live**: indexierbar, in Sitemap, llms.txt, Menü, Footer und Hub-Liste |

**Vor der Gewerbeanmeldung bleiben alle Standortseiten auf `draft: true` und `noindex: true`.**
Freigeschaltet wird nur auf ausdrückliches Signal von Gio.

Entwürfe ansehen (lokal, nie in den Repo-Ordner bauen):

```bash
pip install -r requirements.txt
cp -r . /tmp/vorschau && ENTWUERFE=1 python3 _build/build.py /tmp/vorschau
cd /tmp/vorschau && python3 -m http.server 8000     # http://localhost:8000/immobilienmakler-moedling.html
```

In der Vorschau zeigen Entwürfe oben ein Schild „Entwurf · nicht veröffentlicht“ und erscheinen in Menü, Footer und Hub-Listen.

## Dateiname = URL

`immobilienmakler-<ort>.md`, nur `a-z`, `0-9`, `-`, keine Umlaute (`ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`).
Beispiele: `immobilienmakler-wiener-neustadt.md`, `immobilienmakler-st-poelten.md`.
**Nach dem Veröffentlichen nie umbenennen oder löschen.**

## Ortsseite (`typ: ortsseite`)

```yaml
---
typ: ortsseite
ort: "Mödling"                    # Pflicht, Anzeigename
region: "Niederösterreich"        # Pflicht
plz: ["2340"]                     # vierstellig, eine oder mehrere
title: "Immobilienmakler in Mödling: verkaufen und bewerten"   # Pflicht, ist die H1
seo_title: "Immobilienmakler Mödling · Iveria Immobilien"      # Pflicht wenn title > 60 Zeichen, max. 60
description: "..."                # Pflicht, 70–160 Zeichen, wird auch als Einleitung unter der H1 gezeigt
hub: "immobilienmakler-niederoesterreich"   # Pflicht, Dateiname der Hub-Seite ohne .md
preis_wohnung_min: 4200           # €/m², ganze Zahl, nur gemeinsam mit _max
preis_wohnung_max: 5800
preis_haus_min: null
preis_haus_max: null
preis_haus_einheit: "m2"          # "m2" = pro m², "gesamt" = Gesamtpreis
preis_stand: "2026-Q4"            # Pflicht, sobald Preise gesetzt sind
preis_quelle: "Iveria-Markteinschätzung"   # Pflicht, sobald Preise gesetzt sind
lagen: ["...", "..."]             # gefragte Lagen/Grätzl
objektarten: ["...", "..."]       # typische Objektarten
image: /Images/standorte/immobilienmakler-moedling.webp
image_alt: "..."
faq:                              # 3 bis 6 Fragen, sichtbar + FAQPage-Schema
  - q: "..."
    a: "..."
related: [immobilienmakler-baden, immobilienertragsteuer-oesterreich]   # Standort- oder Ratgeber-Dateinamen
draft: true
noindex: true
---
```

Leere Preis-, Lagen- oder Objektarten-Felder blenden den jeweiligen Block einfach aus. **Zahlen, Lagen und Objektarten
nur aus echten Quellen eintragen, nie schätzen oder erfinden.**

### Pflicht-Gerüst im Text (der Build prüft Wortlaut und Reihenfolge)

```markdown
Einleitung (2–4 Sätze, Ortsbezug) ...

## Was kostet ein Immobilienmakler in Mödling?

Antwort in 1–2 Sätzen (erster Absatz, wird als Featured-Snippet-Kandidat genutzt).

Vertiefung ... [Maklerprovision in Österreich](/ratgeber/maklerprovision-oesterreich.html)

## Was ist meine Immobilie in Mödling wert?

Antwort in 1–2 Sätzen. ← hier fügt der Build die Preistabelle ein

Vertiefung ... [Bewertung anfragen](/bewertung.html)

## Wie ist der Immobilienmarkt in Mödling?

Antwort in 1–2 Sätzen. ← hier fügt der Build Objektarten und Lagen ein

## Wie läuft der Verkauf in Mödling ab?

Antwort in 1–2 Sätzen. ... [Immobilie verkaufen](/verkaufen.html)

## Welche Steuern fallen beim Verkauf an?

Antwort in 1–2 Sätzen. ... [Immobilienertragsteuer](/ratgeber/immobilienertragsteuer-oesterreich.html)
```

- Die ersten fünf `##` müssen genau so lauten (mit dem `ort` aus dem Front-Matter). Weitere `##` danach sind erlaubt.
- Unter jeder dieser `##` muss zuerst ein Absatz stehen (keine Liste, Tabelle oder Überschrift).
- Pflicht-Links im Text: `/verkaufen.html`, `/bewertung.html`, `/ratgeber/maklerprovision-oesterreich.html`,
  `/ratgeber/immobilienertragsteuer-oesterreich.html`. Der Link zum Hub kommt automatisch.
  Links auf noch nicht veröffentlichte Ratgeber oder Standortseiten werden vorerst als normaler Text ausgegeben (keine toten Links).
- Keine H1 (`#`) im Text.

## Hub (`typ: hub`)

```yaml
---
typ: hub
name: "Niederösterreich"          # Pflicht, kurzer Name für Breadcrumb, Menü, Footer
region: "Niederösterreich"
title: "Immobilienmakler in Niederösterreich"
seo_title: "..."
description: "..."
faq: [...]                        # 3 bis 6
seiten: [immobilienmakler-moedling]   # optional: zusätzliche Ortsseiten, die nicht diesen Hub als `hub` haben
draft: true
noindex: true
---
```

**Menü und Footer-Spalte „Standorte“:** genau die Primär-Regionen Wien und Niederösterreich (`ST_PRIMAER_REGIONEN` in `_build/standorte.py`), in dieser Reihenfolge, sobald die jeweilige Seite live ist. Keine weiteren Hubs, keine Ortsseiten. Die Felder `menu` (Hub) und `footer` (Ortsseite) haben keine Wirkung mehr.
**Sitemap:** alle Live-Seiten, unabhängig von Menü und Footer.

Alle Ortsseiten mit `hub: <dieser Hub>` werden automatisch oben als Liste verlinkt (ItemList-Schema).
Kleine Orte ohne eigene Seite (z. B. Perchtoldsdorf, Brunn am Gebirge) bekommen im Hub-Text eine eigene `##`-Überschrift
mit eigenem Absatz, keine eigene URL. Eine Ortsseite kann erst live gehen, wenn ihr Hub live ist.

## Prüfungen, die den Build abbrechen

- Pflichtfelder, Längen (`seo_title` ≤ 60, `description` 70–160), unbekannte Felder, Dateiname
- Titelbild unter `/Images/standorte/` mit `image_alt` (Empfehlung: WebP, ≥ 1200 px breit, 16:10, < 250 KB)
- H2-Gerüst und Kurzantworten (Ortsseiten)
- Preise ohne `preis_stand`/`preis_quelle`, `min` > `max`
- **Doorway-Schutz:** Fließtext zweier Standortseiten mehr als 70 % gleich (Ortsnamen, PLZ und Überschriften werden dabei ignoriert)
- Bei `draft: false`: `[PLATZHALTER`-Texte, fehlende Pflicht-Links, weniger als 3 oder mehr als 6 FAQ, Hub nicht live

Prüfen vor dem Push: `python3 _build/build.py /tmp/iveria-check` (Exit-Code 0).

## Inhalt

- Österreichisches Deutsch, Sie-Form, echter Ortsbezug (Lage, Anbindung, Käufergruppen, Bebauung). Kein Text, in dem nur der Ortsname getauscht ist
- Keine Ortsadresse, keine zweite Adresse: Iveria hat genau ein Büro in Wien. Nichts erfinden (Zahlen, Lagen, Referenzen, Kundenstimmen)

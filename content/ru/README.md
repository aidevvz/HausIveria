# Sprachversionen (EN unter /en/, RU unter /ru/)

Deutsch bleibt Standard und wird nicht angefasst. Übersetzte Seiten liegen als Markdown in `content/en/` und `content/ru/`.
Beim Push auf `main` baut Netlify alles neu. Regeln gelten für beide Sprachordner.

## Dateiname = URL

| Datei | URL |
|---|---|
| `content/en/index.md` | `https://iveria.at/en/` |
| `content/en/sell.md` | `https://iveria.at/en/sell.html` |
| `content/en/<guide-slug>.md` mit `typ: guide` | `https://iveria.at/en/guide/<guide-slug>.html` |

Kernseiten v1: `index`, `buy`, `sell`, `valuation`, `contact` (EN und RU), dazu EN-Guide `buying-property-in-vienna-as-a-foreigner`.
Nur `a-z`, `0-9`, `-`. **Nach Veröffentlichung nie umbenennen.**

## Seite (`typ: seite`)

```yaml
---
typ: seite
pendant: verkaufen.html          # deutsche Entsprechung (index.html, kaufen.html, verkaufen.html, bewertung.html, kontakt.html, ratgeber/<slug>.html …)
title: "Sell property"           # H1-Text (falls h1 leer) und Basis für den Seitentitel
seo_title: "Sell property in Vienna · Iveria Immobilien"   # max. 60 Zeichen
description: "…"                 # 70–160 Zeichen, auch Einleitung im Kopf (wenn lead leer)
eyebrow: "For owners"            # kleine Zeile über der H1
h1: "Sell your property with <em>care</em>."   # optional, <em> = bronze Kursiv
lead: ""                         # optional, Text unter der H1
hero_image: /Images/hero-verkaufen.webp   # optional: mit Bild = Bogen-Hero wie auf den deutschen Seiten
hero_alt: "…"
service: true                    # Service-Schema (für Leistungsseiten)
kontaktblock: false              # true = E-Mail, Erreichbarkeit, Adresse aus site.json unter dem Text
faq: [{q: "…", a: "…"}]          # sichtbar + FAQPage-Schema
draft: true                      # true = nicht gebaut
noindex: false
---
Text mit ## Zwischenüberschriften (keine #).
```

## Guide (`typ: guide`)

Felder wie im deutschen Ratgeber: `title`, `seo_title`, `description`, `date`, `updated`, `category`, `image` (unter `/Images/`), `image_alt`, `faq`,
optional `pendant: ratgeber/<slug>.html`, wenn es einen deutschen Artikel zum selben Thema gibt.

## Was automatisch passiert

- `<html lang>`, Canonical auf die eigene Sprach-URL, `og:locale`
- **hreflang:** reziprok zwischen allen **live** Sprachversionen mit gleichem `pendant` (+ `x-default` = Deutsch). Ohne Übersetzung kein hreflang
- Sitemap mit allen Sprachversionen und `xhtml:link`-Alternates
- **Sprachumschalter** DE/EN/RU im Kopf (erscheint, sobald eine EN- oder RU-Seite live ist): führt auf das Pendant, sonst auf die Startseite der Sprache
- Menü, Footer, Buttons, Cookie-Hinweis, FAQ-Überschrift in der Seitensprache aus `_build/i18n/strings.<lang>.json`
- Menüpunkte erscheinen nur für Seiten, die es in der Sprache gibt
- Schema: dieselbe Organisation (`@id`) wie auf Deutsch, dazu WebPage mit `inLanguage`, Service, FAQPage, BreadcrumbList in der Sprache
- Keine automatische Weiterleitung nach Browsersprache

## UI-Texte

`_build/i18n/strings.en.json` und `strings.ru.json`. Derzeit Entwürfe, bitte prüfen und ersetzen. Schlüssel nicht umbenennen;
`nav` ist die Menüreihenfolge (`[Datei, Beschriftung]`).

## Prüfen und Vorschau

```bash
python3 _build/build.py /tmp/check                              # Exit-Code 0 = alles in Ordnung
cp -r . /tmp/vorschau && ENTWUERFE=1 python3 _build/build.py /tmp/vorschau   # Entwürfe ansehen
```

Der Build bricht ab bei: fehlenden Pflichtfeldern, Längen, unbekannten Feldern, `pendant` ohne deutsche Live-Seite,
doppeltem `pendant` in einer Sprache, fehlenden Bildern/Alt-Texten, `#` im Text, `[PLATZHALTER` bei `draft: false`.

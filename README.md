# Haus Iveria — Website (v2, Sotheby-Style)

Static website (Plain HTML/CSS/JS, no build step). Hosting: GitHub + Netlify.

**Stil:** Editorial-Layout im Sotheby's-International-Realty-Stil. Off-White Hintergrund, schlanke Typografie, viel Whitespace, große hochwertige Fotos, abwechselnde Editorial-Sections.

**Brand-Farben:** Ink #161513, Paper #FAFAF7, Bronze #B08D57 als Akzent.
**Typografie:** Cormorant Garamond (display, light 300) + Inter (body, light 300).

---

## Datei-Übersicht

| Datei | Zweck |
|---|---|
| `index.html` | Startseite mit Foto-Hero |
| `verkaufen.html` | Für Eigentümer: 5-Schritte-Prozess, 6 Leistungen, Provision-CTA, FAQ |
| `kaufen.html` | Filter + 6 Objekte mit Fotos, Suchauftrag-Formular |
| `bautraeger.html` | Stats, Leistungen, 3 Referenzprojekte, CTA |
| `ueber-uns.html` | Prose-Story, Werte, Stats, Qualifikation |
| `bewertung.html` | Zwei Varianten, Schnellbewertungs-Formular |
| `kontakt.html` | Kontakt-Blocks + Hauptformular |
| `impressum.html` | § 25 MedienG / § 5 ECG |
| `datenschutz.html` | DSGVO-konform |
| `danke.html` | Form-Bestätigung |
| `404.html` | Fehlerseite |
| `netlify.toml`, `robots.txt`, `sitemap.xml` | Konfiguration |

---

## Wichtig: Bilder

Aktuell sind **Unsplash-Platzhalter-Bilder** verwendet. Sie werden direkt von Unsplash geladen — kein Download nötig, alles funktioniert sofort. **Aber:**

1. Die Bilder sind **frei nutzbar** unter der Unsplash-Lizenz, also rechtlich sicher
2. Du solltest sie aber **so schnell wie möglich durch eigene Fotos** ersetzen — sobald du Objekte vermarktest

**Wie eigene Bilder einsetzen:** In jeder `.html` finden sich URLs wie:
```
url('https://images.unsplash.com/photo-XXXXXX?w=...')
```
Diese durch eigene Bild-URLs ersetzen, z.B.:
```
url('images/altbauwohnung-stadtpark.jpg')
```
Und die Bilder in einen `images/`-Unterordner legen.

---

## Vor dem Deploy: Platzhalter ersetzen

Suchen Sie in allen `.html`-Dateien:

- `+43 (0)1 …` → echte Telefonnummer
- `https://wa.me/43` → echte WhatsApp-Nummer (Format: `https://wa.me/43XXXXXXXXX`)
- In `impressum.html`: `[Firmenwortlaut]`, `[Vorname Nachname]`, `[Straße Hausnummer]`, `[PLZ Ort]`, `[FN]`, `[ATU]`, `[Behörde]`, `[zuständiges Gericht]`, `[Versicherungsgesellschaft]`
- In `datenschutz.html`: `[Firmenwortlaut]`, `[Straße Hausnummer]`, `[PLZ Ort]`, `[Datum]`
- In `kontakt.html`: `[Straße Hausnummer]`, `[PLZ]`

---

## Deploy

1. **GitHub**: Neues Repo anlegen, alle Dateien hochladen
2. **Netlify**: Import existing project → Repo wählen → Publish directory: `.`
3. **Forms**: Werden beim ersten Deploy automatisch erkannt. Im Netlify-Dashboard unter "Forms" → E-Mail-Notification einrichten
4. **Domain**: `hausiveria.at` registrieren, in Netlify unter "Domain settings" hinzufügen, DNS-Einträge übernehmen

---

## Brand Reference

| | Hex | Verwendung |
|---|---|---|
| Ink | `#161513` | Haupttext, Footer, dunkle Sections |
| Ink-Soft | `#2A2825` | Sekundärer Text |
| Ink-Mute | `#6F6B65` | Tertiärer Text, Eyebrows |
| Paper | `#FAFAF7` | Body-Hintergrund |
| Paper-Warm | `#F2EFE9` | Section-Variation |
| Bronze | `#B08D57` | Akzente (em-Tags, Trennstriche, Logo-Linie) |
| Bronze-Soft | `#C9A674` | Bronze auf dunklem Hintergrund |

**Tagline:** „Wo aus vier Wänden Zuhause wird."

---

## Was technisch passiert

- **Intro-Animation** läuft beim Laden jeder Seite (~5 Sekunden). Bogen wird gezeichnet, dann Schriftzug, dann Fade zur Seite.
- **Header** ist auf der Startseite **transparent** über dem Hero-Foto, wird auf anderen Seiten direkt als feste Leiste angezeigt.
- **Cookie-Banner** erscheint nach ca. 6,5 Sekunden (nach Intro), nur beim ersten Besuch.
- **WhatsApp-Button** ist auf jeder Seite fest unten rechts.
- **Aktive Navigation** wird automatisch erkannt (Bronze-Unterstrich unter dem aktuellen Menüpunkt).

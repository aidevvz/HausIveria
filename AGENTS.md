# iveria.at – Hinweise für Agents

Statische Website von Iveria Immobilien e.U. (Immobilienmakler, Wien). Hosting: Netlify, Repo `aidevvz/HausIveria`, Branch `main`.
Jeder Push auf `main` löst auf Netlify `python3 _build/build.py` aus und geht automatisch live.

## Ratgeber-Artikel veröffentlichen (SEO-Agent)

**Aktueller SEO-Stand, offene Punkte und Prioritäten: [`docs/seo-briefing.md`](docs/seo-briefing.md).**

**Alle Regeln, Felder und Prüfungen: [`content/ratgeber/README.md`](content/ratgeber/README.md). Vor dem ersten Artikel lesen.**

Ablauf:

1. Artikel als `content/ratgeber/<url-slug>.md` anlegen (Vorlage: `content/ratgeber/_vorlage.md`)
2. Bilder nach `Images/ratgeber/` legen
3. Prüfen: `pip install -r requirements.txt && python3 _build/build.py /tmp/iveria-check` (muss mit Exit-Code 0 enden)
4. Nur diese Dateien committen und auf `main` pushen. Commit-Nachricht: `Ratgeber: <Titel>`
5. Nach ca. 2 Minuten prüfen, dass `https://iveria.at/ratgeber/<url-slug>.html` mit Status 200 antwortet

Ohne lokale Umgebung geht es auch über die GitHub-API (Datei anlegen = Commit auf `main`); Schritt 3 übernimmt dann Netlify.
Bei einem Fehler bleibt die alte Version online, die Fehlerliste steht im Netlify-Deploy-Log.

Für eine Freigabe vor Veröffentlichung: Branch + Pull Request statt Push auf `main`. Netlify erstellt eine Vorschau-URL (Deploy Preview).

## Standortseiten (Ortsseiten und Hubs)

**Regeln: [`content/standorte/README.md`](content/standorte/README.md).** Gleiche Mechanik wie der Ratgeber, eigene Prüfungen
(H2-Gerüst, Pflicht-Links, Doorway-Schutz). Bis zur Freigabe durch Gio bleiben alle Standortseiten auf `draft: true` und `noindex: true`.
Marktzahlen, Lagen und Objektarten nur von Gio bzw. aus angegebener Quelle, nie selbst befüllen.

## Nicht anfassen

- Die generierten `*.html` (auch `immobilienmakler-*.html`), `ratgeber/`, `sitemap.xml`, `llms.txt` (werden bei jedem Build überschrieben)
- `_build/`, `assets/`, `_build/site.json` (Firmendaten), `netlify.toml`, `_redirects`
- Bestehende Artikel nicht umbenennen oder löschen (URL ginge verloren). Überarbeiten: Text ändern und `updated` setzen

## Fakten

Autor der Artikel ist zentral `ratgeber_autor` in `_build/site.json` (Giorgi Gorgodze, MA), das Feld `author` im Artikel nur bei Gastautoren setzen.

Firmendaten (Name, E-Mail, Einzugsgebiet Wien, Niederösterreich, Burgenland, Kärnten, Öffnungszeiten) stehen in `_build/site.json`.
Nichts erfinden, was dort oder auf der Website nicht steht: keine Adresse, Telefonnummer, Personennamen, Verkaufszahlen, Referenzen oder Kundenstimmen.

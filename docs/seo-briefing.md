# SEO-Briefing iveria.at

Stand: 1. November 2026 · für den SEO-Agent von Iveria Immobilien

## 1. Ausgangslage

- **Unternehmen:** Iveria Immobilien e.U., Immobilienmakler. Ein Büro in **1120 Wien** (Grenze zu 1230 Liesing). Straße ist noch offen.
- **Leistungen:** Verkauf, Vermietung, Bauträgervermarktung und Bewertung.
- **Einzugsgebiet laut Website:** Wien, Niederösterreich, Burgenland, Kärnten. Der lokale Schwerpunkt für neue Inhalte ist Wien Süd und Niederösterreich Süd.
- **Sprache und Markt:** Deutsch (de-AT), Österreich. Leser in der Sie-Form ansprechen.
- **Status:** Die Gewerbeanmeldung und das Google-Unternehmensprofil sind noch ausständig. Deshalb bleiben alle Standortseiten Entwürfe (siehe Abschnitt 5).
- **Rankings:** Google Österreich zeigte am 27.10.2026 noch kein Ranking. Die Sitemap wurde erst am 30.10.2026 eingereicht, Ergebnisse brauchen Wochen.

## 2. Technik

| Bereich | Stand |
|---|---|
| Repo | `aidevvz/HausIveria`, Branch `main` |
| Hosting | Netlify. Jeder Push auf `main` löst `python3 _build/build.py` aus und geht nach 1–2 Minuten live |
| Build-Kontrolle | Jede live gebaute Seite endet mit `<!-- build <commit> -->`. So lässt sich prüfen, ob ein Commit live ist |
| Fehlerfall | Bricht der Build ab, bleibt die letzte Version online. Die Fehlerliste steht im Netlify-Deploy-Log |
| Lokaler Test | `pip install -r requirements.txt && python3 _build/build.py /tmp/check` muss mit Exit-Code 0 enden |
| Firmendaten (NAP) | Nur in `_build/site.json`. Footer, Kontakt, Impressum und Schema lesen von dort |
| Anleitungen | `AGENTS.md`, `content/ratgeber/README.md`, `content/standorte/README.md` |

## 3. Seiten und Titles

| URL | Title | Schema |
|---|---|---|
| `/` | Iveria Immobilien · Immobilienmakler in Wien | RealEstateAgent, WebSite, FAQPage |
| `/verkaufen.html` | Immobilie verkaufen in Wien mit Makler · Iveria Immobilien | Service, FAQPage, Breadcrumb |
| `/kaufen.html` | Immobilie kaufen & Suchauftrag · Iveria Immobilien | Breadcrumb |
| `/bautraeger.html` | Bauträgervermarktung Wien & Österreich · Iveria Immobilien | Service, Breadcrumb |
| `/bewertung.html` | Immobilienbewertung Wien, online kostenlos · Iveria Immobilien | Service mit Preis 290–490 €, Breadcrumb |
| `/ueber-uns.html` | Über uns · Iveria Immobilien, Makler in Wien | Breadcrumb |
| `/kontakt.html` | Kontakt & Erstgespräch · Iveria Immobilien Wien | Breadcrumb |
| `/ratgeber/` | Immobilien-Ratgeber Wien · Iveria Immobilien | Blog, Breadcrumb |
| `/ratgeber/immobilienertragsteuer-oesterreich.html` | Immobilienertragsteuer Österreich: Wer zahlt wie viel? | BlogPosting, FAQPage, Breadcrumb |
| `/impressum.html`, `/datenschutz.html` | … · Iveria Immobilien | Breadcrumb |

Auf allen Seiten gilt außerdem:
- **RealEstateAgent** (`https://iveria.at/#organization`) ist sitewide eingebunden.
- **Head:** `lang="de-AT"`, selbstreferenzierender Canonical (URLs mit `.html`), Open Graph und Twitter Card, Favicons.
- **Danke- und 404-Seite** stehen auf `noindex`.

## 4. Was schon erledigt ist

- **Strukturierte Daten:** wie in der Tabelle oben. Jede Angabe im Schema steht sichtbar auf der Seite, FAQ-Schema nur mit wörtlich sichtbaren Fragen.
- **Sitemap:** `sitemap.xml` wird automatisch erzeugt, mit `lastmod` je Seite.
  - Bei normalen Seiten ist `lastmod` das Datum der letzten inhaltlichen Änderung.
  - Bei Artikeln ist es `updated`, sonst `date`.
- **Weitere Dateien:**
  - `robots.txt`: erlaubt alles und verweist auf die Sitemap
  - `llms.txt`: automatisch, mit Leistungen und Ratgeber-Artikeln
  - RSS-Feed des Ratgebers: `/ratgeber/feed.xml`
- **Google Search Console:** Domain-Property `iveria.at` ist bestätigt.
  - Sitemap am 30.10.2026 eingereicht, Status „Erfolgreich“, 9 Seiten.
  - Indexierung beantragt für `/`, `/verkaufen.html`, `/bautraeger.html`, `/bewertung.html` und `/kaufen.html`.
- **Bing Webmaster Tools:** per Meta-Tag bestätigt (Code in `site.json`, nicht entfernen). Sitemap am 01.11.2026 eingereicht. Bing beliefert auch DuckDuckGo, Ecosia und Yahoo.
- **Gemini und KI-Übersichten:** Sie nutzen den Google-Index. Es gibt nichts separat einzureichen.
- **Lighthouse:** SEO 100, Accessibility 95–96. Der verbleibende Kontrastmangel ist der bronzene Kursivtext, eine bewusste Designentscheidung.

## 5. Content-Systeme

### Ratgeber (`content/ratgeber/*.md` → `/ratgeber/<slug>.html`)

- **Live:** 1 Artikel, `immobilienertragsteuer-oesterreich` (Recht & Steuern, 01.11.2026).
- **Autor:** Zentral „Giorgi Gorgodze, MA“ (Schema: Person mit `worksFor` Iveria). Das Feld `author` nur bei Gastautoren setzen.
- **Regeln, die der Build prüft:**
  - `title` ist die H1. Bei mehr als 60 Zeichen braucht es `seo_title` mit höchstens 60.
  - `description` 70–160 Zeichen.
  - Keine `#` im Text.
  - Bilder unter `/Images/ratgeber/`, mit Alternativtext.
  - Keine unbekannten Felder.
- **Inhaltliche Regeln:**
  - Mindestens 2 interne Links: einer auf eine Leistungsseite, einer auf einen anderen Artikel.
  - Gesetzliche und steuerliche Zahlen nur mit aktueller, verlinkter Quelle (RIS, BMF, oesterreich.gv.at, WKO).
- **Kategorien einheitlich:** Verkaufen, Kaufen, Vermieten, Bewertung, Bauträger, Recht & Steuern, Markt Wien.

### Standortseiten (`content/standorte/*.md` → `/<slug>.html`)

- **Angelegt, alle als Entwurf** (`draft: true`, `noindex: true`, nicht erreichbar):
  - `immobilienmakler-moedling` (Vorlage, nur Platzhalter)
  - Hub `immobilienmakler-niederoesterreich`
  - Hub `immobilienmakler-wien-umgebung-sued` (mit Abschnitten für Liesing, Perchtoldsdorf, Brunn am Gebirge, Maria Enzersdorf, Vösendorf, Gumpoldskirchen)
- **Geplant:**
  - Tier 1: Baden, Wiener Neustadt, Klosterneuburg
  - Tier 2: St. Pölten, Tulln, Korneuburg
  - Keine eigenen Seiten für Wiener Bezirke und Kärnten.
- **Pflicht-Gerüst für jede Ortsseite:**
  - Die ersten fünf `##` haben einen festen Wortlaut, darunter jeweils zuerst eine Kurzantwort in 1–2 Sätzen.
  - Pflicht-Links: `/verkaufen.html`, `/bewertung.html`, `/ratgeber/maklerprovision-oesterreich.html`, `/ratgeber/immobilienertragsteuer-oesterreich.html`.
  - 3–6 FAQ.
- **Doorway-Schutz:** Ist der Fließtext zweier Standortseiten zu mehr als 70 % gleich, bricht der Build ab.
- **Marktzahlen, Lagen und Objektarten** liefert ausschließlich Gio, mit Stand und Quelle. Nie schätzen oder selbst befüllen.
- **Freischaltung** (`draft: false`, `noindex: false`) nur auf ausdrückliches Signal von Gio, nach Gewerbeanmeldung und Google-Unternehmensprofil. Ein Hub muss vor seinen Ortsseiten live gehen.
- **Automatisch ab der ersten Live-Seite:** Menüpunkt und Footer-Spalte „Standorte“, Sitemap, llms.txt.

## 6. Harte Regeln

1. **Nichts erfinden:**
   - keine Zahlen, Preise, Lagen, Verkaufszahlen, Referenzen oder Kundenstimmen
   - keine Personennamen außer dem Autor
   - keine Adressen und keine zweite Adresse
   - keine Telefonnummer, solange in `site.json` keine steht
2. **Schema nur mit sichtbarem Inhalt.** Keine `aggregateRating` ohne echte, sichtbare Bewertungen.
3. **URLs nie umbenennen oder löschen.** Überarbeiten heißt: Text ändern und `updated` setzen.
4. **Ein Suchthema pro URL.** Bevor ein neuer Artikel entsteht, prüfen, ob ein bestehender das Thema schon abdeckt. Keine Kannibalisierung.
5. **Nicht anfassen:** generiertes HTML, `_build/`, `assets/`, `site.json`, `netlify.toml`, `_redirects`.
6. **Keine Texte, in denen nur der Ortsname getauscht ist.** Jede Seite braucht echten eigenen Inhalt.

## 7. Offene Punkte (bekannt, nicht vom Agent zu lösen)

| Punkt | Auswirkung |
|---|---|
| Straße, Telefon, WhatsApp, UID, FN, Firmenbuchgericht, Gewerbebehörde, Aufsichtsbehörde, Versicherer, Inhaber fehlen in `site.json` | Impressum zeigt noch Platzhalter; LocalBusiness-Schema ohne `streetAddress`/`telephone` (Warnungen im Rich-Results-Test) |
| Google-Unternehmensprofil fehlt | Schwächt lokale Suche, Maps und Gemini-Antworten stark. Höchste Priorität, sobald das Gewerbe angemeldet ist |
| Kontaktformulare vorübergehend aus (`formulare_aktiv: false`) | Auf /kontakt, /bewertung und /kaufen steht statt Formular ein E-Mail-Hinweis. Der Title von /bewertung verspricht noch „online kostenlos“ |
| `referenzen_echt` offen | Die 3 Objekte auf der Startseite und die Projektkarten auf /bautraeger sind noch Demo-Inhalte |
| `anzahl_vermittelte_objekte` offen | Startseite zeigt 120+, Über uns 80+. Beides hängt an einer Variable, Wert fehlt |
| FAQ-Rich-Results | Google zeigt sie nur noch für Behörden- und Gesundheitsseiten. Das Schema bleibt trotzdem sinnvoll |

## 8. Empfohlene nächste Schritte für den Agent

1. **Ratgeber `maklerprovision-oesterreich` schreiben.** Er ist Pflicht-Link aller Standortseiten und bis dahin dort nur als Text ausgegeben. Themen: Höchstsätze nach IMV bei Kauf, Verkauf und Miete; Bestellerprinzip bei Miete seit 1. Juli 2023, mit Quelle RIS.
2. **Keyword-Recherche für Österreich** (Standort AT, Sprache de) für Ratgeberthemen mit Verkaufsabsicht, zum Beispiel:
   - Immobilie verkaufen, welche Unterlagen
   - Grunderwerbsteuer und Eintragungsgebühr
   - Energieausweis beim Verkauf
   - Wohnung verkaufen mit Kredit
   - Hauptwohnsitzbefreiung
   - Wohnrecht oder Fruchtgenuss beim Verkauf
   - Ergebnis als Themenliste mit Suchvolumen und Konkurrenz zur Freigabe an Gio.
3. **Interne Verlinkung:** Jeder neue Artikel verlinkt mindestens eine Leistungsseite. Bestehende Artikel bei Gelegenheit auf neue Artikel verlinken (`updated` setzen).
4. **Monitoring in Search Console:**
   - Indexierungsstatus unter „Seiten“ prüfen
   - neue Artikel einzeln per URL-Prüfung zur Indexierung beantragen
   - Suchanfragen unter „Leistung“ beobachten, sobald Daten da sind (erfahrungsgemäß nach 2–4 Wochen)
5. **Standortseiten:** Texte für Mödling, Baden, Wiener Neustadt, Klosterneuburg und die zwei Hubs entwerfen, mit eigenem Ortsbezug. Ohne Marktzahlen; die liefert Gio. Alles auf `draft: true` lassen.

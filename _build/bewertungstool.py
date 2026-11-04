# Bewertungs-Assistent (mehrstufiges Lead-Formular). Wird von build.py per exec geladen.
#
# - Eigene Route /bewertung-anfragen.html, noindex, nicht in der Sitemap (noindex-Seiten werden automatisch ausgelassen).
# - site.json "bewertungstool_auf_bewertungsseite": true  → Assistent ersetzt zusätzlich das alte Formular auf bewertung.html.
# - Versand über Netlify Forms (Formularname "bewertung-anfrage"). Solange "formulare_aktiv" false ist, läuft der
#   Assistent im Vorschaumodus: alle Schritte sind bedienbar, beim Absenden wird nichts übertragen.
# - Keine automatische Wertanzeige.
#
# TEXTE: Alles in BW_TEXT ist ENTWURF und mit Gio abzustimmen (Lastenheft §5).

BW_FORM = 'bewertung-anfrage'

BW_TEXT = {  # ENTWURF, mit Gio abzustimmen
    'eyebrow': 'Unverbindliche Bewertung',
    'h1': 'Was ist Ihre Immobilie <em>wert</em>?',
    'lead': 'Ein paar Fragen, etwa drei Minuten. Danach sieht sich Giorgi Gorgodze Ihre Angaben persönlich an und meldet sich mit einer ehrlichen Einschätzung. Kein Auftrag, keine Verpflichtung.',
    'trust': ['Unverbindlich &amp; kostenlos', 'Antwort i. d. R. innerhalb von 24&nbsp;h', 'Ihre Daten werden vertraulich behandelt'],
    'lage_hint': 'Die genaue Adresse hilft uns bei der Einschätzung der Mikrolage, ist aber optional.',
    'consent': 'Ich bin damit einverstanden, dass Iveria Immobilien meine Angaben zur Erstellung einer unverbindlichen Immobilienbewertung verarbeitet und mich zu diesem Zweck kontaktiert. Die <a href="/datenschutz.html" target="_blank" rel="noopener">Datenschutzerklärung</a> habe ich gelesen.',
    'submit': 'Unverbindliche Bewertung anfragen',
    'danke_h': 'Vielen <em>Dank</em>!',
    'danke_p': 'Wir sehen uns Ihre Angaben an und melden uns persönlich mit einer ehrlichen Einschätzung. Unverbindlich und kostenlos.',
    'vorschau': 'Vorschau: Der Versand ist noch nicht aktiviert. Es wurden keine Daten übertragen.',
}

BW_ORTE = ([f'Wien {n}., {b}' for n, b in enumerate(['Innere Stadt', 'Leopoldstadt', 'Landstraße', 'Wieden', 'Margareten', 'Mariahilf', 'Neubau',
            'Josefstadt', 'Alsergrund', 'Favoriten', 'Simmering', 'Meidling', 'Hietzing', 'Penzing', 'Rudolfsheim-Fünfhaus', 'Ottakring', 'Hernals',
            'Währing', 'Döbling', 'Brigittenau', 'Floridsdorf', 'Donaustadt', 'Liesing'], 1)]
           + ['Mödling', 'Baden', 'Wiener Neustadt', 'Klosterneuburg', 'St. Pölten', 'Tulln', 'Korneuburg', 'Perchtoldsdorf', 'Brunn am Gebirge',
              'Maria Enzersdorf', 'Gumpoldskirchen', 'Wiener Neudorf', 'Vösendorf', 'Schwechat', 'Purkersdorf', 'Gerasdorf', 'Bad Vöslau',
              'Traiskirchen', 'Gänserndorf', 'Bruck an der Leitha'])

_BW_ICON = {  # Linienzeichnungen im Stil des Bogen-Logos
    'Wohnung': '<rect x="14" y="8" width="36" height="48" rx="1"/><path d="M22 18h6M36 18h6M22 28h6M36 28h6M22 38h6M36 38h6M28 56v-8h8v8"/>',
    'Haus': '<path d="M10 56V30L32 12l22 18v26z"/><path d="M27 56V42q5-5 10 0v14"/>',
    'Grundstück': '<path d="M6 46l18-8 16 6 18-8"/><path d="M6 56l18-8 16 6 18-8"/><path d="M24 38V18M24 18l8 4-8 4"/>',
    'Gewerbeobjekt': '<rect x="10" y="20" width="44" height="36" rx="1"/><path d="M10 30h44M24 56V40h16v16M20 20v-8h24v8"/>',
    'Anlageobjekt / Zinshaus': '<path d="M12 56V18q20-14 40 0v38z"/><path d="M20 26h6M38 26h6M20 36h6M38 36h6M20 46h6M38 46h6M29 56v-8h6v8"/>',
}

BW_IDS = set()
def _bw_id(name, v=''):
    """Eindeutige ID (gleiche Feldnamen kommen in mehreren Objektart-Gruppen vor)."""
    b = 'bw-' + re.sub(r'[^a-z0-9]+', '-', (name + '-' + v).lower()).strip('-')
    i, k = b, 2
    while i in BW_IDS: i, k = f'{b}-{k}', k + 1
    BW_IDS.add(i); return i

def _bw_err(i): return f'<p class="bw-err" id="{i}-err" hidden></p>'

def bw_wahl(name, legend, optionen, req=False, kacheln=False, icons=False, sub=''):
    """Auswahl als große Kacheln (Radio). req=True → Pflicht (per JS, damit no-JS nicht an ausgeblendeten Feldern hängt)."""
    gid = _bw_id(name)
    items = []
    for o in optionen:
        i = _bw_id(name, o)
        ic = f'<svg viewBox="0 0 64 64" aria-hidden="true">{_BW_ICON[o]}</svg>' if icons else ''
        items.append(f'<label class="bw-opt" for="{i}"><input type="radio" id="{i}" name="{name}" value="{_html.escape(o)}"><span>{ic}{o}</span></label>')
    star = ' <i aria-hidden="true">*</i>' if req else ' <small>(optional)</small>'
    return (f'<fieldset class="bw-q{" bw-tiles" if kacheln else ""}{" bw-icons" if icons else ""}" id="{gid}"{" data-req" if req else ""} aria-describedby="{gid}-err">'
            f'<legend>{legend}{star}</legend>{sub}<div class="bw-opts">{"".join(items)}</div>{_bw_err(gid)}</fieldset>')

def bw_feld(name, label, typ='text', req=False, hint='', attrs='', breit=False):
    i = _bw_id(name)
    star = ' <i aria-hidden="true">*</i>' if req else ' <small>(optional)</small>'
    desc = f'{i}-err' + (f' {i}-hint' if hint else '')
    h = f'<p class="bw-hint" id="{i}-hint">{hint}</p>' if hint else ''
    if typ == 'textarea':
        el = f'<textarea id="{i}" name="{name}" rows="4" aria-describedby="{desc}"{attrs}></textarea>'
    else:
        el = f'<input type="{typ}" id="{i}" name="{name}" aria-describedby="{desc}"{attrs}>'
    return f'<div class="bw-f{" bw-wide" if breit else ""}"{" data-req" if req else ""}><label for="{i}">{label}{star}</label>{el}{h}{_bw_err(i)}</div>'

def bw_zahl(name, label, req=False, einheit='', mn=0, mx=None, step='any', breit=False):
    a = f' inputmode="decimal" min="{mn}"' + (f' max="{mx}"' if mx else '') + f' step="{step}"'
    lab = label + (f' <span class="bw-unit">({einheit})</span>' if einheit else '')
    return bw_feld(name, lab, 'number', req, attrs=a, breit=breit)

def _bw_grp(fuer, inhalt):
    """Felder nur für bestimmte Objektarten. fuer = Liste der Objektart-Werte."""
    return f'<div class="bw-grp" data-for="{_html.escape("|".join(fuer))}">{inhalt}</div>'

JA_NEIN = ['Ja', 'Nein']

def bewertungstool_html(standalone=False):
    T = BW_TEXT
    BW_IDS.clear()
    live = bool(cfg('formulare_aktiv'))
    W, H, G, GEW = 'Wohnung', 'Haus', 'Grundstück', ['Gewerbeobjekt', 'Anlageobjekt / Zinshaus']
    schritte = [
        ('Objektart', 'Um welche Immobilie geht es?', None,
         bw_wahl('Objektart', 'Objektart', list(_BW_ICON), req=True, kacheln=True, icons=True)),
        ('Lage', 'Wo liegt die Immobilie?', None,
         '<div class="bw-row">'
         + bw_feld('Bezirk_Ort', 'Bezirk oder Ort', req=True, attrs=' list="bw-orte" autocomplete="off" placeholder="z. B. Wien 12., Meidling oder Mödling"', breit=True)
         + bw_feld('PLZ', 'PLZ', attrs=' inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="postal-code" placeholder="1120"')
         + bw_feld('Strasse_Adresse', 'Straße und Hausnummer', attrs=' autocomplete="street-address"')
         + f'</div><p class="bw-hint">{T["lage_hint"]}</p>'
         + '<datalist id="bw-orte">' + ''.join(f'<option value="{o}">' for o in BW_ORTE) + '</datalist>'),
        ('Eckdaten', 'Die wichtigsten Eckdaten.', None,
         _bw_grp([W], '<div class="bw-row">'
             + bw_zahl('Wohnflaeche_m2', 'Wohnfläche', True, 'm²') + bw_zahl('Zimmer', 'Zimmer', True, mn=1, step='0.5')
             + bw_feld('Stockwerk', 'Stockwerk', req=True, attrs=' placeholder="z. B. 3. OG, DG"') + bw_feld('Baujahr', 'Baujahr', req=True, attrs=' placeholder="z. B. 1910 oder 1960er"')
             + '</div>' + bw_wahl('Lift', 'Lift vorhanden', JA_NEIN, req=True)
             + '<div class="bw-row">' + bw_feld('Freiflaeche', 'Balkon, Loggia, Terrasse', attrs=' placeholder="z. B. Balkon 6 m²"')
             + bw_feld('Keller_Abstellraum', 'Keller oder Abstellraum', attrs=' placeholder="z. B. Kellerabteil"')
             + bw_feld('Parken', 'Parkplatz, Garage, Tiefgarage', attrs=' placeholder="z. B. TG-Platz"')
             + bw_zahl('Betriebskosten_monatlich_EUR', 'Betriebskosten monatlich', einheit='€') + '</div>'
             + bw_wahl('Rechtsform', 'Eigentum, Genossenschaft oder Miete', ['Eigentum', 'Genossenschaft', 'Miete'], kacheln=True))
         + _bw_grp([H], bw_wahl('Haustyp', 'Haustyp', ['Freistehend', 'Doppelhaushälfte', 'Reihenhaus'], req=True, kacheln=True)
             + '<div class="bw-row">' + bw_zahl('Wohnflaeche_m2', 'Wohnfläche', True, 'm²') + bw_zahl('Grundstuecksflaeche_m2', 'Grundstücksfläche', True, 'm²')
             + bw_zahl('Zimmer', 'Zimmer', True, mn=1, step='0.5') + bw_feld('Baujahr', 'Baujahr', req=True, attrs=' placeholder="z. B. 1985"')
             + bw_zahl('Etagen', 'Anzahl Etagen', mn=1, step='1') + bw_feld('Garten_Terrasse', 'Garten, Terrasse', attrs=' placeholder="z. B. Garten 300 m²"')
             + bw_feld('Garage_Stellplatz', 'Garage, Stellplatz') + bw_feld('Keller_Dachboden', 'Keller, Dachboden') + '</div>')
         + _bw_grp([G], '<div class="bw-row">' + bw_zahl('Grundstuecksflaeche_m2', 'Grundstücksfläche', True, 'm²') + '</div>'
             + bw_wahl('Widmung', 'Widmung', ['Bauland', 'Grünland', 'Unbekannt'], kacheln=True)
             + bw_wahl('Bebauung', 'Bebaubar oder bebaut', ['Unbebaut, bebaubar', 'Bebaut', 'Unbekannt'], kacheln=True)
             + bw_wahl('Aufschliessung', 'Aufschließung (Kanal, Wasser, Strom)', ['Voll aufgeschlossen', 'Teilweise', 'Nicht aufgeschlossen', 'Unbekannt'], kacheln=True))
         + _bw_grp(GEW, '<div class="bw-row">' + bw_zahl('Nutzflaeche_m2', 'Nutzfläche', True, 'm²')
             + bw_zahl('Einheiten', 'Anzahl Einheiten', mn=1, step='1') + bw_zahl('Jahresnettomiete_EUR', 'Jahresnettomiete, falls vermietet', einheit='€') + '</div>'
             + bw_wahl('Nutzungsart', 'Nutzungsart', ['Büro', 'Geschäft', 'Lager', 'Wohnen', 'Gemischt'], req=True, kacheln=True)
             + bw_wahl('Vermietet', 'Vermietet', ['Ja, voll', 'Teilweise', 'Nein'], kacheln=True))),
        ('Zustand', 'Zustand und Ausstattung.', 'Grundstück',
         bw_wahl('Zustand', 'Zustand', ['Neuwertig / saniert', 'Gepflegt', 'Renovierungsbedürftig', 'Sanierungsbedürftig'], req=True, kacheln=True)
         + bw_wahl('Ausstattung', 'Ausstattungsqualität', ['Einfach', 'Mittel', 'Gehoben', 'Luxuriös'], kacheln=True)
         + '<div class="bw-row">' + bw_feld('Letzte_Sanierung', 'Letzte Sanierung', attrs=' placeholder="z. B. 2015"')
         + bw_feld('Heizung', 'Heizungsart', attrs=' placeholder="z. B. Fernwärme, Gas, Wärmepumpe"')
         + bw_feld('HWB', 'Energieausweis, HWB-Wert', attrs=' placeholder="z. B. HWB 85 oder nicht vorhanden"') + '</div>'
         + bw_wahl('Nutzung', 'Aktuelle Nutzung', ['Eigengenutzt', 'Vermietet', 'Leerstehend'], kacheln=True)),
        ('Anlass', 'Wofür brauchen Sie die Bewertung?', None,
         bw_wahl('Anlass', 'Grund der Bewertung', ['Verkauf geplant', 'Vermietung', 'Schenkung / Erbschaft', 'Finanzierung / Bank', 'Nur Interesse'], req=True, kacheln=True)
         + bw_wahl('Zeithorizont', 'Zeithorizont', ['So bald wie möglich', 'In 3 bis 6 Monaten', 'In 6 bis 12 Monaten', 'Noch offen'], req=True, kacheln=True)),
        ('Kontakt', 'Wohin dürfen wir die Einschätzung schicken?', None,
         '<div class="bw-row">' + bw_feld('Vorname', 'Vorname', req=True, attrs=' autocomplete="given-name"') + bw_feld('Nachname', 'Nachname', req=True, attrs=' autocomplete="family-name"')
         + bw_feld('E_Mail', 'E-Mail', 'email', req=True, attrs=' autocomplete="email" inputmode="email"')
         + bw_feld('Telefon', 'Telefon', 'tel', attrs=' autocomplete="tel" inputmode="tel"', hint='Empfohlen, falls ein kurzer Rückruf schneller geht.') + '</div>'
         + bw_feld('Nachricht', 'Noch etwas, das wir wissen sollten?', 'textarea', breit=True)
         + f'<div class="bw-f bw-consent" data-req><label class="bw-check" for="bw-einwilligung"><input type="checkbox" id="bw-einwilligung" name="Einwilligung" value="Ja, erteilt" aria-describedby="bw-einwilligung-err"><span>{T["consent"]} <i aria-hidden="true">*</i></span></label>{_bw_err("bw-einwilligung")}</div>'),
    ]
    n = len(schritte)
    steps = []
    for k, (key, h, ohne, body) in enumerate(schritte, 1):
        skip = f' data-skip="{_html.escape(ohne)}"' if ohne else ''
        steps.append(f'''<fieldset class="bw-step" data-step="{key}"{skip}>
        <legend class="bw-h"><span class="bw-n">{k:02d}</span> {h}</legend>
        {body}
      </fieldset>''')
    trust = ''.join(f'<li><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>{t}</li>' for t in T['trust'])
    hx = 'h1' if standalone else 'h2'
    return f'''<section class="bw-sec pad" id="bewertungstool">
  <div class="wrap bw-grid">
    <div class="bw-side">
      <p class="eyebrow">{T["eyebrow"]}</p>
      <{hx} class="bw-title">{T["h1"]}</{hx}>
      <p class="lead">{T["lead"]}</p>
      <ul class="bw-trust">{trust}</ul>
    </div>
    <div class="bw-panel">
      <div class="bw-progress" hidden>
        <p class="bw-count" aria-live="polite"><span class="bw-cur">Schritt 1</span> von <span class="bw-tot">{n}</span><span class="bw-name"></span></p>
        <div class="bw-bar" aria-hidden="true"><i></i></div>
      </div>
      <form class="bw" name="{BW_FORM}" method="POST" action="/danke.html" data-netlify="true" netlify-honeypot="bot-field" novalidate data-live="{1 if live else 0}" data-mail="{_html.escape(cfg("email") or "")}">
        <input type="hidden" name="form-name" value="{BW_FORM}">
        <div class="hp" aria-hidden="true"><label>Nicht ausfüllen <input name="bot-field" tabindex="-1" autocomplete="off"></label></div>
        {"".join(steps)}
        <div class="bw-nav">
          <button type="button" class="bw-back" hidden><span aria-hidden="true">←</span> Zurück</button>
          <button type="button" class="btn solid bw-next" hidden>Weiter <span class="ar" aria-hidden="true">→</span></button>
          <button type="submit" class="btn solid bw-submit">{T["submit"]} <span class="ar" aria-hidden="true">→</span></button>
        </div>
        <p class="bw-note"><i aria-hidden="true">*</i> Pflichtfeld. Unverbindliche Anfrage, kein Maklerauftrag.</p>
        <p class="bw-status" role="alert" hidden></p>
        <ul class="bw-trust-m" aria-hidden="true">{trust}</ul>
      </form>
      <div class="bw-done" hidden tabindex="-1">
        <svg class="bw-done-arch" viewBox="0 0 100 70" aria-hidden="true"><path d="M 22 68 L 22 38 Q 50 10 78 38 L 78 68"/><path d="M 50 26 L 50 66"/></svg>
        <h2>{T["danke_h"]}</h2>
        <p>{T["danke_p"]}</p>
        <p class="bw-done-vorschau" hidden>{T["vorschau"]}</p>
        <a href="/index.html" class="link">Zur Startseite <span class="ar">→</span></a>
      </div>
    </div>
  </div>
</section>
'''

def build_bewertungstool():
    main = bewertungstool_html(standalone=True)
    page("bewertung-anfragen.html", "bewertung", "Bewertung anfragen · Iveria Immobilien",
         "Unverbindliche Immobilienbewertung in Wien und Niederösterreich anfragen. Schritt für Schritt, persönliche Einschätzung statt Rechenwert.",
         main, noindex=True)

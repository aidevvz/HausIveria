# -*- coding: utf-8 -*-
"""
Standortseiten (Ortsseiten + Hubs) für iveria.at.

Quelle:  content/standorte/<slug>.md   (typ: ortsseite | hub; Regeln: content/standorte/README.md)
Ausgabe: /<slug>.html im Root + Einträge in sitemap.xml, llms.txt, Menü und Footer (nur Seiten, die "live" sind)

Status je Seite:
  draft: true            -> wird NICHT gebaut (außer Vorschau mit ENTWUERFE=1 in einen Testordner)
  draft: false, noindex  -> gebaut, aber noindex, nicht in Sitemap/Menü/Footer/Hub-Listen
  draft: false           -> live

Wird von build.py per exec() im selben Namensraum geladen (nach ratgeber.py).
"""
import difflib

ST_DIR = os.path.join(SRC, 'content', 'standorte')
ST_PREVIEW = os.environ.get('ENTWUERFE') == '1'
if ST_PREVIEW and os.path.abspath(OUT) == os.path.abspath(SRC):
    print('ENTWUERFE=1 nur mit Testordner verwenden, z. B.: ENTWUERFE=1 python3 _build/build.py /tmp/vorschau', file=sys.stderr)
    sys.exit(1)

ST_AEHNLICHKEIT_MAX = 0.70   # Doorway-Schutz: höhere Textähnlichkeit zweier Standortseiten bricht den Build ab
ST_PLATZHALTER = '[PLATZHALTER'
ST_H2 = ['Was kostet ein Immobilienmakler in {ort}?', 'Was ist meine Immobilie in {ort} wert?', 'Wie ist der Immobilienmarkt in {ort}?',
         'Wie läuft der Verkauf in {ort} ab?', 'Welche Steuern fallen beim Verkauf an?']
ST_PFLICHTLINKS = ['/verkaufen.html', '/bewertung.html', '/ratgeber/maklerprovision-oesterreich.html', '/ratgeber/immobilienertragsteuer-oesterreich.html']
ST_FELDER = {
    'ortsseite': {'typ', 'ort', 'region', 'plz', 'title', 'seo_title', 'description', 'hub', 'preis_wohnung_min', 'preis_wohnung_max', 'preis_haus_min',
                  'preis_haus_max', 'preis_haus_einheit', 'preis_stand', 'preis_quelle', 'lagen', 'objektarten', 'image', 'image_alt', 'faq', 'related',
                  'footer', 'draft', 'noindex'},
    'hub': {'typ', 'name', 'region', 'title', 'seo_title', 'description', 'image', 'image_alt', 'faq', 'related', 'seiten', 'menu', 'draft', 'noindex'},
}

def _ja(v, default=False):
    if v is None or v == '': return default
    return str(v).strip().lower() in ('true', 'yes', 'ja', '1')

def _zahl(v, feld, fehler, name):
    if v in (None, '', 'null', '~'): return None
    try: return int(str(v).replace('.', '').replace(' ', ''))
    except Exception: fehler.append(f'{name}: {feld} muss eine ganze Zahl sein (ist: {v!r})'); return None

def _liste(v):
    if v in (None, '', 'null'): return []
    return [str(x).strip() for x in (v if isinstance(v, list) else [v]) if str(x).strip()]

def _eur(n): return '€ ' + f'{n:,}'.replace(',', '.')

def _vergleichstext(s):
    """Fließtext ohne Überschriften, Links, Platzhalter und Ortsnamen, als Wortliste (für den Doorway-Vergleich)."""
    t = '\n'.join(l for l in s['body'].splitlines() if not l.lstrip().startswith('#') and ST_PLATZHALTER not in l)
    t = re.sub(r'\]\([^)]*\)', ']', t)
    for w in [s.get('ort') or '', s.get('name') or ''] + s.get('plz', []):
        if w: t = re.sub(re.escape(w), ' ORT ', t, flags=re.I)
    return re.findall(r'\w+', t.lower())

def load_standorte():
    seiten, fehler, warn, kaputt = [], [], [], set()
    for path in sorted(glob.glob(os.path.join(ST_DIR, '*.md'))):
        name = os.path.basename(path)
        if name.startswith('_') or name.upper() == 'README.MD': continue
        slug = name[:-3]
        raw = open(path, encoding='utf-8').read()
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
        if not m: fehler.append(f'{name}: Front-Matter fehlt (Datei muss mit --- beginnen und einem zweiten --- enden)'); continue
        try: fm = yaml.load(m.group(1), Loader=yaml.BaseLoader) or {}
        except Exception as e: fehler.append(f'{name}: Front-Matter ist kein gültiges YAML ({e})'); continue
        body = m.group(2).strip()
        typ = str(fm.get('typ', '')).strip()
        if typ not in ST_FELDER: fehler.append(f'{name}: typ muss "ortsseite" oder "hub" sein (ist: {typ!r})'); continue
        n0 = len(fehler)
        if not re.fullmatch(r'immobilienmakler(-[a-z0-9]+)+', slug): fehler.append(f'{name}: Dateiname muss mit "immobilienmakler-" beginnen, nur a-z, 0-9 und Bindestriche (keine Umlaute)')
        unbekannt = set(fm) - ST_FELDER[typ]
        if unbekannt: fehler.append(f'{name}: unbekannte Felder {sorted(unbekannt)} (Tippfehler?)')
        pflicht = ('ort', 'region', 'title', 'description', 'hub') if typ == 'ortsseite' else ('name', 'title', 'description')
        for k in pflicht:
            if not str(fm.get(k) or '').strip(): fehler.append(f'{name}: Pflichtfeld "{k}" fehlt')
        title = str(fm.get('title', '')).strip(); desc = str(fm.get('description', '')).strip(); seo = str(fm.get('seo_title') or '').strip()
        if seo and len(seo) > 60: fehler.append(f'{name}: seo_title hat {len(seo)} Zeichen, maximal 60')
        if title and not seo and len(title) > 60: fehler.append(f'{name}: title hat {len(title)} Zeichen. Bei mehr als 60 bitte ein kürzeres seo_title (max. 60) angeben')
        if desc and not (70 <= len(desc) <= 160): fehler.append(f'{name}: description hat {len(desc)} Zeichen, erlaubt sind 70 bis 160')
        img = fm.get('image') or None; alt = str(fm.get('image_alt') or '').strip()
        if img:
            if not str(img).startswith('/Images/standorte/'): fehler.append(f'{name}: image muss unter /Images/standorte/ liegen (ist: {img})')
            elif not os.path.exists(os.path.join(SRC, str(img).lstrip('/'))): fehler.append(f'{name}: Bild {img} nicht gefunden')
            else:
                w, h = _Img.open(os.path.join(SRC, str(img).lstrip('/'))).size
                if w < 1200: warn.append(f'{name}: Titelbild ist nur {w}px breit, empfohlen sind mindestens 1200px')
                if os.path.getsize(os.path.join(SRC, str(img).lstrip('/'))) > 250_000: warn.append(f'{name}: Titelbild ist größer als 250 KB')
            if not alt: fehler.append(f'{name}: image_alt fehlt')
        faq_items = []
        for i, it in enumerate(fm.get('faq') or []):
            if not isinstance(it, dict) or not it.get('q') or not it.get('a'): fehler.append(f'{name}: faq Eintrag {i+1} braucht "q" und "a"'); continue
            faq_items.append((str(it['q']).strip(), str(it['a']).strip()))
        if re.search(r'^#\s', body, re.M): fehler.append(f'{name}: Text darf keine H1 (# ...) enthalten. Der Titel ist die H1, im Text mit ## beginnen')
        if re.search(r'!\[\s*\]\(', body): fehler.append(f'{name}: Bild im Text ohne Alternativtext')
        for src in re.findall(r'!\[[^\]]*\]\(([^)\s]+)', body):
            if src.startswith('/') and not os.path.exists(os.path.join(SRC, src.lstrip('/'))): fehler.append(f'{name}: Bild {src} im Text nicht gefunden')
        draft = _ja(fm.get('draft')); noindex = _ja(fm.get('noindex'))
        s = dict(slug=slug, file=name, typ=typ, title=title, seo_title=seo, desc=desc, image=img, image_alt=alt, faq=faq_items, body=body,
                 related=_liste(fm.get('related')), draft=draft, noindex=noindex, url=f'{DOMAIN}/{slug}.html',
                 region=str(fm.get('region') or '').strip())
        # Was öffentlich gebaut wird, muss fertig sein
        oeffentlich = not draft
        streng = fehler if oeffentlich else warn
        if ST_PLATZHALTER in body or any(ST_PLATZHALTER in q + a for q, a in faq_items):
            if oeffentlich: fehler.append(f'{name}: enthält noch {ST_PLATZHALTER}...]-Texte, kann nicht veröffentlicht werden (draft: true lassen)')
        if not (3 <= len(faq_items) <= 6): streng.append(f'{name}: faq braucht 3 bis 6 Fragen (sind: {len(faq_items)})')
        if typ == 'ortsseite':
            s['ort'] = str(fm.get('ort') or '').strip(); s['hub'] = str(fm.get('hub') or '').strip(); s['plz'] = _liste(fm.get('plz'))
            s['footer'] = _ja(fm.get('footer'), True)
            for p in s['plz']:
                if not re.fullmatch(r'\d{4}', p): fehler.append(f'{name}: PLZ "{p}" ist keine vierstellige österreichische Postleitzahl')
            # Preise
            pr = {k: _zahl(fm.get(k), k, fehler, name) for k in ('preis_wohnung_min', 'preis_wohnung_max', 'preis_haus_min', 'preis_haus_max')}
            for art in ('wohnung', 'haus'):
                lo, hi = pr[f'preis_{art}_min'], pr[f'preis_{art}_max']
                if (lo is None) != (hi is None): fehler.append(f'{name}: preis_{art}_min und preis_{art}_max nur gemeinsam angeben')
                elif lo is not None and lo > hi: fehler.append(f'{name}: preis_{art}_min ist größer als preis_{art}_max')
            einheit = str(fm.get('preis_haus_einheit') or 'm2').strip()
            if einheit not in ('m2', 'gesamt'): fehler.append(f'{name}: preis_haus_einheit muss "m2" oder "gesamt" sein')
            s['preise'] = pr; s['preis_haus_einheit'] = einheit
            s['preis_stand'] = str(fm.get('preis_stand') or '').strip(); s['preis_quelle'] = str(fm.get('preis_quelle') or '').strip()
            if s['preis_quelle'] in ('null', '~'): s['preis_quelle'] = ''
            if any(v is not None for v in pr.values()) and not (s['preis_stand'] and s['preis_quelle']):
                fehler.append(f'{name}: Preise ohne preis_stand und preis_quelle dürfen nicht ausgegeben werden')
            s['lagen'] = _liste(fm.get('lagen')); s['objektarten'] = _liste(fm.get('objektarten'))
            # H2-Gerüst
            h2 = [x.strip() for x in re.findall(r'^##\s+(.+?)\s*$', body, re.M)]
            soll = [x.format(ort=s['ort']) for x in ST_H2]
            if h2[:5] != soll:
                fehler.append(f'{name}: Die ersten fünf ##-Überschriften müssen genau so lauten und in dieser Reihenfolge stehen:\n      ' + '\n      '.join('## ' + x for x in soll) + '\n    gefunden:\n      ' + '\n      '.join('## ' + x for x in h2[:5]))
            else:
                for x in soll:
                    nach = body.split('## ' + x, 1)[1].lstrip('\n')
                    erster = nach.split('\n\n', 1)[0].strip()
                    if not erster or erster.startswith(('#', '-', '*', '|', '>', '!', '1.')): fehler.append(f'{name}: Unter "## {x}" muss zuerst eine kurze Antwort (1 bis 2 Sätze) als Absatz stehen')
                    elif len(re.findall(r'[.!?](\s|$)', erster)) > 2 or len(erster) > 320: warn.append(f'{name}: Antwort unter "## {x}" ist länger als 1 bis 2 Sätze')
            for l in ST_PFLICHTLINKS:
                if f']({l}' not in body: streng.append(f'{name}: Pflicht-Link auf {l} fehlt im Text')
        else:
            s['name'] = str(fm.get('name') or '').strip(); s['seiten'] = _liste(fm.get('seiten')); s['menu'] = _ja(fm.get('menu'), True)
        if len(fehler) > n0: kaputt.add(slug); continue
        seiten.append(s)

    by = {s['slug']: s for s in seiten}
    for s in seiten:
        if s['typ'] == 'ortsseite':
            h = by.get(s['hub'])
            if s['hub'] in kaputt: continue
            if not h or h['typ'] != 'hub': fehler.append(f'{s["file"]}: hub "{s["hub"]}" ist keine vorhandene Hub-Seite in content/standorte/')
            elif _st_live(s) and not _st_live(h): fehler.append(f'{s["file"]}: ist live, aber der Hub {h["file"]} noch nicht (erst den Hub freischalten)')
    # Doorway-Schutz
    texte = [(s, _vergleichstext(s)) for s in seiten]
    for i in range(len(texte)):
        for j in range(i + 1, len(texte)):
            (a, wa), (b, wb) = texte[i], texte[j]
            if len(wa) < 80 or len(wb) < 80: continue
            r = difflib.SequenceMatcher(None, wa, wb, autojunk=False).ratio()
            if r > ST_AEHNLICHKEIT_MAX:
                fehler.append(f'{a["file"]} und {b["file"]}: Text zu {r:.0%} gleich (erlaubt bis {ST_AEHNLICHKEIT_MAX:.0%}). Jede Standortseite braucht eigenen Ortsinhalt (Doorway-Schutz)')
    for w in warn: print('  WARNUNG', w)
    if fehler:
        print('\nSTANDORTE: Build abgebrochen, bitte beheben:\n  - ' + '\n  - '.join(fehler), file=sys.stderr)
        sys.exit(1)
    return seiten

def _st_live(s): return not s['draft'] and not s['noindex']
def _st_sichtbar(s): return _st_live(s) or ST_PREVIEW   # in Menü, Footer, Hub-Listen (Vorschau: alles)

STANDORTE = load_standorte()
ST_BY = {s['slug']: s for s in STANDORTE}
ST_SICHTBAR = [s for s in STANDORTE if _st_sichtbar(s)]
ST_HUBS = [s for s in ST_SICHTBAR if s['typ'] == 'hub']
ST_ORTE = [s for s in ST_SICHTBAR if s['typ'] == 'ortsseite']
def _st_kinder(h): return [s for s in ST_ORTE if s['hub'] == h['slug']] + [ST_BY[x] for x in h['seiten'] if x in ST_BY and ST_BY[x] in ST_SICHTBAR and ST_BY[x]['hub'] != h['slug']]
# Menü und Footer-Spalte "Standorte": genau die Primär-Regionen, in dieser Reihenfolge (Wien zuerst = Kernmarkt).
# Andere Hubs (z. B. "Wien Süd und Umgebung") und alle Ortsseiten erscheinen dort nicht, sondern nur über Hub-Listen und Sitemap.
# Eine Region erscheint automatisch, sobald ihre Seite live ist (draft: false, noindex: false).
ST_PRIMAER_REGIONEN = ['immobilienmakler-wien', 'immobilienmakler-niederoesterreich']
ST_REGIONEN = [ST_BY[x] for x in ST_PRIMAER_REGIONEN if x in ST_BY and ST_BY[x] in ST_HUBS]

def st_nav():
    """Menüpunkt "Standorte": Label ohne eigenes Ziel, Untermenü mit den Primär-Regionen (Desktop aufklappend, Handy eingerückt)."""
    if not ST_REGIONEN: return ''
    sub = ''.join(f'<a href="{h["slug"]}.html">{_html.escape(h["name"])}</a>' for h in ST_REGIONEN)
    return (f'      <div class="nav-group"><button type="button" class="nav-label" data-page="standorte" aria-haspopup="true">Standorte</button>'
            f'<div class="nav-sub" aria-label="Standorte">{sub}</div></div>\n')

def st_footer_spalte():
    if not ST_REGIONEN: return ''
    li = ''.join(f'<li><a href="{h["slug"]}.html">{_html.escape(h["name"])}</a></li>' for h in ST_REGIONEN)
    return f'<div><h2 class="fh">Standorte</h2><ul>{li}</ul></div>'

def _st_card(s):
    if s['typ'] == 'hub': kopf, titel = 'Region', s['name']
    else: kopf, titel = ' · '.join(x for x in [', '.join(s['plz']), s['region']] if x), s['ort']
    img = f'<div class="ph"><img src="{s["image"]}" alt="{_html.escape(s["image_alt"])}" loading="lazy"></div>' if s['image'] else ''
    return f'''<a href="/{s["slug"]}.html" class="rt-card st-card">
        {img}
        <div class="rt-meta"><span>{_html.escape(kopf)}</span></div>
        <h3>{_html.escape(titel)}</h3>
        <p>{_html.escape(s["desc"])}</p>
      </a>'''

def _st_links_pruefen(h, s):
    """Links auf nicht veröffentlichte Ratgeber-Artikel oder Standortseiten als Text ausgeben (keine toten Links)."""
    rt_live = {p['slug'] for p in POSTS}; gemeldet = set()
    def hinweis(t):
        if t not in gemeldet: gemeldet.add(t); print(t)
    def fix(m):
        href, text = m.group(1), m.group(2)
        r = re.fullmatch(r'/ratgeber/([a-z0-9-]+)\.html(#.*)?', href)
        if r and r.group(1) not in rt_live:
            hinweis(f'  HINWEIS {s["file"]}: Ratgeber "{r.group(1)}" ist nicht veröffentlicht, Link wird vorerst als Text ausgegeben'); return text
        r = re.fullmatch(r'/(immobilienmakler-[a-z0-9-]+)\.html(#.*)?', href)
        if r and (r.group(1) not in ST_BY or not _st_sichtbar(ST_BY[r.group(1)])):
            hinweis(f'  HINWEIS {s["file"]}: Standortseite "{r.group(1)}" ist nicht live, Link wird vorerst als Text ausgegeben'); return text
        return m.group(0)
    return re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', fix, h)

def _st_einfuegen(body_html, s):
    """Preistabelle nach der Kurzantwort im 2. Abschnitt, Lagen/Objektarten nach der Kurzantwort im 3. Abschnitt."""
    teile = re.split(r'(?=<h2)', body_html)
    def nach_erstem_absatz(t, block):
        i = t.find('</p>')
        return t if i < 0 or not block else t[:i + 4] + '\n' + block + t[i + 4:]
    pr = s['preise']; zeilen = []
    if pr['preis_wohnung_min'] is not None: zeilen.append(('Wohnung', f'{_eur(pr["preis_wohnung_min"])} bis {_eur(pr["preis_wohnung_max"])} pro m²'))
    if pr['preis_haus_min'] is not None:
        zeilen.append(('Haus', f'{_eur(pr["preis_haus_min"])} bis {_eur(pr["preis_haus_max"])}' + (' pro m²' if s['preis_haus_einheit'] == 'm2' else ' Gesamtpreis')))
    tabelle = ''
    if zeilen:
        tabelle = ('<div class="tbl st-preise"><table><thead><tr><th>Objektart</th><th>Preisspanne in ' + _html.escape(s['ort']) + '</th></tr></thead><tbody>'
                   + ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in zeilen) + '</tbody></table></div>'
                   + f'<p class="st-quelle">Stand: {_html.escape(s["preis_stand"])} · Quelle: {_html.escape(s["preis_quelle"])}. Richtwerte, ersetzen keine Bewertung im Einzelfall.</p>')
    listen = ''
    for titel, werte in (('Typische Objektarten', s['objektarten']), ('Gefragte Lagen', s['lagen'])):
        if werte: listen += f'<div class="st-liste"><p class="eyebrow">{titel}</p><ul>' + ''.join(f'<li>{_html.escape(w)}</li>' for w in werte) + '</ul></div>'
    if listen: listen = f'<div class="st-listen">{listen}</div>'
    if len(teile) > 3:
        teile[2] = nach_erstem_absatz(teile[2], tabelle)
        teile[3] = nach_erstem_absatz(teile[3], listen)
    return ''.join(teile)

def _st_toc(toc):
    if len(toc) < 3: return ''
    return '<nav class="rt-toc" aria-label="Inhalt"><p class="eyebrow">Inhalt</p><ol>' + ''.join(f'<li><a href="#{t["id"]}">{_html.escape(_html.unescape(t["name"]))}</a></li>' for t in toc) + '</ol></nav>'

def _st_related(s):
    rt = {p['slug']: p for p in POSTS}
    karten = []
    for r in s['related']:
        if r in ST_BY and ST_BY[r] in ST_SICHTBAR and r != s['slug']: karten.append(_st_card(ST_BY[r]))
        elif r in rt: karten.append(_card(rt[r]))
    if not karten: return ''
    return f'''<section class="pad-s rt-related">
  <div class="wrap">
    <p class="eyebrow">Weiterlesen</p>
    <div class="rt-grid">
      {"".join(karten[:3])}
    </div>
  </div>
</section>
'''

def _st_titel(s):
    t = s['seo_title'] or s['title']
    if 'iveria' not in t.lower() and len(t) + len(' · Iveria Immobilien') <= 60: t += ' · Iveria Immobilien'
    return t

def _st_entwurf(s):
    if s['draft']: return '<p class="st-entwurf">Entwurf · nicht veröffentlicht</p>'
    if s['noindex']: return '<p class="st-entwurf">Nicht im Google-Index (noindex)</p>'
    return ''

def build_standorte():
    gebaut = set()
    for s in STANDORTE:
        if s['draft'] and not ST_PREVIEW: continue
        body, toc = _md(s['body'])
        body = _st_links_pruefen(body, s)
        hero = f'<figure class="rt-hero"><img src="{s["image"]}" alt="{_html.escape(s["image_alt"])}" fetchpriority="high"></figure>' if s['image'] else ''
        faq_html = faq([(_html.escape(q), _html.escape(a)) for q, a in s['faq']], h2='Häufige Fragen zu <em>' + _html.escape(s.get('ort') or s['name']) + '</em>.') if s['faq'] else ''
        if s['typ'] == 'ortsseite':
            hub = ST_BY[s['hub']]
            body = _st_einfuegen(body, s)
            ort_zeile = ' '.join(x for x in [', '.join(s['plz']), s['ort']] if x)
            main = f'''<article>
<header class="ehead warm rt-head">
  <div class="wrap-prose">
    {_st_entwurf(s)}<p class="eyebrow"><a href="/{hub["slug"]}.html">{_html.escape(hub["name"])}</a> · {_html.escape(ort_zeile)}</p>
    <h1>{_html.escape(s["title"])}</h1>
    <p class="lead">{_html.escape(s["desc"])}</p>
  </div>
</header>
<div class="pad-s">
  <div class="wrap-prose">
    {hero}
    {_st_toc(toc)}
    <div class="prose rt-body">
{body}
    </div>
    <p class="st-hub"><a href="/{hub["slug"]}.html" class="link">Alle Standorte: {_html.escape(hub["name"])} {ARR}</a></p>
  </div>
</div>
</article>
{faq_html}''' + cta('Bewertung', f'Was ist Ihre Immobilie in {_html.escape(s["ort"])} <em>wert</em>?', 'Kostenfreie Schnellbewertung online oder fundierte Bewertung vor Ort.', [BTN('/bewertung.html', 'Bewertung anfragen →', 'solid'), BTN('/verkaufen.html', 'Verkauf besprechen')]) + _st_related(s)
            city = {"@type": "City", "name": s['ort'], "containedInPlace": {"@type": "State", "name": s['region']}}
            lokal = org_schema(); lokal.update({"@id": s['url'] + '#makler', "url": s['url'], "areaServed": [city], "parentOrganization": {"@id": ORG_ID}})
            service = {"@context": "https://schema.org", "@type": "Service", "name": s['title'], "serviceType": "Immobilienvermittlung und Immobilienbewertung",
                       "description": s['desc'], "url": s['url'], "provider": {"@id": s['url'] + '#makler'}, "areaServed": city}
            schema = [lokal, service]
            crumbs = [(hub['name'], hub['url']), (s['ort'], s['url'])]
            org = False
        else:
            kinder = _st_kinder(s)
            liste = ('<nav class="st-orte" aria-label="Orte in der Region"><p class="eyebrow">Orte in der Region</p><ul>' + ''.join(
                f'<li><a href="/{k["slug"]}.html"><span class="st-o">{_html.escape(k.get("ort") or k["name"])}</span><span class="st-p">{_html.escape(", ".join(k.get("plz", [])))}</span><span class="ar">→</span></a></li>'
                for k in kinder) + '</ul></nav>') if kinder else ''
            main = f'''<header class="ehead warm rt-head">
  <div class="wrap-prose">
    {_st_entwurf(s)}<p class="eyebrow">Standorte · {_html.escape(s["name"])}</p>
    <h1>{_html.escape(s["title"])}</h1>
    <p class="lead">{_html.escape(s["desc"])}</p>
  </div>
</header>
<div class="pad-s">
  <div class="wrap-prose">
    {hero}
    {liste}
    {_st_toc(toc)}
    <div class="prose rt-body">
{body}
    </div>
  </div>
</div>
{faq_html}''' + cta('Persönliche Beratung', 'Sprechen wir über Ihre <em>Immobilie</em>.', 'Unverbindliches Erstgespräch zu Verkauf, Vermietung oder Bewertung.', [BTN('/bewertung.html', 'Bewertung anfragen →', 'solid'), BTN('/kontakt.html', 'Kontakt')]) + _st_related(s)
            schema = []
            if kinder:
                schema.append({"@context": "https://schema.org", "@type": "ItemList", "name": s['title'], "url": s['url'],
                               "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": k['url'], "name": k.get('ort') or k['name']} for i, k in enumerate(kinder)]})
            crumbs = [(s['name'], s['url'])]
            org = True
        main = main.replace(' data-split', '')   # kein Text hinter Einblend-Animationen
        page(f'{s["slug"]}.html', 'standorte', _html.escape(_st_titel(s)), _html.escape(s['desc']), main, preload=s['image'], schema=schema, crumbs=crumbs,
             noindex=s['draft'] or s['noindex'], og_image=(DOMAIN + s['image']) if s['image'] else None, og_image_alt=s['image_alt'], org=org)
        gebaut.add(s['slug'])
    # Nicht (mehr) gebaute Standortseiten aus dem Ausgabeordner entfernen, damit nichts Veraltetes online bleibt
    for s in STANDORTE:
        f = os.path.join(OUT, f'{s["slug"]}.html')
        if s['slug'] not in gebaut and os.path.exists(f): os.remove(f); print('  entfernt', f'{s["slug"]}.html')
    print('Standorte:', len(gebaut), 'gebaut,', sum(_st_live(s) for s in STANDORTE), 'live')

# -*- coding: utf-8 -*-
"""
Mehrsprachigkeit (EN, RU) für iveria.at. Deutsch bleibt Standard und unverändert.

Quellen:  content/en/*.md, content/ru/*.md   (typ: seite | guide; Regeln: content/en/README.md)
          _build/i18n/strings.<lang>.json     (UI-Texte: Menü, Footer, Buttons, Cookie-Hinweis ...)
Ausgabe:  /en/<slug>.html, /en/ (index.md), /en/guide/<slug>.html, /en/guide/  (RU analog)
          + hreflang (reziprok, nur für vorhandene Live-Übersetzungen), Sprachumschalter, Sitemap-Alternates

Zuordnung: Jede übersetzte Seite nennt im Front-Matter `pendant:` die deutsche Datei (z. B. verkaufen.html).
Seiten mit demselben Pendant sind Sprachversionen voneinander. Ohne Pendant steht die Seite für sich.
Wird von build.py per exec() geladen (nach standorte.py).
"""
I18N_DIR = os.path.join(HERE, 'i18n')
I18N_LANGS = ['en', 'ru']
STR = {l: json.load(open(os.path.join(I18N_DIR, f'strings.{l}.json'), encoding='utf-8')) for l in ['de'] + I18N_LANGS}
I18N_FELDER = {
    'seite': {'typ', 'pendant', 'title', 'seo_title', 'description', 'eyebrow', 'h1', 'lead', 'hero_image', 'hero_alt', 'faq', 'kontaktblock',
              'service', 'draft', 'noindex'},
    'guide': {'typ', 'pendant', 'title', 'seo_title', 'description', 'date', 'updated', 'category', 'image', 'image_alt', 'faq', 'draft', 'noindex'},
}
DE_STAMM = ['index.html', 'verkaufen.html', 'kaufen.html', 'bautraeger.html', 'bewertung.html', 'ueber-uns.html', 'kontakt.html', 'impressum.html', 'datenschutz.html']

def _lang_url(lang, rel):
    rel = '' if rel in ('index.html', '') else rel
    return f'{DOMAIN}/{lang}/{rel}'

def load_i18n():
    seiten, fehler, warn = [], [], []
    de_keys = set(DE_STAMM) | {f'ratgeber/{p["slug"]}.html' for p in POSTS} | {f'{s["slug"]}.html' for s in STANDORTE if _st_live(s)}
    for lang in I18N_LANGS:
        for path in sorted(glob.glob(os.path.join(SRC, 'content', lang, '*.md'))):
            name = f'{lang}/{os.path.basename(path)}'
            if os.path.basename(path).startswith('_') or path.upper().endswith('README.MD'): continue
            slug = os.path.basename(path)[:-3]
            raw = open(path, encoding='utf-8').read()
            m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
            if not m: fehler.append(f'{name}: Front-Matter fehlt'); continue
            try: fm = yaml.load(m.group(1), Loader=yaml.BaseLoader) or {}
            except Exception as e: fehler.append(f'{name}: Front-Matter ist kein gültiges YAML ({e})'); continue
            body = m.group(2).strip(); typ = str(fm.get('typ', 'seite')).strip()
            if typ not in I18N_FELDER: fehler.append(f'{name}: typ muss "seite" oder "guide" sein'); continue
            n0 = len(fehler)
            if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug): fehler.append(f'{name}: Dateiname nur a-z, 0-9 und Bindestriche')
            if typ == 'guide' and slug == 'index': fehler.append(f'{name}: ein Guide darf nicht index heißen')
            unbekannt = set(fm) - I18N_FELDER[typ]
            if unbekannt: fehler.append(f'{name}: unbekannte Felder {sorted(unbekannt)}')
            for k in ('title', 'description') + (('date', 'category') if typ == 'guide' else ()):
                if not str(fm.get(k) or '').strip(): fehler.append(f'{name}: Pflichtfeld "{k}" fehlt')
            title = str(fm.get('title', '')).strip(); desc = str(fm.get('description', '')).strip(); seo = str(fm.get('seo_title') or '').strip()
            if seo and len(seo) > 60: fehler.append(f'{name}: seo_title hat {len(seo)} Zeichen, maximal 60')
            if title and not seo and len(title) > 60: fehler.append(f'{name}: title hat {len(title)} Zeichen. Bei mehr als 60 bitte seo_title (max. 60) angeben')
            if desc and not (70 <= len(desc) <= 160): fehler.append(f'{name}: description hat {len(desc)} Zeichen, erlaubt sind 70 bis 160')
            pendant = str(fm.get('pendant') or '').strip()
            if pendant and pendant not in de_keys: fehler.append(f'{name}: pendant "{pendant}" ist keine vorhandene deutsche Live-Seite (z. B. verkaufen.html, ratgeber/<slug>.html)')
            bild = str(fm.get('hero_image' if typ == 'seite' else 'image') or '').strip()
            alt = str(fm.get('hero_alt' if typ == 'seite' else 'image_alt') or '').strip()
            if bild:
                if not bild.startswith('/Images/'): fehler.append(f'{name}: Bild muss unter /Images/ liegen')
                elif not os.path.exists(os.path.join(SRC, bild.lstrip('/'))): fehler.append(f'{name}: Bild {bild} nicht gefunden')
                if not alt: fehler.append(f'{name}: Alternativtext zum Bild fehlt')
            faq_items = []
            for i, it in enumerate(fm.get('faq') or []):
                if not isinstance(it, dict) or not it.get('q') or not it.get('a'): fehler.append(f'{name}: faq Eintrag {i+1} braucht "q" und "a"'); continue
                faq_items.append((str(it['q']).strip(), str(it['a']).strip()))
            if re.search(r'^#\s', body, re.M): fehler.append(f'{name}: Text darf keine H1 (# ...) enthalten, mit ## beginnen')
            if re.search(r'!\[\s*\]\(', body): fehler.append(f'{name}: Bild im Text ohne Alternativtext')
            draft = _ja(fm.get('draft')); noindex = _ja(fm.get('noindex'))
            if not draft and (ST_PLATZHALTER in body or ST_PLATZHALTER in title + desc + str(fm.get('h1', '')) + str(fm.get('lead', ''))):
                fehler.append(f'{name}: enthält noch [PLATZHALTER...]-Texte, kann nicht veröffentlicht werden (draft: true lassen)')
            d = u = None
            if typ == 'guide':
                d = _as_date(fm.get('date'), 'date', fehler, name) if fm.get('date') else None
                u = _as_date(fm.get('updated'), 'updated', fehler, name) if fm.get('updated') else None
            if len(fehler) > n0: continue
            rel = ('' if slug == 'index' else f'{slug}.html') if typ == 'seite' else f'guide/{slug}.html'
            seiten.append(dict(lang=lang, slug=slug, typ=typ, file=name, fname=f'{lang}/{rel or "index.html"}', url=_lang_url(lang, rel),
                               pendant=pendant, title=title, seo_title=seo, desc=desc, body=body, faq=faq_items, draft=draft, noindex=noindex,
                               eyebrow=str(fm.get('eyebrow') or '').strip(), h1=str(fm.get('h1') or '').strip(), lead=str(fm.get('lead') or '').strip(),
                               bild=bild, alt=alt, kontaktblock=_ja(fm.get('kontaktblock')), service=_ja(fm.get('service')),
                               date=d, updated=u or d, category=str(fm.get('category') or '').strip()))
    # je Sprache ein Pendant nur einmal
    gesehen = {}
    for s in seiten:
        if s['pendant']:
            k = (s['lang'], s['pendant'])
            if k in gesehen: fehler.append(f'{s["file"]} und {gesehen[k]}: gleiches pendant "{s["pendant"]}" in derselben Sprache')
            gesehen[k] = s['file']
    for w in warn: print('  WARNUNG', w)
    if fehler:
        print('\nSPRACHEN: Build abgebrochen, bitte beheben:\n  - ' + '\n  - '.join(fehler), file=sys.stderr)
        sys.exit(1)
    return seiten

def _i_live(s): return not s['draft'] and not s['noindex']
def _i_gebaut(s): return not s['draft'] or ST_PREVIEW
def _i_sichtbar(s): return _i_live(s) or ST_PREVIEW

I18N = load_i18n()
I18N_SICHTBAR = [s for s in I18N if _i_sichtbar(s)]
I18N_LANGS_LIVE = [l for l in I18N_LANGS if any(s['lang'] == l for s in I18N_SICHTBAR)]
I18N_HOME = {l: next((s for s in I18N_SICHTBAR if s['lang'] == l and s['slug'] == 'index' and s['typ'] == 'seite'), None) for l in I18N_LANGS}

# Gruppen für hreflang: Schlüssel = deutsche Datei (pendant) oder die Seite selbst
def _gruppe_key(s): return s['pendant'] or s['fname']
I18N_GRUPPEN = {}
for s in I18N:
    if _i_live(s): I18N_GRUPPEN.setdefault(_gruppe_key(s), {})[s['lang']] = s['url']
for k, g in I18N_GRUPPEN.items():
    if k in DE_STAMM or k.startswith('ratgeber/') or k[:-5] in ST_BY:
        g['de'] = DOMAIN + '/' if k == 'index.html' else f'{DOMAIN}/{k}'

def i18n_alternates(key):
    """hreflang-Liste [(hreflang, url)] inkl. x-default, nur wenn mindestens zwei Sprachen live sind."""
    g = I18N_GRUPPEN.get(key) or {}
    if len(g) < 2: return []
    out = [(STR[l]['hreflang'], g[l]) for l in ['de'] + I18N_LANGS if l in g]
    out.append(('x-default', g.get('de') or g.get('en') or next(iter(g.values()))))
    return out

def lang_switch(key, cur, self_url=None):
    """Sprachumschalter DE/EN/RU: Pendant der aktuellen Seite, sonst Startseite der Sprache."""
    if not I18N_LANGS_LIVE: return ''
    g = I18N_GRUPPEN.get(key) or {}
    if ST_PREVIEW:  # in der Vorschau auch Entwürfe verknüpfen
        g = dict(g)
        for s in I18N_SICHTBAR:
            if _gruppe_key(s) == key: g[s['lang']] = s['url']
        if key in DE_STAMM or key.startswith('ratgeber/'): g.setdefault('de', DOMAIN + '/' if key == 'index.html' else f'{DOMAIN}/{key}')
    if self_url: g = dict(g); g[cur] = self_url
    links = []
    for l in ['de'] + I18N_LANGS_LIVE:
        ziel = g.get(l) or (DOMAIN + '/' if l == 'de' else (I18N_HOME[l]['url'] if I18N_HOME[l] else None))
        if not ziel: continue
        akt = ' class="on" aria-current="true"' if l == cur else ''
        links.append(f'<a href="{ziel.replace(DOMAIN, "")}" hreflang="{STR[l]["hreflang"]}" lang="{STR[l]["html_lang"]}" title="{STR[l]["name"]}"{akt}>{STR[l]["label"]}</a>')
    aria = STR[cur].get('lang_aria', 'Sprache')
    return f'<div class="lang-switch" role="navigation" aria-label="{aria}">' + ''.join(links) + '</div>'

# ---------------------------------------------------------------------
# Kopf, Fuß, Schluss in der Seitensprache
# ---------------------------------------------------------------------
def _i_vorhanden(lang, rel):
    rel_f = rel if rel.endswith('.html') else rel + 'index.html'
    if rel.startswith('guide/'): return any(s['lang'] == lang and s['typ'] == 'guide' for s in I18N_SICHTBAR)
    return any(s['lang'] == lang and s['fname'] == f'{lang}/{rel_f}' for s in I18N_SICHTBAR)

def header_i18n(lang, key, self_url=None):
    S = STR[lang]
    nav = '\n'.join(f'      <a href="/{lang}/{rel}" data-page="{lang}-{rel.split(".")[0].rstrip("/")}">{_html.escape(t)}</a>' for rel, t in S['nav'] if _i_vorhanden(lang, rel))
    btn_link = S['nav_extra_btn_link'] if _i_vorhanden(lang, S['nav_extra_btn_link']) else ''
    btn = f'\n        <a href="/{lang}/{btn_link}" class="btn solid" tabindex="-1">{S["nav_extra_btn"]}</a>' if btn_link else ''
    return f'''<header class="site-header" id="siteHeader">
  <div class="wrap">
    <a href="/{lang}/" class="brand" aria-label="{S["brand_aria"]}">
      {LOGO()}
      <span class="brand-name">Iveria <small>Immobilien</small></span>
    </a>
    {lang_switch(key, lang, self_url)}
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="nav" data-open="{S["menu_open"]}" data-close="{S["menu_close"]}">{S["menu_open"]}</button>
    <nav class="nav" id="nav" aria-label="{S["nav_aria"]}">
{nav}
      <div class="nav-extra" aria-hidden="true">
        <p class="eyebrow">{S["nav_extra_title"]}</p>
        <a href="mailto:{cfg("email")}" tabindex="-1">{cfg("email")}</a>
        <span>{S["hours"]}</span>{btn}
      </div>
    </nav>
  </div>
</header>
'''

def footer_i18n(lang):
    S = STR[lang]
    leist = ''.join(f'<li><a href="/{lang}/{rel}">{_html.escape(t)}</a></li>' for rel, t in S['nav'] if _i_vorhanden(lang, rel))
    nap = ''.join([f'<li>{_html.escape(cfg("firmenname"))}</li>', f'<li><a href="mailto:{cfg("email")}">{cfg("email")}</a></li>',
                   f'<li>{TEL_A}</li>' if TEL_A else '', f'<li style="color:rgba(250,250,247,.6)">{_html.escape(ADR_ZEILE)}</li>',
                   f'<li style="color:rgba(250,250,247,.6)">{S["hours"]}</li>'])
    return f'''<footer class="site-footer dark">
  <div class="wrap">
    <div class="ftop">
      <div>
        <a href="/{lang}/" class="brand" aria-label="{S["brand_aria"]}">
          {LOGO("#FAFAF7")}
          <span class="brand-name">Iveria <small>Immobilien</small></span>
        </a>
        <p>{S["footer_text"]}</p>
      </div>
      <div><h2 class="fh">{S["footer_services"]}</h2><ul>{leist}</ul></div>
      <div><h2 class="fh">{S["footer_company"]}</h2><ul><li><a href="/" hreflang="de-at">Deutsch</a></li><li><a href="/impressum.html" hreflang="de-at">{S["imprint"]}</a></li><li><a href="/datenschutz.html" hreflang="de-at">{S["privacy"]}</a></li></ul></div>
      <div><h2 class="fh">{S["footer_contact"]}</h2><ul>{nap}</ul></div>
    </div>
    <div class="wordmark" id="wordmark" aria-hidden="true"><span>I</span><span>V</span><span>E</span><span>R</span><span>I</span><span>A</span></div>
    <div class="fbot"><span>{S["rights"]}</span><em>{S["claim"]}</em></div>
  </div>
</footer>
'''

def tail_i18n(lang, wa_wait=False):
    S = STR[lang]
    t = tail(wa_wait)
    t = t.replace('aria-hidden="true">Ansehen</div>', f'aria-hidden="true">{S["cursor"]}</div>')
    t = t.replace('aria-label="Cookies und Datenschutz"', f'aria-label="{S["cookie_aria"]}"').replace('<p class="ch">Cookies &amp; Datenschutz</p>', f'<p class="ch">{S["cookie_title"]}</p>')
    t = t.replace('Wir verwenden ausschließlich technisch notwendige Cookies. Mehr in unserer <a href="datenschutz.html">Datenschutzerklärung</a>.',
                  f'{S["cookie_text"]} <a href="/datenschutz.html" hreflang="de-at">{S["cookie_link"]}</a>.')
    return t.replace('>Akzeptieren</button>', f'>{S["accept"]}</button>').replace('>Ablehnen</button>', f'>{S["decline"]}</button>')

# ---------------------------------------------------------------------
# Seiten bauen
# ---------------------------------------------------------------------
def _datum(lang, d):
    S = STR[lang]; return S['date_format'].format(d=d.day, m=S['months'][d.month - 1], y=d.year)

def _i_titel(s):
    t = s['seo_title'] or s['title']
    if 'iveria' not in t.lower() and len(t) + len(' · Iveria Immobilien') <= 60: t += ' · Iveria Immobilien'
    return t

def _i_kontakt(lang):
    S = STR[lang]
    zeilen = [(S['contact_email'], f'<a href="mailto:{cfg("email")}">{cfg("email")}</a>'), (S['contact_hours'], S['hours'])]
    if TEL_A: zeilen.insert(1, ('Tel.', TEL_A))
    if ADR_ZEILE: zeilen.append((S['contact_address'], _html.escape(f'{cfg("firmenname")}, {ADR_ZEILE}')))
    return '<div class="i-kontakt">' + ''.join(f'<div><p class="eyebrow">{k}</p><p>{v}</p></div>' for k, v in zeilen) + '</div>'

def build_i18n():
    for s in I18N:
        if not _i_gebaut(s): continue
        S = STR[s['lang']]; lang = s['lang']; key = _gruppe_key(s)
        body, toc = _md(s['body'])
        body = re.sub(r'<a href="(/[^"]*)"', lambda m: m.group(0), body)
        entwurf = '<p class="st-entwurf">Draft · not published</p>' if s['draft'] else ''
        faq_html = faq([(_html.escape(q), _html.escape(a)) for q, a in s['faq']], eyebrow=S['faq_eyebrow'], h2=S['faq_h2']) if s['faq'] else ''
        cta_html = cta(S['cta_eyebrow'], S['cta_h2'], S['cta_lead'], [BTN(f'/{lang}/{S["cta_btn_link"]}', S['cta_btn'], 'solid')]) \
            if _i_vorhanden(lang, S['cta_btn_link']) and s['slug'] != S['cta_btn_link'][:-5] else ''
        schema = [{"@context": "https://schema.org", "@type": "WebPage", "@id": s['url'] + '#webpage', "url": s['url'], "name": s['title'],
                   "description": s['desc'], "inLanguage": S['html_lang'], "about": {"@id": ORG_ID}}]
        if s['typ'] == 'seite':
            h1 = s['h1'] or _html.escape(s['title'])
            if s['bild']:
                kopf = phero(s['bild'], _html.escape(s['alt']), _html.escape(s['eyebrow']), h1, _html.escape(s['lead'] or s['desc']))
                if entwurf: kopf = kopf.replace('<p class="eyebrow">', entwurf + '<p class="eyebrow">', 1)
            else:
                kopf = f'''<section class="ehead warm rt-head">
  <div class="wrap-prose">
    {entwurf}<p class="eyebrow">{_html.escape(s["eyebrow"])}</p>
    <h1>{h1}</h1>
    <p class="lead">{_html.escape(s["lead"] or s["desc"])}</p>
  </div>
</section>
'''
            main = kopf + f'''<section class="pad-s">
  <div class="wrap-prose">
    <div class="prose rt-body">
{body}
    </div>
    {_i_kontakt(lang) if s["kontaktblock"] else ""}
  </div>
</section>
''' + faq_html + cta_html
            if s['service']:
                schema.append({"@context": "https://schema.org", "@type": "Service", "name": s['title'], "description": s['desc'], "url": s['url'],
                               "provider": {"@id": ORG_ID}, "areaServed": [{"@type": "State", "name": n} for n in S['areas']], "inLanguage": S['html_lang']})
            crumbs = [(s['title'], s['url'])] if s['slug'] != 'index' else None
            og_type, times = 'website', None
        else:
            toc_html = ('<nav class="rt-toc" aria-label="' + S['toc'] + '"><p class="eyebrow">' + S['toc'] + '</p><ol>' +
                        ''.join(f'<li><a href="#{t["id"]}">{_html.escape(_html.unescape(t["name"]))}</a></li>' for t in toc) + '</ol></nav>') if len(toc) >= 3 else ''
            hero = f'<figure class="rt-hero"><img src="{s["bild"]}" alt="{_html.escape(s["alt"])}" fetchpriority="high"></figure>' if s['bild'] else ''
            autor = cfg('ratgeber_autor') or cfg('markenname')
            geaendert = f' · {S["updated"]} <time datetime="{s["updated"].isoformat()}">{_datum(lang, s["updated"])}</time>' if s['updated'] != s['date'] else ''
            main = f'''<article>
<header class="ehead warm rt-head">
  <div class="wrap-prose">
    {entwurf}<p class="eyebrow"><a href="/{lang}/guide/">{S["guide"]}</a> · {_html.escape(s["category"])}</p>
    <h1>{_html.escape(s["title"])}</h1>
    <p class="lead">{_html.escape(s["desc"])}</p>
    <p class="rt-byline">{_html.escape(autor)} · <time datetime="{s["date"].isoformat()}">{_datum(lang, s["date"])}</time>{geaendert} · {_lesezeit(s["body"])} {S["read_min"]}</p>
  </div>
</header>
<div class="pad-s">
  <div class="wrap-prose">
    {hero}
    {toc_html}
    <div class="prose rt-body">
{body}
    </div>
  </div>
</div>
</article>
''' + faq_html + cta_html
            art = {"@context": "https://schema.org", "@type": "BlogPosting", "@id": s['url'] + '#article', "headline": s['title'][:110], "description": s['desc'],
                   "datePublished": s['date'].isoformat(), "dateModified": s['updated'].isoformat(), "author": _author_schema({'author': ''}),
                   "publisher": {"@id": ORG_ID}, "mainEntityOfPage": s['url'], "url": s['url'], "inLanguage": S['html_lang'], "articleSection": s['category']}
            if s['bild']: art['image'] = DOMAIN + s['bild']
            schema = [art]
            crumbs = [(S['guide'], _lang_url(lang, 'guide/')), (s['title'], s['url'])]
            og_type, times = 'article', (s['date'], s['updated'])
        page(s['fname'], f'{lang}-{s["slug"]}' if s['typ'] == 'seite' else f'{lang}-guide', _html.escape(_i_titel(s)), _html.escape(s['desc']), main,
             preload=s['bild'] or None, schema=schema, crumbs=crumbs, noindex=s['draft'] or s['noindex'], og_type=og_type,
             og_image=(DOMAIN + s['bild']) if s['bild'] else None, og_image_alt=s['alt'] or None, article_times=times,
             lang=lang, alt_key=key, url_override=s['url'])
    # Guide-Übersicht je Sprache
    for lang in I18N_LANGS:
        guides = sorted([s for s in I18N_SICHTBAR if s['lang'] == lang and s['typ'] == 'guide'], key=lambda s: s['date'], reverse=True)
        if not guides: continue
        S = STR[lang]
        karten = ''.join(f'''<a href="{g["url"].replace(DOMAIN, "")}" class="rt-card">
        {f'<div class="ph"><img src="{g["bild"]}" alt="{_html.escape(g["alt"])}" loading="lazy"></div>' if g["bild"] else ''}
        <div class="rt-meta"><span>{_html.escape(g["category"])}</span><time datetime="{g["date"].isoformat()}">{_datum(lang, g["date"])}</time></div>
        <h2>{_html.escape(g["title"])}</h2>
        <p>{_html.escape(g["desc"])}</p>
      </a>''' for g in guides)
        main = f'''<section class="ehead warm rt-head">
  <div class="wrap">
    <p class="eyebrow">{S["guide"]}</p>
    <h1>{S["guide_h1"]}</h1>
    <p class="lead">{S["guide_lead"]}</p>
  </div>
</section>
<section class="pad-s">
  <div class="wrap">
    <div class="rt-grid">{karten}</div>
  </div>
</section>
'''
        live = any(_i_live(g) for g in guides)
        page(f'{lang}/guide/index.html', f'{lang}-guide', _html.escape(S['guide_title']), _html.escape(S['guide_desc']), main,
             crumbs=[(S['guide'], _lang_url(lang, 'guide/'))], noindex=not live, lang=lang, alt_key=f'{lang}/guide/index.html', url_override=_lang_url(lang, 'guide/'))
    # nicht mehr gebaute Sprachseiten entfernen
    gebaut = {s['fname'] for s in I18N if _i_gebaut(s)}
    for lang in I18N_LANGS:
        for f in glob.glob(os.path.join(OUT, lang, '*.html')) + glob.glob(os.path.join(OUT, lang, 'guide', '*.html')):
            rel = os.path.relpath(f, OUT)
            if rel not in gebaut and not rel.endswith('guide/index.html'):
                os.remove(f); print('  entfernt', rel)
    print('Sprachen:', sum(_i_gebaut(s) for s in I18N), 'gebaut,', sum(_i_live(s) for s in I18N), 'live')

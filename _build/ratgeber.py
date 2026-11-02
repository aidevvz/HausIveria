# -*- coding: utf-8 -*-
"""
Ratgeber (Blog) für iveria.at.

Quelle:  content/ratgeber/<slug>.md   (Markdown mit YAML-Front-Matter, Regeln: content/ratgeber/README.md)
Ausgabe: ratgeber/index.html, ratgeber/<slug>.html, ratgeber/feed.xml
         + Einträge in sitemap.xml und llms.txt (macht build.py)

Wird von build.py per exec() im selben Namensraum geladen: nutzt page(), head(), DOMAIN, cfg(), ORG_ID usw.
Fehler in einem Artikel brechen den Build ab (Netlify behält dann die letzte funktionierende Version online).
"""
import glob, math, unicodedata
import yaml, markdown

SRC = os.path.dirname(HERE)  # Repo-Wurzel (Quellen), unabhängig vom Ausgabeordner
RT_DIR = os.path.join(SRC, 'content', 'ratgeber')
RT_URL = f'{DOMAIN}/ratgeber/'
RT_CTA = {  # Ziel-Seite am Artikelende: Schlüssel im Front-Matter -> (Link, Eyebrow, Überschrift, Text, Button)
    'verkaufen':  ('/verkaufen.html',  'Verkaufen', 'Ihre Immobilie in <em>guten Händen</em>.', 'Persönliche Begleitung vom Erstgespräch bis zur Schlüsselübergabe. Provision nur im Erfolgsfall.', 'Verkauf besprechen →'),
    'bewertung':  ('/bewertung.html',  'Bewertung', 'Was ist Ihre Immobilie <em>wert</em>?', 'Kostenfreie Schnellbewertung online oder fundierte Bewertung vor Ort.', 'Bewertung anfragen →'),
    'kaufen':     ('/kaufen.html',     'Kaufen', 'Das passende <em>Zuhause</em> finden.', 'Aktuelle Objekte und persönlicher Suchauftrag, bevor Objekte öffentlich werden.', 'Objekte ansehen →'),
    'bautraeger': ('/bautraeger.html', 'Bauträger', 'Projekte vermarkten, die <em>ankommen</em>.', 'Vermarktung kompletter Wohnprojekte von der Konzeptphase bis zur Übergabe.', 'Projekt besprechen →'),
    'kontakt':    ('/kontakt.html',    'Kontakt', 'Sprechen wir <em>persönlich</em>.', 'Unverbindliches Erstgespräch zu Ihrem Vorhaben.', 'Kontakt aufnehmen →'),
}
MONATE = ['Jänner', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
def datum_de(d): return f'{d.day}. {MONATE[d.month-1]} {d.year}'

def _as_date(v, feld, fehler, name):
    if isinstance(v, datetime.datetime): return v.date()
    if isinstance(v, datetime.date): return v
    try: return datetime.date.fromisoformat(str(v))
    except Exception:
        fehler.append(f'{name}: "{feld}" muss ein Datum im Format JJJJ-MM-TT sein (ist: {v!r})'); return None

def _slugify(t):
    t = unicodedata.normalize('NFKD', t.replace('ß', 'ss').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('Ä', 'ae').replace('Ö', 'oe').replace('Ü', 'ue'))
    return re.sub(r'[^a-z0-9]+', '-', t.encode('ascii', 'ignore').decode().lower()).strip('-')

def load_posts():
    """Liest und prüft alle Artikel. Gibt nur veröffentlichte zurück (draft: false und Datum <= heute)."""
    posts, fehler, warn = [], [], []
    heute = datetime.date.today()
    for path in sorted(glob.glob(os.path.join(RT_DIR, '*.md'))):
        name = os.path.basename(path)
        if name.startswith('_') or name.upper() == 'README.MD': continue
        slug = name[:-3]
        raw = open(path, encoding='utf-8').read()
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
        if not m: fehler.append(f'{name}: Front-Matter fehlt (Datei muss mit --- beginnen und einem zweiten --- enden)'); continue
        try: fm = yaml.load(m.group(1), Loader=yaml.BaseLoader) or {}  # alles als Text, Datumsprüfung macht _as_date
        except Exception as e: fehler.append(f'{name}: Front-Matter ist kein gültiges YAML ({e})'); continue
        body = m.group(2).strip()
        n0 = len(fehler)
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug): fehler.append(f'{name}: Dateiname nur aus a-z, 0-9 und Bindestrichen (keine Umlaute), z. B. maklerprovision-oesterreich.md')
        for k in ('title', 'description', 'date', 'category'):
            if not fm.get(k): fehler.append(f'{name}: Pflichtfeld "{k}" fehlt')
        unbekannt = set(fm) - {'title', 'seo_title', 'description', 'date', 'updated', 'author', 'category', 'image', 'image_alt', 'faq', 'cta', 'related', 'draft'}
        if unbekannt: fehler.append(f'{name}: unbekannte Felder {sorted(unbekannt)} (Tippfehler?)')
        title = str(fm.get('title', '')).strip(); desc = str(fm.get('description', '')).strip()
        seo = str(fm.get('seo_title') or '').strip()
        if seo and len(seo) > 60: fehler.append(f'{name}: seo_title hat {len(seo)} Zeichen, maximal 60')
        if title and not seo and len(title) > 60: fehler.append(f'{name}: title hat {len(title)} Zeichen. Bei mehr als 60 bitte ein kürzeres seo_title (max. 60) angeben')
        if desc and not (70 <= len(desc) <= 160): fehler.append(f'{name}: description hat {len(desc)} Zeichen, erlaubt sind 70 bis 160')
        d = _as_date(fm.get('date'), 'date', fehler, name) if fm.get('date') else None
        u = _as_date(fm.get('updated'), 'updated', fehler, name) if fm.get('updated') else None
        if d and u and u < d: fehler.append(f'{name}: updated liegt vor date')
        cta = fm.get('cta', 'kontakt')
        if cta not in RT_CTA: fehler.append(f'{name}: cta muss einer von {sorted(RT_CTA)} sein (ist: {cta!r})')
        img = fm.get('image'); alt = str(fm.get('image_alt') or '').strip()
        if img:
            if not str(img).startswith('/Images/ratgeber/'): fehler.append(f'{name}: image muss unter /Images/ratgeber/ liegen (ist: {img})')
            elif not os.path.exists(os.path.join(SRC, str(img).lstrip('/'))): fehler.append(f'{name}: Bild {img} nicht gefunden')
            else:
                w, h = _Img.open(os.path.join(SRC, str(img).lstrip('/'))).size
                if w < 1200: warn.append(f'{name}: Titelbild ist nur {w}px breit, empfohlen sind mindestens 1200px')
            if not alt: fehler.append(f'{name}: image_alt fehlt (beschreibender Alternativtext zum Titelbild)')
        faq_items = []
        for i, it in enumerate(fm.get('faq') or []):
            if not isinstance(it, dict) or not it.get('q') or not it.get('a'): fehler.append(f'{name}: faq Eintrag {i+1} braucht "q" und "a"'); continue
            faq_items.append((str(it['q']).strip(), str(it['a']).strip()))
        if re.search(r'^#\s', body, re.M): fehler.append(f'{name}: Text darf keine H1 (# ...) enthalten. Der Titel ist die H1, im Text mit ## beginnen')
        if re.search(r'!\[\s*\]\(', body): fehler.append(f'{name}: Bild im Text ohne Alternativtext (![Beschreibung](/Images/ratgeber/...))')
        for src in re.findall(r'!\[[^\]]*\]\(([^)\s]+)', body):
            if src.startswith('/') and not os.path.exists(os.path.join(SRC, src.lstrip('/'))): fehler.append(f'{name}: Bild {src} im Text nicht gefunden')
        if len(fehler) > n0: continue
        draft = str(fm.get('draft', 'false')).strip().lower() in ('true', 'yes', 'ja', '1')
        if draft or d > heute:
            print(f'  Ratgeber: {name} übersprungen ({"Entwurf" if draft else "erscheint am " + d.isoformat()})'); continue
        posts.append(dict(slug=slug, file=name, title=title, seo_title=seo, desc=desc, date=d, updated=u or d, author=str(fm.get('author') or '').strip(),
                          category=str(fm['category']).strip(), image=img, image_alt=alt, faq=faq_items, cta=cta, related=fm.get('related') or [], body=body,
                          url=f'{DOMAIN}/ratgeber/{slug}.html'))
    for w in warn: print('  WARNUNG', w)
    if fehler:
        print('\nRATGEBER: Build abgebrochen, bitte beheben:\n  - ' + '\n  - '.join(fehler), file=sys.stderr)
        sys.exit(1)
    slugs = {p['slug'] for p in posts}
    for p in posts:
        for r in p['related']:
            if r not in slugs: print(f'  WARNUNG {p["file"]}: related "{r}" ist kein veröffentlichter Artikel und wird ignoriert')
    posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    return posts

POSTS = load_posts()

def _md(body):
    md = markdown.Markdown(extensions=['extra', 'sane_lists', 'toc', 'smarty'],
                           extension_configs={'toc': {'slugify': lambda v, sep: _slugify(v), 'toc_depth': '2'},
                                              'smarty': {'substitutions': {'left-double-quote': '„', 'right-double-quote': '“', 'left-single-quote': '‚', 'right-single-quote': '‘'}}})
    h = md.convert(body)
    h = re.sub(r'<table>', '<div class="tbl"><table>', h).replace('</table>', '</table></div>')
    # externe Links in neuem Tab, interne bleiben
    h = re.sub(r'<a href="(https?://(?!iveria\.at)[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', h)
    return h, md.toc_tokens

def _lesezeit(body): return max(1, math.ceil(len(re.findall(r'\w+', body)) / 200))

def _author_schema(p):
    a = p['author'] or cfg('ratgeber_autor')
    if not a: return {"@id": ORG_ID}
    name, _, suffix = a.partition(', ')
    o = {"@type": "Person", "name": name, "worksFor": {"@id": ORG_ID}}
    if suffix: o["honorificSuffix"] = suffix
    return o

def _card(p, h='h3'):
    img = f'<div class="ph"><img src="{p["image"]}" alt="{_html.escape(p["image_alt"])}" loading="lazy"></div>' if p['image'] else '<div class="ph ph-empty" aria-hidden="true">' + LOGO() + '</div>'
    return f'''<a href="/ratgeber/{p["slug"]}.html" class="rt-card">
        {img}
        <div class="rt-meta"><span>{_html.escape(p["category"])}</span><time datetime="{p["date"].isoformat()}">{datum_de(p["date"])}</time></div>
        <{h}>{_html.escape(p["title"])}</{h}>
        <p>{_html.escape(p["desc"])}</p>
      </a>'''

FEED_LINK = f'<link rel="alternate" type="application/rss+xml" title="Iveria Immobilien Ratgeber" href="{DOMAIN}/ratgeber/feed.xml">\n'

def build_ratgeber():
    os.makedirs(os.path.join(OUT, 'ratgeber'), exist_ok=True)
    # --- Übersicht ---
    if POSTS:
        karten = "\n      ".join(_card(p, 'h2') for p in POSTS)
        liste = f'<div class="rt-grid">\n      {karten}\n    </div>'
    else:
        liste = '<p class="lead">Die ersten Beiträge erscheinen in Kürze.</p>'
    main = f'''<section class="ehead warm rt-head">
  <div class="wrap">
    <p class="eyebrow">Ratgeber</p>
    <h1>Wissen rund um <em>Immobilien</em>.</h1>
    <p class="lead">Verkaufen, kaufen, vermieten und bewerten in Wien und Niederösterreich: verständlich erklärt, mit Blick auf die Praxis.</p>
  </div>
</section>
<section class="pad-s">
  <div class="wrap">
    {liste}
  </div>
</section>
''' + cta("Persönliche Beratung", "Ihre Frage ist nicht <em>dabei</em>?", "Wir beantworten sie gerne persönlich und unverbindlich.", [BTN("/kontakt.html", "Kontakt aufnehmen →", "solid")])
    blog = {"@context": "https://schema.org", "@type": "Blog", "@id": RT_URL + '#blog', "name": "Iveria Immobilien Ratgeber", "url": RT_URL,
            "inLanguage": "de-AT", "publisher": {"@id": ORG_ID},
            "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": p['url'], "datePublished": p['date'].isoformat()} for p in POSTS]}
    page('ratgeber/index.html', 'ratgeber', 'Immobilien-Ratgeber Wien · Iveria Immobilien',
         'Ratgeber von Iveria Immobilien: Verkaufen, Kaufen, Vermieten und Bewerten von Immobilien in Wien und Niederösterreich verständlich erklärt.',
         main, schema=[blog], crumb='Ratgeber', noindex=not POSTS, url_override=RT_URL, extra_head=FEED_LINK if POSTS else '')

    # --- Artikel ---
    by_slug = {p['slug']: p for p in POSTS}
    for p in POSTS:
        body, toc = _md(p['body'])
        toc_html = ''
        if len(toc) >= 3:
            toc_html = '<nav class="rt-toc" aria-label="Inhalt"><p class="eyebrow">Inhalt</p><ol>' + ''.join(f'<li><a href="#{t["id"]}">{_html.escape(_html.unescape(t["name"]))}</a></li>' for t in toc) + '</ol></nav>'
        hero = f'<figure class="rt-hero"><img src="{p["image"]}" alt="{_html.escape(p["image_alt"])}" fetchpriority="high"></figure>' if p['image'] else ''
        autor = p['author'] or cfg('ratgeber_autor') or cfg('markenname')
        geaendert = f' · Aktualisiert <time datetime="{p["updated"].isoformat()}">{datum_de(p["updated"])}</time>' if p['updated'] != p['date'] else ''
        faq_html = faq([(_html.escape(q), _html.escape(a)) for q, a in p['faq']], h2='Kurz <em>beantwortet</em>.') if p['faq'] else ''
        rel = [by_slug[r] for r in p['related'] if r in by_slug and r != p['slug']]
        if len(rel) < 2:  # auffüllen: gleiche Kategorie, dann neueste
            rest = [q for q in POSTS if q['slug'] != p['slug'] and q not in rel]
            rest.sort(key=lambda q: (q['category'] != p['category'], -q['date'].toordinal()))
            rel += rest[:3 - len(rel)]
        rel = rel[:3]
        rel_html = f'''<section class="pad-s rt-related">
  <div class="wrap">
    <p class="eyebrow">Weiterlesen</p>
    <div class="rt-grid">
      {"".join(_card(q) for q in rel)}
    </div>
  </div>
</section>
''' if rel else ''
        l, eb, h2, lead, btn = RT_CTA[p['cta']]
        main = f'''<article>
<header class="ehead warm rt-head">
  <div class="wrap-prose">
    <p class="eyebrow"><a href="/ratgeber/">Ratgeber</a> · {_html.escape(p["category"])}</p>
    <h1>{_html.escape(p["title"])}</h1>
    <p class="lead">{_html.escape(p["desc"])}</p>
    <p class="rt-byline">{_html.escape(autor)} · <time datetime="{p["date"].isoformat()}">{datum_de(p["date"])}</time>{geaendert} · {_lesezeit(p["body"])} Min. Lesezeit</p>
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
{faq_html}{cta(eb, h2, lead, [BTN(l, btn, "solid")])}{rel_html}'''
        art = {"@context": "https://schema.org", "@type": "BlogPosting", "@id": p['url'] + '#article', "headline": p['title'][:110],
               "description": p['desc'], "datePublished": p['date'].isoformat(), "dateModified": p['updated'].isoformat(),
               "author": _author_schema(p), "publisher": {"@id": ORG_ID}, "mainEntityOfPage": p['url'], "url": p['url'],
               "inLanguage": "de-AT", "articleSection": p['category'], "isPartOf": {"@id": RT_URL + '#blog'},
               "wordCount": len(re.findall(r'\w+', p['body']))}
        if p['image']: art["image"] = DOMAIN + p['image']
        title = p['seo_title'] or p['title']
        if len(title) + len(' · Iveria Immobilien') <= 60: title += ' · Iveria Immobilien'
        page(f'ratgeber/{p["slug"]}.html', 'ratgeber', _html.escape(title), _html.escape(p['desc']), main,
             preload=p['image'], schema=[art], crumbs=[('Ratgeber', RT_URL), (p['title'], p['url'])],
             og_type='article', og_image=(DOMAIN + p['image']) if p['image'] else None, og_image_alt=p['image_alt'],
             article_times=(p['date'], p['updated']), extra_head=FEED_LINK)

    # --- RSS ---
    def esc(t): return _html.escape(t, quote=False)
    items = "\n".join(f'''  <item>
    <title>{esc(p["title"])}</title>
    <link>{p["url"]}</link>
    <guid isPermaLink="true">{p["url"]}</guid>
    <description>{esc(p["desc"])}</description>
    <category>{esc(p["category"])}</category>
    <pubDate>{datetime.datetime.combine(p["date"], datetime.time(8, 0)).strftime("%a, %d %b %Y %H:%M:%S +0100")}</pubDate>
  </item>''' for p in POSTS[:30])
    open(os.path.join(OUT, 'ratgeber', 'feed.xml'), 'w', encoding='utf-8').write(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Iveria Immobilien Ratgeber</title>
  <link>{RT_URL}</link>
  <atom:link href="{DOMAIN}/ratgeber/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Ratgeber rund um Immobilien in Wien und Niederösterreich</description>
  <language>de-AT</language>
{items}
</channel>
</rss>
''')
    print('geschrieben ratgeber/feed.xml', len(POSTS), 'Artikel')

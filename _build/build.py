#!/usr/bin/env python3
"""Baut alle Seiten von Iveria Immobilien aus gemeinsamen Bausteinen."""
import os, sys, json, re, subprocess, datetime, html as _html
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
V = "20261029a"
SITE = json.load(open(os.path.join(HERE, 'site.json'), encoding='utf-8'))
DOMAIN = SITE['domain'].rstrip('/')
def cfg(k): return SITE.get(k)
def ph(k, label):
    """Wert aus site.json oder sichtbarer Platzhalter (nur für Impressum/Datenschutz)."""
    v = cfg(k); return _html.escape(v) if v else f'[{label}]'
TEL_A = (f'<a href="tel:{cfg("telefon_e164")}">{_html.escape(cfg("telefon_anzeige"))}</a>' if cfg('telefon_e164') and cfg('telefon_anzeige') else None)
WA_URL = f'https://wa.me/{cfg("whatsapp_e164")}' if cfg('whatsapp_e164') else None
ADR_ZEILE = ", ".join(x for x in [cfg('strasse'), " ".join(x for x in [cfg('plz'), cfg('ort')] if x)] if x)
FAQ_CURRENT = []
OBJ = cfg('anzahl_vermittelte_objekte')
def obj_stat(fallback):
    n = OBJ if OBJ is not None else fallback
    return (n, "+", f"{n}+", "Vermittelte Objekte")

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23161513'/%3E%3Cpath d='M 22 80 L 22 50 Q 50 22 78 50 L 78 80' fill='none' stroke='%23FAFAF7' stroke-width='1.4' stroke-linecap='round'/%3E%3Cline x1='50' y1='38' x2='50' y2='78' stroke='%23B08D57' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E"
FONTS = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Inter:wght@300;400;500&display=swap"
LOGO = lambda stroke="currentColor": f'<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M 22 80 L 22 50 Q 50 22 78 50 L 78 80" fill="none" stroke="{stroke}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/><line x1="50" y1="38" x2="50" y2="78" stroke="#B08D57" stroke-width="1.8" stroke-linecap="round"/></svg>'
ARR = '<span class="ar">→</span>'
ARCHLINE = '<svg class="arch-line" viewBox="0 0 100 70" aria-hidden="true"><path d="M 22 68 L 22 38 Q 50 10 78 38 L 78 68"/><path d="M 50 26 L 50 66" style="stroke-width:1.4"/></svg>'

def head(title, desc, preload=None, canonical=None, schema=(), noindex=False):
    pl = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">\n' if preload else ''
    can = f'<link rel="canonical" href="{canonical}">\n' if canonical else ''
    robots = '<meta name="robots" content="noindex, follow">\n' if noindex else ''
    og = ''
    if canonical:
        og = f'''<meta property="og:type" content="website">
<meta property="og:locale" content="de_AT">
<meta property="og:site_name" content="{cfg('markenname')}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMAIN}/Images/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Iveria Immobilien – Wo aus vier Wänden Zuhause wird.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{DOMAIN}/Images/og-image.jpg">
'''
    ver = ''
    v = SITE.get('verifizierung') or {}
    if v.get('google'): ver += f'<meta name="google-site-verification" content="{v["google"]}">\n'
    if v.get('bing'): ver += f'<meta name="msvalidate.01" content="{v["bing"]}">\n'
    ld = ''.join(f'<script type="application/ld+json">{jsonld(x)}</script>\n' for x in schema)
    return f'''<!DOCTYPE html>
<html lang="de-AT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}{can}<meta name="theme-color" content="#FAFAF7">
{og}{ver}<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{pl}<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="assets/iveria.css?v={V}">
<script>document.documentElement.classList.add('js');setTimeout(function(){{document.documentElement.classList.add('ready')}},2500)</script>
{ld}</head>
'''

def jsonld(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

def strip_tags(t):
    return _html.unescape(re.sub(r'<[^>]+>', '', t)).strip()

AREAS = [{"@type": "State", "name": n} for n in ["Wien", "Niederösterreich", "Burgenland", "Kärnten"]]
ORG_ID = f'{DOMAIN}/#organization'
def org_schema():
    o = {"@context": "https://schema.org", "@type": "RealEstateAgent", "@id": ORG_ID,
         "name": cfg('markenname'), "legalName": cfg('firmenname'), "url": DOMAIN + '/',
         "logo": f'{DOMAIN}/icon-512.png', "image": f'{DOMAIN}/Images/og-image.jpg',
         "email": cfg('email')}
    if cfg('telefon_e164'): o["telephone"] = cfg('telefon_e164')
    if cfg('uid'): o["vatID"] = cfg('uid')
    adr = {"@type": "PostalAddress"}
    if cfg('strasse'): adr["streetAddress"] = cfg('strasse')
    if cfg('plz'): adr["postalCode"] = cfg('plz')
    adr["addressLocality"] = cfg('ort'); adr["addressCountry"] = "AT"
    o["address"] = adr
    o["areaServed"] = AREAS
    oz = cfg('oeffnungszeiten')
    o["openingHoursSpecification"] = [{"@type": "OpeningHoursSpecification", "dayOfWeek": oz['tage'], "opens": oz['von'], "closes": oz['bis']}]
    if cfg('google_business_profile_url'): o["sameAs"] = [cfg('google_business_profile_url')]
    return o

def breadcrumb(name, url):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Startseite", "item": DOMAIN + '/'},
        {"@type": "ListItem", "position": 2, "name": name, "item": url}]}

def service(name, desc, url, offers=None):
    o = {"@context": "https://schema.org", "@type": "Service", "name": name, "description": strip_tags(desc),
         "url": url, "provider": {"@id": ORG_ID}, "areaServed": AREAS}
    if offers: o["offers"] = offers
    return o

def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in items]}

def header():
    links = [("kaufen.html","kaufen","Objekte"),("verkaufen.html","verkaufen","Verkaufen"),("bautraeger.html","bautraeger","Bauträger"),("ueber-uns.html","ueber-uns","Über uns"),("kontakt.html","kontakt","Kontakt")]
    nav = "\n".join(f'      <a href="{h}" data-page="{p}">{t}</a>' for h,p,t in links)
    return f'''<header class="site-header" id="siteHeader">
  <div class="wrap">
    <a href="index.html" class="brand" aria-label="Iveria Immobilien, Startseite">
      {LOGO()}
      <span class="brand-name">Iveria <small>Immobilien</small></span>
    </a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="nav">Menü</button>
    <nav class="nav" id="nav" aria-label="Hauptnavigation">
{nav}
    </nav>
  </div>
</header>
'''

FOOT_NAP = "".join([
    f'<li>{_html.escape(cfg("firmenname"))}</li>',
    f'<li><a href="mailto:{cfg("email")}">{cfg("email")}</a></li>',
    f'<li>{TEL_A}</li>' if TEL_A else '',
    f'<li style="color:rgba(250,250,247,.6)">{_html.escape(ADR_ZEILE)}</li>',
    f'<li style="color:rgba(250,250,247,.6)">{cfg("oeffnungszeiten_anzeige")}</li>'])
FOOTER = f'''<footer class="site-footer dark">
  <div class="wrap">
    <div class="ftop">
      <div>
        <a href="index.html" class="brand" aria-label="Iveria Immobilien, Startseite">
          {LOGO("#FAFAF7")}
          <span class="brand-name">Iveria <small>Immobilien</small></span>
        </a>
        <p>Persönliche Immobilienvermittlung und Projektvermarktung in Wien, Niederösterreich, Burgenland und Kärnten. Wo aus vier Wänden Zuhause wird.</p>
      </div>
      <div><h2 class="fh">Leistungen</h2><ul><li><a href="verkaufen.html">Verkaufen &amp; Vermieten</a></li><li><a href="kaufen.html">Objekte ansehen</a></li><li><a href="bautraeger.html">Bauträgervermarktung</a></li><li><a href="bewertung.html">Bewertung anfragen</a></li></ul></div>
      <div><h2 class="fh">Iveria Immobilien</h2><ul><li><a href="ueber-uns.html">Über uns</a></li><li><a href="kontakt.html">Kontakt</a></li><li><a href="impressum.html">Impressum</a></li><li><a href="datenschutz.html">Datenschutz</a></li></ul></div>
      <div><h2 class="fh">Kontakt</h2><ul>{FOOT_NAP}</ul></div>
    </div>
    <div class="wordmark" id="wordmark" aria-hidden="true"><span>I</span><span>V</span><span>E</span><span>R</span><span>I</span><span>A</span></div>
    <div class="fbot"><span>© 2026 Iveria Immobilien. Alle Rechte vorbehalten.</span><em>Wo aus vier Wänden Zuhause wird.</em></div>
  </div>
</footer>
'''

WA_PATH = "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"

def tail(wa_wait=False):
    w = ' wait' if wa_wait else ''
    wa = f'''<a href="{WA_URL}" class="wa{w}" aria-label="WhatsApp" target="_blank" rel="noopener">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="{WA_PATH}"/></svg>
</a>
''' if WA_URL else ''
    return wa + f'''<div class="cursor" id="cursor" aria-hidden="true">Ansehen</div>
<div class="cookie dark" id="cookie-banner" role="dialog" aria-label="Cookies und Datenschutz">
  <p class="ch">Cookies &amp; Datenschutz</p>
  <p>Wir verwenden ausschließlich technisch notwendige Cookies. Mehr in unserer <a href="datenschutz.html">Datenschutzerklärung</a>.</p>
  <div class="btns"><button class="btn solid" id="cookie-accept">Akzeptieren</button><button class="btn" id="cookie-decline">Ablehnen</button></div>
</div>
<script src="assets/vendor/gsap.min.js?v=3.12.5"></script>
<script src="assets/vendor/ScrollTrigger.min.js?v=3.12.5"></script>
<script src="assets/vendor/lenis.min.js?v=1.1.13"></script>
<script src="assets/iveria.js?v={V}"></script>
</body>
</html>
'''

PAGES = []
def page(fname, pid, title, desc, main, preload=None, extra_before_header="", wa_wait=False, schema=(), crumb=None, noindex=False):
    global FAQ_CURRENT
    url = DOMAIN + '/' if fname == 'index.html' else f'{DOMAIN}/{fname}'
    sc = [org_schema()] + list(schema)
    if FAQ_CURRENT: sc.append(faq_schema(FAQ_CURRENT))
    if crumb: sc.append(breadcrumb(crumb, url))
    html = head(title, desc, preload, None if noindex else url, sc, noindex) + f'<body data-page="{pid}">\n' + extra_before_header + header() + '\n<main>\n' + main + '\n</main>\n\n' + FOOTER + '\n' + tail(wa_wait)
    FAQ_CURRENT = []
    html = img_dims(html)
    if not noindex: PAGES.append((fname, url))
    if fname == '404.html':
        html = html.replace('="assets/', '="/assets/').replace('="Images/', '="/Images/')
        html = re.sub(r'href="([a-z0-9-]+\.html)"', r'href="/\1"', html)
    open(os.path.join(OUT, fname), 'w').write(html)
    print('geschrieben', fname, len(html)//1024, 'KB')

from PIL import Image as _Img
def img_dims(h):
    """Setzt width/height aus der Bilddatei und loading=lazy auf allen Bildern außer dem ersten (Hero)."""
    def fix(m):
        tag = m.group(0); src = re.search(r'src="([^"]+)"', tag).group(1).lstrip('/')
        if 'width=' not in tag:
            try:
                w, hh = _Img.open(os.path.join(OUT, src)).size
                tag = tag.replace('<img ', f'<img width="{w}" height="{hh}" ', 1)
            except Exception: pass
        if 'loading=' not in tag and 'fetchpriority=' not in tag:
            tag = tag.replace('<img ', '<img loading="lazy" ', 1)
        return tag
    return re.sub(r'<img [^>]+>', fix, h)

def phero(img, alt, eyebrow, h1, p):
    return f'''<section class="phero">
  <div class="ph-window"><img src="{img}" alt="{alt}" fetchpriority="high"></div>
  <div class="ph-text wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p>{p}</p>
  </div>
</section>
'''

def faq(items, eyebrow="Häufige Fragen", h2="Was Sie wissen <em>sollten</em>."):
    FAQ_CURRENT.extend(items)
    ds = "\n".join(f'        <details><summary><span class="n">{i+1:02d}</span><span>{q}</span><span class="pm"></span></summary><div class="ans"><p>{a}</p></div></details>' for i,(q,a) in enumerate(items))
    return f'''<section class="faq pad">
  <div class="wrap grid">
    <div class="side"><p class="eyebrow">{eyebrow}</p><h2 class="h-l" data-split>{h2}</h2></div>
    <div>
{ds}
    </div>
  </div>
</section>
'''

def cta(eyebrow, h2, lead, buttons, door=None, door_alt=""):
    b = "".join(buttons)
    if door:
        return f'''<section class="cta dark pad">
  <div class="wrap grid">
    <div>
      <p class="eyebrow">{eyebrow}</p>
      <h2 data-split>{h2}</h2>
      <p class="lead">{lead}</p>
      <div class="btns">{b}</div>
    </div>
    <div class="door"><img src="{door}" alt="{door_alt}" loading="lazy"></div>
  </div>
</section>
'''
    return f'''<section class="cta dark pad center">
  <div class="wrap-narrow">
    {ARCHLINE}
    <p class="eyebrow">{eyebrow}</p>
    <h2 data-split>{h2}</h2>
    <p class="lead">{lead}</p>
    <div class="btns">{b}</div>
  </div>
</section>
'''

def stats(items, eyebrow=None, h2=None, cls="dark", regions=False):
    st = "\n".join(f'      <div class="stat"><b{(" data-to=%s data-suf=%s" % (chr(34)+str(to)+chr(34), chr(34)+suf+chr(34))) if to is not None else ""}>{disp}</b><span>{lab}</span></div>' for to,suf,disp,lab in items)
    hd = f'<p class="eyebrow">{eyebrow}</p>\n    <h2 class="h-l" data-split>{h2}</h2>' if h2 else ''
    rg = '''
    <div class="regions" id="regions" aria-label="Wien, Niederösterreich, Burgenland, Kärnten"><span>Wien</span><i>·</i><span>Niederösterreich</span><i>·</i><span>Burgenland</span><i>·</i><span>Kärnten</span></div>''' if regions else ''
    return f'''<section class="stats {cls} pad">
  <div class="wrap">
    {hd}
    <div class="sgrid">
{st}
    </div>{rg}
  </div>
</section>
'''

def feats(items):
    return '<ul class="feats">\n' + "\n".join(f'      <li class="feat"><span class="fn">{i+1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i,(t,d) in enumerate(items)) + '\n    </ul>'

def steps(items):
    li = "\n".join(f'      <li><span class="sn">{n}</span><h3>{t}</h3><p>{d}</p></li>' for n,(t,d) in zip(["I","II","III","IV","V","VI"], items))
    return f'<ol class="steps" style="--n:{len(items)}"><i class="bar" aria-hidden="true"></i>\n{li}\n    </ol>'

BTN = lambda href, text, cls="", ext="": f'<a href="{href}" class="btn {cls} magnetic"{ext}>{text}</a>'
PRIV = 'Mit dem Absenden stimmen Sie der Verarbeitung Ihrer Daten gemäß unserer <a href="datenschutz.html">Datenschutzerklärung</a> zu.'

# =====================================================================
# STARTSEITE
# =====================================================================
INTRO = '''<div class="intro" id="intro" aria-hidden="true">
  <div>
    <svg viewBox="0 0 100 100"><path class="a" id="introArch" d="M 22 80 L 22 50 Q 50 22 78 50 L 78 80"/><line class="i" id="introI" x1="50" y1="38" x2="50" y2="78"/></svg>
    <div class="nm" id="introName">IVERIA</div>
  </div>
  <button class="intro-skip" id="introSkip">Intro überspringen</button>
</div>
'''
index_main = f'''<section class="hero" id="hero" aria-label="Wo aus vier Wänden Zuhause wird">
  <div class="h-window" id="hWin"><img src="Images/hero-kaufen.webp" alt="Gründerzeithaus in Wien im Abendlicht" fetchpriority="high"></div>
  <h1 class="sr">Wo aus vier Wänden Zuhause wird.</h1>
  <div class="h-line h-l1 wrap" aria-hidden="true"><span class="in">Wo aus vier Wänden</span></div>
  <div class="h-line h-l2 wrap" aria-hidden="true"><span class="in"><em>Zuhause</em> wird.</span></div>
  <div class="h-copy wrap" id="hCopy">
    <div class="eyebrow">Immobilien · Projektvermarktung · Bewertung</div>
    <p>Persönliche Immobilienvermittlung in Wien, Niederösterreich, Burgenland und Kärnten. Mit Sorgfalt, Erfahrung und einem Auge für Details.</p>
    <a href="kaufen.html" class="link">Objekte entdecken {ARR}</a>
  </div>
  <div class="h-meta wrap" aria-hidden="true"><span class="sc">Scroll<i></i><svg class="finger" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"><g transform="rotate(180 12 12)"><path d="M22 14a8 8 0 0 1-8 8"/><path d="M18 11v-1a2 2 0 0 0-4 0"/><path d="M14 10V9a2 2 0 0 0-4 0v1"/><path d="M10 9.5V4a2 2 0 0 0-4 0v10"/><path d="M18 11a2 2 0 1 1 4 0v3a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/></g></svg></span><span>Wien &amp; Niederösterreich<br>Seit über 10 Jahren</span></div>
</section>

<section class="walls" id="walls">
  <div class="wrap grid">
    <div>
      <p class="eyebrow">Über uns</p>
      <h2 class="h-l">Klassische Maklerei mit <em>persönlicher</em> Note.</h2>
      <p class="lead">Über zehn Jahre Erfahrung im österreichischen Immobilienmarkt. Die Sorgfalt eines Familienunternehmens. Und das Verständnis, dass jede Immobilie eine Geschichte ist.</p>
    </div>
    <div class="house" id="house" aria-hidden="true">
      <svg viewBox="20 34 60 48">
        <line class="w" x1="22" y1="80" x2="22" y2="50"/>
        <line class="w" x1="22" y1="80" x2="78" y2="80"/>
        <line class="w" x1="78" y1="80" x2="78" y2="50"/>
        <path class="arch" d="M 22 50 Q 50 22 78 50"/>
        <line class="iline" x1="50" y1="38" x2="50" y2="78"/>
      </svg>
      <div class="lbl l1"><span>Erste Wand</span><b>Persönlich</b></div>
      <div class="lbl l2"><span>Zweite Wand</span><b>Sorgfalt</b></div>
      <div class="lbl l3"><span>Dritte Wand</span><b>Transparenz</b></div>
      <div class="lbl l4"><span>Das Dach</span><b>11 Jahre Erfahrung</b></div>
    </div>
  </div>
</section>

<section class="pad" id="objekte">
  <div class="wrap">
    <div class="head-split">
      <div><p class="eyebrow">Aktuelle Objekte</p><h2 class="h-xl" data-split>Eine Auswahl unserer <em>Vermittlungen</em>.</h2></div>
      <a href="kaufen.html" class="link">Alle Objekte {ARR}</a>
    </div>
    <div class="props stagger">
      <a href="kaufen.html" class="prop" data-cursor="Ansehen">
        <div class="ph"><img src="Images/objekt-altbau-stadtpark.webp" alt="Altbauzimmer mit Stuck und Luster" loading="lazy"></div>
        <div class="meta"><span>1010 Wien · Stadtpark</span><span>Kauf</span></div>
        <h3>Altbauwohnung am Stadtpark</h3>
        <div class="row"><span class="info">3 Zimmer · 92 m² · Stuck · Erstbezug nach Sanierung</span><span class="pr">€ 745.000</span></div>
      </a>
      <a href="kaufen.html" class="prop" data-cursor="Ansehen">
        <div class="ph"><img src="Images/objekt-haus-perchtoldsdorf.webp" alt="Haus mit großem Garten" loading="lazy"></div>
        <div class="meta"><span>2380 Perchtoldsdorf</span><span>Kauf</span></div>
        <h3>Familienhaus mit Garten</h3>
        <div class="row"><span class="info">5 Zimmer · 168 m² · 620 m² Grund · Bj. 1962, saniert</span><span class="pr">€ 1.290.000</span></div>
      </a>
      <a href="kaufen.html" class="prop" data-cursor="Ansehen">
        <div class="ph"><img src="Images/objekt-velden-seeblick.webp" alt="Haus mit Terrasse über einem See im Abendlicht" loading="lazy"></div>
        <div class="meta"><span>9220 Velden · Wörthersee</span><span>Kauf</span></div>
        <h3>Penthouse mit Seeblick</h3>
        <div class="row"><span class="info">4 Zimmer · 142 m² · Dachterrasse · Wörtherseeblick</span><span class="pr">€ 1.850.000</span></div>
      </a>
    </div>
  </div>
</section>

<section class="svc" id="leistungen" style="padding-bottom:10vh">
  <div class="wrap">
    <div class="head-split" style="padding-top:6vh"><div><p class="eyebrow">Leistungen</p><h2 class="h-xl" data-split>Drei Wege, <em>ein</em> Ansprechpartner.</h2></div><p>Ob Sie verkaufen, ein Projekt vermarkten oder ein Zuhause suchen: Sie haben einen festen Ansprechpartner. Keine Hotline, kein Fallmanager.</p></div>
    <div class="cards">
      <article class="card">
        <div class="img"><img src="Images/hero-verkaufen.webp" alt="Wohnzimmer mit Blick über die Stadt" loading="lazy"></div>
        <div class="txt"><div><span class="eyebrow">Für Eigentümer</span><h3>Verkaufen &amp; <em>Vermieten</em></h3><p>Vom Erstgespräch über Bewertung und Vermarktung bis zur Schlüsselübergabe. Volle Vermarktung ohne Aufpreis. Persönlich, sorgfältig und auf Erfolgsbasis.</p>
          <ul><li>Marktwerteinschätzung</li><li>Exposé, Fotos und Vermarktung</li><li>Besichtigungen und Verhandlung</li></ul>
          <a href="verkaufen.html" class="link">Mehr erfahren {ARR}</a></div><div class="num">I</div></div>
      </article>
      <article class="card">
        <div class="img"><img src="Images/hero-bautraeger.webp" alt="Neues Wohnprojekt in der Abenddämmerung" loading="lazy"></div>
        <div class="txt"><div><span class="eyebrow">Für Bauträger</span><h3>Projekte vermarkten, die <em>ankommen</em>.</h3><p>Von der Konzeptphase bis zur letzten Schlüsselübergabe. Wir vermarkten komplette Wohnprojekte mit der Sorgfalt, mit der sie geplant wurden.</p>
          <ul><li>Begleitung ab der Konzeptphase</li><li>Vermarktung kompletter Wohnprojekte</li><li>Individuelle Konditionen</li></ul>
          <a href="bautraeger.html" class="link">Mehr erfahren {ARR}</a></div><div class="num">II</div></div>
      </article>
      <article class="card">
        <div class="img"><img src="Images/hero-bewertung.webp" alt="Gründerzeitfassade mit schmiedeeisernem Balkon" loading="lazy"></div>
        <div class="txt"><div><span class="eyebrow">Für Käufer</span><h3>Suchen &amp; <em>Kaufen</em></h3><p>Aktuelle Objekte in Wien, Niederösterreich, Burgenland und Kärnten. Kuratiert vermittelt. Auf Wunsch auch ein persönlicher Suchauftrag, bevor Objekte öffentlich werden.</p>
          <ul><li>Kuratierte Objekte</li><li>Persönlicher Suchauftrag</li><li>Zugang vor der Veröffentlichung</li></ul>
          <a href="kaufen.html" class="link">Objekte ansehen {ARR}</a></div><div class="num">III</div></div>
      </article>
    </div>
  </div>
</section>

''' + stats([obj_stat(120),(10,"","10","Jahre Erfahrung"),(4,"","4","Bundesländer"),(100,"%","100%","Erfolgsbasiert")],
            "Auf einen Blick", "Klassische Werte. <em>Messbare</em> Ergebnisse.", regions=True) + "\n" + faq([
  ("Was kostet die Vermittlung?","Unsere Provision orientiert sich an der Immobilienmaklerverordnung (IMV). Üblich sind 3 % zzgl. 20 % USt. vom Käufer und Verkäufer. Sie zahlen nur im Erfolgsfall. Bei Bauträgermandaten vereinbaren wir individuelle Konditionen."),
  ("In welchen Regionen sind Sie tätig?","Schwerpunkt Wien, Niederösterreich, Burgenland und Kärnten. Bei Mandaten außerhalb dieser Regionen arbeiten wir mit ausgewählten lokalen Partnern zusammen. Die Betreuung bleibt aber bei uns."),
  ("Wie lange dauert ein Verkauf üblicherweise?","Vom Erstgespräch bis zur Übergabe rechnen wir mit drei bis sechs Monaten. Abhängig von Marktlage, Preisstellung und Komplexität. Wir geben Ihnen im Erstgespräch eine realistische Einschätzung."),
  ("Was unterscheidet Sie von größeren Maklerketten?","Wir nehmen weniger Mandate an, dafür betreuen wir jedes persönlich. Sie haben einen festen Ansprechpartner. Keine Hotline, kein Fallmanager. Bei jedem Termin sind wir selbst vor Ort."),
  ("Bieten Sie auch Bewertungen ohne Verkaufsabsicht an?","Ja. Eine Marktwerteinschätzung kostet zwischen € 290 und € 490. Abhängig vom Aufwand. Bei einem späteren Verkaufsmandat verrechnen wir den Betrag mit der Provision."),
]) + "\n" + cta("Erstgespräch", "Bereit, ein Zuhause zu finden. Oder <em>loszulassen</em>.", "Schreiben Sie uns kurz, was Sie planen. Wir melden uns innerhalb von 24 Stunden.",
     [BTN("kontakt.html","Kontakt aufnehmen →","solid"), BTN("bewertung.html","Bewertung anfragen")], door="Images/hero-kontakt.webp", door_alt="Eingangsportal mit Bogentür am Abend") + '''
<!-- Netlify Form Detection (versteckt) -->
<form name="kontakt" netlify netlify-honeypot="bot-field" hidden>
    <input type="text" name="name"/>
    <input type="email" name="email"/>
    <input type="tel" name="telefon"/>
    <select name="anliegen"><option></option></select>
    <textarea name="nachricht"></textarea>
</form>
<form name="bewertung" netlify netlify-honeypot="bot-field" hidden>
    <input type="text" name="name"/>
    <input type="email" name="email"/>
    <input type="tel" name="telefon"/>
    <select name="typ"><option></option></select>
    <input type="text" name="adresse"/>
    <input type="number" name="flaeche"/>
    <input type="number" name="zimmer"/>
    <input type="number" name="baujahr"/>
    <select name="zustand"><option></option></select>
    <textarea name="besonderheiten"></textarea>
</form>
<form name="suchauftrag" netlify netlify-honeypot="bot-field" hidden>
    <input type="text" name="name"/>
    <input type="email" name="email"/>
    <select name="typ"><option></option></select>
    <select name="region"><option></option></select>
    <input type="text" name="budget"/>
    <textarea name="wuensche"></textarea>
</form>
'''
page("index.html","index","Immobilienmakler Wien &amp; Projektvermarktung · Iveria Immobilien",
     "Iveria Immobilien — persönliche Immobilienvermittlung und Projektvermarktung in Wien, Niederösterreich, Burgenland und Kärnten. Wo aus vier Wänden Zuhause wird.",
     index_main, preload="Images/hero-kaufen.webp", wa_wait=True,
     schema=[{"@context":"https://schema.org","@type":"WebSite","@id":f"{DOMAIN}/#website","url":DOMAIN+"/","name":cfg('markenname'),"inLanguage":"de-AT","publisher":{"@id":ORG_ID}}])

# =====================================================================
# VERKAUFEN
# =====================================================================
verkaufen = phero("Images/hero-verkaufen.webp","Wohnzimmer mit Blick über die Stadt","Für Eigentümer","Verkaufen &amp; <em>Vermieten</em>","Vom Erstgespräch bis zur Schlüsselübergabe. Volle Vermarktung ohne Aufpreis. Persönlich, sorgfältig und auf Erfolgsbasis.") + f'''
<section class="statement pad center">
  <div class="wrap-narrow">
    <p class="eyebrow">Unser Ansatz</p>
    <h2 class="h-xl" data-split>Ihre Immobilie verdient mehr als <em>Standard</em>.</h2>
    <p class="lead" data-rise>Wir nehmen weniger Mandate an, dafür betreuen wir jedes persönlich. Bei jedem Termin sind wir selbst vor Ort. Sie haben einen festen Ansprechpartner. Vom ersten Gespräch bis zur Schlüsselübergabe.</p>
  </div>
</section>

<section class="dark pad">
  <div class="wrap">
    <div class="head-split"><div><p class="eyebrow">Wie wir arbeiten</p><h2 class="h-xl" data-split>In fünf Schritten zum <em>Verkauf</em>.</h2></div></div>
    {steps([("Erstgespräch","Kostenfrei und unverbindlich. Wir lernen Sie und Ihre Immobilie kennen."),("Bewertung","Marktwert auf Basis aktueller Vergleichsdaten und Lage."),("Vermarktung","Exposé, professionelle Fotografie, Inserate und persönliche Anfragen."),("Besichtigungen","Wir filtern, organisieren und begleiten. Sie bleiben außen vor."),("Abschluss","Vom Notartermin bis zur Schlüsselübergabe.")])}
  </div>
</section>

<section class="pad">
  <div class="wrap">
    <div class="editorial">
      <div class="ed-img arch"><img src="Images/leistungen-verkaufen.webp" alt="Ruhiges Wohnzimmer mit Samtsofa" loading="lazy"></div>
      <div class="ed-txt">
        <span class="eyebrow">Inkludierte Leistungen</span>
        <h2 class="h-xl" data-split>Sechs Leistungen. <em>Eine</em> Provision.</h2>
        <p>Keine Pakete, keine Aufpreise. Was zur professionellen Vermarktung gehört, ist drin. Marktwertanalyse, Architekturfotografie, Exposé, Inserate, Besichtigungen, Bonitätsprüfung und Notarbegleitung.</p>
        <a href="kontakt.html" class="link">Erstgespräch vereinbaren {ARR}</a>
      </div>
    </div>
  </div>
</section>

<section class="warm pad">
  <div class="wrap">
    <div class="head-split"><div><p class="eyebrow">Im Detail</p><h2 class="h-xl" data-split>Was inkludiert ist.</h2></div></div>
    {feats([("Marktwertanalyse","Realistische Preisermittlung auf Basis aktueller Vergleichsdaten, Lage, Zustand und Markttrends. Keine geschönten Schätzungen."),("Architekturfotografie","Professionelle Bilder, die das Beste der Immobilie zeigen. Bei richtigem Licht, mit Auge für Details und Atmosphäre."),("Exposé &amp; Inserate","Hochwertiges Exposé in Print- und Digitalqualität sowie Vermarktung über alle relevanten Plattformen. willhaben, ImmoScout, Bestlage und mehr."),("Besichtigungen","Wir filtern Interessenten vor, koordinieren Termine und führen Sie persönlich durch die Immobilie."),("Bonitätsprüfung","Wir prüfen die Zahlungsfähigkeit der ernsthaften Käufer, bevor Verträge in Bewegung gesetzt werden."),("Notarbegleitung","Wir koordinieren mit dem Notar, prüfen den Kaufvertrag in Ihrem Sinne und begleiten Sie zum Termin.")])}
  </div>
</section>

''' + cta("Provision","Sie zahlen nur im <em>Erfolgsfall</em>.","Unsere Provision orientiert sich an der Immobilienmaklerverordnung (IMV). Üblich sind 3 % zzgl. 20 % USt. vom Käufer und Verkäufer. Keine Vorabpauschalen, keine versteckten Gebühren. Wenn nicht verkauft wird, zahlen Sie nichts.",
  [BTN("kontakt.html","Erstgespräch vereinbaren →","solid")]) + "\n" + faq([
  ("Was kostet ein Verkauf konkret?","Sie zahlen nur im Erfolgsfall. 3 % des Kaufpreises zzgl. 20 % USt. Also brutto 3,6 %. Beispiel: Bei einem Kaufpreis von € 500.000 entstehen Kosten von € 18.000 brutto. Vorab fallen keine Kosten an."),
  ("Wie lange dauert ein Verkauf üblicherweise?","Vom Erstgespräch bis zur Übergabe rechnen wir mit drei bis sechs Monaten. Abhängig von Marktlage, Preisstellung und Komplexität. Wir geben Ihnen im Erstgespräch eine realistische Einschätzung."),
  ("Was unterscheidet Sie von Maklerketten?","Wir nehmen weniger Mandate an, dafür betreuen wir jedes persönlich. Sie haben einen festen Ansprechpartner. Keine Hotline, kein Fallmanager. Bei jedem Termin sind wir selbst vor Ort."),
  ("Werden Sie auch außerhalb von Wien tätig?","Ja. Schwerpunkt ist Wien, Niederösterreich, Burgenland und Kärnten. Bei besonderen Mandaten arbeiten wir auch in anderen Regionen. Kommen Sie einfach auf uns zu."),
  ("Können Sie auch Mietobjekte vermarkten?","Ja, wir vermarkten auch Mietwohnungen und Geschäftsflächen. Die Vorgehensweise ist ähnlich, die Provision orientiert sich an branchenüblichen Sätzen."),
  ("Was passiert, wenn ich nicht verkaufe?","Dann zahlen Sie nichts. Unsere Tätigkeit ist erfolgsbasiert. Sollten Sie aus unvorhergesehenen Gründen ausscheiden müssen, finden wir eine faire Lösung."),
])
page("verkaufen.html","verkaufen","Immobilie verkaufen in Wien mit Makler · Iveria Immobilien","Persönliche Vermarktung Ihrer Immobilie in Österreich. Vom Erstgespräch bis zur Schlüsselübergabe.", verkaufen, preload="Images/hero-verkaufen.webp", crumb="Verkaufen & Vermieten",
     schema=[service("Verkaufen & Vermieten", "Vom Erstgespräch bis zur Schlüsselübergabe. Volle Vermarktung ohne Aufpreis. Persönlich, sorgfältig und auf Erfolgsbasis.", f"{DOMAIN}/verkaufen.html")])

# =====================================================================
# KAUFEN
# =====================================================================
kaufen = phero("Images/hero-kaufen.webp","Gründerzeithaus in Wien im Abendlicht","Für Käufer","Suchen &amp; <em>Kaufen</em>","Aktuelle Objekte in Wien, Niederösterreich, Burgenland und Kärnten. Kuratiert vermittelt. Auf Wunsch auch ein persönlicher Suchauftrag, bevor Objekte öffentlich werden.") + f'''
<section class="pad">
  <div class="wrap">
    <div class="empty">
      {ARCHLINE}
      <p class="eyebrow">Aktuell verfügbar</p>
      <h2 class="h-xl" data-split>Zurzeit keine <em>Objekte</em> in Vermarktung.</h2>
      <p data-rise>Momentan vermarkten wir keine Objekte öffentlich. Schauen Sie gerne bald wieder vorbei — oder hinterlegen Sie unverbindlich Ihre Suchanfrage, und wir melden uns, sobald etwas Passendes für Sie dabei ist.</p>
      <div class="btns"><a href="#suchauftrag" class="btn magnetic">Suchanfrage stellen →</a></div>
    </div>
  </div>
</section>

<section class="dark pad" id="suchauftrag">
  <div class="wrap">
    <div class="editorial" style="align-items:start">
      <div class="ed-txt">
        <p class="eyebrow">Suchauftrag</p>
        <h2 class="h-xl" data-split>Bevor wir öffentlich vermarkten. Fragen wir <em>Sie</em>.</h2>
        <p>Viele unserer schönsten Objekte erscheinen nie auf einer Plattform. Vermögende Verkäufer schätzen Diskretion, Bauträger geben uns Vorab-Tipps zu kommenden Projekten.</p>
        <p>Wenn Sie uns Ihre Wünsche schildern, kontaktieren wir Sie persönlich, sobald ein passendes Objekt verfügbar wird. Oft Wochen, bevor es öffentlich beworben wird.</p>
      </div>
      <form class="form" data-form="suchauftrag" name="suchauftrag" method="POST" action="/danke.html" data-netlify="true" netlify-honeypot="bot-field" data-rise>
        <input type="hidden" name="form-name" value="suchauftrag">
        <div class="hp" aria-hidden="true"><label>Nicht ausfüllen <input name="bot-field" tabindex="-1" autocomplete="off"></label></div>
        <div class="frow">
          <div><label for="s-name">Name</label><input type="text" id="s-name" name="name" autocomplete="name" required></div>
          <div><label for="s-email">E-Mail</label><input type="email" id="s-email" name="email" autocomplete="email" required></div>
        </div>
        <div class="frow three">
          <div><label for="s-typ">Typ</label><select id="s-typ" name="typ"><option>Wohnung</option><option>Haus</option><option>Anlage</option><option>Grundstück</option><option>Gewerbe</option></select></div>
          <div><label for="s-region">Region</label><select id="s-region" name="region"><option>Wien</option><option>Niederösterreich</option><option>Burgenland</option><option>Kärnten</option><option>Andere</option></select></div>
          <div><label for="s-budget">Budget</label><input type="text" id="s-budget" name="budget" placeholder="bis € 800.000"></div>
        </div>
        <div><label for="s-wuensche">Was ist Ihnen wichtig?</label><textarea id="s-wuensche" name="wuensche" placeholder="Größe, Lage, besondere Wünsche, Zeithorizont"></textarea></div>
        <p class="note">{PRIV}</p>
        <button type="submit" class="btn solid">Suchauftrag senden →</button>
      </form>
    </div>
  </div>
</section>
'''
page("kaufen.html","kaufen","Immobilie kaufen &amp; Suchauftrag · Iveria Immobilien","Aktuelle Immobilien in Wien, Niederösterreich, Burgenland und Kärnten. Kuratiert vermittelt.", kaufen, preload="Images/hero-kaufen.webp", crumb="Suchen & Kaufen")

# =====================================================================
# BAUTRÄGER
# =====================================================================
bautraeger = phero("Images/hero-bautraeger.webp","Neues Wohnprojekt in der Abenddämmerung","Für Bauträger","Projekte vermarkten, die <em>ankommen</em>.","Von der Konzeptphase bis zur letzten Schlüsselübergabe. Wir vermarkten Ihre Wohnprojekte mit der Sorgfalt, mit der sie geplant wurden.") + f'''
<section class="pad">
  <div class="wrap">
    <div class="editorial">
      <div class="ed-img"><img src="Images/ansatz-bautraeger.webp" alt="Architekturmodell eines Wohnbaus auf Plänen" loading="lazy"></div>
      <div class="ed-txt">
        <span class="eyebrow">Unser Ansatz</span>
        <h2 class="h-xl" data-split>Wir verstehen <em>Bauträgerdenken</em>.</h2>
        <p>Wir wissen, wie wichtig Liquidität in der Vermarktungsphase ist. Wir wissen, dass jede unverkaufte Einheit Zinsen kostet. Und wir wissen, dass eine ruhige, strukturierte Vermarktung mehr wert ist als laute Werbung.</p>
        <p>Deshalb bekommen Sie bei uns einen festen Ansprechpartner für das gesamte Projekt. Keine wechselnden Sachbearbeiter, keine Eskalationshotlines.</p>
        <a href="kontakt.html" class="link">Projekt besprechen {ARR}</a>
      </div>
    </div>
  </div>
</section>

''' + stats([(3,"","3","Aktive Mandate"),(52,"+","52+","Vermarktete Einheiten"),(100,"<small>%</small>","100<small>%</small>","Vor Übergabe verkauft"),(None,"","9 Mo","Ø Vermarktungszeit")],
            "Auf einen Blick","Klassische Werte. <em>Messbare</em> Ergebnisse.") + f'''
<section class="warm pad">
  <div class="wrap">
    <div class="head-split"><div><p class="eyebrow">Unsere Leistungen</p><h2 class="h-xl" data-split>Sechs Bereiche. <em>Ein</em> Ansprechpartner.</h2></div></div>
    {feats([("Konzeptberatung","Frühzeitige Einschätzung von Wohnungsmix, Preisstellung und Zielgruppe. Bevor der Spaten in der Erde steckt."),("Pre-Marketing","Off-Market-Vermarktung an unsere Bestandskunden und Suchaufträge. Oft Monate vor öffentlichem Verkaufsstart."),("Verkaufsunterlagen","Hochwertige Exposés, Visualisierungen und Online-Präsenz. Alles aus einem Guss, alles mit Ihrer Markenidentität."),("Reservierung &amp; Abwicklung","Wir führen die Reservierungslisten, kommunizieren mit Käufern und koordinieren Notartermine."),("Bonitätsprüfung","Wir prüfen die Zahlungsfähigkeit aller Reservierer, bevor Verträge unterschrieben werden. Sie bekommen nur ernsthafte Käufer."),("Übergabe-Begleitung","Wir koordinieren die Übergabetermine, dokumentieren Mängel und sorgen für eine reibungslose Übergabe.")])}
  </div>
</section>

<section class="pad">
  <div class="wrap">
    <div class="head-split"><div><p class="eyebrow">Aktuelle Mandate</p><h2 class="h-xl" data-split>Eine Auswahl unserer <em>Projekte</em>.</h2></div></div>
    <div class="props three">
      <div class="prop">
        <div class="ph"><img src="Images/projekt-huetteldorf.webp" alt="Gründerzeitfassade in Wien" loading="lazy"></div>
        <div class="meta"><span>1140 Wien</span><span>In Vermarktung</span></div>
        <h3>Wohnpark Hütteldorf</h3>
        <p class="info">24 Einheiten · 2 bis 4 Zimmer · Übergabe Q3 2027 · Sanierter Altbestand mit Neubauergänzung.</p>
      </div>
      <div class="prop">
        <div class="ph"><img src="Images/projekt-klostergarten.webp" alt="Haus mit Garten und Weg" loading="lazy"></div>
        <div class="meta"><span>3400 Klosterneuburg</span><span>Reservierungsphase</span></div>
        <h3>Klostergarten</h3>
        <p class="info">12 Einheiten · 3 bis 5 Zimmer · Übergabe Q1 2027 · Reihenhäuser mit Eigengärten.</p>
      </div>
      <div class="prop">
        <div class="ph"><img src="Images/projekt-velden.webp" alt="Haus am See vor Bergwald in der Dämmerung" loading="lazy"></div>
        <div class="meta"><span>9220 Velden</span><span>Off-Market</span></div>
        <h3>Seenähe Velden</h3>
        <p class="info">8 Einheiten · 3 bis 5 Zimmer · Übergabe Q2 2028 · Premium-Apartments mit Bergblick.</p>
      </div>
    </div>
  </div>
</section>

''' + cta("Erstgespräch","Sie haben ein Projekt. Wir haben <em>Zeit</em>.","Erzählen Sie uns davon. Wir melden uns innerhalb von 24 Stunden für ein erstes Gespräch. Vertraulich und unverbindlich.",
  [BTN("mailto:projekte@iveria.at","projekte@iveria.at →","solid"), BTN("kontakt.html","Kontaktformular")], door="Images/hero-bautraeger.webp", door_alt="Wohnprojekt in der Abenddämmerung")
page("bautraeger.html","bautraeger","Bauträgervermarktung Wien &amp; Österreich · Iveria Immobilien","Vermarktung kompletter Wohnprojekte für Bauträger in Österreich. Konzept, Pre-Marketing, Reservierung und Übergabe.", bautraeger, preload="Images/hero-bautraeger.webp", crumb="Bauträgervermarktung",
     schema=[service("Bauträgervermarktung", "Von der Konzeptphase bis zur letzten Schlüsselübergabe. Wir vermarkten Ihre Wohnprojekte mit der Sorgfalt, mit der sie geplant wurden.", f"{DOMAIN}/bautraeger.html")])

# =====================================================================
# BEWERTUNG
# =====================================================================
bewertung = phero("Images/hero-bewertung.webp","Gründerzeitfassade mit schmiedeeisernem Balkon","Marktwert","Was ist meine Immobilie <em>wert</em>?","Schnell, persönlich oder vor Ort. Wir bieten zwei Wege zur ehrlichen Marktwerteinschätzung. Wählen Sie, was zu Ihnen passt.") + f'''
<section class="pad">
  <div class="wrap">
    <div class="editorial">
      <div class="ed-img"><img src="Images/bewertung-online.webp" alt="Essbereich mit rundem Tisch in einer Wohnung" loading="lazy"></div>
      <div class="ed-txt">
        <span class="eyebrow">Variante 1</span>
        <h2 class="h-xl" data-split>Schnellbewertung <em>online</em>.</h2>
        <p>Sie füllen in fünf Minuten unser Formular aus, wir melden uns innerhalb von 48 Stunden mit einer ersten, fundierten Einschätzung. Kostenfrei und unverbindlich.</p>
        <ul class="blist">
          <li><strong>Innerhalb von 48 Stunden</strong>Erste fundierte Einschätzung per E-Mail.</li>
          <li><strong>Kostenfrei und unverbindlich</strong>Keine versteckten Gebühren, keine Verkaufsverpflichtung.</li>
          <li><strong>Spannweite, keine Punktschätzung</strong>Mit Empfehlung zum nächsten Schritt.</li>
        </ul>
        <a href="#schnellbewertung" class="link">Formular ausfüllen <span class="ar">↓</span></a>
      </div>
    </div>
    <div class="editorial reverse">
      <div class="ed-img arch"><img src="Images/bewertung-vor-ort.webp" alt="Historische Hausfassade in Wien" loading="lazy"></div>
      <div class="ed-txt">
        <span class="eyebrow">Variante 2</span>
        <h2 class="h-xl" data-split>Bewertung <em>vor Ort</em>.</h2>
        <p>Für eine genauere Einschätzung kommen wir vor Ort, sehen uns Ihre Immobilie persönlich an und erstellen einen schriftlichen Bewertungsbericht.</p>
        <ul class="blist">
          <li><strong>Persönliche Besichtigung</strong>Wir kommen zu Ihnen, mit Zeit für Details und Fragen.</li>
          <li><strong>Schriftlicher Bewertungsbericht</strong>Ausführliche Dokumentation mit Vergleichsobjekten.</li>
          <li><strong>€ 290 bis € 490</strong>Bei späterem Verkaufsmandat verrechenbar.</li>
        </ul>
        <a href="kontakt.html" class="link">Termin anfragen {ARR}</a>
      </div>
    </div>
  </div>
</section>

<section id="schnellbewertung" class="dark pad">
  <div class="wrap-narrow">
    <div style="text-align:center;margin-bottom:5rem">
      <p class="eyebrow">Schnellbewertung</p>
      <h2 class="h-xl" data-split style="margin:1.4rem auto 1.6rem;max-width:18ch">Erzählen Sie uns von Ihrer <em>Immobilie</em>.</h2>
      <p class="lead" style="margin:0 auto">Je genauer Ihre Angaben, desto präziser unsere Einschätzung. Wir melden uns innerhalb von 48 Stunden.</p>
    </div>
    <form class="form" data-form="bewertung" name="bewertung" method="POST" action="/danke.html" data-netlify="true" netlify-honeypot="bot-field" data-rise>
      <input type="hidden" name="form-name" value="bewertung">
      <div class="hp" aria-hidden="true"><label>Nicht ausfüllen <input name="bot-field" tabindex="-1" autocomplete="off"></label></div>
      <div class="frow">
        <div><label for="b-name">Name *</label><input type="text" id="b-name" name="name" autocomplete="name" required></div>
        <div><label for="b-email">E-Mail *</label><input type="email" id="b-email" name="email" autocomplete="email" required></div>
      </div>
      <div class="frow">
        <div><label for="b-tel">Telefon</label><input type="tel" id="b-tel" name="telefon" autocomplete="tel"></div>
        <div><label for="b-typ">Objekttyp *</label><select id="b-typ" name="typ" required><option>Wohnung</option><option>Einfamilienhaus</option><option>Doppelhaushälfte</option><option>Reihenhaus</option><option>Mehrparteienhaus</option><option>Anlage</option><option>Grundstück</option><option>Gewerbe</option></select></div>
      </div>
      <div class="frow three">
        <div><label for="b-adresse">Adresse / PLZ *</label><input type="text" id="b-adresse" name="adresse" required placeholder="1010 Wien"></div>
        <div><label for="b-flaeche">Wohnfläche (m²) *</label><input type="number" id="b-flaeche" name="flaeche" required></div>
        <div><label for="b-zimmer">Zimmer</label><input type="number" id="b-zimmer" name="zimmer"></div>
      </div>
      <div class="frow">
        <div><label for="b-bj">Baujahr</label><input type="number" id="b-bj" name="baujahr" placeholder="1995"></div>
        <div><label for="b-zustand">Zustand</label><select id="b-zustand" name="zustand"><option>Erstbezug / neuwertig</option><option>Sehr gut</option><option>Gut</option><option>Sanierungsbedürftig</option><option>Abbruchhaus / Grundstück</option></select></div>
      </div>
      <div><label for="b-besonderheiten">Besonderheiten</label><textarea id="b-besonderheiten" name="besonderheiten" placeholder="Balkon, Terrasse, Lift, Tiefgarage, Garten, Energieklasse, kürzlich renoviert, Denkmalschutz, Vermietung"></textarea></div>
      <p class="note">{PRIV} * = Pflichtfeld</p>
      <button type="submit" class="btn solid">Bewertung anfordern →</button>
    </form>
  </div>
</section>

<section class="pad">
  <div class="wrap-prose prose">
    <h2 data-split>Wie zuverlässig ist eine Online-Bewertung?</h2>
    <p>Eine Online-Bewertung gibt Ihnen eine fundierte <strong>Spannweite</strong>. Keine exakte Zahl. Wir basieren unsere Einschätzung auf aktuellen Vergleichsobjekten in Ihrer Region, Markttrends und Ihren Angaben.</p>
    <p>Für eine punktgenaue Bewertung — etwa für Erbschaftsfälle, Schenkungen oder Kreditverlängerungen — empfehlen wir die <strong>Bewertung vor Ort</strong>. Dabei prüfen wir Bausubstanz, Lage, Ausstattung und rechtliche Aspekte persönlich.</p>
    <p>In beiden Fällen gilt: <strong>Wir verschönern nichts</strong>. Eine ehrliche Einschätzung dient Ihnen langfristig mehr als eine geschönte Zahl, die später am Markt nicht zu halten ist.</p>
  </div>
</section>
'''
page("bewertung.html","bewertung","Immobilienbewertung Wien, online kostenlos · Iveria Immobilien","Marktwerteinschätzung Ihrer Immobilie. Kostenfrei online oder mit persönlichem Termin vor Ort.", bewertung, preload="Images/hero-bewertung.webp", crumb="Bewertung",
     schema=[service("Immobilienbewertung", "Schnell, persönlich oder vor Ort. Wir bieten zwei Wege zur ehrlichen Marktwerteinschätzung. Wählen Sie, was zu Ihnen passt.", f"{DOMAIN}/bewertung.html",
        offers=[{"@type":"Offer","name":"Schnellbewertung online","description":"Kostenfrei und unverbindlich.","price":"0","priceCurrency":"EUR"},
                {"@type":"Offer","name":"Bewertung vor Ort","description":"Persönliche Besichtigung und schriftlicher Bewertungsbericht. Bei späterem Verkaufsmandat verrechenbar.",
                 "priceSpecification":{"@type":"PriceSpecification","minPrice":290,"maxPrice":490,"priceCurrency":"EUR"}}])])

# =====================================================================
# ÜBER UNS
# =====================================================================
ueber = phero("Images/hero-ueber-uns.webp","Arbeitszimmer mit Ledersessel und Bücherwand","Über uns","Klassische Maklerei mit <em>persönlicher</em> Note.","Über zehn Jahre Erfahrung im österreichischen Immobilienmarkt. Die Sorgfalt eines Familienunternehmens. Und das Verständnis, dass jede Immobilie eine Geschichte ist.") + f'''
<section class="pad">
  <div class="wrap-prose prose">
    <h2 class="h-l" data-split style="font-size:clamp(2.2rem,4vw,3.4rem)">Warum Iveria Immobilien?</h2>
    <p>Wer heute in Österreich eine Immobilie kauft oder verkauft, muss sich oft zwischen zwei Welten entscheiden. Die großen Maklerketten mit ihrer Effizienz, aber wechselnden Sachbearbeitern. Oder kleine Einzelmakler, die persönlich sind, aber oft am Vermarktungshandwerk scheitern.</p>
    <p>Wir wollten eine dritte Option schaffen. <strong>Klassische Maklerei mit den Qualitäten beider Welten.</strong> Die Sorgfalt eines Familienunternehmens, kombiniert mit professioneller Vermarktung. Architekturfotografie, hochwertige Exposés, klare Reservierungsstrukturen.</p>
    <p>Was uns von größeren Anbietern unterscheidet: Sie sprechen bei jedem Termin mit der gleichen Person. Wir nehmen weniger Mandate an, weil wir jedes selbst betreuen wollen. Und weil eine Immobilie zu verkaufen oder zu kaufen eine der wichtigsten Lebensentscheidungen ist.</p>
  </div>
</section>

<section class="dark pad quote">
  <div class="wrap-narrow">
    {ARCHLINE}
    <p class="eyebrow">Unser Versprechen</p>
    <blockquote>„Wir behandeln jede Immobilie, jeden Verkauf und jeden Kauf so, als wäre es unser eigenes Zuhause."</blockquote>
  </div>
</section>

<section class="pad">
  <div class="wrap">
    <div class="head-split"><div><p class="eyebrow">Unsere Werte</p><h2 class="h-xl" data-split>Drei Versprechen, die wir <em>ernst</em> meinen.</h2></div></div>
    <div class="vals">
      <div class="val"><div class="fn">I</div><h3>Wir handeln in Ihrem Sinne.</h3><p>Jede Empfehlung dient der Sache, nicht der Provision. Wir sagen offen, wann ein Verkauf nicht der richtige Zeitpunkt ist. Auch wenn das gegen unser kurzfristiges Interesse spricht.</p></div>
      <div class="val"><div class="fn">II</div><h3>Wir nehmen uns Zeit.</h3><p>Eine Immobilie zu kaufen oder verkaufen ist eine Lebensentscheidung. Wir behandeln sie auch so. Keine Massenabfertigung, keine Standardexposés, keine Drei-Termine-pro-Tag-Mentalität.</p></div>
      <div class="val"><div class="fn">III</div><h3>Wir bleiben verbunden.</h3><p>Auch nach dem Notartermin sind wir erreichbar. Bei Fragen zur Übergabe, zur ersten Heizperiode, zur Hausordnung. Wir verschwinden nicht, wenn die Provision überwiesen ist.</p></div>
    </div>
  </div>
</section>

''' + stats([obj_stat(80),(10,"+","10+","Jahre Erfahrung"),(3,"","3","Aktive Bauträgermandate"),(4,"","4","Bundesländer")], cls="warm") + f'''
<section class="pad">
  <div class="wrap">
    <div class="editorial">
      <div class="ed-img arch"><img src="Images/qualifikation-ueberuns.webp" alt="Schreibtisch in einem ruhigen Büro" loading="lazy"></div>
      <div class="ed-txt">
        <span class="eyebrow">Qualifikation</span>
        <h2 class="h-xl" data-split>Lizenziert. Geprüft. <em>Versichert</em>.</h2>
        <p>Wir sind keine Quereinsteiger. Hinter Iveria Immobilien steht über ein Jahrzehnt Erfahrung im österreichischen Immobilienmarkt. Mit allen rechtlichen, steuerlichen und vertraglichen Anforderungen, die dazugehören.</p>
        <ul class="blist">
          <li><strong>Befähigungsnachweis Immobilientreuhänder</strong>Gewerbeberechtigung gemäß § 117 GewO. Maklerei, Verwaltung und Bauträger.</li>
          <li><strong>Mitgliedschaft Wirtschaftskammer</strong>Eingetragen in die Fachgruppe der Immobilien- und Vermögenstreuhänder Wien.</li>
          <li><strong>Berufshaftpflichtversicherung</strong>Volle Deckung gemäß den Anforderungen des österreichischen Maklergesetzes (MaklerG).</li>
        </ul>
      </div>
    </div>
  </div>
</section>

''' + cta("Lernen Sie uns kennen","Ein Erstgespräch sagt mehr als jede <em>Webseite</em>.","Schreiben Sie uns oder rufen Sie an. Wir freuen uns auf das Gespräch.",
  [BTN("kontakt.html","Kontakt aufnehmen →","solid"), BTN("bewertung.html","Bewertung anfragen")], door="Images/hero-kontakt.webp", door_alt="Eingangsportal mit Bogentür am Abend")
page("ueber-uns.html","ueber-uns","Über uns · Iveria Immobilien, Makler in Wien","Über Iveria Immobilien — persönliche Immobilienvermittlung mit über zehn Jahren Erfahrung in Österreich.", ueber, preload="Images/hero-ueber-uns.webp", crumb="Über uns")

# =====================================================================
# KONTAKT
# =====================================================================
KONTAKT_TEL = (f'''        <div class="cblock"><h2 class="cbh">Telefon</h2><p class="v">{TEL_A}</p><p class="s">{cfg('oeffnungszeiten_anzeige')} · Termine nach Vereinbarung auch außerhalb.</p></div>\n''' if TEL_A else
               f'''        <div class="cblock"><h2 class="cbh">Erreichbarkeit</h2><p class="v" style="font-size:1.35rem">{cfg('oeffnungszeiten_anzeige')}</p><p class="s">Termine nach Vereinbarung auch außerhalb.</p></div>\n''')
KONTAKT_ADR = "<br>".join(_html.escape(x) for x in [cfg('firmenname'), cfg('strasse'), " ".join(y for y in [cfg('plz'), cfg('ort')] if y)] if x)
KONTAKT_WA = (f'''        <div class="cblock"><h2 class="cbh">WhatsApp</h2><p class="v"><a href="{WA_URL}" target="_blank" rel="noopener">+{cfg('whatsapp_e164')}</a></p><p class="s">Schnelle Rückfragen, Terminbestätigungen, kurze Updates.</p></div>\n''' if WA_URL else '')
_btns = ([BTN(f"tel:{cfg('telefon_e164')}","Anrufen →","solid")] if TEL_A else []) + ([BTN(WA_URL,"WhatsApp","",' target="_blank" rel="noopener"')] if WA_URL else [])
kontakt = phero("Images/hero-kontakt.webp","Eingangsportal mit Bogentür am Abend","Kontakt","Schreiben Sie <em>uns</em>.","Erstgespräch immer kostenfrei und unverbindlich. Wir melden uns innerhalb von 24 Stunden.") + f'''
<section class="pad">
  <div class="wrap">
    <div class="contact-grid">
      <div data-rise>
        <div class="cblock"><h2 class="cbh">E-Mail</h2><p class="v"><a href="mailto:{cfg('email')}">{cfg('email')}</a></p><p class="s">Für Bauträgeranfragen: <a href="mailto:{cfg('email_projekte')}">{cfg('email_projekte')}</a></p></div>
{KONTAKT_TEL}        <div class="cblock"><h2 class="cbh">Adresse</h2><p class="v" style="font-size:1.35rem">{KONTAKT_ADR}</p></div>
{KONTAKT_WA}      </div>
      <form class="form" data-form="kontakt" name="kontakt" method="POST" action="/danke.html" data-netlify="true" netlify-honeypot="bot-field" data-rise>
        <input type="hidden" name="form-name" value="kontakt">
        <div class="hp" aria-hidden="true"><label>Nicht ausfüllen <input name="bot-field" tabindex="-1" autocomplete="off"></label></div>
        <div class="frow">
          <div><label for="k-name">Name *</label><input type="text" id="k-name" name="name" autocomplete="name" required></div>
          <div><label for="k-email">E-Mail *</label><input type="email" id="k-email" name="email" autocomplete="email" required></div>
        </div>
        <div class="frow">
          <div><label for="k-tel">Telefon</label><input type="tel" id="k-tel" name="telefon" autocomplete="tel"></div>
          <div><label for="k-anliegen">Mein Anliegen *</label><select id="k-anliegen" name="anliegen" required><option value="">Bitte wählen</option><option>Verkauf einer Immobilie</option><option>Vermietung</option><option>Suche / Kauf</option><option>Bauträgervermarktung</option><option>Bewertung</option><option>Allgemeine Anfrage</option></select></div>
        </div>
        <div><label for="k-nachricht">Nachricht *</label><textarea id="k-nachricht" name="nachricht" required placeholder="Erzählen Sie uns kurz, worum es geht. Lage, Größe, Zeithorizont, was Ihnen wichtig ist."></textarea></div>
        <p class="note">{PRIV} * = Pflichtfeld</p>
        <button type="submit" class="btn">Nachricht senden →</button>
      </form>
    </div>
  </div>
</section>

''' + (cta("Persönlich","Lieber direkt <em>sprechen</em>?","Manche Fragen klären sich am besten am Telefon. Rufen Sie uns an oder schreiben Sie uns auf WhatsApp.", _btns) if _btns else '')
page("kontakt.html","kontakt","Kontakt &amp; Erstgespräch · Iveria Immobilien Wien","Kontaktieren Sie Iveria Immobilien. Erstgespräch kostenfrei und unverbindlich. Wir melden uns innerhalb von 24 Stunden.", kontakt, preload="Images/hero-kontakt.webp", crumb="Kontakt")

# =====================================================================
# RECHTLICHES
# =====================================================================
def legal(title_h1, lead, body):
    return f'''<section class="ehead warm">
  <div class="wrap-prose">
    <p class="eyebrow">Rechtliches</p>
    <h1 data-split>{title_h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>
<section class="pad-s">
  <div class="wrap-prose prose">
{body}
  </div>
</section>
'''
impressum_body = '''    <h2>Medieninhaber &amp; Diensteanbieter</h2>
    <p><strong>''' + ph('firmenname','Firmenname') + '''</strong><br>''' + ph('inhaber','Vorname Nachname') + '''<br>''' + ph('strasse','Straße Hausnummer') + '''<br>''' + ph('plz','PLZ') + ' ' + ph('ort','Ort') + ''', Österreich</p>
    <h2>Kontakt</h2>
    <p>Telefon: ''' + (TEL_A or '[Telefon]') + '''<br>E-Mail: <a href="mailto:''' + cfg('email') + '">' + cfg('email') + '''</a><br>Web: <a href="https://iveria.at">iveria.at</a></p>
    <h2>Unternehmensdaten</h2>
    <p><strong>Firmenbuchnummer:</strong> ''' + ph('firmenbuchnummer','FN') + '''<br><strong>Firmenbuchgericht:</strong> ''' + ph('firmenbuchgericht','zuständiges Gericht') + '''<br><strong>UID-Nummer:</strong> ''' + ph('uid','ATU') + '''<br><strong>Gewerbe:</strong> Immobilientreuhänder (Immobilienmakler, Immobilienverwalter, Bauträger) gem. § 117 GewO<br><strong>Gewerbebehörde:</strong> ''' + ph('gewerbebehoerde','Behörde') + '''<br><strong>Mitglied:</strong> Wirtschaftskammer Österreich, Fachgruppe der Immobilien- und Vermögenstreuhänder</p>
    <h2>Anwendbare Rechtsvorschriften</h2>
    <p>Es gelten die Bestimmungen der österreichischen Gewerbeordnung (GewO), des Maklergesetzes (MaklerG) sowie der Immobilienmaklerverordnung (IMV). Abrufbar unter <a href="https://www.ris.bka.gv.at" target="_blank" rel="noopener">ris.bka.gv.at</a>.</p>
    <h2>Aufsichtsbehörde</h2>
    <p>''' + ph('aufsichtsbehoerde','Bezirkshauptmannschaft / Magistrat') + '''</p>
    <h2>Berufshaftpflichtversicherung</h2>
    <p><strong>Versicherer:</strong> ''' + ph('versicherung','Versicherungsgesellschaft') + '''<br><strong>Geltungsbereich:</strong> Österreich</p>
    <h2>Streitbeilegung</h2>
    <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr" target="_blank" rel="noopener">ec.europa.eu/consumers/odr</a>. Wir sind nicht verpflichtet und nicht bereit, an einem Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
    <h2>Urheberrecht</h2>
    <p>Inhalte und Werke auf dieser Website unterliegen dem österreichischen Urheberrecht. Vervielfältigung, Bearbeitung, Verbreitung oder Verwertung außerhalb der Grenzen des Urheberrechts bedürfen unserer schriftlichen Zustimmung.</p>
    <h2>Bildnachweis</h2>
    <p>Einzelne Fotos stammen von <a href="https://www.pexels.com" target="_blank" rel="noopener">Pexels</a> und werden gemäß der Pexels-Lizenz verwendet.</p>
    <h2>Haftung für Inhalte</h2>
    <p>Die Inhalte dieser Website wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte übernehmen wir keine Gewähr. Als Diensteanbieter sind wir gemäß § 7 ECG für eigene Inhalte auf dieser Website nach den allgemeinen Gesetzen verantwortlich.</p>
    <h2>Haftung für Links</h2>
    <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist ohne konkreten Hinweis auf eine Rechtsverletzung nicht zumutbar.</p>'''
page("impressum.html","impressum","Impressum · Iveria Immobilien","Impressum von Iveria Immobilien gemäß § 25 MedienG und § 5 ECG.", legal("Impressum","Offenlegung gemäß § 25 MedienG und § 5 ECG.", impressum_body), crumb="Impressum")

datenschutz_body = '''    <h2>1. Verantwortlicher</h2>
    <p><strong>''' + ph('firmenname','Firmenwortlaut') + '''</strong><br>''' + ph('strasse','Straße Hausnummer') + '''<br>''' + ph('plz','PLZ') + ' ' + ph('ort','Ort') + ''', Österreich<br>E-Mail: <a href="mailto:''' + cfg('email') + '">' + cfg('email') + '''</a><br>Telefon: ''' + (TEL_A or '[Telefon]') + '''</p>
    <h2>2. Erhebung und Verarbeitung personenbezogener Daten</h2>
    <p>Wir verarbeiten personenbezogene Daten ausschließlich im Rahmen der gesetzlichen Bestimmungen. Insbesondere DSGVO, Datenschutzgesetz (DSG) und Telekommunikationsgesetz (TKG).</p>
    <h3>Bei Kontaktanfragen über Formulare oder E-Mail</h3>
    <p>Wenn Sie uns über das Kontaktformular oder per E-Mail kontaktieren, verarbeiten wir folgende Daten:</p>
    <ul>
      <li>Name, E-Mail-Adresse, Telefonnummer (sofern angegeben)</li>
      <li>Angaben zu Ihrer Anfrage und Immobilie</li>
      <li>Zeitpunkt der Anfrage</li>
    </ul>
    <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Anbahnung eines Vertragsverhältnisses) bzw. Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an der Beantwortung Ihrer Anfrage).</p>
    <h3>Bei Bewertungsanfragen</h3>
    <p>Zusätzlich zu den oben genannten Daten verarbeiten wir Angaben zu Ihrer Immobilie (Adresse, Größe, Zustand, Baujahr etc.) zur Erstellung einer Marktwerteinschätzung.</p>
    <h3>Bei Server-Zugriffen</h3>
    <p>Beim Aufruf unserer Website werden technisch notwendige Daten in Server-Logs erfasst (IP-Adresse, Datum, Uhrzeit, aufgerufene Seite, Browser, Betriebssystem). Diese Daten werden ausschließlich zur Sicherung des Betriebs verarbeitet und nach 30 Tagen gelöscht.</p>
    <h2>3. Cookies</h2>
    <p>Wir verwenden ausschließlich technisch notwendige Cookies. Etwa zur Speicherung Ihrer Cookie-Einstellung. Es werden <strong>keine Tracking- oder Marketing-Cookies</strong> eingesetzt.</p>
    <h2>4. Auftragsverarbeiter</h2>
    <p>Für den technischen Betrieb der Website nutzen wir folgende Dienstleister:</p>
    <ul>
      <li><strong>Netlify, Inc.</strong> (Hosting). Datenverarbeitung in den USA, abgesichert durch Standardvertragsklauseln und EU-US Data Privacy Framework.</li>
      <li><strong>Google Fonts</strong> (Schriftarten). Datenverarbeitung erfolgt direkt aus Ihrem Browser. Bei Aufruf wird Ihre IP-Adresse an Google übermittelt.</li>
    </ul>
    <p>Alle Bilder und Skripte dieser Website werden direkt von unserem Hosting-Anbieter ausgeliefert. Es werden keine Inhalte von weiteren Drittanbietern nachgeladen.</p>
    <h2>5. Speicherdauer</h2>
    <p>Wir speichern Ihre Daten nur solange, wie es für die jeweiligen Zwecke notwendig ist:</p>
    <ul>
      <li>Anfragen ohne Vertragsabschluss: bis zu 12 Monate</li>
      <li>Vertragsdaten: 7 Jahre (gem. § 132 BAO)</li>
      <li>Server-Logs: 30 Tage</li>
    </ul>
    <h2>6. Ihre Rechte</h2>
    <p>Sie haben jederzeit das Recht auf:</p>
    <ul>
      <li><strong>Auskunft</strong> über die zu Ihrer Person verarbeiteten Daten (Art. 15 DSGVO)</li>
      <li><strong>Berichtigung</strong> unrichtiger Daten (Art. 16 DSGVO)</li>
      <li><strong>Löschung</strong> Ihrer Daten (Art. 17 DSGVO)</li>
      <li><strong>Einschränkung</strong> der Verarbeitung (Art. 18 DSGVO)</li>
      <li><strong>Datenübertragbarkeit</strong> (Art. 20 DSGVO)</li>
      <li><strong>Widerspruch</strong> gegen die Verarbeitung (Art. 21 DSGVO)</li>
    </ul>
    <p>Bitte richten Sie entsprechende Anfragen an <a href="mailto:office@iveria.at">office@iveria.at</a>.</p>
    <h2>7. Beschwerderecht</h2>
    <p>Sie haben das Recht, sich bei der österreichischen Datenschutzbehörde zu beschweren:</p>
    <p><strong>Österreichische Datenschutzbehörde</strong><br>Barichgasse 40-42, 1030 Wien<br>Telefon: +43 1 52 152-0<br>E-Mail: <a href="mailto:dsb@dsb.gv.at">dsb@dsb.gv.at</a><br>Web: <a href="https://www.dsb.gv.at" target="_blank" rel="noopener">dsb.gv.at</a></p>
    <h2>8. Aktualität dieser Erklärung</h2>
    <p>Diese Datenschutzerklärung hat den Stand <strong>[Datum]</strong>. Durch Weiterentwicklung unserer Website oder gesetzliche Änderungen kann eine Anpassung erforderlich werden.</p>'''
page("datenschutz.html","datenschutz","Datenschutz · Iveria Immobilien","Datenschutzerklärung gemäß DSGVO. Information zur Verarbeitung Ihrer personenbezogenen Daten bei Iveria Immobilien.", legal("Datenschutzerklärung","Information zur Verarbeitung Ihrer personenbezogenen Daten gemäß DSGVO.", datenschutz_body), crumb="Datenschutz")

# =====================================================================
# DANKE / 404
# =====================================================================
danke = f'''<section class="cta dark center" style="min-height:100svh;display:grid;align-items:center;padding-block:18vh 12vh">
  <div class="wrap-narrow">
    {ARCHLINE}
    <p class="eyebrow">Vielen Dank</p>
    <h1 data-split style="font-size:clamp(2.6rem,5.6vw,5.4rem);line-height:1.02;margin:1.4rem auto 2rem;max-width:14ch">Ihre Nachricht ist <em>angekommen</em>.</h1>
    <p class="lead" style="margin:0 auto 2.6rem">Wir melden uns innerhalb von 24 Stunden bei Ihnen. Meist deutlich schneller. Sollten Sie unsere Antwort nicht im Posteingang finden, prüfen Sie bitte Ihren Spam-Ordner.</p>
    <div class="btns">{BTN("index.html","Zurück zur Startseite →","solid")}{BTN("kaufen.html","Aktuelle Objekte ansehen")}</div>
  </div>
</section>
'''
page("danke.html","danke","Vielen Dank · Iveria Immobilien","Ihre Nachricht ist bei Iveria Immobilien angekommen. Wir melden uns innerhalb von 24 Stunden.", danke, noindex=True)

notfound = f'''<section class="cta dark center" style="min-height:100svh;display:grid;align-items:center;padding-block:18vh 12vh">
  <div class="wrap-narrow">
    <p class="eyebrow">Fehler 404</p>
    <div class="big-num" aria-hidden="true">404</div>
    <h1 data-split style="font-size:clamp(2.2rem,4.4vw,3.8rem);line-height:1.05;margin:1.4rem auto 2rem;max-width:16ch">Seite nicht <em>gefunden</em>.</h1>
    <p class="lead" style="margin:0 auto 2.6rem">Die Seite, die Sie suchen, existiert nicht oder wurde verschoben. Vielleicht hilft Ihnen einer der folgenden Wege weiter.</p>
    <div class="btns">{BTN("index.html","Zur Startseite →","solid")}{BTN("kontakt.html","Kontakt")}</div>
  </div>
</section>
'''
page("404.html","404","Seite nicht gefunden · Iveria Immobilien","Die gesuchte Seite existiert nicht. Zurück zur Startseite von Iveria Immobilien.", notfound, noindex=True)


# =====================================================================
# SITEMAP (lastmod = letzter Commit der jeweiligen Seite, sonst heute)
# =====================================================================
def lastmod(fname):
    try:
        d = subprocess.run(['git', '-C', OUT, 'log', '-1', '--format=%cs', '--', fname], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', '-C', OUT, 'status', '--porcelain', '--', fname], capture_output=True, text=True).stdout.strip()
        if d and not dirty: return d
    except Exception: pass
    return datetime.date.today().isoformat()
PRIO = {'index.html': ('weekly', '1.0'), 'verkaufen.html': ('monthly', '0.9'), 'kaufen.html': ('weekly', '0.9'), 'bautraeger.html': ('monthly', '0.9'),
        'bewertung.html': ('monthly', '0.8'), 'ueber-uns.html': ('monthly', '0.7'), 'kontakt.html': ('monthly', '0.7'), 'impressum.html': ('yearly', '0.3'), 'datenschutz.html': ('yearly', '0.3')}
urls = []
for fname, url in PAGES:
    if fname not in PRIO: continue
    cf, pr = PRIO[fname]
    urls.append(f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod(fname)}</lastmod>\n    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>')
open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
print('geschrieben sitemap.xml', len(urls), 'URLs')

# =====================================================================
# llms.txt (nur Fakten, die auch auf der Website stehen)
# =====================================================================
kontakt_z = [f"- E-Mail: {cfg('email')}", f"- Bauträgeranfragen: {cfg('email_projekte')}"]
if cfg('telefon_anzeige'): kontakt_z.append(f"- Telefon: {cfg('telefon_anzeige')}")
kontakt_z.append(f"- Adresse: {', '.join(x for x in [cfg('firmenname'), ADR_ZEILE] if x)}")
kontakt_z.append(f"- Erreichbarkeit: {cfg('oeffnungszeiten_anzeige')}")
kontakt_z.append(f"- Kontaktformular: {DOMAIN}/kontakt.html")
llms = f"""# {cfg('firmenname')}

> Persönliche Immobilienvermittlung und Projektvermarktung in Österreich. Verkauf, Vermietung, Bauträgervermarktung und Bewertung von Immobilien, mit Sitz in Wien.

## Leistungen

- [Verkaufen & Vermieten]({DOMAIN}/verkaufen.html): Vom Erstgespräch bis zur Schlüsselübergabe. Volle Vermarktung ohne Aufpreis, Provision nur im Erfolgsfall.
- [Suchen & Kaufen]({DOMAIN}/kaufen.html): Aktuelle Objekte und persönlicher Suchauftrag, bevor Objekte öffentlich werden.
- [Bauträgervermarktung]({DOMAIN}/bautraeger.html): Vermarktung kompletter Wohnprojekte von der Konzeptphase bis zur Übergabe.
- [Bewertung]({DOMAIN}/bewertung.html): Kostenfreie Schnellbewertung online oder Bewertung vor Ort (€ 290 bis € 490, bei späterem Verkaufsmandat verrechenbar).
- [Über uns]({DOMAIN}/ueber-uns.html): Über zehn Jahre Erfahrung im österreichischen Immobilienmarkt.

## Einzugsgebiet

Wien, Niederösterreich, Burgenland und Kärnten.

## Kontakt

""" + "\n".join(kontakt_z) + "\n"
open(os.path.join(OUT, 'llms.txt'), 'w').write(llms)
print('geschrieben llms.txt')

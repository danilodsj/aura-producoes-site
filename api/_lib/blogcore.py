"""Motor do blog: lê os artigos em api/_content/posts/*.md e gera o HTML.

Usado pela função da Vercel (api/blog.py), que publica cada artigo
automaticamente quando a data dele chega (horário de Brasília), e pelo
preview local (scripts/build-blog.py).
"""
import datetime, html, json, pathlib, re
from email.utils import format_datetime

CONTENT = pathlib.Path(__file__).resolve().parent.parent / '_content'
SITE = 'https://auraproducoeseeventos.com.br'
BRT = datetime.timezone(datetime.timedelta(hours=-3))  # Brasil sem horário de verão
WHATS = 'https://wa.me/5521969076484'
PAGES = json.loads((CONTENT / 'services.json').read_text(encoding='utf-8'))
SERVICES = {p['slug']: p for p in PAGES}
MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

def today(): return datetime.datetime.now(BRT).date()

def esc(x): return html.escape(str(x), quote=True)

# ---------------- leitura dos posts ----------------
def parse_post(path):
    raw = path.read_text(encoding='utf-8')
    m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
    if not m: raise SystemExit(f'{path.name}: falta o cabeçalho entre ---')
    meta = {}
    for line in m.group(1).splitlines():
        line = re.sub(r'\s+#.*$', '', line)
        if ':' in line:
            k, v = line.split(':', 1); meta[k.strip()] = v.strip().strip('"')
    for k in ('title', 'description', 'slug', 'date'):
        if not meta.get(k): raise SystemExit(f'{path.name}: falta "{k}" no cabeçalho')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', meta['slug']): raise SystemExit(f'{path.name}: slug inválido')
    if meta.get('service') and meta['service'] not in SERVICES: raise SystemExit(f'{path.name}: service "{meta["service"]}" não existe')
    try:
        meta['date'] = datetime.date.fromisoformat(meta['date'])
        meta['updated'] = datetime.date.fromisoformat(meta['updated']) if meta.get('updated') else meta['date']
    except ValueError:
        raise SystemExit(f'{path.name}: data inválida (use AAAA-MM-DD)')
    meta['tags'] = [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]
    meta['draft'] = meta.get('draft', 'false').lower() == 'true'
    meta['body'] = m.group(2).strip()
    meta['file'] = path.name
    return meta

# ---------------- markdown mínimo ----------------
def inline(t):
    t = esc(t)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m.group(2)}"' + (' rel="noopener"' if m.group(2).startswith('http') else '') + f'>{m.group(1)}</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<em>\1</em>', t)
    return t

def slugify(t):
    import unicodedata
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def markdown(md):
    out, toc, faq = [], [], []
    blocks = re.split(r'\n\s*\n', md)
    in_faq, cur_q = False, None
    for b in blocks:
        b = b.strip('\n')
        if not b: continue
        h = re.match(r'(#{2,3}) (.+)', b)
        if h and '\n' not in b:
            lvl, txt = len(h.group(1)), h.group(2).strip()
            hid = slugify(txt)
            if lvl == 2:
                toc.append((hid, txt)); in_faq = txt.lower().startswith('perguntas frequentes'); cur_q = None
            elif in_faq:
                cur_q = {'q': txt, 'a': []}; faq.append(cur_q)
            out.append(f'<h{lvl} id="{hid}">{inline(txt)}</h{lvl}>'); continue
        lines = b.split('\n')
        if all(re.match(r'[-*] ', l) for l in lines):
            out.append('<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in lines) + '</ul>')
        elif all(re.match(r'\d+\. ', l) for l in lines):
            out.append('<ol>' + ''.join(f'<li>{inline(re.sub(r"^\d+\. ", "", l))}</li>' for l in lines) + '</ol>')
        elif all(l.startswith('>') for l in lines):
            out.append('<blockquote><p>' + inline(' '.join(l.lstrip('> ') for l in lines)) + '</p></blockquote>')
        else:
            txt = ' '.join(lines); out.append(f'<p>{inline(txt)}</p>')
            if cur_q is not None: cur_q['a'].append(re.sub(r'<[^>]+>', '', inline(txt)))
    return '\n'.join(out), toc, faq

def reading_time(md): return max(1, round(len(re.findall(r'\w+', md)) / 200))
def data_br(d): return f'{d.day} de {MESES[d.month - 1]} de {d.year}'

# ---------------- layout ----------------
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Michroma&family=Sora:wght@300;400;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">'
CSS = """
:root{--night:#0f0a1e;--night-2:#1a1330;--line:#2a2238;--cream:#f3efe6;--muted:#b9b2c9;--pink:#e0218a;--cyan:#12b5f0}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--night);color:var(--cream);font-family:'Sora',sans-serif;font-weight:300;line-height:1.7;font-size:17px}
a{color:var(--cyan)}a:hover{color:#4cc9f5}
.wrap{padding-left:5%;padding-right:5%}
header.site{border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;padding-top:12px;padding-bottom:12px}
.logo{display:inline-flex;align-items:center;gap:6px;text-decoration:none;color:var(--cream);font-family:'Michroma',sans-serif;font-size:36px;line-height:1}
.logo img{display:block}
nav.main{display:flex;flex-wrap:wrap;gap:4px}
nav.main a{font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);text-decoration:none;padding:10px}
nav.main a:hover,nav.main a[aria-current]{color:var(--cream)}
.cta{display:inline-block;background:var(--pink);color:var(--cream);text-decoration:none;font-family:'Michroma',sans-serif;font-size:13px;letter-spacing:.15em;text-transform:uppercase;padding:16px 28px}
.cta:hover{background:#ec4fa3;color:var(--cream)}
.eyebrow{font-family:'Space Mono',monospace;font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--cyan)}
h1,h2,h3{font-family:'Michroma',sans-serif;font-weight:400;letter-spacing:.02em;line-height:1.2}
h1{font-size:clamp(26px,5vw,46px);margin:12px 0 16px}
.article{max-width:760px;margin:0 auto;padding:48px 0 64px}
.article h2{font-size:clamp(20px,3vw,26px);margin:48px 0 12px}
.article h3{font-size:18px;margin:32px 0 8px}
.article p,.article li{color:#ddd7ea}
.article strong{color:var(--cream);font-weight:600}
.article blockquote{margin:24px 0;padding:4px 24px;border-left:3px solid var(--pink);background:var(--night-2)}
.meta{font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.1em;color:var(--muted)}
.crumbs{font-family:'Space Mono',monospace;font-size:12px;color:var(--muted)}
.crumbs a{color:var(--muted)}
.hero-img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block;border:1px solid var(--line);margin:24px 0 8px}
.toc{background:var(--night-2);border:1px solid var(--line);padding:16px 24px;margin:24px 0}
.toc strong{font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.2em;color:var(--muted);font-weight:700}
.toc ol{margin:8px 0 0;padding-left:20px}.toc li{margin:4px 0}
.box{background:var(--night-2);border:1px solid var(--line);border-top:2px solid var(--pink);padding:28px;margin:48px 0}
.box h2{margin-top:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px;margin:32px 0 64px}
.card{background:var(--night-2);border:1px solid var(--line);text-decoration:none;color:var(--cream);display:flex;flex-direction:column}
.card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;border-bottom:2px solid var(--pink)}
.card div{padding:20px 22px 24px}
.card h2,.card h3{font-size:17px;margin:8px 0;color:var(--cream)}
.card p{color:var(--muted);font-size:15px;margin:0}
footer.site{border-top:1px solid var(--line);padding:32px 0;color:var(--muted);font-size:14px}
footer.site .wrap{display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between}
"""

def page(title, desc, url, body, ld, image=None, og_type='website', extra_head=''):
    image = image or SITE + '/og-image.jpg'
    short = {'mobilia-para-eventos': 'Mobília', 'plataforma-360': '360°', 'pequeno-tequileiro': 'Tequileiro', 'story-maker': 'Story Maker', 'podcast-para-eventos': 'Podcast', 'chopeira-movel': 'Chopeira'}
    nav = ''.join(f'<a href="/{p["slug"]}">{esc(short.get(p["slug"], p["name"]))}</a>' for p in PAGES)
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0f0a1e">
<meta property="og:type" content="{og_type}"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Aura Produções e Eventos">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Blog Aura" href="/blog/feed.xml">
{FONTS}
<style>{CSS}</style>
{extra_head}<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="site"><div class="wrap">
<a class="logo" href="/" aria-label="Aura Produções e Eventos — início"><img src="/img/aura-symbol-pink.svg" alt="" width="30" height="28"><span>UR</span><img src="/img/aura-symbol-cyan.svg" alt="" width="30" height="28"></a>
<nav class="main" aria-label="Serviços">{nav}<a href="/blog" aria-current="page">Blog</a></nav>
<a class="cta" rel="noopener" href="{WHATS}">Garantir minha data</a>
</div></header>
{body}
<footer class="site"><div class="wrap"><span>© {today().year} Aura Produções e Eventos · Rio de Janeiro</span><span><a href="{WHATS}" rel="noopener">WhatsApp (21) 96907-6484</a> · <a href="/blog">Blog</a></span></div></footer>
</body>
</html>
'''

ORG = {"@type": "Organization", "@id": SITE + "/#empresa", "name": "Aura Produções e Eventos", "url": SITE + "/", "logo": SITE + "/apple-touch-icon.png"}

def card(p, level='h2'):
    return (f'<a class="card" href="/blog/{p["slug"]}"><img src="{p.get("image") or "/og-image.jpg"}" alt="{esc(p.get("image_alt", ""))}" loading="lazy" width="400" height="250">'
            f'<div><span class="eyebrow">{data_br(p["date"])}</span><{level}>{esc(p["title"])}</{level}><p>{esc(p["description"])}</p></div></a>')

def build_post(p, posts):
    url = f'{SITE}/blog/{p["slug"]}'
    body_html, toc, faq = markdown(p['body'])
    svc = SERVICES.get(p.get('service'))
    img = p.get('image')
    toc_html = ('<nav class="toc" aria-label="Neste artigo"><strong>NESTE ARTIGO</strong><ol>' + ''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc) + '</ol></nav>') if len(toc) >= 3 else ''
    box = ''
    if svc:
        box = (f'<aside class="box"><span class="eyebrow">Aura Produções e Eventos</span><h2>{esc(svc["name"])} para o seu evento</h2>'
               f'<p>{esc(svc["desc"])}</p><p><a class="cta" rel="noopener" href="{WHATS}">Consultar disponibilidade</a> &nbsp; <a href="/{svc["slug"]}">Conheça o serviço →</a></p></aside>')
    others = [q for q in posts if q is not p]
    related = ([q for q in others if q.get('service') == p.get('service')] + [q for q in others if q.get('service') != p.get('service')])[:3]
    rel_html = ('<h2>Leia também</h2><div class="grid">' + ''.join(card(q, 'h3') for q in related) + '</div>') if related else ''
    graph = [{"@type": "BlogPosting", "headline": p['title'], "description": p['description'], "url": url, "mainEntityOfPage": url,
              "datePublished": p['date'].isoformat(), "dateModified": p['updated'].isoformat(), "inLanguage": "pt-BR",
              "image": SITE + img if img else SITE + '/og-image.jpg', "author": {"@id": SITE + "/#empresa"}, "publisher": {"@id": SITE + "/#empresa"},
              "keywords": ', '.join(p['tags'])}, ORG,
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"},
                 {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog"},
                 {"@type": "ListItem", "position": 3, "name": p['title'], "item": url}]}]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": ' '.join(f['a'])}} for f in faq if f['a']]})
    hero = f'<img class="hero-img" src="{img}" alt="{esc(p.get("image_alt", ""))}" width="1200" height="675" fetchpriority="high">' if img else ''
    body = f'''<main class="wrap"><article class="article">
<nav class="crumbs" aria-label="Você está em"><a href="/">Início</a> › <a href="/blog">Blog</a> › {esc(p["title"])}</nav>
<h1>{esc(p["title"])}</h1>
<p class="meta"><time datetime="{p["date"].isoformat()}">{data_br(p["date"])}</time> · {reading_time(p["body"])} min de leitura</p>
{hero}
{toc_html}
{body_html}
{box}
{rel_html}
</article></main>'''
    ld = {"@context": "https://schema.org", "@graph": graph}
    meta_extra = f'<meta property="article:published_time" content="{p["date"].isoformat()}">\n'
    return page(p['title'] + (' | Blog Aura' if len(p['title']) <= 48 else ''), p['description'], url, body, ld, SITE + img if img else None, 'article', meta_extra)

def build_index(posts):
    url = SITE + '/blog'
    title = 'Blog Aura | Ideias para Festas, Casamentos e Eventos no RJ'
    desc = 'Dicas e ideias para casamentos, 15 anos, aniversários e eventos corporativos: experiências, mobília, plataforma 360, chopp, tequila e conteúdo para redes sociais.'
    body = f'''<main class="wrap"><div style="padding:48px 0 0">
<span class="eyebrow">Blog</span>
<h1>Ideias para fazer a festa subir de nível</h1>
<p style="color:var(--muted);max-width:640px">Dicas práticas para casamentos, 15 anos, aniversários e eventos corporativos no Rio de Janeiro.</p>
</div>
<div class="grid">{"".join(card(p) for p in posts) or "<p>Em breve.</p>"}</div></main>'''
    ld = {"@context": "https://schema.org", "@graph": [{"@type": "Blog", "name": "Blog Aura", "url": url, "description": desc, "publisher": {"@id": SITE + "/#empresa"},
          "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": f'{SITE}/blog/{p["slug"]}', "datePublished": p['date'].isoformat()} for p in posts]}, ORG]}
    return page(title, desc, url, body, ld)

def build_feed(posts):
    items = ''.join(f'''<item><title>{esc(p["title"])}</title><link>{SITE}/blog/{p["slug"]}</link><guid>{SITE}/blog/{p["slug"]}</guid>
<pubDate>{format_datetime(datetime.datetime.combine(p["date"], datetime.time(9), BRT))}</pubDate><description>{esc(p["description"])}</description></item>
''' for p in posts)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Blog Aura Produções e Eventos</title><link>{SITE}/blog</link><description>Ideias para festas e eventos no RJ</description><language>pt-BR</language>
{items}</channel></rss>
'''

def build_sitemap(posts):
    urls = [(SITE + '/', '1.0', None, None)]
    urls += [(f'{SITE}/{p["slug"]}', '0.8', None, f'{SITE}/img/{p["img"]}.webp') for p in PAGES]
    urls.append((SITE + '/blog', '0.7', posts[0]['updated'] if posts else None, None))
    urls += [(f'{SITE}/blog/{p["slug"]}', '0.6', p['updated'], SITE + p['image'] if p.get('image') else None) for p in posts]
    rows = []
    for loc, pr, lm, img in urls:
        r = f'  <url><loc>{loc}</loc>' + (f'<lastmod>{lm.isoformat()}</lastmod>' if lm else '') + f'<priority>{pr}</priority>'
        if img: r += f'<image:image><image:loc>{img}</image:loc></image:image>'
        rows.append(r + '</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + '\n'.join(rows) + '\n</urlset>\n')

_cache = {}

def all_posts():
    files = sorted((CONTENT / 'posts').glob('*.md'))
    key = tuple((f.name, f.stat().st_mtime) for f in files)
    if _cache.get('key') != key:
        posts = [parse_post(f) for f in files]
        slugs = [p['slug'] for p in posts]
        dup = {x for x in slugs if slugs.count(x) > 1}
        if dup: raise SystemExit(f'slugs repetidos: {dup}')
        _cache.update(key=key, posts=posts)
    return _cache['posts']

def published(day=None):
    day = day or today()
    return sorted([p for p in all_posts() if not p['draft'] and p['date'] <= day], key=lambda p: (p['date'], p['slug']), reverse=True)

def seconds_to_midnight():
    now = datetime.datetime.now(BRT)
    nxt = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0, 0, 5), BRT)
    return max(60, int((nxt - now).total_seconds()))

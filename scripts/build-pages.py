"""Gera uma página HTML por serviço a partir de index.html.

Uso: python3 scripts/build-pages.py   (rodar na raiz do repositório após editar index.html)
Cada página tem título, descrição, canonical, prévia de compartilhamento, dados
estruturados e texto sem JavaScript próprios, e abre direto no serviço.
"""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://auraproducoeseeventos.com.br'
HOME_TITLE = 'Aura Produções e Eventos | Mobília, Plataforma 360 e Experiências para Festas no RJ'
HOME_DESC = ('Aura Produções e Eventos no Rio de Janeiro: mobília para eventos, plataforma 360°, tequileiro, '
             'story maker, podcast do evento e chopeira móvel para casamentos, 15 anos, aniversários e eventos corporativos.')

PAGES = json.loads((ROOT / 'api' / '_content' / 'services.json').read_text(encoding='utf-8'))

def esc(x): return html.escape(x, quote=True)

def head_block(title, desc, url, image, ld):
    return (f'<title>{esc(title)}</title>\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<meta name="description" content="{esc(desc)}">\n'
      f'<link rel="canonical" href="{url}">\n'
      '<meta name="robots" content="index, follow, max-image-preview:large">\n'
      '<meta name="theme-color" content="#0f0a1e">\n'
      '<meta property="og:type" content="website">\n<meta property="og:locale" content="pt_BR">\n'
      '<meta property="og:site_name" content="Aura Produções e Eventos">\n'
      f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:description" content="{esc(desc)}">\n'
      f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{image}">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
      f'<meta name="twitter:title" content="{esc(title)}">\n<meta name="twitter:description" content="{esc(desc)}">\n'
      f'<meta name="twitter:image" content="{image}">\n'
      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')

HEAD_RE = re.compile(r'<title>.*?</title>\n.*?<script type="application/ld\+json">.*?</script>\n', re.S)
STATIC_RE = re.compile(r'<main id="__bundler_placeholder".*?</main>', re.S)

def nav_links(current):
    links = ''.join(f'<li><a href="/{p["slug"]}" style="color:#12b5f0">{p["name"]}</a></li>' for p in PAGES if p['slug'] != current)
    return f'<h2>Serviços</h2><ul>{links}</ul>'

def static_main(h1, paras, current):
    ps = ''.join(f'<p>{esc(p)}</p>' for p in paras)
    home = '' if current is None else '<p><a href="/" style="color:#12b5f0">← Aura Produções e Eventos</a></p>'
    return (f'<main id="__bundler_placeholder" style="max-width:720px;padding:24px;font-family:sans-serif;color:#f3efe6">'
            f'{home}<h1>{esc(h1)}</h1>{ps}{nav_links(current)}'
            '<p><a href="/blog" style="color:#12b5f0">Blog: ideias para festas e eventos</a></p><p><a href="https://wa.me/5521969076484" style="color:#12b5f0">WhatsApp (21) 96907-6484</a></p></main>')

def build(src, title, desc, url, image, ld, page_id, main_html):
    s = src
    m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', s, re.S)
    t = json.loads(m.group(2))
    t, n = HEAD_RE.subn(lambda _: head_block(title, desc, url, image, ld), t, count=1); assert n == 1
    t, n = re.subn(r"this\.state = \{ page: [^}]*\}", f"this.state = {{ page: '{page_id}' }}", t, count=1); assert n == 1
    enc = json.dumps(t, ensure_ascii=False).replace('</', '<\\u002F')
    s = s[:m.start(2)] + enc + s[m.end(2):]
    s, n = HEAD_RE.subn(lambda _: head_block(title, desc, url, image, ld).rstrip('\n').replace('\n', '\n  ') + '\n', s, count=1); assert n == 1
    s, n = STATIC_RE.subn(lambda _: main_html, s, count=1); assert n == 1
    return s

def main():
    src = (ROOT / 'index.html').read_text(encoding='utf-8')
    org = {"@type": "LocalBusiness", "@id": SITE + "/#empresa", "name": "Aura Produções e Eventos", "url": SITE + "/",
           "telephone": "+55 21 96907-6484", "image": SITE + "/og-image.jpg",
           "address": {"@type": "PostalAddress", "addressRegion": "RJ", "addressCountry": "BR"},
           "areaServed": {"@type": "State", "name": "Rio de Janeiro"}}
    # Home: reescreve só o conteúdo sem JS (links para as páginas) e o estado inicial
    home_ld = dict({"@context": "https://schema.org"}, **org, description=HOME_DESC,
                   hasOfferCatalog={"@type": "OfferCatalog", "name": "Serviços para eventos",
                                    "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": p['name'], "url": f"{SITE}/{p['slug']}"}} for p in PAGES]})
    home_main = static_main('Aura Produções e Eventos: seu evento merece ser inesquecível',
                            ['Casamentos, aniversários, 15 anos e eventos corporativos no Rio de Janeiro. Escolha as experiências e monte o seu pacote.'], None)
    (ROOT / 'index.html').write_text(build(src, HOME_TITLE, HOME_DESC, SITE + '/', SITE + '/og-image.jpg', home_ld, 'home', home_main), encoding='utf-8')
    for p in PAGES:
        url = f"{SITE}/{p['slug']}"
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": p['name'], "serviceType": p['name'], "description": p['desc'], "url": url,
             "image": f"{SITE}/img/{p['img']}.webp", "provider": {"@id": SITE + "/#empresa"},
             "areaServed": {"@type": "State", "name": "Rio de Janeiro"}},
            org,
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": p['name'], "item": url}]}]}
        out = build(src, p['title'], p['desc'], url, f"{SITE}/img/{p['img']}.webp", ld, p['id'], static_main(p['h1'], [p['body']], p['slug']))
        (ROOT / f"{p['slug']}.html").write_text(out, encoding='utf-8')
    print('ok:', ', '.join(p['slug'] for p in PAGES))

if __name__ == '__main__':
    main()

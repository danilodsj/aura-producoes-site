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

PAGES = [
  dict(id='moveis', slug='mobilia-para-eventos', name='Mobília para eventos', img='mobilia',
       title='Mobília para Eventos no RJ | Cadeiras, Mesas e Lounges | Aura',
       desc='Aluguel de mobília para eventos no Rio de Janeiro: cadeiras Tiffany, Dior e Eiffel, mesas, bistrôs e lounges. Entrega, montagem e retirada inclusas.',
       h1='Mobília para eventos no Rio de Janeiro',
       body='Cadeiras, mesas, lounges e bistrôs para casamentos, aniversários, 15 anos e eventos corporativos. Trabalhamos com modelos Tiffany, Tiffany Cristal, Dior, Eiffel e Jacobsen, do clássico ao moderno. Entrega, montagem e retirada por nossa conta, e você pode juntar a mobília com as outras experiências da Aura no mesmo pacote.'),
  dict(id='p360', slug='plataforma-360', name='Plataforma 360', img='plataforma-360',
       title='Plataforma 360 para Festas e Casamentos no RJ | Aura',
       desc='Aluguel de plataforma 360° para casamentos, 15 anos e eventos no Rio de Janeiro. Vídeo em câmera lenta enviado na hora para o celular do convidado.',
       h1='Plataforma 360 para festas no Rio de Janeiro',
       body='Seus convidados sobem na plataforma e saem com um vídeo 360° em câmera lenta, com iluminação de palco e ring light, pronto para postar nos stories. O vídeo é enviado na hora para o celular do convidado e pode levar moldura e trilha com a identidade do seu evento.'),
  dict(id='teq', slug='pequeno-tequileiro', name='Pequeno Tequileiro', img='tequileiro',
       title='Tequileiro para Festas e Casamentos no RJ | Pequeno Tequileiro | Aura',
       desc='Contrate o Pequeno Tequileiro para sua festa no Rio de Janeiro: personagem caracterizado servindo tequila direto aos convidados, com animação e interação.',
       h1='Pequeno Tequileiro: tequila servida na pista',
       body='Uma experiência de tequila servida direto aos convidados, com atitude e muita animação. O personagem caracterizado circula entre os convidados, serve a dose onde a festa estiver acontecendo e cria momentos que viram foto, vídeo e história para contar.'),
  dict(id='story', slug='story-maker', name='Story Maker', img='story-maker',
       title='Story Maker para Casamentos e Eventos no RJ | Aura',
       desc='Story maker no Rio de Janeiro: um profissional produzindo stories e conteúdo para o Instagram dos noivos, do aniversariante ou da sua marca, em tempo real.',
       h1='Story Maker para casamentos e eventos',
       body='Você vive a festa e a gente conta a história. Um profissional dedicado produz stories e conteúdo para o Instagram dos noivos, do aniversariante ou da sua marca em tempo real, registrando os bastidores e os momentos mais importantes do evento.'),
  dict(id='pod', slug='podcast-para-eventos', name='Podcast do evento', img='podcast',
       title='Podcast para Casamentos e Eventos no RJ | Estúdio no Evento | Aura',
       desc='Estúdio de podcast dentro do seu evento no Rio de Janeiro: grave um episódio exclusivo com anfitrião e convidados, com histórias e homenagens. Edição inclusa.',
       h1='Podcast do evento: um estúdio dentro da sua festa',
       body='Montamos um estúdio de podcast dentro do evento, com microfones, câmeras e cenário, para gravar um episódio exclusivo com o anfitrião e os convidados: histórias, homenagens e risadas. O episódio editado é entregue depois do evento.'),
  dict(id='chopp', slug='chopeira-movel', name='Chopeira móvel', img='chopeira',
       title='Chopeira Móvel para Festas no RJ | Chopp na Mochila | Aura',
       desc='Chopeira móvel para festas e eventos no Rio de Janeiro: promoter com mochila de chopp servindo os convidados na pista, sempre gelado e sem fila.',
       h1='Chopeira móvel: o chopp vai até o convidado',
       body='Um promoter com mochila de chopp circula pela festa servindo os convidados onde eles estiverem: sem fila e sem sair da pista. A mochila térmica tira o chopp na hora, sempre gelado, e copos e mochila podem ser personalizados.'),
]

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
            '<p><a href="https://wa.me/5521969076484" style="color:#12b5f0">WhatsApp (21) 96907-6484</a></p></main>')

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
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
          f'  <url><loc>{SITE}/</loc><priority>1.0</priority></url>']
    sm += [f'  <url><loc>{SITE}/{p["slug"]}</loc><priority>0.8</priority><image:image><image:loc>{SITE}/img/{p["img"]}.webp</image:loc></image:image></url>' for p in PAGES]
    sm.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8')
    print('ok:', ', '.join(p['slug'] for p in PAGES))

if __name__ == '__main__':
    main()
